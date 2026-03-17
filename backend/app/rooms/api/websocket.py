"""
WebSocket connection manager and endpoint for real-time room communication.

Flow:
  1. Client opens WS /ws/{room_id}?token=<room_scoped_jwt>
  2. Server decodes the token; rejects (1008) if invalid or room_id mismatch.
  3. Server sends room_state to the new joiner.
  4. Server broadcasts player_joined to all existing members.
  5. Server listens for messages and routes them by their 'type' field.
  6. On disconnect, server broadcasts player_left.

Supported incoming event types:
  - dice_roll         { "type": "dice_roll", "sides": 20 }
  - dm_announcement   { "type": "dm_announcement", "content": "..." }  (DM only)
  - chat_message      { "type": "chat_message", "content": "..." }
  - start_session     { "type": "start_session" }  (DM only)

All outgoing messages are JSON objects with at least a "type" field.
"""

import json
import logging
import random
import uuid

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.campaigns.infrastructure.repositories import SqlAlchemyCampaignRepository
from app.core.exceptions import AuthenticationError
from app.db.session import SessionLocal
from app.dungeons.infrastructure.repositories import SQLAlchemyDungeonRepository
from app.rooms.infrastructure.repositories import SqlAlchemyRoomRepository
from app.users.infrastructure.auth import decode_access_token
from app.worlds.infrastructure.repositories import SQLAlchemyWorldRepository

logger = logging.getLogger(__name__)

ws_router = APIRouter(tags=["websocket"])


# ---------------------------------------------------------------------------
# In-memory connection manager (module-level singleton)
# ---------------------------------------------------------------------------


class ConnectionManager:
    """
    Tracks active WebSocket connections per room.

    State is in-memory only — restarting the server clears all connections.
    Each connection entry is a tuple of (websocket, user_id_str, role_str).
    """

    def __init__(self) -> None:
        # room_id_str → list of (WebSocket, user_id str, role str)
        self._rooms: dict[str, list[tuple[WebSocket, str, str]]] = {}

    async def connect(
        self, websocket: WebSocket, room_id: str, user_id: str, role: str
    ) -> None:
        await websocket.accept()
        self._rooms.setdefault(room_id, []).append((websocket, user_id, role))
        logger.info(
            "ConnectionManager.connect: user_id=%s role=%s joined room=%s",
            user_id,
            role,
            room_id,
        )

    def disconnect(self, websocket: WebSocket, room_id: str) -> str | None:
        """
        Removes the connection from the room. Returns the user_id of the
        disconnected client so the caller can broadcast player_left.
        """
        conns = self._rooms.get(room_id, [])
        for i, (ws, user_id, _) in enumerate(conns):
            if ws is websocket:
                conns.pop(i)
                logger.info(
                    "ConnectionManager.disconnect: user_id=%s left room=%s",
                    user_id,
                    room_id,
                )
                return user_id
        return None

    async def broadcast(self, room_id: str, message: dict[str, object]) -> None:
        """Sends a JSON message to every connected client in the room."""
        text = json.dumps(message)
        conns = self._rooms.get(room_id, [])
        # Collect dead connections for cleanup.
        dead: list[WebSocket] = []
        for ws, _, _ in conns:
            try:
                await ws.send_text(text)
            except Exception as exc:  # noqa: BLE001
                logger.warning("ConnectionManager.broadcast: send failed: %s", exc)
                dead.append(ws)
        if dead:
            self._rooms[room_id] = [
                (ws, uid, role) for ws, uid, role in conns if ws not in dead
            ]

    async def send_to(self, websocket: WebSocket, message: dict[str, object]) -> None:
        """Sends a JSON message to a single WebSocket client."""
        await websocket.send_text(json.dumps(message))

    def get_user_ids(self, room_id: str) -> list[str]:
        """Returns the user_id strings of everyone currently connected."""
        return [uid for _, uid, _ in self._rooms.get(room_id, [])]


# Module-level singleton — shared across all requests in this process.
connection_manager = ConnectionManager()


# ---------------------------------------------------------------------------
# Start session handler
# ---------------------------------------------------------------------------


async def _handle_start_session(
    websocket: WebSocket,
    room_id: uuid.UUID,
    room_id_str: str,
    manager: ConnectionManager,
) -> None:
    """
    Load the room's linked dungeon, campaign, and world then broadcast the
    dungeon_intro payload to all connections in the room.

    Uses a short-lived DB session scoped to this operation — WebSocket
    endpoints cannot use FastAPI's Depends(), so SessionLocal is called
    directly here. The session is closed in the finally block to avoid leaks.

    @param websocket   - The DM's WebSocket, used to send error events.
    @param room_id     - UUID of the room being started.
    @param room_id_str - String form of room_id used as the ConnectionManager key.
    @param manager     - The module-level ConnectionManager singleton.
    """
    db = SessionLocal()
    try:
        room_repo = SqlAlchemyRoomRepository(db)
        dungeon_repo = SQLAlchemyDungeonRepository(db)
        campaign_repo = SqlAlchemyCampaignRepository(db)
        world_repo = SQLAlchemyWorldRepository(db)

        room = room_repo.get_by_id(room_id)
        if room is None or room.dungeon_id is None:
            logger.warning(
                "_handle_start_session: room %s has no dungeon_id", room_id_str
            )
            await manager.send_to(
                websocket,
                {
                    "type": "error",
                    "detail": "Room has no dungeon linked. Assign a dungeon before starting.",
                },
            )
            return

        # Campaign is required to supply narrative context (world lore, tone,
        # themes) to the dungeon_intro broadcast.
        if room.campaign_id is None:
            logger.warning(
                "_handle_start_session: room %s has no campaign_id", room_id_str
            )
            await manager.send_to(
                websocket,
                {"type": "error", "message": "Room has no campaign linked."},
            )
            return

        dungeon = dungeon_repo.get_by_id(room.dungeon_id)
        if dungeon is None:
            logger.warning(
                "_handle_start_session: dungeon %s not found for room %s",
                room.dungeon_id,
                room_id_str,
            )
            await manager.send_to(
                websocket,
                {
                    "type": "error",
                    "detail": f"Dungeon {room.dungeon_id} not found.",
                },
            )
            return

        campaign = campaign_repo.get_by_id(room.campaign_id)
        if campaign is None:
            logger.warning(
                "_handle_start_session: campaign %s not found for room %s",
                room.campaign_id,
                room_id_str,
            )
            await manager.send_to(
                websocket,
                {
                    "type": "error",
                    "message": f"Campaign {room.campaign_id} not found.",
                },
            )
            return

        world = world_repo.get_by_id(campaign.world_id)
        if world is None:
            logger.warning(
                "_handle_start_session: world %s not found for campaign %s room %s",
                campaign.world_id,
                campaign.id,
                room_id_str,
            )
            await manager.send_to(
                websocket,
                {
                    "type": "error",
                    "message": f"World {campaign.world_id} not found.",
                },
            )
            return

        logger.info(
            "_handle_start_session: broadcasting dungeon_intro for "
            "room=%s dungeon=%s campaign=%s world=%s",
            room_id_str,
            dungeon.id,
            campaign.id,
            world.id,
        )
        await manager.broadcast(
            room_id_str,
            {
                "type": "dungeon_intro",
                "dungeon_name": dungeon.name,
                "premise": dungeon.premise,
                "quest": {
                    "name": dungeon.quest.name,
                    "description": dungeon.quest.description,
                    "stages": list(dungeon.quest.stages),
                },
                "rooms": [
                    {"name": r.name, "description": r.description}
                    for r in dungeon.rooms
                ],
                "world": {
                    "name": world.name,
                    "lore_summary": world.lore_summary,
                    "theme": world.theme.value,
                },
                "campaign": {
                    "name": campaign.name,
                    "tone": campaign.tone.value,
                    "themes": list(campaign.themes),
                },
            },
        )
    finally:
        db.close()


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------


@ws_router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: uuid.UUID,
    token: str = Query(..., description="Room-scoped JWT obtained at join/create time"),
) -> None:
    """
    Real-time room communication over WebSocket.

    Authentication: the client passes the room-scoped JWT as ?token=<jwt>.
    The token must have been issued for this specific room_id; cross-room
    tokens are rejected with close code 1008 (Policy Violation).
    """
    room_id_str = str(room_id)

    # -- Auth --
    try:
        payload = decode_access_token(token)
    except AuthenticationError:
        logger.warning("websocket_endpoint: invalid token for room=%s", room_id_str)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Ensure the token was issued for exactly this room.
    if payload.room_id != room_id:
        logger.warning(
            "websocket_endpoint: token room_id=%s does not match path room_id=%s",
            payload.room_id,
            room_id,
        )
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id_str = str(payload.user_id)
    role = payload.role

    # -- Accept + initial state --
    await connection_manager.connect(websocket, room_id_str, user_id_str, role)

    # Send the full player list to the newly connected client only.
    current_players = connection_manager.get_user_ids(room_id_str)
    await connection_manager.send_to(
        websocket,
        {"type": "room_state", "players": current_players},
    )

    # Broadcast to everyone else that a new player arrived.
    await connection_manager.broadcast(
        room_id_str,
        {"type": "player_joined", "user_id": user_id_str, "role": role},
    )

    # -- Message loop --
    try:
        while True:
            raw = await websocket.receive_text()

            try:
                message: dict[str, object] = json.loads(raw)
            except json.JSONDecodeError:
                await connection_manager.send_to(
                    websocket, {"type": "error", "detail": "Invalid JSON"}
                )
                continue

            event_type = message.get("type")
            logger.debug(
                "websocket_endpoint: room=%s user=%s event=%s",
                room_id_str,
                user_id_str,
                event_type,
            )

            if event_type == "dice_roll":
                # Server owns randomness — clients cannot spoof results.
                sides = message.get("sides", 20)
                sides_int = int(sides) if isinstance(sides, (int, float)) else 20
                sides_int = max(2, min(sides_int, 1000))
                result = random.randint(1, sides_int)
                await connection_manager.broadcast(
                    room_id_str,
                    {
                        "type": "dice_roll",
                        "user_id": user_id_str,
                        "sides": sides_int,
                        "result": result,
                    },
                )

            elif event_type == "dm_announcement":
                if role != "dm":
                    await connection_manager.send_to(
                        websocket,
                        {
                            "type": "error",
                            "detail": "Only the DM can send announcements",
                        },
                    )
                else:
                    content = str(message.get("content", ""))
                    await connection_manager.broadcast(
                        room_id_str,
                        {"type": "dm_announcement", "content": content},
                    )

            elif event_type == "chat_message":
                content = str(message.get("content", ""))
                await connection_manager.broadcast(
                    room_id_str,
                    {
                        "type": "chat_message",
                        "user_id": user_id_str,
                        "role": role,
                        "content": content,
                    },
                )

            elif event_type == "start_session":
                # Only the DM may start a session.
                if role != "dm":
                    await connection_manager.send_to(
                        websocket,
                        {
                            "type": "error",
                            "detail": "Only the DM can start a session",
                        },
                    )
                else:
                    await _handle_start_session(
                        websocket, room_id, room_id_str, connection_manager
                    )

            else:
                await connection_manager.send_to(
                    websocket,
                    {"type": "error", "detail": f"Unknown event type: {event_type!r}"},
                )

    except WebSocketDisconnect:
        left_user_id = connection_manager.disconnect(websocket, room_id_str)
        if left_user_id:
            await connection_manager.broadcast(
                room_id_str,
                {"type": "player_left", "user_id": left_user_id},
            )

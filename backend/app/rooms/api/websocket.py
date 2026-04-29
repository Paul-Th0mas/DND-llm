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
from app.dungeons.domain.models import DungeonRoom
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
# Room serializer for WebSocket broadcasts
# ---------------------------------------------------------------------------


def _room_to_broadcast(room: DungeonRoom) -> dict[str, object]:
    """Serialize a DungeonRoom into a broadcast-safe dict."""
    result: dict[str, object] = {
        "index": room.index,
        "room_type": room.room_type.value,
        "name": room.name,
        "description": room.description,
    }
    if room.enemies is not None:
        e = room.enemies
        result["enemies"] = {
            "initial": list(e.initial),
            "reinforcements": list(e.reinforcements),
            "trigger_condition": e.trigger_condition,
            "environmental_hazards": e.environmental_hazards,
            "boss": e.boss,
            "special_attacks": list(e.special_attacks),
        }
    if room.mechanics is not None:
        m = room.mechanics
        result["mechanics"] = {
            "skill_checks": [
                {
                    "type": sc.type,
                    "dc": sc.dc,
                    "on_success": sc.on_success,
                    "on_failure": sc.on_failure,
                }
                for sc in m.skill_checks
            ],
            "rest_benefit": m.rest_benefit,
            "victory_items": list(m.victory_items),
            "game_effects": [
                {
                    "effect_type": ge.effect_type.value,
                    "trigger": {
                        "trigger_action": ge.trigger.trigger_action,
                        "check_stat": ge.trigger.check_stat,
                        "dc": ge.trigger.dc,
                    },
                    "value": ge.value,
                    "status": ge.status,
                    "item_id": ge.item_id,
                }
                for ge in m.game_effects
            ],
        }
    if room.loot_table is not None:
        result["loot_table"] = [
            {
                "item": li.item,
                "quantity": li.quantity,
                "value": li.value,
                "rarity": li.rarity,
            }
            for li in room.loot_table
        ]
    if room.npc_data is not None:
        result["npc_data"] = [
            {
                "name": nd.name,
                "role": nd.role,
                "inventory": [{"item": i.item, "price": i.price} for i in nd.inventory],
                "interaction_dc": nd.interaction_dc,
            }
            for nd in room.npc_data
        ]
    return result


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
        qm = dungeon.quest_metadata
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
                # US-070: include quest_metadata fields if present.
                "global_modifiers": qm.global_modifiers if qm is not None else None,
                "environment": qm.environment if qm is not None else None,
            },
        )
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Dungeon progression handlers (US-069, US-070)
# ---------------------------------------------------------------------------


async def _handle_advance_room(
    websocket: WebSocket,
    room_id: uuid.UUID,
    room_id_str: str,
    message: dict[str, object],
    manager: ConnectionManager,
) -> None:
    """
    Handle advance_room: persist current_room_index and broadcast room_advanced.

    @param websocket   - The DM's WebSocket, for sending error events.
    @param room_id     - UUID of the room.
    @param room_id_str - String form of room_id for ConnectionManager.
    @param message     - The parsed WebSocket message dict.
    @param manager     - The module-level ConnectionManager singleton.
    """
    db = SessionLocal()
    try:
        room_repo = SqlAlchemyRoomRepository(db)
        dungeon_repo = SQLAlchemyDungeonRepository(db)

        room = room_repo.get_by_id(room_id)
        if room is None or room.dungeon_id is None:
            await manager.send_to(
                websocket,
                {
                    "type": "dungeon_not_found",
                    "detail": "No dungeon linked to this room.",
                },
            )
            return

        dungeon = dungeon_repo.get_by_id(room.dungeon_id)
        if dungeon is None:
            await manager.send_to(
                websocket,
                {
                    "type": "dungeon_not_found",
                    "detail": f"Dungeon {room.dungeon_id} not found.",
                },
            )
            return

        ri_raw = message.get("room_index")
        ri = ri_raw if isinstance(ri_raw, int) else -1
        if ri < 0 or ri >= len(dungeon.rooms):
            await manager.send_to(
                websocket,
                {
                    "type": "validation_error",
                    "detail": f"room_index {ri} is out of range.",
                },
            )
            return

        dungeon_repo.update_room_index(dungeon.id, ri)
        db.commit()
        logger.info(
            "_handle_advance_room: room=%s dungeon=%s advancing to index=%d",
            room_id_str,
            dungeon.id,
            ri,
        )
        target_room = dungeon.rooms[ri]
        await manager.broadcast(
            room_id_str,
            {
                "type": "room_advanced",
                "room_index": ri,
                "room": _room_to_broadcast(target_room),
            },
        )
    finally:
        db.close()


async def _handle_advance_quest_stage(
    websocket: WebSocket,
    room_id: uuid.UUID,
    room_id_str: str,
    message: dict[str, object],
    manager: ConnectionManager,
) -> None:
    """
    Handle advance_quest_stage: persist stage completion and broadcast quest_stage_advanced.

    @param websocket   - The DM's WebSocket, for sending error events.
    @param room_id     - UUID of the room.
    @param room_id_str - String form of room_id for ConnectionManager.
    @param message     - The parsed WebSocket message dict.
    @param manager     - The module-level ConnectionManager singleton.
    """
    db = SessionLocal()
    try:
        room_repo = SqlAlchemyRoomRepository(db)
        dungeon_repo = SQLAlchemyDungeonRepository(db)

        room = room_repo.get_by_id(room_id)
        if room is None or room.dungeon_id is None:
            await manager.send_to(
                websocket,
                {
                    "type": "dungeon_not_found",
                    "detail": "No dungeon linked to this room.",
                },
            )
            return

        dungeon = dungeon_repo.get_by_id(room.dungeon_id)
        if dungeon is None:
            await manager.send_to(
                websocket,
                {
                    "type": "dungeon_not_found",
                    "detail": f"Dungeon {room.dungeon_id} not found.",
                },
            )
            return

        si_raw = message.get("stage_index")
        si = si_raw if isinstance(si_raw, int) else -1
        if si < 0 or si >= len(dungeon.quest.stages):
            await manager.send_to(
                websocket,
                {
                    "type": "validation_error",
                    "detail": f"stage_index {si} is out of range.",
                },
            )
            return

        dungeon_repo.complete_quest_stage(dungeon.id, si)
        db.commit()
        logger.info(
            "_handle_advance_quest_stage: room=%s dungeon=%s completing stage=%d",
            room_id_str,
            dungeon.id,
            si,
        )
        await manager.broadcast(
            room_id_str,
            {
                "type": "quest_stage_advanced",
                "stage_index": si,
                "stage_text": dungeon.quest.stages[si],
            },
        )
    finally:
        db.close()


async def _handle_resolve_skill_check(
    websocket: WebSocket,
    room_id: uuid.UUID,
    room_id_str: str,
    message: dict[str, object],
    manager: ConnectionManager,
) -> None:
    """
    Handle resolve_skill_check: compare roll against DC and broadcast outcome.

    @param websocket   - The sender's WebSocket, for sending error events.
    @param room_id     - UUID of the room.
    @param room_id_str - String form of room_id for ConnectionManager.
    @param message     - The parsed WebSocket message dict.
    @param manager     - The module-level ConnectionManager singleton.
    """
    db = SessionLocal()
    try:
        room_repo = SqlAlchemyRoomRepository(db)
        dungeon_repo = SQLAlchemyDungeonRepository(db)

        room = room_repo.get_by_id(room_id)
        if room is None or room.dungeon_id is None:
            await manager.send_to(
                websocket,
                {
                    "type": "dungeon_not_found",
                    "detail": "No dungeon linked to this room.",
                },
            )
            return

        dungeon = dungeon_repo.get_by_id(room.dungeon_id)
        if dungeon is None:
            await manager.send_to(
                websocket,
                {
                    "type": "dungeon_not_found",
                    "detail": f"Dungeon {room.dungeon_id} not found.",
                },
            )
            return

        ri_raw = message.get("room_index")
        st_raw = message.get("skill_type")
        rr_raw = message.get("roll_result")

        if (
            not isinstance(ri_raw, int)
            or not isinstance(st_raw, str)
            or not isinstance(rr_raw, int)
        ):
            await manager.send_to(
                websocket,
                {
                    "type": "validation_error",
                    "detail": "room_index, skill_type, and roll_result are required.",
                },
            )
            return

        if ri_raw < 0 or ri_raw >= len(dungeon.rooms):
            await manager.send_to(
                websocket,
                {
                    "type": "validation_error",
                    "detail": f"room_index {ri_raw} is out of range.",
                },
            )
            return

        target_room = dungeon.rooms[ri_raw]
        mechanics = target_room.mechanics
        if mechanics is None or not mechanics.skill_checks:
            await manager.send_to(
                websocket,
                {
                    "type": "validation_error",
                    "detail": f"No skill checks in room {ri_raw}.",
                },
            )
            return

        # Case-insensitive match; first match wins.
        check = next(
            (c for c in mechanics.skill_checks if c.type.lower() == st_raw.lower()),
            None,
        )
        if check is None:
            await manager.send_to(
                websocket,
                {
                    "type": "validation_error",
                    "detail": f"No skill check of type '{st_raw}' found in room {ri_raw}.",
                },
            )
            return

        outcome = "success" if rr_raw >= check.dc else "failure"
        narrative = check.on_success if outcome == "success" else check.on_failure
        payload: dict[str, object] = {
            "type": "room_event_outcome",
            "room_index": ri_raw,
            "skill_type": st_raw,
            "roll_result": rr_raw,
            "dc": check.dc,
            "outcome": outcome,
        }
        if narrative is not None:
            payload["narrative"] = narrative

        logger.info(
            "_handle_resolve_skill_check: room=%s room_index=%d skill=%s roll=%d dc=%d outcome=%s",
            room_id_str,
            ri_raw,
            st_raw,
            rr_raw,
            check.dc,
            outcome,
        )
        await manager.broadcast(room_id_str, payload)
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

            elif event_type == "advance_room":
                # Only the DM may advance the active room (US-069).
                if role != "dm":
                    await connection_manager.send_to(
                        websocket,
                        {
                            "type": "permission_denied",
                            "detail": "Only the DM can advance rooms.",
                        },
                    )
                else:
                    await _handle_advance_room(
                        websocket, room_id, room_id_str, message, connection_manager
                    )

            elif event_type == "advance_quest_stage":
                # Only the DM may advance quest stages (US-069).
                if role != "dm":
                    await connection_manager.send_to(
                        websocket,
                        {
                            "type": "permission_denied",
                            "detail": "Only the DM can advance quest stages.",
                        },
                    )
                else:
                    await _handle_advance_quest_stage(
                        websocket, room_id, room_id_str, message, connection_manager
                    )

            elif event_type == "resolve_skill_check":
                # Any participant may submit a roll result (US-070).
                await _handle_resolve_skill_check(
                    websocket, room_id, room_id_str, message, connection_manager
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

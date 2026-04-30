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
from app.characters.infrastructure.repositories import SqlAlchemyCharacterRepository
from app.core.exceptions import AuthenticationError
from app.db.session import SessionLocal
from app.dungeons.domain.models import DungeonRoom, EffectType, GameEffect
from app.dungeons.infrastructure.repositories import SQLAlchemyDungeonRepository
from app.rooms.infrastructure.repositories import (
    SqlAlchemyPlayerStateRepository,
    SqlAlchemyRoomRepository,
)
from app.users.infrastructure.auth import decode_access_token
from app.users.infrastructure.repositories import SqlAlchemyUserRepository
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
    Each connection entry is a 4-tuple of (websocket, user_id_str, role_str, username_str).
    The username is cached at connect time to avoid repeated DB lookups per broadcast.
    """

    def __init__(self) -> None:
        # room_id_str -> list of (WebSocket, user_id str, role str, username str)
        self._rooms: dict[str, list[tuple[WebSocket, str, str, str]]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        room_id: str,
        user_id: str,
        role: str,
        username: str,
    ) -> None:
        await websocket.accept()
        self._rooms.setdefault(room_id, []).append(
            (websocket, user_id, role, username)
        )
        logger.info(
            "ConnectionManager.connect: user_id=%s username=%s role=%s joined room=%s",
            user_id,
            username,
            role,
            room_id,
        )

    def disconnect(self, websocket: WebSocket, room_id: str) -> tuple[str, str] | None:
        """
        Removes the connection from the room.
        Returns (user_id, username) of the disconnected client so the caller
        can broadcast player_left.
        """
        conns = self._rooms.get(room_id, [])
        for i, (ws, user_id, _, username) in enumerate(conns):
            if ws is websocket:
                conns.pop(i)
                logger.info(
                    "ConnectionManager.disconnect: user_id=%s left room=%s",
                    user_id,
                    room_id,
                )
                return (user_id, username)
        return None

    async def broadcast(self, room_id: str, message: dict[str, object]) -> None:
        """Sends a JSON message to every connected client in the room."""
        text = json.dumps(message)
        conns = self._rooms.get(room_id, [])
        # Collect dead connections for cleanup.
        dead: list[WebSocket] = []
        for ws, _, _, _ in conns:
            try:
                await ws.send_text(text)
            except Exception as exc:  # noqa: BLE001
                logger.warning("ConnectionManager.broadcast: send failed: %s", exc)
                dead.append(ws)
        if dead:
            self._rooms[room_id] = [
                (ws, uid, role, uname)
                for ws, uid, role, uname in conns
                if ws not in dead
            ]

    async def send_to(self, websocket: WebSocket, message: dict[str, object]) -> None:
        """Sends a JSON message to a single WebSocket client."""
        await websocket.send_text(json.dumps(message))

    def get_user_ids(self, room_id: str) -> list[str]:
        """Returns the user_id strings of everyone currently connected."""
        return [uid for _, uid, _, _ in self._rooms.get(room_id, [])]

    def get_username_for_user(self, room_id: str, user_id: str) -> str:
        """
        Returns the cached username for a connected user in the given room.
        Falls back to 'Unknown Player' if the user is not found.

        @param room_id - String key of the room.
        @param user_id - The user_id string to look up.
        @returns The cached display name.
        """
        for _, uid, _, uname in self._rooms.get(room_id, []):
            if uid == user_id:
                return uname
        return "Unknown Player"

    def get_players(self, room_id: str) -> list[dict[str, object]]:
        """
        Returns a list of player info dicts for all connected users in the room.
        Used to build the room_state payload with usernames (US-081).
        """
        return [
            {"user_id": uid, "username": uname, "connected": True}
            for _, uid, _, uname in self._rooms.get(room_id, [])
        ]


# Module-level singleton — shared across all requests in this process.
connection_manager = ConnectionManager()

# ---------------------------------------------------------------------------
# Player action helpers
# ---------------------------------------------------------------------------

# Maps skill/ability check names (lower-case) to AbilityScores field names.
_STAT_TO_ABILITY: dict[str, str] = {
    "strength": "strength",
    "athletics": "strength",
    "dexterity": "dexterity",
    "acrobatics": "dexterity",
    "stealth": "dexterity",
    "sleight of hand": "dexterity",
    "constitution": "constitution",
    "intelligence": "intelligence",
    "arcana": "intelligence",
    "history": "intelligence",
    "investigation": "intelligence",
    "nature": "intelligence",
    "religion": "intelligence",
    "wisdom": "wisdom",
    "animal handling": "wisdom",
    "insight": "wisdom",
    "medicine": "wisdom",
    "perception": "wisdom",
    "survival": "wisdom",
    "charisma": "charisma",
    "deception": "charisma",
    "intimidation": "charisma",
    "performance": "charisma",
    "persuasion": "charisma",
}


def _ability_modifier(score: int) -> int:
    """Compute D&D ability modifier: floor((score - 10) / 2)."""
    return (score - 10) // 2


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
                    "description": ge.description,
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
# Player action handler (US-073)
# ---------------------------------------------------------------------------


async def _handle_player_action(
    websocket: WebSocket,
    room_id: uuid.UUID,
    room_id_str: str,
    user_id_str: str,
    username: str,
    message: dict[str, object],
    manager: ConnectionManager,
) -> None:
    """
    Handle player:action -- match the submitted action against the current
    room's mechanics array, resolve dice math, apply effects, and broadcast
    outcomes.

    AC1-AC11 from US-073.

    @param websocket   - The player's WebSocket, for sending error events.
    @param room_id     - UUID of the room.
    @param room_id_str - String form of room_id for ConnectionManager.
    @param user_id_str - String form of the acting player's user_id.
    @param username    - Display name of the acting player (cached, US-081).
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

        # Resolve room index: use message field if valid, else current.
        ri_raw = message.get("room_index")
        room_idx = (
            ri_raw
            if isinstance(ri_raw, int) and 0 <= ri_raw < len(dungeon.rooms)
            else dungeon.current_room_index
        )
        target_room = dungeon.rooms[room_idx]

        action = str(message.get("action", "")).lower().strip()

        # Find all GameEffects matching the trigger_action (case-insensitive).
        matching: list[GameEffect] = []
        if target_room.mechanics is not None:
            matching = [
                ge
                for ge in target_room.mechanics.game_effects
                if ge.trigger.trigger_action.lower() == action
            ]

        if not matching:
            await manager.send_to(
                websocket,
                {
                    "type": "validation_error",
                    "detail": f"No mechanic found for action '{action}' in room {room_idx}.",
                },
            )
            return

        # Warn if multiple distinct DCs share the same trigger_action.
        if len({ge.trigger.dc for ge in matching}) > 1:
            logger.warning(
                "_handle_player_action: multiple mechanics with trigger_action='%s' "
                "in dungeon=%s room=%d; resolving against first trigger",
                action,
                dungeon.id,
                room_idx,
            )

        trigger = matching[0].trigger
        dc = trigger.dc
        narrative = matching[0].description or f"Action '{action}' resolved."

        # Resolve: roll if dc is set, else auto-success.
        roll: int | None = None
        if dc is not None:
            modifier = 0
            check_stat = trigger.check_stat
            if check_stat is not None:
                ability = _STAT_TO_ABILITY.get(check_stat.lower())
                if ability is not None and room.campaign_id is not None:
                    try:
                        user_uuid = uuid.UUID(user_id_str)
                        char_repo = SqlAlchemyCharacterRepository(db)
                        character = char_repo.get_by_campaign_and_owner(
                            room.campaign_id, user_uuid
                        )
                        if character is not None:
                            score: int = getattr(character.ability_scores, ability, 10)
                            modifier = _ability_modifier(score)
                        else:
                            logger.warning(
                                "_handle_player_action: no character for user=%s campaign=%s; modifier=0",
                                user_id_str,
                                room.campaign_id,
                            )
                    except Exception:  # noqa: BLE001
                        logger.warning(
                            "_handle_player_action: character lookup failed for user=%s; modifier=0",
                            user_id_str,
                        )
                else:
                    logger.warning(
                        "_handle_player_action: unknown check_stat='%s'; modifier=0",
                        check_stat,
                    )
            roll = random.randint(1, 20) + modifier
            outcome: str = "success" if roll >= dc else "failure"
        else:
            # No DC -- automatic success.
            outcome = "success"

        # On failure: only DAMAGE and APPLY_STATUS apply.
        _FAILURE_ONLY_APPLICABLE = {EffectType.DAMAGE, EffectType.APPLY_STATUS}
        effects_to_apply = [
            ge
            for ge in matching
            if outcome == "success" or ge.effect_type in _FAILURE_ONLY_APPLICABLE
        ]
        effects_applied = [ge.effect_type.value for ge in effects_to_apply]

        # Broadcast event:resolution to all participants (US-081: include username).
        await manager.broadcast(
            room_id_str,
            {
                "type": "event:resolution",
                "player_id": user_id_str,
                "username": username,
                "action": action,
                "roll": roll,
                "dc": dc,
                "outcome": outcome,
                "effects_applied": effects_applied,
                "narrative": narrative,
            },
        )
        logger.info(
            "_handle_player_action: room=%s room_idx=%d action='%s' roll=%s dc=%s outcome=%s",
            room_id_str,
            room_idx,
            action,
            roll,
            dc,
            outcome,
        )

        # Apply individual effects and send secondary broadcasts.
        # Re-use the same db session opened at the top of this handler.
        ps_repo = SqlAlchemyPlayerStateRepository(db)
        user_uuid_for_state = uuid.UUID(user_id_str)

        for ge in effects_to_apply:
            if ge.effect_type == EffectType.DAMAGE and ge.value is not None:
                # Load current persisted state; fall back to defaults for new players.
                existing = ps_repo.get_by_player(room_id, user_uuid_for_state)
                cur_int = existing.current_hp if existing is not None else 10
                max_int = existing.max_hp if existing is not None else 10
                statuses_list: list[str] = (
                    existing.status_effects if existing is not None else []
                )
                new_hp = max(0, cur_int - ge.value)
                downed_new = new_hp <= 0
                # Persist the new HP state. Failure is non-blocking — broadcast still proceeds.
                try:
                    ps_repo.upsert(
                        room_id,
                        user_uuid_for_state,
                        new_hp,
                        max_int,
                        downed_new,
                        statuses_list,
                    )
                    db.commit()
                except Exception as persist_exc:  # noqa: BLE001
                    logger.error(
                        "_handle_player_action: DAMAGE upsert failed user=%s room=%s: %s",
                        user_id_str,
                        room_id_str,
                        persist_exc,
                    )
                    db.rollback()
                await manager.broadcast(
                    room_id_str,
                    {
                        "type": "state:player_update",
                        "player_id": user_id_str,
                        "username": username,
                        "current_hp": new_hp,
                        "max_hp": max_int,
                        "downed": downed_new,
                        "status_effects": statuses_list,
                    },
                )
            elif ge.effect_type == EffectType.APPLY_STATUS and ge.status is not None:
                existing2 = ps_repo.get_by_player(room_id, user_uuid_for_state)
                cur2_int = existing2.current_hp if existing2 is not None else 10
                max2_int = existing2.max_hp if existing2 is not None else 10
                downed2_bool = existing2.downed if existing2 is not None else False
                statuses: list[str] = (
                    list(existing2.status_effects) if existing2 is not None else []
                )
                if ge.status not in statuses:
                    statuses.append(ge.status)
                try:
                    ps_repo.upsert(
                        room_id,
                        user_uuid_for_state,
                        cur2_int,
                        max2_int,
                        downed2_bool,
                        statuses,
                    )
                    db.commit()
                except Exception as persist_exc2:  # noqa: BLE001
                    logger.error(
                        "_handle_player_action: APPLY_STATUS upsert failed user=%s room=%s: %s",
                        user_id_str,
                        room_id_str,
                        persist_exc2,
                    )
                    db.rollback()
                await manager.broadcast(
                    room_id_str,
                    {
                        "type": "state:player_update",
                        "player_id": user_id_str,
                        "username": username,
                        "current_hp": cur2_int,
                        "max_hp": max2_int,
                        "downed": downed2_bool,
                        "status_effects": statuses,
                    },
                )
            elif ge.effect_type == EffectType.GRANT_LOOT:
                loot_items: list[dict[str, object]] = []
                if target_room.loot_table:
                    for li in target_room.loot_table:
                        if ge.item_id is None or li.item == ge.item_id:
                            loot_items.append(
                                {
                                    "item_id": ge.item_id or li.item,
                                    "name": li.item,
                                    "quantity": li.quantity,
                                }
                            )
                if loot_items:
                    await manager.broadcast(
                        room_id_str,
                        {
                            "type": "loot:awarded",
                            "player_id": user_id_str,
                            "username": username,
                            "items": loot_items,
                        },
                    )
            elif ge.effect_type == EffectType.UNLOCK_PATH:
                await manager.broadcast(
                    room_id_str,
                    {
                        "type": "event:path_unlocked",
                        "room_index": room_idx,
                        "target": ge.item_id,
                    },
                )
            elif ge.effect_type == EffectType.SPAWN_ENEMY:
                await manager.broadcast(
                    room_id_str,
                    {
                        "type": "event:enemy_spawned",
                        "room_index": room_idx,
                        "enemy_id": ge.item_id,
                    },
                )
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Username resolver (US-081)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# DM enemy attack handler (US-082)
# ---------------------------------------------------------------------------

# Default enemy attack bonus for MVP. TODO: make this configurable per enemy.
_ENEMY_ATTACK_BONUS: int = 0

# Default armor class when no character record is found (D&D fallback).
_DEFAULT_AC: int = 10


async def _handle_dm_enemy_attack(
    websocket: WebSocket,
    room_id: uuid.UUID,
    room_id_str: str,
    message: dict[str, object],
    manager: ConnectionManager,
) -> None:
    """
    Handle dm:enemy_attack -- DM triggers an attack by an active enemy on a
    target player. Rolls 1d20 + attack bonus vs the target's AC, applies damage
    on hit, persists new HP, and broadcasts the outcome to all participants.

    AC1-AC10 from US-082.

    @param websocket   - The DM's WebSocket, for sending error events.
    @param room_id     - UUID of the room.
    @param room_id_str - String form of room_id for ConnectionManager.
    @param message     - The parsed WebSocket message dict.
    @param manager     - The module-level ConnectionManager singleton.
    """
    enemy_id_raw = message.get("enemy_id")
    target_raw = message.get("target_player_id")

    if not isinstance(enemy_id_raw, str) or not enemy_id_raw:
        await manager.send_to(
            websocket,
            {"type": "validation_error", "detail": "enemy_id is required."},
        )
        return

    if not isinstance(target_raw, str) or not target_raw:
        await manager.send_to(
            websocket,
            {"type": "validation_error", "detail": "target_player_id is required."},
        )
        return

    enemy_id: str = enemy_id_raw
    target_player_id: str = target_raw

    # Validate target player is connected to this room.
    if target_player_id not in manager.get_user_ids(room_id_str):
        await manager.send_to(
            websocket,
            {
                "type": "validation_error",
                "detail": f"Player {target_player_id} is not in this room.",
            },
        )
        return

    target_username = manager.get_username_for_user(room_id_str, target_player_id)
    enemy_label = (
        f"Enemy {enemy_id[:8]}" if len(enemy_id) > 8 else f"Enemy {enemy_id}"
    )

    # Load target character's AC from the DB.
    ac = _DEFAULT_AC
    db = SessionLocal()
    try:
        room_repo = SqlAlchemyRoomRepository(db)
        char_repo = SqlAlchemyCharacterRepository(db)
        ps_repo = SqlAlchemyPlayerStateRepository(db)

        room = room_repo.get_by_id(room_id)
        if room is not None and room.campaign_id is not None:
            try:
                target_uuid = uuid.UUID(target_player_id)
                character = char_repo.get_by_campaign_and_owner(
                    room.campaign_id, target_uuid
                )
                # Character domain model has no armor_class field in MVP;
                # default to AC 10 and log a warning.
                if character is not None:
                    logger.warning(
                        "_handle_dm_enemy_attack: character %s has no armor_class field; "
                        "defaulting to AC %d for room=%s",
                        character.id,
                        _DEFAULT_AC,
                        room_id_str,
                    )
            except Exception as char_exc:  # noqa: BLE001
                logger.warning(
                    "_handle_dm_enemy_attack: character lookup failed for "
                    "target=%s room=%s: %s; using AC %d",
                    target_player_id,
                    room_id_str,
                    char_exc,
                    _DEFAULT_AC,
                )
        else:
            logger.warning(
                "_handle_dm_enemy_attack: room=%s has no campaign_id; using AC %d",
                room_id_str,
                _DEFAULT_AC,
            )

        # Roll attack: 1d20 + attack bonus vs target AC.
        roll = random.randint(1, 20) + _ENEMY_ATTACK_BONUS
        hit = roll >= ac
        damage: int | None = None

        if hit:
            # Roll damage: 1d6 (MVP). TODO: use per-enemy damage die.
            damage = random.randint(1, 6)
            target_uuid_dmg = uuid.UUID(target_player_id)
            existing = ps_repo.get_by_player(room_id, target_uuid_dmg)
            cur_hp = existing.current_hp if existing is not None else 10
            max_hp = existing.max_hp if existing is not None else 10
            statuses = list(existing.status_effects) if existing is not None else []
            new_hp = max(0, cur_hp - damage)
            downed_new = new_hp <= 0
            try:
                ps_repo.upsert(
                    room_id, target_uuid_dmg, new_hp, max_hp, downed_new, statuses
                )
                db.commit()
            except Exception as dmg_exc:  # noqa: BLE001
                logger.error(
                    "_handle_dm_enemy_attack: HP upsert failed target=%s room=%s: %s",
                    target_player_id,
                    room_id_str,
                    dmg_exc,
                )
                db.rollback()
            # Broadcast updated HP to all participants.
            await manager.broadcast(
                room_id_str,
                {
                    "type": "state:player_update",
                    "player_id": target_player_id,
                    "username": target_username,
                    "current_hp": new_hp,
                    "max_hp": max_hp,
                    "downed": downed_new,
                    "status_effects": statuses,
                },
            )
            logger.info(
                "_handle_dm_enemy_attack: hit! enemy=%s target=%s roll=%d ac=%d dmg=%d new_hp=%d",
                enemy_id,
                target_player_id,
                roll,
                ac,
                damage,
                new_hp,
            )
        else:
            logger.info(
                "_handle_dm_enemy_attack: miss! enemy=%s target=%s roll=%d ac=%d",
                enemy_id,
                target_player_id,
                roll,
                ac,
            )

        # Broadcast attack result to all participants.
        narrative = (
            f"{enemy_label} attacks and hits {target_username}."
            if hit
            else f"{enemy_label} swings wildly and misses {target_username}."
        )
        await manager.broadcast(
            room_id_str,
            {
                "type": "event:enemy_attack_result",
                "enemy_id": enemy_id,
                "target_player_id": target_player_id,
                "target_username": target_username,
                "roll": roll,
                "ac": ac,
                "outcome": "hit" if hit else "miss",
                "damage": damage,
                "narrative": narrative,
            },
        )
    finally:
        db.close()


def _resolve_username(user_id: uuid.UUID, user_id_str: str) -> str:
    """
    Look up the display name (username) for a user from the database.
    Called once per WebSocket connection and cached in the connection tuple
    to avoid N+1 DB queries for every broadcast.

    Fallback chain:
    1. User not found -> "Unknown Player"
    2. User.name is empty string -> first 8 chars of user_id_str
    3. Otherwise -> User.name

    @param user_id     - UUID of the user to look up.
    @param user_id_str - String form used as the truncation fallback.
    @returns A non-empty display name string.
    """
    db = SessionLocal()
    try:
        user_repo = SqlAlchemyUserRepository(db)
        user = user_repo.get_by_id(user_id)
        if user is None:
            logger.warning(
                "_resolve_username: user %s not found; using 'Unknown Player'",
                user_id_str,
            )
            return "Unknown Player"
        if not user.name:
            logger.warning(
                "_resolve_username: user %s has empty name; using id prefix",
                user_id_str,
            )
            return user_id_str[:8]
        return user.name
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "_resolve_username: DB error for user %s: %s", user_id_str, exc
        )
        return "Unknown Player"
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

    # -- Resolve username once at connect time (US-081).
    # Cache per connection to avoid N+1 DB queries per broadcast.
    # NOTE: if a user changes their username mid-session, the cached value
    # will be stale for the remainder of the session. Acceptable for MVP.
    username = _resolve_username(payload.user_id, user_id_str)

    # -- Accept + initial state --
    await connection_manager.connect(
        websocket, room_id_str, user_id_str, role, username
    )

    # Send the full player list (with usernames) to the newly connected client only.
    current_players = connection_manager.get_players(room_id_str)

    # Load persisted player HP states from the DB so the client can restore
    # combat context immediately on (re)connect (US-079/US-080).
    db_rs = SessionLocal()
    try:
        ps_repo_rs = SqlAlchemyPlayerStateRepository(db_rs)
        hp_states = ps_repo_rs.get_by_room(room_id)
        player_hp_payload: list[dict[str, object]] = [
            {
                "player_id": str(ps.user_id),
                "current_hp": ps.current_hp,
                "max_hp": ps.max_hp,
                "downed": ps.downed,
                "status_effects": ps.status_effects,
            }
            for ps in hp_states
        ]
    except Exception as rs_exc:  # noqa: BLE001
        logger.error(
            "websocket_endpoint: failed to load player HP for room=%s: %s",
            room_id_str,
            rs_exc,
        )
        player_hp_payload = []
    finally:
        db_rs.close()

    await connection_manager.send_to(
        websocket,
        {
            "type": "room_state",
            "players": current_players,
            # HP snapshot from DB — allows client to restore sidebar immediately.
            "player_hp": player_hp_payload,
            # session_started/ended and dungeon fields are placeholders;
            # fully populated by the dungeon state query in a future story.
            "session_started": False,
            "session_ended": False,
            "current_room_index": None,
            "current_quest_stage": None,
            "recent_events": [],
            "current_mechanics": [],
        },
    )

    # Broadcast to everyone else that a new player arrived (US-081: include username).
    await connection_manager.broadcast(
        room_id_str,
        {
            "type": "player_joined",
            "user_id": user_id_str,
            "username": username,
            "role": role,
        },
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
                        "username": username,
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
                        {
                            "type": "dm_announcement",
                            "user_id": user_id_str,
                            "username": username,
                            "content": content,
                        },
                    )

            elif event_type == "chat_message":
                content = str(message.get("content", ""))
                await connection_manager.broadcast(
                    room_id_str,
                    {
                        "type": "chat_message",
                        "user_id": user_id_str,
                        "username": username,
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

            elif event_type == "player:action":
                # Players (not DM) submit mechanic-based actions (US-073).
                await _handle_player_action(
                    websocket,
                    room_id,
                    room_id_str,
                    user_id_str,
                    username,
                    message,
                    connection_manager,
                )

            elif event_type == "dm:enemy_attack":
                # DM triggers an enemy attack on a target player (US-082).
                if role != "dm":
                    await connection_manager.send_to(
                        websocket,
                        {
                            "type": "permission_denied",
                            "detail": "Only the DM can trigger enemy attacks.",
                        },
                    )
                else:
                    await _handle_dm_enemy_attack(
                        websocket, room_id, room_id_str, message, connection_manager
                    )

            else:
                await connection_manager.send_to(
                    websocket,
                    {"type": "error", "detail": f"Unknown event type: {event_type!r}"},
                )

    except WebSocketDisconnect:
        left = connection_manager.disconnect(websocket, room_id_str)
        if left is not None:
            left_user_id, _ = left
            await connection_manager.broadcast(
                room_id_str,
                {"type": "player_left", "user_id": left_user_id},
            )

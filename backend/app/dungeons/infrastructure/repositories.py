"""
SQLAlchemy implementation of DungeonRepository.

Maps between DungeonORM rows and Dungeon domain aggregates.
The dungeon_data JSON column stores rooms, quest, and quest_metadata.
Type-narrowing helpers are used throughout to satisfy mypy strict mode.
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dungeons.domain.models import (
    Dungeon,
    DungeonQuest,
    DungeonRoom,
    EffectType,
    EnemyData,
    GameEffect,
    LootItem,
    NpcData,
    NpcInventoryItem,
    QuestMetadata,
    RoomMechanics,
    RoomType,
    SkillCheck,
    TriggerData,
)
from app.dungeons.domain.repositories import DungeonRepository
from app.dungeons.infrastructure.orm_models import DungeonORM

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Type-narrowing helpers for JSON dicts
# ---------------------------------------------------------------------------


def _str(d: dict[str, object], key: str, default: str = "") -> str:
    v = d.get(key, default)
    return v if isinstance(v, str) else default


def _int(d: dict[str, object], key: str, default: int = 0) -> int:
    v = d.get(key, default)
    return v if isinstance(v, int) else default


def _nullable_str(d: dict[str, object], key: str) -> str | None:
    v = d.get(key)
    return v if isinstance(v, str) else None


def _nullable_int(d: dict[str, object], key: str) -> int | None:
    v = d.get(key)
    return v if isinstance(v, int) else None


def _list_of_str(d: dict[str, object], key: str) -> list[str]:
    v = d.get(key, [])
    if not isinstance(v, list):
        return []
    return [s for s in v if isinstance(s, str)]


def _list_of_int(d: dict[str, object], key: str) -> list[int]:
    v = d.get(key, [])
    if not isinstance(v, list):
        return []
    return [i for i in v if isinstance(i, int)]


def _as_dict(v: object) -> dict[str, object] | None:
    return v if isinstance(v, dict) else None


# ---------------------------------------------------------------------------
# Structured field deserializers
# ---------------------------------------------------------------------------


def _skill_check_from_dict(raw: object) -> SkillCheck | None:
    d = _as_dict(raw)
    if d is None:
        return None
    return SkillCheck(
        type=_str(d, "type", "Unknown"),
        dc=_int(d, "dc", 10),
        on_success=_str(d, "on_success", ""),
        on_failure=_nullable_str(d, "on_failure"),
    )


def _trigger_data_from_dict(raw: object) -> TriggerData | None:
    """Deserialize a raw JSON object into a TriggerData value object."""
    d = _as_dict(raw)
    if d is None:
        return None
    return TriggerData(
        trigger_action=_str(d, "trigger_action", "unknown"),
        check_stat=_nullable_str(d, "check_stat"),
        dc=_nullable_int(d, "dc"),
    )


def _game_effect_from_dict(raw: object) -> GameEffect | None:
    """
    Deserialize a raw JSON object into a GameEffect value object.

    Returns None for malformed entries so callers can filter them out.
    """
    d = _as_dict(raw)
    if d is None:
        return None
    try:
        effect_type = EffectType(_str(d, "effect_type", EffectType.NONE.value))
    except ValueError:
        effect_type = EffectType.NONE
    trigger = _trigger_data_from_dict(d.get("trigger"))
    if trigger is None:
        # Every GameEffect must have a trigger; discard malformed entries.
        logger.warning("_game_effect_from_dict: missing trigger, skipping entry")
        return None
    return GameEffect(
        effect_type=effect_type,
        trigger=trigger,
        value=_nullable_int(d, "value"),
        status=_nullable_str(d, "status"),
        item_id=_nullable_str(d, "item_id"),
        description=_str(d, "description"),
    )


def _mechanics_from_dict(raw: object) -> RoomMechanics | None:
    d = _as_dict(raw)
    if d is None:
        return None
    checks_raw = d.get("skill_checks", [])
    checks_list = checks_raw if isinstance(checks_raw, list) else []
    checks = tuple(
        c
        for c in (_skill_check_from_dict(item) for item in checks_list)
        if c is not None
    )
    vi_raw = d.get("victory_items", [])
    vi = tuple(_list_of_str(d, "victory_items")) if isinstance(vi_raw, list) else ()
    ge_raw = d.get("game_effects", [])
    ge_list = ge_raw if isinstance(ge_raw, list) else []
    game_effects = tuple(
        ge
        for ge in (_game_effect_from_dict(item) for item in ge_list)
        if ge is not None
    )
    return RoomMechanics(
        skill_checks=checks,
        rest_benefit=_nullable_str(d, "rest_benefit"),
        victory_items=vi,
        game_effects=game_effects,
    )


def _enemy_data_from_dict(raw: object) -> EnemyData | None:
    d = _as_dict(raw)
    if d is None:
        return None
    return EnemyData(
        initial=tuple(_list_of_str(d, "initial")),
        reinforcements=tuple(_list_of_str(d, "reinforcements")),
        trigger_condition=_nullable_str(d, "trigger_condition"),
        environmental_hazards=_nullable_str(d, "environmental_hazards"),
        boss=_nullable_str(d, "boss"),
        special_attacks=tuple(_list_of_str(d, "special_attacks")),
    )


def _loot_item_from_dict(raw: object) -> LootItem | None:
    d = _as_dict(raw)
    if d is None:
        return None
    return LootItem(
        item=_str(d, "item"),
        quantity=_int(d, "quantity", 1),
        value=_nullable_str(d, "value"),
        rarity=_nullable_str(d, "rarity"),
    )


def _npc_data_from_dict(raw: object) -> NpcData | None:
    d = _as_dict(raw)
    if d is None:
        return None
    inv_raw = d.get("inventory", [])
    inv_list = inv_raw if isinstance(inv_raw, list) else []
    inventory: list[NpcInventoryItem] = []
    for item in inv_list:
        item_d = _as_dict(item)
        if item_d is not None:
            inventory.append(
                NpcInventoryItem(
                    item=_str(item_d, "item"),
                    price=_int(item_d, "price"),
                )
            )
    idc = d.get("interaction_dc")
    return NpcData(
        name=_str(d, "name"),
        role=_str(d, "role", "Unknown"),
        inventory=tuple(inventory),
        interaction_dc=idc if isinstance(idc, dict) else None,
    )


def _quest_metadata_from_dict(raw: object) -> QuestMetadata | None:
    d = _as_dict(raw)
    if d is None:
        return None
    return QuestMetadata(
        name=_str(d, "name"),
        recommended_level=_int(d, "recommended_level", 1),
        environment=_str(d, "environment", "Dungeon"),
        global_modifiers=_str(d, "global_modifiers"),
    )


# ---------------------------------------------------------------------------
# Room deserializer with legacy mapping
# ---------------------------------------------------------------------------


def _room_from_dict(raw: object, room_type_hint: str = "COMBAT") -> DungeonRoom:
    """
    Deserialize a raw JSON object into a DungeonRoom value object.

    Legacy mapping rules:
    - If 'enemies' key is absent but 'enemy_names' present: map to EnemyData.initial
    - If 'mechanics' key is absent but 'special_notes' present: map to RoomMechanics
    - If 'npc_data' key is absent but 'npc_names' present: map each name to NpcData stub
    """
    if not isinstance(raw, dict):
        return DungeonRoom(
            index=0,
            room_type=RoomType.COMBAT,
            name="Unknown Room",
            description="",
        )
    d: dict[str, object] = raw

    try:
        room_type = RoomType(_str(d, "room_type", room_type_hint))
    except ValueError:
        room_type = RoomType.COMBAT

    # Legacy flat fields.
    legacy_enemy_names = tuple(_list_of_str(d, "enemy_names"))
    legacy_npc_names = tuple(_list_of_str(d, "npc_names"))

    # Warn if a legacy record still carries special_notes -- the field is no
    # longer part of the domain model (dropped in US-071).
    if "special_notes" in d:
        logger.warning(
            "_room_from_dict: legacy 'special_notes' key found in JSON record "
            "index=%d; field is no longer used",
            _int(d, "index"),
        )

    # Structured enemies: prefer new key, fall back to legacy.
    enemies_raw = d.get("enemies")
    if enemies_raw is not None:
        enemies = _enemy_data_from_dict(enemies_raw)
    elif legacy_enemy_names:
        enemies = EnemyData(initial=legacy_enemy_names, reinforcements=())
    else:
        enemies = None

    # Structured mechanics: prefer new key, no legacy fallback.
    mechanics_raw = d.get("mechanics")
    if mechanics_raw is not None:
        mechanics = _mechanics_from_dict(mechanics_raw)
    else:
        mechanics = None

    # Loot table: only present on TREASURE rooms.
    loot_raw = d.get("loot_table")
    loot_table: tuple[LootItem, ...] | None = None
    if isinstance(loot_raw, list):
        items = [_loot_item_from_dict(item) for item in loot_raw]
        loot_table = tuple(li for li in items if li is not None)

    # NPC data: prefer new key, fall back to npc_names.
    npc_data_raw = d.get("npc_data")
    npc_data: tuple[NpcData, ...] | None = None
    if isinstance(npc_data_raw, list):
        parsed = [_npc_data_from_dict(n) for n in npc_data_raw]
        npc_data = tuple(n for n in parsed if n is not None)
    elif legacy_npc_names:
        npc_data = tuple(
            NpcData(name=name, role="Unknown", inventory=())
            for name in legacy_npc_names
        )

    return DungeonRoom(
        index=_int(d, "index"),
        room_type=room_type,
        name=_str(d, "name"),
        description=_str(d, "description"),
        enemy_names=legacy_enemy_names,
        npc_names=legacy_npc_names,
        enemies=enemies,
        mechanics=mechanics,
        loot_table=loot_table,
        npc_data=npc_data,
    )


def _quest_from_dict(raw: object) -> DungeonQuest:
    """Deserialize a raw JSON object into a DungeonQuest value object."""
    if not isinstance(raw, dict):
        return DungeonQuest(name="Unknown Quest", description="", stages=())
    d: dict[str, object] = raw
    return DungeonQuest(
        name=_str(d, "name"),
        description=_str(d, "description"),
        stages=tuple(_list_of_str(d, "stages")),
    )


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------


def _room_to_dict(room: DungeonRoom) -> dict[str, object]:
    """Serialize a DungeonRoom value object for JSON column storage."""
    data: dict[str, object] = {
        "index": room.index,
        "room_type": room.room_type.value,
        "name": room.name,
        "description": room.description,
        "enemy_names": list(room.enemy_names),
        "npc_names": list(room.npc_names),
    }
    if room.enemies is not None:
        e = room.enemies
        data["enemies"] = {
            "initial": list(e.initial),
            "reinforcements": list(e.reinforcements),
            "trigger_condition": e.trigger_condition,
            "environmental_hazards": e.environmental_hazards,
            "boss": e.boss,
            "special_attacks": list(e.special_attacks),
        }
    if room.mechanics is not None:
        m = room.mechanics
        data["mechanics"] = {
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
        data["loot_table"] = [
            {
                "item": li.item,
                "quantity": li.quantity,
                "value": li.value,
                "rarity": li.rarity,
            }
            for li in room.loot_table
        ]
    if room.npc_data is not None:
        data["npc_data"] = [
            {
                "name": nd.name,
                "role": nd.role,
                "inventory": [
                    {"item": inv.item, "price": inv.price} for inv in nd.inventory
                ],
                "interaction_dc": nd.interaction_dc,
            }
            for nd in room.npc_data
        ]
    return data


def _quest_to_dict(quest: DungeonQuest) -> dict[str, object]:
    """Serialize a DungeonQuest value object for JSON column storage."""
    return {
        "name": quest.name,
        "description": quest.description,
        "stages": list(quest.stages),
    }


def _quest_metadata_to_dict(qm: QuestMetadata) -> dict[str, object]:
    """Serialize QuestMetadata for JSON column storage."""
    return {
        "name": qm.name,
        "recommended_level": qm.recommended_level,
        "environment": qm.environment,
        "global_modifiers": qm.global_modifiers,
    }


# ---------------------------------------------------------------------------
# ORM <-> Domain mapping
# ---------------------------------------------------------------------------


def _to_domain(row: DungeonORM) -> Dungeon:
    """Map a DungeonORM row to a Dungeon domain aggregate."""
    data = row.dungeon_data if isinstance(row.dungeon_data, dict) else {}

    rooms_raw = data.get("rooms", [])
    raw_rooms = rooms_raw if isinstance(rooms_raw, list) else []

    # current_room_index and completed_stage_indices live in ORM columns.
    cri = row.current_room_index if isinstance(row.current_room_index, int) else 0
    csi_raw = row.completed_stage_indices
    csi = (
        [i for i in csi_raw if isinstance(i, int)] if isinstance(csi_raw, list) else []
    )

    return Dungeon(
        id=row.id,
        campaign_id=row.campaign_id,
        world_id=row.world_id,
        name=row.name,
        premise=row.premise,
        rooms=tuple(_room_from_dict(r) for r in raw_rooms),
        quest=_quest_from_dict(data.get("quest")),
        created_at=row.created_at,
        quest_metadata=_quest_metadata_from_dict(data.get("quest_metadata")),
        current_room_index=cri,
        completed_stage_indices=csi,
    )


def _to_orm(dungeon: Dungeon) -> DungeonORM:
    """Map a Dungeon domain aggregate to a DungeonORM row."""
    dungeon_data: dict[str, object] = {
        "rooms": [_room_to_dict(r) for r in dungeon.rooms],
        "quest": _quest_to_dict(dungeon.quest),
    }
    if dungeon.quest_metadata is not None:
        dungeon_data["quest_metadata"] = _quest_metadata_to_dict(dungeon.quest_metadata)

    return DungeonORM(
        id=dungeon.id,
        campaign_id=dungeon.campaign_id,
        world_id=dungeon.world_id,
        name=dungeon.name,
        premise=dungeon.premise,
        dungeon_data=dungeon_data,
        created_at=dungeon.created_at,
        current_room_index=dungeon.current_room_index,
        completed_stage_indices=list(dungeon.completed_stage_indices),
    )


# ---------------------------------------------------------------------------
# Repository implementation
# ---------------------------------------------------------------------------


class SQLAlchemyDungeonRepository(DungeonRepository):
    """SQLAlchemy-backed implementation of DungeonRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, dungeon: Dungeon) -> None:
        """Insert or update a Dungeon aggregate."""
        logger.debug("DungeonRepository.save: id=%s", dungeon.id)
        self._session.merge(_to_orm(dungeon))
        self._session.flush()

    def get_by_id(self, dungeon_id: uuid.UUID) -> Dungeon | None:
        """Return the dungeon with the given id, or None if not found."""
        logger.debug("DungeonRepository.get_by_id: id=%s", dungeon_id)
        stmt = select(DungeonORM).where(DungeonORM.id == dungeon_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        if row is None:
            return None
        return _to_domain(row)

    def list_by_campaign_id(self, campaign_id: uuid.UUID) -> list[Dungeon]:
        """Return all dungeons for the given campaign, newest first."""
        logger.debug(
            "DungeonRepository.list_by_campaign_id: campaign_id=%s", campaign_id
        )
        stmt = (
            select(DungeonORM)
            .where(DungeonORM.campaign_id == campaign_id)
            .order_by(DungeonORM.created_at.desc())
        )
        rows = self._session.execute(stmt).scalars().all()
        logger.info(
            "DungeonRepository.list_by_campaign_id: found %d for campaign_id=%s",
            len(rows),
            campaign_id,
        )
        return [_to_domain(row) for row in rows]

    def update_room_index(
        self, dungeon_id: uuid.UUID, room_index: int
    ) -> Dungeon | None:
        """Set current_room_index on the dungeon and return the updated aggregate."""
        logger.debug(
            "DungeonRepository.update_room_index: id=%s index=%d",
            dungeon_id,
            room_index,
        )
        stmt = select(DungeonORM).where(DungeonORM.id == dungeon_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        if row is None:
            return None
        row.current_room_index = room_index
        self._session.flush()
        return _to_domain(row)

    def complete_quest_stage(
        self, dungeon_id: uuid.UUID, stage_index: int
    ) -> Dungeon | None:
        """Append stage_index to completed_stage_indices and return the updated aggregate."""
        logger.debug(
            "DungeonRepository.complete_quest_stage: id=%s stage=%d",
            dungeon_id,
            stage_index,
        )
        stmt = select(DungeonORM).where(DungeonORM.id == dungeon_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        if row is None:
            return None
        existing = (
            list(row.completed_stage_indices)
            if isinstance(row.completed_stage_indices, list)
            else []
        )
        if stage_index not in existing:
            existing.append(stage_index)
            row.completed_stage_indices = existing
        self._session.flush()
        return _to_domain(row)

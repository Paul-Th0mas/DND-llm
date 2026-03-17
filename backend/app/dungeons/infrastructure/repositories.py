"""
SQLAlchemy implementation of DungeonRepository.

Maps between DungeonORM rows and Dungeon domain aggregates.
The dungeon_data JSON column stores rooms and quest. Type-narrowing helpers
are used throughout to satisfy mypy strict mode.
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dungeons.domain.models import (
    Dungeon,
    DungeonQuest,
    DungeonRoom,
    RoomType,
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


def _list_of_str(d: dict[str, object], key: str) -> list[str]:
    v = d.get(key, [])
    if not isinstance(v, list):
        return []
    return [s for s in v if isinstance(s, str)]


# ---------------------------------------------------------------------------
# Deserializers
# ---------------------------------------------------------------------------


def _room_from_dict(raw: object) -> DungeonRoom:
    """Deserialize a raw JSON object into a DungeonRoom value object."""
    if not isinstance(raw, dict):
        return DungeonRoom(
            index=0,
            room_type=RoomType.COMBAT,
            name="Unknown Room",
            description="",
            enemy_names=(),
            npc_names=(),
        )
    d: dict[str, object] = raw
    special = d.get("special_notes")
    return DungeonRoom(
        index=_int(d, "index"),
        room_type=RoomType(_str(d, "room_type", "COMBAT")),
        name=_str(d, "name"),
        description=_str(d, "description"),
        enemy_names=tuple(_list_of_str(d, "enemy_names")),
        npc_names=tuple(_list_of_str(d, "npc_names")),
        special_notes=special if isinstance(special, str) else None,
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
    return {
        "index": room.index,
        "room_type": room.room_type.value,
        "name": room.name,
        "description": room.description,
        "enemy_names": list(room.enemy_names),
        "npc_names": list(room.npc_names),
        "special_notes": room.special_notes,
    }


def _quest_to_dict(quest: DungeonQuest) -> dict[str, object]:
    """Serialize a DungeonQuest value object for JSON column storage."""
    return {
        "name": quest.name,
        "description": quest.description,
        "stages": list(quest.stages),
    }


# ---------------------------------------------------------------------------
# ORM ↔ Domain mapping
# ---------------------------------------------------------------------------


def _to_domain(row: DungeonORM) -> Dungeon:
    """Map a DungeonORM row to a Dungeon domain aggregate."""
    data = row.dungeon_data if isinstance(row.dungeon_data, dict) else {}

    rooms_raw = data.get("rooms", [])
    raw_rooms = rooms_raw if isinstance(rooms_raw, list) else []

    return Dungeon(
        id=row.id,
        campaign_id=row.campaign_id,
        world_id=row.world_id,
        name=row.name,
        premise=row.premise,
        rooms=tuple(_room_from_dict(r) for r in raw_rooms),
        quest=_quest_from_dict(data.get("quest")),
        created_at=row.created_at,
    )


def _to_orm(dungeon: Dungeon) -> DungeonORM:
    """Map a Dungeon domain aggregate to a DungeonORM row."""
    return DungeonORM(
        id=dungeon.id,
        campaign_id=dungeon.campaign_id,
        world_id=dungeon.world_id,
        name=dungeon.name,
        premise=dungeon.premise,
        dungeon_data={
            "rooms": [_room_to_dict(r) for r in dungeon.rooms],
            "quest": _quest_to_dict(dungeon.quest),
        },
        created_at=dungeon.created_at,
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

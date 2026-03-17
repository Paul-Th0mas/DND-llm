"""
SQLAlchemy implementation of WorldRepository.

Maps between WorldORM rows and World domain aggregates.
JSON columns (factions, bosses) are deserialized with type-narrowing helpers
to satisfy mypy strict mode — never use cast() or Any for JSON fields.
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.worlds.domain.models import PresetBoss, PresetFaction, Theme, World
from app.worlds.domain.repositories import WorldRepository
from app.worlds.infrastructure.orm_models import WorldORM

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Type-narrowing helpers for JSON dicts
# These helpers safely extract typed values from dict[str, object] columns
# without resorting to cast() or Any, which mypy strict mode forbids.
# ---------------------------------------------------------------------------


def _str(d: dict[str, object], key: str, default: str = "") -> str:
    v = d.get(key, default)
    return v if isinstance(v, str) else default


def _list_of_str(d: dict[str, object], key: str) -> list[str]:
    v = d.get(key, [])
    if not isinstance(v, list):
        return []
    return [s for s in v if isinstance(s, str)]


# ---------------------------------------------------------------------------
# Deserializers
# ---------------------------------------------------------------------------


def _faction_from_dict(raw: object) -> PresetFaction:
    """Deserialize a raw JSON object into a PresetFaction value object."""
    if not isinstance(raw, dict):
        return PresetFaction(
            name="Unknown",
            description="",
            alignment="",
            public_reputation="",
            hidden_agenda="",
        )
    d: dict[str, object] = raw
    return PresetFaction(
        name=_str(d, "name"),
        description=_str(d, "description"),
        alignment=_str(d, "alignment"),
        public_reputation=_str(d, "public_reputation"),
        hidden_agenda=_str(d, "hidden_agenda"),
    )


def _boss_from_dict(raw: object) -> PresetBoss:
    """Deserialize a raw JSON object into a PresetBoss value object."""
    if not isinstance(raw, dict):
        return PresetBoss(
            name="Unknown",
            description="",
            challenge_rating="",
            abilities=(),
            lore="",
        )
    d: dict[str, object] = raw
    return PresetBoss(
        name=_str(d, "name"),
        description=_str(d, "description"),
        challenge_rating=_str(d, "challenge_rating"),
        abilities=tuple(_list_of_str(d, "abilities")),
        lore=_str(d, "lore"),
    )


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------


def _faction_to_dict(f: PresetFaction) -> dict[str, object]:
    """Serialize a PresetFaction value object for JSON column storage."""
    return {
        "name": f.name,
        "description": f.description,
        "alignment": f.alignment,
        "public_reputation": f.public_reputation,
        "hidden_agenda": f.hidden_agenda,
    }


def _boss_to_dict(b: PresetBoss) -> dict[str, object]:
    """Serialize a PresetBoss value object for JSON column storage."""
    return {
        "name": b.name,
        "description": b.description,
        "challenge_rating": b.challenge_rating,
        "abilities": list(b.abilities),
        "lore": b.lore,
    }


# ---------------------------------------------------------------------------
# ORM ↔ Domain mapping
# ---------------------------------------------------------------------------


def _to_domain(row: WorldORM) -> World:
    """Map a WorldORM row to a World domain aggregate."""
    raw_factions = row.factions if isinstance(row.factions, list) else []
    raw_bosses = row.bosses if isinstance(row.bosses, list) else []

    return World(
        id=row.id,
        name=row.name,
        theme=Theme(row.theme),
        description=row.description,
        lore_summary=row.lore_summary,
        factions=tuple(_faction_from_dict(f) for f in raw_factions),
        bosses=tuple(_boss_from_dict(b) for b in raw_bosses),
        is_active=row.is_active,
        created_at=row.created_at,
    )


def _to_orm(world: World) -> WorldORM:
    """Map a World domain aggregate to a WorldORM row (for seeding)."""
    return WorldORM(
        id=world.id,
        name=world.name,
        theme=world.theme.value,
        description=world.description,
        lore_summary=world.lore_summary,
        factions=[_faction_to_dict(f) for f in world.factions],
        bosses=[_boss_to_dict(b) for b in world.bosses],
        is_active=world.is_active,
        created_at=world.created_at,
    )


# ---------------------------------------------------------------------------
# Repository implementation
# ---------------------------------------------------------------------------


class SQLAlchemyWorldRepository(WorldRepository):
    """SQLAlchemy-backed implementation of WorldRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all_active(self) -> list[World]:
        """Return all worlds where is_active is True, ordered by name."""
        logger.debug("WorldRepository.get_all_active")
        stmt = (
            select(WorldORM).where(WorldORM.is_active.is_(True)).order_by(WorldORM.name)
        )
        rows = self._session.execute(stmt).scalars().all()
        logger.info("WorldRepository.get_all_active: found %d worlds", len(rows))
        return [_to_domain(row) for row in rows]

    def get_by_id(self, world_id: uuid.UUID) -> World | None:
        """Return the world with the given id, or None if not found."""
        logger.debug("WorldRepository.get_by_id: id=%s", world_id)
        stmt = select(WorldORM).where(WorldORM.id == world_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        if row is None:
            logger.debug("WorldRepository.get_by_id: not found id=%s", world_id)
            return None
        return _to_domain(row)

    def save(self, world: World) -> None:
        """
        Persist a World aggregate. Used by the seed script only.

        merge() is used instead of add() so the method is idempotent — calling
        save() on an already-persisted world updates it rather than failing.
        """
        logger.debug("WorldRepository.save: id=%s name='%s'", world.id, world.name)
        orm_row = _to_orm(world)
        self._session.merge(orm_row)

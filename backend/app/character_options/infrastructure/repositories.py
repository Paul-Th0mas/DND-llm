"""
Concrete SQLAlchemy repository implementations for the character_options
bounded context.

Maps between ORM rows and domain aggregates.
JSON columns (traits) are deserialized with type-narrowing helpers to satisfy
mypy strict mode.
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.character_options.domain.models import CharacterClass, CharacterSpecies
from app.character_options.domain.repositories import (
    CharacterClassRepository,
    CharacterSpeciesRepository,
)
from app.character_options.infrastructure.orm_models import (
    CharacterClassORM,
    CharacterSpeciesORM,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# JSON field type-narrowing helpers
# ---------------------------------------------------------------------------


def _str_list(value: object) -> list[str]:
    """Safely convert a JSON array value to list[str], filtering non-strings."""
    if isinstance(value, list):
        return [x for x in value if isinstance(x, str)]
    return []


# ---------------------------------------------------------------------------
# CharacterClass repository
# ---------------------------------------------------------------------------


class SqlAlchemyCharacterClassRepository(CharacterClassRepository):
    """SQLAlchemy-backed implementation of CharacterClassRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_theme(self, theme: str) -> list[CharacterClass]:
        """Return all active classes for the given world theme."""
        logger.debug("list_by_theme: theme=%s", theme)
        stmt = (
            select(CharacterClassORM)
            .where(
                CharacterClassORM.theme == theme,
                CharacterClassORM.is_active.is_(True),
            )
            .order_by(CharacterClassORM.display_name)
        )
        rows = self._session.execute(stmt).scalars().all()
        logger.info("list_by_theme: theme=%s found %d classes", theme, len(rows))
        return [self._to_domain(row) for row in rows]

    def get_by_id(self, class_id: uuid.UUID) -> CharacterClass | None:
        """Return a single active class by UUID, or None."""
        logger.debug("get_by_id: class_id=%s", class_id)
        stmt = select(CharacterClassORM).where(
            CharacterClassORM.id == class_id,
            CharacterClassORM.is_active.is_(True),
        )
        row = self._session.execute(stmt).scalar_one_or_none()
        return self._to_domain(row) if row is not None else None

    @staticmethod
    def _to_domain(orm: CharacterClassORM) -> CharacterClass:
        """Map a CharacterClassORM row to a CharacterClass domain object."""
        return CharacterClass(
            id=orm.id,
            display_name=orm.display_name,
            chassis_name=orm.chassis_name,
            hit_die=orm.hit_die,
            primary_ability=orm.primary_ability,
            spellcasting_ability=orm.spellcasting_ability,
            theme=orm.theme,
        )


# ---------------------------------------------------------------------------
# CharacterSpecies repository
# ---------------------------------------------------------------------------


class SqlAlchemyCharacterSpeciesRepository(CharacterSpeciesRepository):
    """SQLAlchemy-backed implementation of CharacterSpeciesRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_theme(self, theme: str) -> list[CharacterSpecies]:
        """Return all active species for the given world theme."""
        logger.debug("list_by_theme: theme=%s", theme)
        stmt = (
            select(CharacterSpeciesORM)
            .where(
                CharacterSpeciesORM.theme == theme,
                CharacterSpeciesORM.is_active.is_(True),
            )
            .order_by(CharacterSpeciesORM.display_name)
        )
        rows = self._session.execute(stmt).scalars().all()
        logger.info("list_by_theme: theme=%s found %d species", theme, len(rows))
        return [self._to_domain(row) for row in rows]

    def get_by_id(self, species_id: uuid.UUID) -> CharacterSpecies | None:
        """Return a single active species by UUID, or None."""
        logger.debug("get_by_id: species_id=%s", species_id)
        stmt = select(CharacterSpeciesORM).where(
            CharacterSpeciesORM.id == species_id,
            CharacterSpeciesORM.is_active.is_(True),
        )
        row = self._session.execute(stmt).scalar_one_or_none()
        return self._to_domain(row) if row is not None else None

    @staticmethod
    def _to_domain(orm: CharacterSpeciesORM) -> CharacterSpecies:
        """Map a CharacterSpeciesORM row to a CharacterSpecies domain object."""
        return CharacterSpecies(
            id=orm.id,
            display_name=orm.display_name,
            archetype_key=orm.archetype_key,
            size=orm.size,
            speed=orm.speed,
            traits=tuple(_str_list(orm.traits)),
            theme=orm.theme,
        )

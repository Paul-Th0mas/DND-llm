"""
Concrete SQLAlchemy repository implementation for the characters bounded context.

Maps between CharacterORM rows and Character domain aggregates.
The ability_scores JSON column is deserialized with type-narrowing helpers
to satisfy mypy strict mode.
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.characters.domain.models import AbilityScores, Character
from app.characters.domain.repositories import CharacterRepository
from app.characters.infrastructure.orm_models import CharacterORM

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# JSON field type-narrowing helpers
# ---------------------------------------------------------------------------


def _jint(d: dict[str, object], key: str, default: int = 10) -> int:
    """Safely read an integer from a JSON dict, returning default on failure."""
    v = d.get(key, default)
    return v if isinstance(v, int) else default


def _jstr_list(value: object) -> list[str]:
    """Safely convert a JSON array value to list[str], filtering non-strings."""
    if isinstance(value, list):
        return [x for x in value if isinstance(x, str)]
    return []


# ---------------------------------------------------------------------------
# Repository implementation
# ---------------------------------------------------------------------------


class SqlAlchemyCharacterRepository(CharacterRepository):
    """SQLAlchemy-backed implementation of CharacterRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, character: Character) -> None:
        """Insert or update a Character aggregate."""
        logger.debug("save: character id=%s name=%s", character.id, character.name)
        scores = character.ability_scores
        orm = CharacterORM(
            id=character.id,
            name=character.name,
            owner_id=character.owner_id,
            world_id=character.world_id,
            class_id=character.class_id,
            species_id=character.species_id,
            background=character.background,
            ability_scores={
                "strength": scores.strength,
                "dexterity": scores.dexterity,
                "constitution": scores.constitution,
                "intelligence": scores.intelligence,
                "wisdom": scores.wisdom,
                "charisma": scores.charisma,
            },
            campaign_id=character.campaign_id,
            created_at=character.created_at,
            skill_proficiencies=character.skill_proficiencies,
            starting_equipment=character.starting_equipment,
            spells=character.spells,
        )
        self._session.merge(orm)
        self._session.flush()
        logger.info("save: character id=%s persisted", character.id)

    def get_by_id(self, character_id: uuid.UUID) -> Character | None:
        """Return a Character by UUID, or None if not found."""
        logger.debug("get_by_id: character_id=%s", character_id)
        stmt = select(CharacterORM).where(CharacterORM.id == character_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        return self._to_domain(row) if row is not None else None

    def list_by_owner_id(self, owner_id: uuid.UUID) -> list[Character]:
        """Return all characters owned by the given user, newest first."""
        logger.debug("list_by_owner_id: owner_id=%s", owner_id)
        stmt = (
            select(CharacterORM)
            .where(CharacterORM.owner_id == owner_id)
            .order_by(CharacterORM.created_at.desc())
        )
        rows = self._session.execute(stmt).scalars().all()
        logger.info(
            "list_by_owner_id: found %d characters for owner=%s", len(rows), owner_id
        )
        return [self._to_domain(row) for row in rows]

    def list_by_campaign_id(self, campaign_id: uuid.UUID) -> list[Character]:
        """Return all characters linked to the given campaign."""
        logger.debug("list_by_campaign_id: campaign_id=%s", campaign_id)
        stmt = (
            select(CharacterORM)
            .where(CharacterORM.campaign_id == campaign_id)
            .order_by(CharacterORM.created_at.asc())
        )
        rows = self._session.execute(stmt).scalars().all()
        logger.info(
            "list_by_campaign_id: found %d characters for campaign=%s",
            len(rows),
            campaign_id,
        )
        return [self._to_domain(row) for row in rows]

    def get_by_campaign_and_owner(
        self, campaign_id: uuid.UUID, owner_id: uuid.UUID
    ) -> Character | None:
        """Return the character owned by owner_id linked to campaign_id."""
        logger.debug(
            "get_by_campaign_and_owner: campaign_id=%s owner_id=%s",
            campaign_id,
            owner_id,
        )
        stmt = select(CharacterORM).where(
            CharacterORM.campaign_id == campaign_id,
            CharacterORM.owner_id == owner_id,
        )
        row = self._session.execute(stmt).scalar_one_or_none()
        return self._to_domain(row) if row is not None else None

    @staticmethod
    def _to_domain(orm: CharacterORM) -> Character:
        """Map a CharacterORM row to a Character domain aggregate."""
        scores_raw = orm.ability_scores if isinstance(orm.ability_scores, dict) else {}
        scores = AbilityScores(
            strength=_jint(scores_raw, "strength"),
            dexterity=_jint(scores_raw, "dexterity"),
            constitution=_jint(scores_raw, "constitution"),
            intelligence=_jint(scores_raw, "intelligence"),
            wisdom=_jint(scores_raw, "wisdom"),
            charisma=_jint(scores_raw, "charisma"),
        )
        return Character(
            id=orm.id,
            name=orm.name,
            owner_id=orm.owner_id,
            world_id=orm.world_id,
            class_id=orm.class_id,
            species_id=orm.species_id,
            background=orm.background,
            ability_scores=scores,
            campaign_id=orm.campaign_id,
            created_at=orm.created_at,
            skill_proficiencies=_jstr_list(orm.skill_proficiencies),
            starting_equipment=_jstr_list(orm.starting_equipment),
            spells=_jstr_list(orm.spells),
        )

"""
Domain models for the characters bounded context.

Character is the aggregate root. It represents a player-owned character
created for a specific world and optionally linked to a campaign.

AbilityScores is a value object that groups the six D&D ability score fields
and enforces the valid range (1–30).

No SQLAlchemy or FastAPI imports belong here. Pure Python domain logic only.
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from app.characters.domain.exceptions import (
    InvalidCharacterError,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ABILITY_SCORE_MIN = 1
ABILITY_SCORE_MAX = 30
CHARACTER_NAME_MAX_LEN = 100
CHARACTER_BACKGROUND_MAX_LEN = 500

# ---------------------------------------------------------------------------
# Value Objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AbilityScores:
    """
    The six core D&D ability scores.

    Each score must be between 1 and 30 inclusive. Modifiers are not stored
    here — they are derived by callers as floor((score - 10) / 2).
    """

    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    def __post_init__(self) -> None:
        for field_name in (
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, int):
                raise InvalidCharacterError(
                    f"Ability score '{field_name}' must be an integer"
                )
            if value < ABILITY_SCORE_MIN or value > ABILITY_SCORE_MAX:
                raise InvalidCharacterError(
                    f"Ability score '{field_name}' must be between "
                    f"{ABILITY_SCORE_MIN} and {ABILITY_SCORE_MAX}, got {value}"
                )


# ---------------------------------------------------------------------------
# Aggregate Root
# ---------------------------------------------------------------------------


@dataclass
class Character:
    """
    Aggregate root for the characters bounded context.

    A character is created by a player (or DM) and belongs to a specific
    world (for theme validation). It may optionally be linked to a campaign.

    Invariants enforced here:
    - name must not be empty and must not exceed CHARACTER_NAME_MAX_LEN
    - background must not exceed CHARACTER_BACKGROUND_MAX_LEN
    - class_id and species_id must be set (they are validated against theme at
      the application layer, not here)
    """

    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    world_id: uuid.UUID
    class_id: uuid.UUID
    species_id: uuid.UUID
    background: str
    ability_scores: AbilityScores
    # campaign_id is set when the character is linked to a campaign (US-029).
    # None means the character exists but has not been linked yet.
    campaign_id: uuid.UUID | None
    created_at: datetime

    @classmethod
    def create(
        cls,
        name: str,
        owner_id: uuid.UUID,
        world_id: uuid.UUID,
        class_id: uuid.UUID,
        species_id: uuid.UUID,
        background: str,
        ability_scores: AbilityScores,
    ) -> "Character":
        """
        Factory method that enforces domain invariants before creating a character.

        Raises InvalidCharacterError if any field violates the business rules.
        """
        name = name.strip()
        if not name:
            raise InvalidCharacterError("Character name must not be empty")
        if len(name) > CHARACTER_NAME_MAX_LEN:
            raise InvalidCharacterError(
                f"Character name must not exceed {CHARACTER_NAME_MAX_LEN} characters"
            )
        if len(background) > CHARACTER_BACKGROUND_MAX_LEN:
            raise InvalidCharacterError(
                f"Background must not exceed {CHARACTER_BACKGROUND_MAX_LEN} characters"
            )

        char_id = uuid.uuid4()
        logger.info(
            "Character.create: id=%s name=%s owner_id=%s world_id=%s",
            char_id,
            name,
            owner_id,
            world_id,
        )
        return cls(
            id=char_id,
            name=name,
            owner_id=owner_id,
            world_id=world_id,
            class_id=class_id,
            species_id=species_id,
            background=background,
            ability_scores=ability_scores,
            campaign_id=None,
            created_at=datetime.now(tz=timezone.utc),
        )

    def link_to_campaign(self, campaign_id: uuid.UUID) -> None:
        """
        Link this character to a campaign.

        Raises InvalidCharacterError if the character is already linked
        to a different campaign.
        """
        if self.campaign_id is not None and self.campaign_id != campaign_id:
            raise InvalidCharacterError(
                f"Character {self.id} is already linked to campaign {self.campaign_id}"
            )
        logger.info(
            "Character.link_to_campaign: character_id=%s campaign_id=%s",
            self.id,
            campaign_id,
        )
        self.campaign_id = campaign_id

    def unlink_from_campaign(self) -> None:
        """Remove the campaign link from this character."""
        logger.info("Character.unlink_from_campaign: character_id=%s", self.id)
        self.campaign_id = None

"""
Domain models for the campaigns bounded context.

Campaign is the aggregate root. It captures the DM's requirements for a
campaign and links to the admin-seeded World that was selected at creation.
world_id is set at creation and never changes — a campaign belongs to exactly
one world for its entire lifetime.

No SQLAlchemy or FastAPI imports belong here. Pure Python domain logic only.
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from app.campaigns.domain.exceptions import InvalidCampaignError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PLAYER_COUNT_MIN = 1
PLAYER_COUNT_MAX = 8
LEVEL_MIN = 1
LEVEL_MAX = 20


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CampaignTone(str, Enum):
    """Emotional register and narrative style of the campaign."""

    DARK_FANTASY = "dark_fantasy"
    HIGH_FANTASY = "high_fantasy"
    HORROR = "horror"
    POLITICAL_INTRIGUE = "political_intrigue"
    SWASHBUCKLING = "swashbuckling"


# ---------------------------------------------------------------------------
# Value Objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LevelRange:
    """
    Ordered pair of start and end levels for the campaign arc.

    Validated on construction — raises InvalidCampaignError if the range
    violates LEVEL_MIN <= start <= end <= LEVEL_MAX.
    """

    start: int
    end: int

    def __post_init__(self) -> None:
        if not (LEVEL_MIN <= self.start <= self.end <= LEVEL_MAX):
            raise InvalidCampaignError(
                f"LevelRange must satisfy {LEVEL_MIN} <= start <= end <= {LEVEL_MAX}, "
                f"got start={self.start} end={self.end}"
            )


@dataclass(frozen=True)
class ContentBoundaries:
    """
    Safety tool for tonal content management.

    Lines are hard limits the LLM must never generate.
    Stored as an immutable tuple of DM-entered strings.
    """

    lines: tuple[str, ...]


# ---------------------------------------------------------------------------
# Aggregate Root
# ---------------------------------------------------------------------------


@dataclass
class Campaign:
    """
    Aggregate root for the campaigns bounded context.

    Holds all DM requirements for a campaign and permanently references the
    World selected at creation. world_id is required and immutable after
    creation — the world provides the narrative context for dungeon generation.

    Business invariants are enforced by Campaign.create() — never set fields
    directly.
    """

    id: uuid.UUID
    name: str
    edition: str
    tone: CampaignTone
    player_count: int
    level_range: LevelRange
    themes: tuple[str, ...]
    content_boundaries: ContentBoundaries
    dm_id: uuid.UUID
    # world_id is mandatory — set at creation from the selected admin world
    world_id: uuid.UUID
    created_at: datetime

    @classmethod
    def create(
        cls,
        name: str,
        edition: str,
        tone: CampaignTone,
        player_count: int,
        level_range: LevelRange,
        themes: tuple[str, ...],
        content_boundaries: ContentBoundaries,
        dm_id: uuid.UUID,
        world_id: uuid.UUID,
    ) -> "Campaign":
        """
        Factory method — creates a new Campaign and validates invariants.

        world_id is the UUID of the admin-seeded World the DM selected.
        The id and created_at are generated here so callers never set them.
        LevelRange validates its own range in __post_init__; remaining
        checks are done below.

        @param world_id - UUID of the selected World aggregate (required).
        @raises InvalidCampaignError if player_count is out of range.
        """
        if not (PLAYER_COUNT_MIN <= player_count <= PLAYER_COUNT_MAX):
            raise InvalidCampaignError(
                f"player_count must be {PLAYER_COUNT_MIN}–{PLAYER_COUNT_MAX}, "
                f"got {player_count}"
            )

        campaign_id = uuid.uuid4()
        now = datetime.now(tz=timezone.utc)
        campaign = cls(
            id=campaign_id,
            name=name,
            edition=edition,
            tone=tone,
            player_count=player_count,
            level_range=level_range,
            themes=themes,
            content_boundaries=content_boundaries,
            dm_id=dm_id,
            world_id=world_id,
            created_at=now,
        )
        logger.info(
            "Campaign.create: id=%s name='%s' dm_id=%s world_id=%s",
            campaign_id,
            name,
            dm_id,
            world_id,
        )
        return campaign

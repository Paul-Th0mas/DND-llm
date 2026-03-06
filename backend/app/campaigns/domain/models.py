"""
Domain models for the campaigns bounded context.

Campaign is the aggregate root. It captures all DM requirements for a
campaign: tone, themes, content boundaries (Lines & Veils), edition, and
level range. The world_id field is None until POST /campaigns/{id}/world
is called.

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
SESSION_COUNT_MIN = 1
SESSION_COUNT_MAX = 100


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


class SettingPreference(str, Enum):
    """Published world or homebrew setting the campaign uses."""

    HOMEBREW = "homebrew"
    FORGOTTEN_REALMS = "forgotten_realms"
    EBERRON = "eberron"
    RAVENLOFT = "ravenloft"
    GREYHAWK = "greyhawk"


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
    Safety tool for tonal content management (Lines & Veils).

    Lines are hard limits the LLM must never generate.
    Veils are topics that may be referenced but never described in detail.
    Both are stored as immutable tuples of DM-entered strings.
    """

    lines: tuple[str, ...]
    veils: tuple[str, ...]


# ---------------------------------------------------------------------------
# Aggregate Root
# ---------------------------------------------------------------------------


@dataclass
class Campaign:
    """
    Aggregate root for the campaigns bounded context.

    Holds all DM requirements for a campaign and acts as the anchor for
    downstream generation (world, quests, session prep). Business invariants
    are enforced by the Campaign.create() factory — never set fields directly.

    The world_id is None until POST /campaigns/{id}/world is called, at which
    point attach_world() links the campaign to its generated world.
    """

    id: uuid.UUID
    name: str
    edition: str
    tone: CampaignTone
    player_count: int
    level_range: LevelRange
    session_count_estimate: int
    setting_preference: SettingPreference
    themes: tuple[str, ...]
    content_boundaries: ContentBoundaries
    homebrew_rules: tuple[str, ...]
    inspirations: str | None
    dm_id: uuid.UUID
    created_at: datetime
    world_id: uuid.UUID | None = None

    @classmethod
    def create(
        cls,
        name: str,
        edition: str,
        tone: CampaignTone,
        player_count: int,
        level_range: LevelRange,
        session_count_estimate: int,
        setting_preference: SettingPreference,
        themes: tuple[str, ...],
        content_boundaries: ContentBoundaries,
        homebrew_rules: tuple[str, ...],
        inspirations: str | None,
        dm_id: uuid.UUID,
    ) -> "Campaign":
        """
        Factory method — creates a new Campaign and validates invariants.

        The id and created_at are generated here so callers never set them manually.
        LevelRange validates its own range in __post_init__; remaining checks are here.
        """
        if not (PLAYER_COUNT_MIN <= player_count <= PLAYER_COUNT_MAX):
            raise InvalidCampaignError(
                f"player_count must be {PLAYER_COUNT_MIN}–{PLAYER_COUNT_MAX}, "
                f"got {player_count}"
            )
        if not (SESSION_COUNT_MIN <= session_count_estimate <= SESSION_COUNT_MAX):
            raise InvalidCampaignError(
                f"session_count_estimate must be {SESSION_COUNT_MIN}–{SESSION_COUNT_MAX}, "
                f"got {session_count_estimate}"
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
            session_count_estimate=session_count_estimate,
            setting_preference=setting_preference,
            themes=themes,
            content_boundaries=content_boundaries,
            homebrew_rules=homebrew_rules,
            inspirations=inspirations,
            dm_id=dm_id,
            created_at=now,
        )
        logger.info(
            "Campaign.create: id=%s name='%s' dm_id=%s", campaign_id, name, dm_id
        )
        return campaign

    def attach_world(self, world_id: uuid.UUID) -> None:
        """
        Link this campaign to a generated world. Can only be called once.

        Raises InvalidCampaignError if a world is already attached, preventing
        accidental world regeneration from overwriting the existing one.
        """
        if self.world_id is not None:
            raise InvalidCampaignError(
                f"Campaign {self.id} already has a world attached: {self.world_id}"
            )
        self.world_id = world_id
        logger.info("Campaign %s attached world %s", self.id, world_id)

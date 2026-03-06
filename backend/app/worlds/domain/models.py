"""
Domain models for the worlds bounded context.

Contains all enums, value objects, and the GeneratedWorld aggregate.

No SQLAlchemy or FastAPI imports belong here. This is pure Python domain logic.
The domain enforces its own invariants via validate() on WorldSettings.
"""

import logging
from dataclasses import dataclass
from enum import Enum

from app.worlds.domain.exceptions import InvalidWorldSettingsError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

# Valid room count bounds — enforced by WorldSettings.validate()
ROOM_COUNT_MIN = 5
ROOM_COUNT_MAX = 15


class Theme(str, Enum):
    """The narrative setting of a generated world."""

    MEDIEVAL_FANTASY = "MEDIEVAL_FANTASY"
    CYBERPUNK = "CYBERPUNK"
    MANHWA = "MANHWA"
    POST_APOCALYPTIC = "POST_APOCALYPTIC"


class Difficulty(str, Enum):
    """How aggressively enemies scale in the generated world."""

    EASY = "EASY"
    NORMAL = "NORMAL"
    HARD = "HARD"
    NIGHTMARE = "NIGHTMARE"


class QuestFocus(str, Enum):
    """The primary narrative lens that shapes the generated quest."""

    EXPLORATION = "EXPLORATION"
    RESCUE = "RESCUE"
    ASSASSINATION = "ASSASSINATION"
    HEIST = "HEIST"
    MYSTERY = "MYSTERY"


class RoomType(str, Enum):
    """The function and flavour of a single dungeon room."""

    COMBAT = "COMBAT"
    SHOP = "SHOP"
    REST = "REST"
    BOSS = "BOSS"
    TREASURE = "TREASURE"
    EVENT = "EVENT"


# ---------------------------------------------------------------------------
# Value Objects (frozen dataclasses — immutable, identity-less)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WorldSettings:
    """
    Describes the DM's configuration for a world generation request.

    This is a value object: two WorldSettings with the same field values are
    considered equal. Immutability prevents accidental mutation during
    the generation pipeline.
    """

    theme: Theme
    difficulty: Difficulty
    room_count: int
    quest_focus: QuestFocus
    dm_notes: str | None = None
    party_size: int = 1

    def validate(self) -> None:
        """
        Enforce domain invariants.

        Raises InvalidWorldSettingsError if any field violates a business rule.
        Called explicitly by the application layer after construction from the
        incoming DTO — keeps validation in the domain, not in schemas or routers.
        """
        if not (ROOM_COUNT_MIN <= self.room_count <= ROOM_COUNT_MAX):
            raise InvalidWorldSettingsError(
                f"room_count must be between {ROOM_COUNT_MIN} and {ROOM_COUNT_MAX}, "
                f"got {self.room_count}"
            )
        logger.debug(
            "WorldSettings validated: theme=%s difficulty=%s rooms=%d",
            self.theme,
            self.difficulty,
            self.room_count,
        )


@dataclass(frozen=True)
class NarratedRoom:
    """
    A single room within a generated world.

    index is 0-based. room_type determines the encounter flavour.
    enemy_names and npc_names are tuples (immutable sequences) of display names.
    """

    index: int
    room_type: RoomType
    name: str
    description: str
    enemy_names: tuple[str, ...]
    npc_names: tuple[str, ...]
    special_notes: str | None = None


@dataclass(frozen=True)
class MainQuest:
    """
    The primary quest thread for a generated world.

    stages is an ordered tuple of narrative beat descriptions — one per
    major milestone the party must reach to complete the quest.
    """

    name: str
    description: str
    stages: tuple[str, ...]


@dataclass(frozen=True)
class GeneratedWorld:
    """
    Aggregate root representing a fully generated world.

    Returned by NarratorPort.generate_world() and handed to the application
    layer for schema conversion. len(rooms) must match the room_count in the
    originating WorldSettings — callers may assert this if needed.
    """

    world_name: str
    world_description: str
    atmosphere: str
    theme: Theme
    rooms: tuple[NarratedRoom, ...]
    main_quest: MainQuest
    active_factions: tuple[str, ...]

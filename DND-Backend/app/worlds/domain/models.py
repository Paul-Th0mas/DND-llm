"""
World domain models.

Contains all enums, value objects, entities, and the WorldSkeleton aggregate root.
No SQLAlchemy or FastAPI imports belong here — pure Python domain logic only.

Key concepts:
  - Theme         — a value object describing narrative style (tone, language, currency)
  - DungeonRoom   — a value object describing one room in a 10-room run
  - EnemyPreset   — an entity storing stat blocks for an enemy archetype
  - ItemPreset    — an entity storing a shop item definition
  - NPCPreset     — an entity storing an NPC personality for the narrator
  - QuestTemplate — an entity defining a quest arc with staged narrative beats
  - WorldSkeleton — the aggregate root; owns the full compiled dungeon run
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto

from app.combat.domain.models import DieType  # reuses the combat die type enum

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ThemeName(str, Enum):
    """The three supported dungeon themes. str base allows JSON serialisation."""

    MEDIEVAL_FANTASY = "medieval_fantasy"
    CYBERPUNK = "cyberpunk"
    MANHWA = "manhwa"


class RoomType(Enum):
    """What kind of encounter waits in a dungeon room."""

    COMBAT = auto()
    SHOP = auto()
    REST = auto()
    BOSS = auto()
    TREASURE = auto()
    EVENT = auto()


class QuestType(Enum):
    MAIN = auto()
    SIDE = auto()


class AIBehavior(Enum):
    """How an enemy AI selects its targets and actions."""

    AGGRESSIVE = auto()  # always attacks the lowest-HP target
    DEFENSIVE = auto()  # retreats / blocks when own HP < 50 %
    STRATEGIC = auto()  # targets the highest-threat player first
    SUPPORT = auto()  # heals/buffs allies before attacking


class ItemType(Enum):
    WEAPON = auto()
    ARMOR = auto()
    ACCESSORY = auto()
    RELIC = auto()


class NPCRole(Enum):
    MERCHANT = auto()
    QUEST_GIVER = auto()
    ANTAGONIST = auto()
    ALLY = auto()


# ---------------------------------------------------------------------------
# Value Objects (frozen — identity comes from content, not reference)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Theme:
    """
    Narrative style definition for a dungeon run.
    All fields are strings that the LLM narrator interpolates into its system prompt.
    """

    name: ThemeName
    tone_descriptor: str  # e.g. "gritty dark fantasy", "neon dystopian"
    language_style: str  # e.g. "archaic formal", "slang-heavy street"
    currency_name: str  # e.g. "Gold", "Credits", "Spirit Coins"
    health_term: str  # e.g. "Hit Points", "Integrity", "Chi"
    death_term: str  # e.g. "slain", "flatlined", "dispersed"
    banned_words: tuple[str, ...]  # words that would break theme immersion


@dataclass(frozen=True)
class QuestStage:
    """A single narrative beat in a multi-stage quest."""

    stage_number: int
    title: str
    description: str  # what the LLM uses to narrate this beat
    trigger_room: int  # which room number activates this stage
    completion_condition: str  # e.g. "defeat boss", "find item", "talk to npc"


@dataclass(frozen=True)
class DungeonRoom:
    """
    One room in the 10-room dungeon sequence.

    enemy_preset_ids — references to EnemyPreset.id values that spawn here.
    npc_preset_id    — optional NPC that appears (merchant, quest giver, etc.).
    lore_seed        — thematic hint phrase passed to the LLM narrator.
    """

    room_number: int  # 1–10
    room_type: RoomType
    enemy_preset_ids: tuple[str, ...]  # empty for non-combat rooms
    npc_preset_id: str | None
    lore_seed: str
    is_boss_room: bool


# ---------------------------------------------------------------------------
# Entities (mutable — identity comes from their id field)
# ---------------------------------------------------------------------------


@dataclass
class EnemyPreset:
    """
    Stat block for a reusable enemy archetype.

    die_type and pool_size feed directly into StartCombatUseCase when the
    combat context creates Combatants from this preset data.
    """

    id: str
    theme: ThemeName
    name: str
    hp: int
    die_type: DieType
    pool_size: int
    ai_behavior: AIBehavior
    lore_tags: list[str]


@dataclass
class ItemPreset:
    """A purchasable shop item. chips_bonus/mult_bonus apply to the combat hand scorer."""

    id: str
    theme: ThemeName
    name: str
    item_type: ItemType
    rarity: str  # "common", "uncommon", "rare", "legendary"
    gold_cost: int
    chips_bonus: int
    mult_bonus: int
    description: str


@dataclass
class NPCPreset:
    """
    Personality definition for an NPC the narrator can voice.

    speech_style is an instruction for the LLM (e.g. "speaks in riddles").
    """

    id: str
    theme: ThemeName
    name: str
    role: NPCRole
    personality_traits: list[str]
    speech_style: str
    faction: str | None


@dataclass
class QuestTemplate:
    """A quest arc with ordered narrative stages and rewards."""

    id: str
    theme: ThemeName
    name: str
    quest_type: QuestType
    stages: list[QuestStage]
    reward_gold: int
    reward_item_ids: list[str]


# ---------------------------------------------------------------------------
# Settings value object
# ---------------------------------------------------------------------------


@dataclass
class WorldSettings:
    """Player-visible configuration submitted when compiling a world."""

    theme: ThemeName
    difficulty: str  # "easy", "normal", "hard", "nightmare"
    room_count: int = 10
    seed: int | None = None  # optional seed for reproducible runs


# ---------------------------------------------------------------------------
# WorldSkeleton — aggregate root
# ---------------------------------------------------------------------------


@dataclass
class WorldSkeleton:
    """
    Aggregate root for a compiled dungeon run.

    Owns the full 10-room sequence, active quests, available shop items, and
    narrative flags set by player choices. All mutations go through methods on
    this class — callers must not mutate sub-objects directly.

    room_id links to the multiplayer Room (rooms bounded context). The worlds
    context does not import Room directly; it only stores the UUID reference.
    """

    id: uuid.UUID
    room_id: uuid.UUID  # FK to rooms.Room (stored as UUID, not imported)
    theme: Theme
    settings: WorldSettings
    room_sequence: list[DungeonRoom]  # ordered 1–10
    active_quests: list[QuestTemplate]
    available_items: list[ItemPreset]  # shop inventory for this run
    world_flags: dict[str, bool]  # narrative flags (e.g. "betrayed_faction_A")
    created_at: datetime

    def get_room(self, room_number: int) -> DungeonRoom:
        """
        Return the DungeonRoom for the given room number (1-based).
        Raises WorldRoomNotFoundError if room_number is out of range.
        Import is local to avoid circular dependency with repositories module.
        """
        # Local import so models.py does not depend on repositories.py.
        from app.worlds.domain.repositories import WorldRoomNotFoundError

        logger.debug("WorldSkeleton %s get_room room_number=%d", self.id, room_number)
        for room in self.room_sequence:
            if room.room_number == room_number:
                return room
        raise WorldRoomNotFoundError(
            f"Room {room_number} does not exist in world {self.id}"
        )

    def set_flag(self, flag: str, value: bool) -> None:
        """
        Set a narrative flag.
        Flags drive branching narration (e.g. 'rescued_prisoner': True).
        """
        logger.debug("WorldSkeleton %s set_flag %s=%s", self.id, flag, value)
        self.world_flags[flag] = value

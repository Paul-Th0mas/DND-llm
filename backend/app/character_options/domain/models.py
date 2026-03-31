"""
Domain models for the character_options bounded context.

CharacterClass and CharacterSpecies are read-only reference data
(seeded by admins). They are aggregate roots in the sense that nothing
else owns them, but they have no lifecycle — they are never mutated by
user actions.

No SQLAlchemy or FastAPI imports belong here. Pure Python domain logic only.
"""

import logging
import uuid
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Aggregates (read-only reference data)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CharacterClass:
    """
    A playable character class (e.g. Fighter, Wizard).

    chassis_name is the internal canonical key (e.g. "fighter").
    display_name is the human-readable label shown to players.
    hit_die is the integer size of the class's hit die (e.g. 10 for d10).
    primary_ability is the key stat for this class (e.g. "Strength").
    spellcasting_ability is None for non-casters; a string (e.g. "Intelligence")
    for classes that can cast spells.
    theme is the world theme this class belongs to (matches worlds.Theme values).
    """

    id: uuid.UUID
    display_name: str
    chassis_name: str
    hit_die: int
    primary_ability: str
    spellcasting_ability: str | None
    theme: str


@dataclass(frozen=True)
class CharacterSpecies:
    """
    A playable species/race (e.g. Human, Elf).

    archetype_key is the internal canonical identifier (e.g. "elf").
    display_name is the human-readable label shown to players.
    size is a string descriptor (e.g. "Medium").
    speed is movement in feet per turn (e.g. 30).
    traits is an ordered list of trait descriptions.
    theme is the world theme this species belongs to.
    """

    id: uuid.UUID
    display_name: str
    archetype_key: str
    size: str
    speed: int
    traits: tuple[str, ...]
    theme: str

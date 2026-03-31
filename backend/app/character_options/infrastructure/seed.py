"""
Seed script for character classes and species.

Populates character_classes and character_species tables with fixed reference
data for all supported world themes. Safe to run multiple times — existing rows
are merged by primary key (idempotent).

UUIDs use a fixed prefix scheme:
  - MEDIEVAL_FANTASY classes:  11111111-0000-0000-0000-{sequence}
  - MEDIEVAL_FANTASY species:  22222222-0000-0000-0000-{sequence}
  - CYBERPUNK classes:         33333333-0000-0000-0000-{sequence}
  - CYBERPUNK species:         44444444-0000-0000-0000-{sequence}
  - POST_APOCALYPTIC classes:  55555555-0000-0000-0000-{sequence}
  - POST_APOCALYPTIC species:  66666666-0000-0000-0000-{sequence}

Usage from CLI (run from the backend/ directory):
    python -m app.character_options.infrastructure.seed
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.character_options.infrastructure.orm_models import (
    CharacterClassORM,
    CharacterSpeciesORM,
)
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

_NOW = datetime.now(tz=timezone.utc)

# ---------------------------------------------------------------------------
# MEDIEVAL_FANTASY — classes (prefix 11111111-...)
# ---------------------------------------------------------------------------

_MF_CLASSES: list[CharacterClassORM] = [
    CharacterClassORM(
        id=uuid.UUID("11111111-0000-0000-0000-000000000001"),
        display_name="Fighter",
        chassis_name="fighter",
        hit_die=10,
        primary_ability="Strength",
        spellcasting_ability=None,
        theme="MEDIEVAL_FANTASY",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterClassORM(
        id=uuid.UUID("11111111-0000-0000-0000-000000000002"),
        display_name="Wizard",
        chassis_name="wizard",
        hit_die=6,
        primary_ability="Intelligence",
        spellcasting_ability="Intelligence",
        theme="MEDIEVAL_FANTASY",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterClassORM(
        id=uuid.UUID("11111111-0000-0000-0000-000000000003"),
        display_name="Rogue",
        chassis_name="rogue",
        hit_die=8,
        primary_ability="Dexterity",
        spellcasting_ability=None,
        theme="MEDIEVAL_FANTASY",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterClassORM(
        id=uuid.UUID("11111111-0000-0000-0000-000000000004"),
        display_name="Cleric",
        chassis_name="cleric",
        hit_die=8,
        primary_ability="Wisdom",
        spellcasting_ability="Wisdom",
        theme="MEDIEVAL_FANTASY",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterClassORM(
        id=uuid.UUID("11111111-0000-0000-0000-000000000005"),
        display_name="Ranger",
        chassis_name="ranger",
        hit_die=10,
        primary_ability="Dexterity",
        spellcasting_ability="Wisdom",
        theme="MEDIEVAL_FANTASY",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterClassORM(
        id=uuid.UUID("11111111-0000-0000-0000-000000000006"),
        display_name="Paladin",
        chassis_name="paladin",
        hit_die=10,
        primary_ability="Strength",
        spellcasting_ability="Charisma",
        theme="MEDIEVAL_FANTASY",
        is_active=True,
        created_at=_NOW,
    ),
]

# ---------------------------------------------------------------------------
# MEDIEVAL_FANTASY — species (prefix 22222222-...)
# ---------------------------------------------------------------------------

_MF_SPECIES: list[CharacterSpeciesORM] = [
    CharacterSpeciesORM(
        id=uuid.UUID("22222222-0000-0000-0000-000000000001"),
        display_name="Human",
        archetype_key="human",
        size="Medium",
        speed=30,
        traits=["Versatile", "Extra skill proficiency", "Extra feat at 1st level"],
        theme="MEDIEVAL_FANTASY",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterSpeciesORM(
        id=uuid.UUID("22222222-0000-0000-0000-000000000002"),
        display_name="Elf",
        archetype_key="elf",
        size="Medium",
        speed=30,
        traits=["Darkvision 60 ft", "Fey Ancestry", "Trance (4-hour rest)"],
        theme="MEDIEVAL_FANTASY",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterSpeciesORM(
        id=uuid.UUID("22222222-0000-0000-0000-000000000003"),
        display_name="Dwarf",
        archetype_key="dwarf",
        size="Medium",
        speed=25,
        traits=[
            "Darkvision 60 ft",
            "Dwarven Resilience (poison advantage & resistance)",
            "Stonecunning",
            "Tool proficiency",
        ],
        theme="MEDIEVAL_FANTASY",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterSpeciesORM(
        id=uuid.UUID("22222222-0000-0000-0000-000000000004"),
        display_name="Halfling",
        archetype_key="halfling",
        size="Small",
        speed=25,
        traits=[
            "Lucky (reroll 1s on d20)",
            "Brave (advantage vs. frightened)",
            "Nimbleness",
        ],
        theme="MEDIEVAL_FANTASY",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterSpeciesORM(
        id=uuid.UUID("22222222-0000-0000-0000-000000000005"),
        display_name="Gnome",
        archetype_key="gnome",
        size="Small",
        speed=25,
        traits=[
            "Darkvision 60 ft",
            "Gnome Cunning (advantage on INT/WIS/CHA saves vs. magic)",
        ],
        theme="MEDIEVAL_FANTASY",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterSpeciesORM(
        id=uuid.UUID("22222222-0000-0000-0000-000000000006"),
        display_name="Half-Orc",
        archetype_key="half_orc",
        size="Medium",
        speed=30,
        traits=[
            "Darkvision 60 ft",
            "Relentless Endurance (1/long rest: drop to 1 HP instead of 0)",
            "Savage Attacks (extra die on crit melee)",
        ],
        theme="MEDIEVAL_FANTASY",
        is_active=True,
        created_at=_NOW,
    ),
]

# ---------------------------------------------------------------------------
# CYBERPUNK — classes (prefix 33333333-...)
# ---------------------------------------------------------------------------

_CP_CLASSES: list[CharacterClassORM] = [
    CharacterClassORM(
        id=uuid.UUID("33333333-0000-0000-0000-000000000001"),
        display_name="Street Samurai",
        chassis_name="street_samurai",
        hit_die=10,
        primary_ability="Strength",
        spellcasting_ability=None,
        theme="CYBERPUNK",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterClassORM(
        id=uuid.UUID("33333333-0000-0000-0000-000000000002"),
        display_name="Netrunner",
        chassis_name="netrunner",
        hit_die=6,
        primary_ability="Intelligence",
        spellcasting_ability="Intelligence",
        theme="CYBERPUNK",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterClassORM(
        id=uuid.UUID("33333333-0000-0000-0000-000000000003"),
        display_name="Ghost",
        chassis_name="ghost",
        hit_die=8,
        primary_ability="Dexterity",
        spellcasting_ability=None,
        theme="CYBERPUNK",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterClassORM(
        id=uuid.UUID("33333333-0000-0000-0000-000000000004"),
        display_name="Medtech",
        chassis_name="medtech",
        hit_die=8,
        primary_ability="Wisdom",
        spellcasting_ability="Wisdom",
        theme="CYBERPUNK",
        is_active=True,
        created_at=_NOW,
    ),
]

# ---------------------------------------------------------------------------
# CYBERPUNK — species (prefix 44444444-...)
# ---------------------------------------------------------------------------

_CP_SPECIES: list[CharacterSpeciesORM] = [
    CharacterSpeciesORM(
        id=uuid.UUID("44444444-0000-0000-0000-000000000001"),
        display_name="Human",
        archetype_key="human_cp",
        size="Medium",
        speed=30,
        traits=["Adaptable (bonus skill)", "Black-market contacts"],
        theme="CYBERPUNK",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterSpeciesORM(
        id=uuid.UUID("44444444-0000-0000-0000-000000000002"),
        display_name="Chrome-Born",
        archetype_key="chrome_born",
        size="Medium",
        speed=30,
        traits=[
            "Subdermal armor (+1 AC)",
            "Neural Interface (advantage on hacking checks)",
            "Chrome Fatigue (disadvantage on Charisma checks with un-augmented)",
        ],
        theme="CYBERPUNK",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterSpeciesORM(
        id=uuid.UUID("44444444-0000-0000-0000-000000000003"),
        display_name="Synth",
        archetype_key="synth",
        size="Medium",
        speed=30,
        traits=[
            "Immune to poison and disease",
            "No need to eat, drink, or breathe",
            "Does not benefit from magical healing — repairs require a Tech check",
        ],
        theme="CYBERPUNK",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterSpeciesORM(
        id=uuid.UUID("44444444-0000-0000-0000-000000000004"),
        display_name="Uplifted",
        archetype_key="uplifted",
        size="Medium",
        speed=30,
        traits=[
            "Enhanced senses (Perception advantage)",
            "Pack Tactics (advantage when ally is adjacent to target)",
        ],
        theme="CYBERPUNK",
        is_active=True,
        created_at=_NOW,
    ),
]

# ---------------------------------------------------------------------------
# POST_APOCALYPTIC — classes (prefix 55555555-...)
# ---------------------------------------------------------------------------

_PA_CLASSES: list[CharacterClassORM] = [
    CharacterClassORM(
        id=uuid.UUID("55555555-0000-0000-0000-000000000001"),
        display_name="Wastelander",
        chassis_name="wastelander",
        hit_die=12,
        primary_ability="Constitution",
        spellcasting_ability=None,
        theme="POST_APOCALYPTIC",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterClassORM(
        id=uuid.UUID("55555555-0000-0000-0000-000000000002"),
        display_name="Techno-Mage",
        chassis_name="techno_mage",
        hit_die=6,
        primary_ability="Intelligence",
        spellcasting_ability="Intelligence",
        theme="POST_APOCALYPTIC",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterClassORM(
        id=uuid.UUID("55555555-0000-0000-0000-000000000003"),
        display_name="Scavenger",
        chassis_name="scavenger",
        hit_die=8,
        primary_ability="Dexterity",
        spellcasting_ability=None,
        theme="POST_APOCALYPTIC",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterClassORM(
        id=uuid.UUID("55555555-0000-0000-0000-000000000004"),
        display_name="Field Medic",
        chassis_name="field_medic",
        hit_die=8,
        primary_ability="Wisdom",
        spellcasting_ability="Wisdom",
        theme="POST_APOCALYPTIC",
        is_active=True,
        created_at=_NOW,
    ),
]

# ---------------------------------------------------------------------------
# POST_APOCALYPTIC — species (prefix 66666666-...)
# ---------------------------------------------------------------------------

_PA_SPECIES: list[CharacterSpeciesORM] = [
    CharacterSpeciesORM(
        id=uuid.UUID("66666666-0000-0000-0000-000000000001"),
        display_name="Survivor",
        archetype_key="survivor",
        size="Medium",
        speed=30,
        traits=[
            "Hardened (advantage vs. exhaustion)",
            "Scavenger's Eye (double proficiency on Survival checks)",
        ],
        theme="POST_APOCALYPTIC",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterSpeciesORM(
        id=uuid.UUID("66666666-0000-0000-0000-000000000002"),
        display_name="Vault Dweller",
        archetype_key="vault_dweller",
        size="Medium",
        speed=30,
        traits=[
            "Vault Training (proficiency in one tool or weapon of choice)",
            "Vault-Tec Education (bonus to History and Technology checks)",
        ],
        theme="POST_APOCALYPTIC",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterSpeciesORM(
        id=uuid.UUID("66666666-0000-0000-0000-000000000003"),
        display_name="Mutant",
        archetype_key="mutant",
        size="Medium",
        speed=30,
        traits=[
            "Radiation Resistance (advantage on saves vs. radiation damage)",
            "Unstable Mutation (roll on mutation table at character creation for a random trait)",
        ],
        theme="POST_APOCALYPTIC",
        is_active=True,
        created_at=_NOW,
    ),
    CharacterSpeciesORM(
        id=uuid.UUID("66666666-0000-0000-0000-000000000004"),
        display_name="Android",
        archetype_key="android",
        size="Medium",
        speed=30,
        traits=[
            "Immune to poison and disease",
            "No need to eat, drink, or sleep (4 hours of maintenance replaces a long rest)",
            "Synthetic Body (disadvantage vs. EMP damage)",
        ],
        theme="POST_APOCALYPTIC",
        is_active=True,
        created_at=_NOW,
    ),
]


# ---------------------------------------------------------------------------
# Seed function
# ---------------------------------------------------------------------------


def seed_character_options(session: Session) -> None:
    """
    Insert or update all character class and species reference data.

    Uses session.merge() so this is safe to call multiple times
    (existing rows with matching PKs are updated, not duplicated).
    """
    all_classes = _MF_CLASSES + _CP_CLASSES + _PA_CLASSES
    all_species = _MF_SPECIES + _CP_SPECIES + _PA_SPECIES

    for cls in all_classes:
        session.merge(cls)
        logger.debug("seed: merged class id=%s name=%s", cls.id, cls.display_name)

    for sp in all_species:
        session.merge(sp)
        logger.debug("seed: merged species id=%s name=%s", sp.id, sp.display_name)

    session.flush()
    logger.info(
        "seed_character_options: seeded %d classes, %d species",
        len(all_classes),
        len(all_species),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with SessionLocal() as _session:
        seed_character_options(_session)
        _session.commit()
    print("Character options seed complete.")

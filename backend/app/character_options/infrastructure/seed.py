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
        skill_options=[
            {"name": "Athletics", "ability": "Strength"},
            {"name": "Acrobatics", "ability": "Dexterity"},
            {"name": "History", "ability": "Intelligence"},
            {"name": "Insight", "ability": "Wisdom"},
            {"name": "Intimidation", "ability": "Charisma"},
            {"name": "Perception", "ability": "Wisdom"},
            {"name": "Survival", "ability": "Wisdom"},
        ],
        skill_choose_count=2,
        starting_equipment_items=[
            "Chain mail",
            "Longsword",
            "Shield",
            "2 Handaxes",
            "Explorer's pack",
        ],
        spell_options=None,
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
        skill_options=[
            {"name": "Arcana", "ability": "Intelligence"},
            {"name": "History", "ability": "Intelligence"},
            {"name": "Insight", "ability": "Wisdom"},
            {"name": "Investigation", "ability": "Intelligence"},
            {"name": "Medicine", "ability": "Wisdom"},
            {"name": "Religion", "ability": "Intelligence"},
        ],
        skill_choose_count=2,
        starting_equipment_items=[
            "Quarterstaff",
            "Spellbook",
            "Arcane focus",
            "Scholar's pack",
        ],
        spell_options=[
            {
                "level": 0,
                "label": "Cantrips",
                "choose_count": 3,
                "spells": [
                    {
                        "name": "Fire Bolt",
                        "description": "A mote of fire hurls at a target, dealing 1d10 fire damage.",
                    },
                    {
                        "name": "Mage Hand",
                        "description": "A spectral hand appears and manipulates objects at range.",
                    },
                    {
                        "name": "Prestidigitation",
                        "description": "Minor magical tricks and sensory effects for 1 hour.",
                    },
                    {
                        "name": "Ray of Frost",
                        "description": "A freezing beam dealing 1d8 cold damage and reducing speed by 10ft.",
                    },
                    {
                        "name": "Shocking Grasp",
                        "description": "Lightning shocks a target for 1d8 lightning and prevents reactions.",
                    },
                    {
                        "name": "Light",
                        "description": "Touch an object to shed bright light in a 20ft radius for 1 hour.",
                    },
                ],
            },
            {
                "level": 1,
                "label": "Level 1 Spells",
                "choose_count": 2,
                "spells": [
                    {
                        "name": "Magic Missile",
                        "description": "Three darts of magical force, each dealing 1d4+1 force damage.",
                    },
                    {
                        "name": "Burning Hands",
                        "description": "A sheet of flames deals 3d6 fire damage in a 15ft cone.",
                    },
                    {
                        "name": "Sleep",
                        "description": "Magical slumber affects up to 5d8 HP worth of creatures.",
                    },
                    {
                        "name": "Charm Person",
                        "description": "Charm a humanoid for 1 hour, treating you as a friendly acquaintance.",
                    },
                    {
                        "name": "Detect Magic",
                        "description": "Sense magic within 30ft for up to 10 minutes.",
                    },
                    {
                        "name": "Identify",
                        "description": "Learn the magical properties of an item or ongoing spell.",
                    },
                    {
                        "name": "Mage Armor",
                        "description": "Magical protection sets AC to 13+DEX modifier for 8 hours.",
                    },
                ],
            },
        ],
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
        skill_options=[
            {"name": "Acrobatics", "ability": "Dexterity"},
            {"name": "Athletics", "ability": "Strength"},
            {"name": "Deception", "ability": "Charisma"},
            {"name": "Insight", "ability": "Wisdom"},
            {"name": "Intimidation", "ability": "Charisma"},
            {"name": "Investigation", "ability": "Intelligence"},
            {"name": "Perception", "ability": "Wisdom"},
            {"name": "Performance", "ability": "Charisma"},
            {"name": "Persuasion", "ability": "Charisma"},
            {"name": "Sleight of Hand", "ability": "Dexterity"},
            {"name": "Stealth", "ability": "Dexterity"},
        ],
        skill_choose_count=4,
        starting_equipment_items=[
            "Rapier",
            "Shortbow",
            "20 arrows",
            "Thieves' tools",
            "Burglar's pack",
        ],
        spell_options=None,
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
        skill_options=[
            {"name": "History", "ability": "Intelligence"},
            {"name": "Insight", "ability": "Wisdom"},
            {"name": "Medicine", "ability": "Wisdom"},
            {"name": "Persuasion", "ability": "Charisma"},
            {"name": "Religion", "ability": "Intelligence"},
        ],
        skill_choose_count=2,
        starting_equipment_items=[
            "Mace",
            "Scale mail",
            "Shield",
            "Holy symbol",
            "Priest's pack",
        ],
        spell_options=[
            {
                "level": 0,
                "label": "Cantrips",
                "choose_count": 3,
                "spells": [
                    {
                        "name": "Sacred Flame",
                        "description": "Radiant flame descends on a target for 1d8 radiant damage, no cover applies.",
                    },
                    {
                        "name": "Guidance",
                        "description": "Touch a willing creature to add 1d4 to one ability check within 1 minute.",
                    },
                    {
                        "name": "Spare the Dying",
                        "description": "Touch a dying creature at 0 HP to stabilize it.",
                    },
                    {
                        "name": "Thaumaturgy",
                        "description": "Manifest minor wonders: tremors, flames, booming voices for 1 minute.",
                    },
                    {
                        "name": "Toll the Dead",
                        "description": "A mournful toll deals 1d12 necrotic to a weakened creature.",
                    },
                    {
                        "name": "Word of Radiance",
                        "description": "Radiant energy deals 1d6 damage to each hostile creature in 5ft.",
                    },
                ],
            },
            {
                "level": 1,
                "label": "Level 1 Spells",
                "choose_count": 2,
                "spells": [
                    {
                        "name": "Bless",
                        "description": "Up to three creatures gain 1d4 to attack rolls and saving throws for 1 minute.",
                    },
                    {
                        "name": "Cure Wounds",
                        "description": "A touch heals 1d8+WIS modifier HP.",
                    },
                    {
                        "name": "Healing Word",
                        "description": "A spoken word heals 1d4+WIS modifier HP at range.",
                    },
                    {
                        "name": "Shield of Faith",
                        "description": "A shimmering field raises a creature's AC by 2 for 10 minutes.",
                    },
                    {
                        "name": "Guiding Bolt",
                        "description": "A burst of light deals 4d6 radiant and grants advantage on the next attack.",
                    },
                    {
                        "name": "Sanctuary",
                        "description": "Ward a creature so attackers must succeed on a WIS save to target it.",
                    },
                    {
                        "name": "Command",
                        "description": "Utter a one-word command that a creature must obey on its next turn.",
                    },
                ],
            },
        ],
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
        skill_options=[
            {"name": "Animal Handling", "ability": "Wisdom"},
            {"name": "Athletics", "ability": "Strength"},
            {"name": "Insight", "ability": "Wisdom"},
            {"name": "Investigation", "ability": "Intelligence"},
            {"name": "Nature", "ability": "Intelligence"},
            {"name": "Perception", "ability": "Wisdom"},
            {"name": "Stealth", "ability": "Dexterity"},
            {"name": "Survival", "ability": "Wisdom"},
        ],
        skill_choose_count=3,
        starting_equipment_items=[
            "Shortsword",
            "Shortbow",
            "20 arrows",
            "Leather armor",
            "Explorer's pack",
        ],
        spell_options=[
            {
                "level": 0,
                "label": "Cantrips",
                "choose_count": 0,
                "spells": [],
            },
            {
                "level": 1,
                "label": "Level 1 Spells",
                "choose_count": 2,
                "spells": [
                    {
                        "name": "Hunter's Mark",
                        "description": "Mark a creature; deal extra 1d6 damage and track it for 1 hour.",
                    },
                    {
                        "name": "Animal Friendship",
                        "description": "Convince an animal you mean no harm with a CHA check.",
                    },
                    {
                        "name": "Cure Wounds",
                        "description": "A touch heals 1d8+WIS modifier HP.",
                    },
                    {
                        "name": "Fog Cloud",
                        "description": "Create a 20ft radius sphere of heavy fog for 1 hour.",
                    },
                    {
                        "name": "Goodberry",
                        "description": "Create 10 berries, each healing 1 HP and providing a day's nourishment.",
                    },
                    {
                        "name": "Longstrider",
                        "description": "Increase a creature's speed by 10ft for 1 hour.",
                    },
                    {
                        "name": "Speak with Animals",
                        "description": "Communicate with beasts for 10 minutes.",
                    },
                ],
            },
        ],
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
        skill_options=[
            {"name": "Athletics", "ability": "Strength"},
            {"name": "Insight", "ability": "Wisdom"},
            {"name": "Intimidation", "ability": "Charisma"},
            {"name": "Medicine", "ability": "Wisdom"},
            {"name": "Persuasion", "ability": "Charisma"},
            {"name": "Religion", "ability": "Intelligence"},
        ],
        skill_choose_count=2,
        starting_equipment_items=[
            "Longsword",
            "Shield",
            "Chain mail",
            "Holy symbol",
            "Priest's pack",
        ],
        spell_options=[
            {
                "level": 0,
                "label": "Cantrips",
                "choose_count": 0,
                "spells": [],
            },
            {
                "level": 1,
                "label": "Level 1 Spells",
                "choose_count": 2,
                "spells": [
                    {
                        "name": "Bless",
                        "description": "Up to three creatures gain 1d4 to attack rolls and saving throws for 1 minute.",
                    },
                    {
                        "name": "Cure Wounds",
                        "description": "A touch heals 1d8+WIS modifier HP.",
                    },
                    {
                        "name": "Divine Favor",
                        "description": "Your weapon glows; add 1d4 radiant damage to attacks for 1 minute.",
                    },
                    {
                        "name": "Heroism",
                        "description": "A willing creature is immune to fear and gains 5 temp HP per turn for 1 minute.",
                    },
                    {
                        "name": "Protection from Evil and Good",
                        "description": "Ward against aberrations, fiends, and undead for 10 minutes.",
                    },
                    {
                        "name": "Searing Smite",
                        "description": "Your next hit deals an extra 1d6 fire and ignites the target.",
                    },
                    {
                        "name": "Thunderous Smite",
                        "description": "Your next hit deals an extra 2d6 thunder and may push the target back.",
                    },
                ],
            },
        ],
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
        skill_options=[
            {"name": "Athletics", "ability": "Strength"},
            {"name": "Acrobatics", "ability": "Dexterity"},
            {"name": "Intimidation", "ability": "Charisma"},
            {"name": "Perception", "ability": "Wisdom"},
            {"name": "Stealth", "ability": "Dexterity"},
            {"name": "Survival", "ability": "Wisdom"},
        ],
        skill_choose_count=2,
        starting_equipment_items=[
            "Katana",
            "Heavy pistol",
            "Ballistic armor",
            "Medkit",
            "Credchip 500eb",
        ],
        spell_options=None,
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
        skill_options=[
            {"name": "Electronics", "ability": "Intelligence"},
            {"name": "Hacking", "ability": "Intelligence"},
            {"name": "Stealth", "ability": "Dexterity"},
            {"name": "Deception", "ability": "Charisma"},
            {"name": "Perception", "ability": "Wisdom"},
            {"name": "Investigation", "ability": "Intelligence"},
        ],
        skill_choose_count=3,
        starting_equipment_items=[
            "Neural Interface",
            "Hacking Deck",
            "Monofilament wire",
            "Stim patches x3",
            "Light armor",
        ],
        spell_options=[
            {
                "level": 0,
                "label": "Cantrips",
                "choose_count": 2,
                "spells": [
                    {
                        "name": "Data Pulse",
                        "description": "Fire a pulse of raw data at a target, dealing 1d10 force damage.",
                    },
                    {
                        "name": "Phantom Signal",
                        "description": "Create a false wireless signal readable within 30ft for 1 minute.",
                    },
                    {
                        "name": "System Scan",
                        "description": "Identify electronic devices and their security rating within 30ft.",
                    },
                    {
                        "name": "Ghost Protocol",
                        "description": "Mask your digital signature from passive scans for 1 minute.",
                    },
                ],
            },
            {
                "level": 1,
                "label": "Level 1 Programs",
                "choose_count": 2,
                "spells": [
                    {
                        "name": "Neural Override",
                        "description": "Temporarily seize control of a nearby electronic device or cyberlimb.",
                    },
                    {
                        "name": "Deep Trace",
                        "description": "Track the digital footprint of a target for 1 hour.",
                    },
                    {
                        "name": "Ice Spike",
                        "description": "Launch a weaponized security program dealing 3d6 force damage.",
                    },
                    {
                        "name": "Firewall",
                        "description": "Raise a digital barrier granting +2 AC against electronic attacks for 1 hour.",
                    },
                    {
                        "name": "Ghost in the Machine",
                        "description": "Become invisible to all electronic surveillance for 10 minutes.",
                    },
                    {
                        "name": "System Crash",
                        "description": "Force a device or cyborg to malfunction for 1 round.",
                    },
                ],
            },
        ],
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
        skill_options=[
            {"name": "Stealth", "ability": "Dexterity"},
            {"name": "Deception", "ability": "Charisma"},
            {"name": "Athletics", "ability": "Strength"},
            {"name": "Acrobatics", "ability": "Dexterity"},
            {"name": "Sleight of Hand", "ability": "Dexterity"},
            {"name": "Investigation", "ability": "Intelligence"},
        ],
        skill_choose_count=3,
        starting_equipment_items=[
            "Monofilament blade",
            "Silenced holdout pistol",
            "Stealth suit",
            "Fake ID",
            "Credchip 300eb",
        ],
        spell_options=None,
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
        skill_options=[
            {"name": "Medicine", "ability": "Wisdom"},
            {"name": "Science", "ability": "Intelligence"},
            {"name": "Persuasion", "ability": "Charisma"},
            {"name": "Insight", "ability": "Wisdom"},
            {"name": "Perception", "ability": "Wisdom"},
            {"name": "Electronics", "ability": "Intelligence"},
        ],
        skill_choose_count=3,
        starting_equipment_items=[
            "Trauma kit",
            "Stim patches x5",
            "Surgical tools",
            "Med scanner",
            "Street clothes",
        ],
        spell_options=[
            {
                "level": 0,
                "label": "Cantrips",
                "choose_count": 0,
                "spells": [],
            },
            {
                "level": 1,
                "label": "Level 1 Techniques",
                "choose_count": 2,
                "spells": [
                    {
                        "name": "Emergency Stabilize",
                        "description": "Stabilize a dying creature instantly with a nanite shot.",
                    },
                    {
                        "name": "Neural Calm",
                        "description": "Calm a creature's nervous system, imposing disadvantage on attacks for 1 minute.",
                    },
                    {
                        "name": "Bio Scan",
                        "description": "Diagnose all injuries and conditions on a creature within 5ft.",
                    },
                    {
                        "name": "Stim Boost",
                        "description": "Inject a stimulant granting 1d8+WIS temporary HP for 1 hour.",
                    },
                    {
                        "name": "Trauma Pack",
                        "description": "Apply emergency trauma care, healing 1d8+WIS HP.",
                    },
                    {
                        "name": "Detox",
                        "description": "Purge toxins or narcotics from a creature's bloodstream.",
                    },
                ],
            },
        ],
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
        skill_options=[
            {"name": "Athletics", "ability": "Strength"},
            {"name": "Survival", "ability": "Wisdom"},
            {"name": "Perception", "ability": "Wisdom"},
            {"name": "Stealth", "ability": "Dexterity"},
            {"name": "Investigation", "ability": "Intelligence"},
            {"name": "Nature", "ability": "Intelligence"},
        ],
        skill_choose_count=3,
        starting_equipment_items=[
            "Hunting rifle",
            "20 rounds",
            "Patchwork armor",
            "Scrap toolkit",
            "3 days rations",
        ],
        spell_options=None,
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
        skill_options=[
            {"name": "Arcana", "ability": "Intelligence"},
            {"name": "Science", "ability": "Intelligence"},
            {"name": "Investigation", "ability": "Intelligence"},
            {"name": "Electronics", "ability": "Intelligence"},
            {"name": "Perception", "ability": "Wisdom"},
            {"name": "History", "ability": "Intelligence"},
        ],
        skill_choose_count=2,
        starting_equipment_items=[
            "Salvaged energy staff",
            "Jury-rigged amplifier",
            "Scavenged armor",
            "Field notebook",
            "2 days rations",
        ],
        spell_options=[
            {
                "level": 0,
                "label": "Cantrips",
                "choose_count": 2,
                "spells": [
                    {
                        "name": "Salvage Spark",
                        "description": "Arc electricity between metal objects, dealing 1d10 lightning damage.",
                    },
                    {
                        "name": "Waste Flame",
                        "description": "Project burning chemical waste, dealing 1d10 fire damage.",
                    },
                    {
                        "name": "Scrap Shield",
                        "description": "Telekinetically assemble debris into a shield granting +2 AC until next turn.",
                    },
                    {
                        "name": "Rad Pulse",
                        "description": "Emit a burst of radiation dealing 1d8 necrotic to all within 5ft.",
                    },
                ],
            },
            {
                "level": 1,
                "label": "Level 1 Rites",
                "choose_count": 2,
                "spells": [
                    {
                        "name": "Junk Golem",
                        "description": "Animate a pile of scrap metal to fight for you for 1 minute.",
                    },
                    {
                        "name": "Static Field",
                        "description": "Create crackling static slowing movement and dealing 1d6 lightning each turn.",
                    },
                    {
                        "name": "Corrode Armor",
                        "description": "Spray acid reducing a target's AC by 2 for 1 minute.",
                    },
                    {
                        "name": "Scrap Storm",
                        "description": "Hurl a storm of debris dealing 3d6 piercing in a 10ft cone.",
                    },
                    {
                        "name": "Improvised Ward",
                        "description": "Assemble a barrier from rubble granting 10 temporary HP.",
                    },
                    {
                        "name": "Signal Boost",
                        "description": "Amplify mental energy to send a telepathic message up to 1 mile.",
                    },
                ],
            },
        ],
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
        skill_options=[
            {"name": "Investigation", "ability": "Intelligence"},
            {"name": "Perception", "ability": "Wisdom"},
            {"name": "Stealth", "ability": "Dexterity"},
            {"name": "Survival", "ability": "Wisdom"},
            {"name": "Athletics", "ability": "Strength"},
            {"name": "Sleight of Hand", "ability": "Dexterity"},
        ],
        skill_choose_count=3,
        starting_equipment_items=[
            "Hunting knife",
            "Crossbow",
            "20 bolts",
            "Patchwork armor",
            "Scavenger's satchel",
        ],
        spell_options=None,
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
        skill_options=[
            {"name": "Medicine", "ability": "Wisdom"},
            {"name": "Science", "ability": "Intelligence"},
            {"name": "Persuasion", "ability": "Charisma"},
            {"name": "Insight", "ability": "Wisdom"},
            {"name": "Perception", "ability": "Wisdom"},
            {"name": "Athletics", "ability": "Strength"},
        ],
        skill_choose_count=3,
        starting_equipment_items=[
            "Medkit",
            "Surgical tools",
            "10 bandages",
            "Water purification tablets",
            "Scavenged armor",
        ],
        spell_options=[
            {
                "level": 0,
                "label": "Cantrips",
                "choose_count": 0,
                "spells": [],
            },
            {
                "level": 1,
                "label": "Level 1 Techniques",
                "choose_count": 2,
                "spells": [
                    {
                        "name": "Wasteland Salve",
                        "description": "Apply improvised medicine from foraged ingredients, healing 1d8+WIS HP.",
                    },
                    {
                        "name": "Rad Purge",
                        "description": "Remove radiation poisoning from a creature, ending the condition.",
                    },
                    {
                        "name": "Stim Shot",
                        "description": "Inject a combat stimulant granting advantage on STR and DEX checks for 1 minute.",
                    },
                    {
                        "name": "Combat Triage",
                        "description": "Quickly stabilize a critical creature, healing 2d4+WIS HP.",
                    },
                    {
                        "name": "Blood Stop",
                        "description": "Seal a wound, preventing continued damage from bleeding injuries.",
                    },
                    {
                        "name": "Shared Pain",
                        "description": "Transfer up to half your HP as healing to a willing creature within 5ft.",
                    },
                ],
            },
        ],
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

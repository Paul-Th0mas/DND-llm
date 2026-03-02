"""
Cyberpunk seed data.

Inserts one Theme row plus the minimum required presets:
  8 enemies, 10 items, 5 NPCs, 3 quests (1 main + 2 side).
"""

import uuid

from sqlalchemy.orm import Session

from app.worlds.infrastructure.orm_models import (
    EnemyPresetORM,
    ItemPresetORM,
    NPCPresetORM,
    QuestTemplateORM,
    ThemeORM,
)

THEME_NAME = "cyberpunk"

ENEMIES = [
    {
        "name": "Street Punk",
        "hp": 14,
        "die_type": "D8",
        "pool_size": 3,
        "ai_behavior": "AGGRESSIVE",
        "lore_tags": ["human", "gang", "melee"],
    },
    {
        "name": "Corp Guard",
        "hp": 22,
        "die_type": "D10",
        "pool_size": 4,
        "ai_behavior": "DEFENSIVE",
        "lore_tags": ["corporate", "armored", "ranged"],
    },
    {
        "name": "Recon Drone",
        "hp": 10,
        "die_type": "D8",
        "pool_size": 3,
        "ai_behavior": "STRATEGIC",
        "lore_tags": ["machine", "drone", "surveillance"],
    },
    {
        "name": "Rogue Hacker",
        "hp": 12,
        "die_type": "D8",
        "pool_size": 4,
        "ai_behavior": "SUPPORT",
        "lore_tags": ["human", "tech", "debuff"],
    },
    {
        "name": "Enforcer",
        "hp": 28,
        "die_type": "D10",
        "pool_size": 5,
        "ai_behavior": "AGGRESSIVE",
        "lore_tags": ["corporate", "heavy", "melee"],
    },
    {
        "name": "Combat Synth",
        "hp": 30,
        "die_type": "D12",
        "pool_size": 5,
        "ai_behavior": "STRATEGIC",
        "lore_tags": ["android", "synthetic", "adaptive"],
    },
    {
        "name": "Fixer",
        "hp": 18,
        "die_type": "D8",
        "pool_size": 4,
        "ai_behavior": "STRATEGIC",
        "lore_tags": ["human", "mercenary", "ambush"],
    },
    {
        "name": "Mega-Corp Executive",
        "hp": 70,
        "die_type": "D20",
        "pool_size": 6,
        "ai_behavior": "STRATEGIC",
        "lore_tags": ["boss", "corporate", "augmented", "powerful"],
    },
]

ITEMS = [
    {
        "name": "Neural Spike",
        "item_type": "WEAPON",
        "rarity": "common",
        "gold_cost": 60,
        "chips_bonus": 5,
        "mult_bonus": 0,
        "description": "A close-range neural disruptor that scrambles enemy focus.",
    },
    {
        "name": "Ballistic Vest",
        "item_type": "ARMOR",
        "rarity": "common",
        "gold_cost": 45,
        "chips_bonus": 0,
        "mult_bonus": 0,
        "description": "Standard corporate-issue armour plating.",
    },
    {
        "name": "Stim Pack",
        "item_type": "ACCESSORY",
        "rarity": "common",
        "gold_cost": 30,
        "chips_bonus": 0,
        "mult_bonus": 0,
        "description": "Combat stimulants that restore integrity in the field.",
    },
    {
        "name": "Scramble Grenade",
        "item_type": "ACCESSORY",
        "rarity": "common",
        "gold_cost": 35,
        "chips_bonus": 3,
        "mult_bonus": 0,
        "description": "Disrupts drone guidance systems on detonation.",
    },
    {
        "name": "Firewall Chip",
        "item_type": "ACCESSORY",
        "rarity": "uncommon",
        "gold_cost": 110,
        "chips_bonus": 5,
        "mult_bonus": 1,
        "description": "Bionic implant that blocks enemy hacking attempts.",
    },
    {
        "name": "Plasma Cutter",
        "item_type": "WEAPON",
        "rarity": "uncommon",
        "gold_cost": 130,
        "chips_bonus": 12,
        "mult_bonus": 0,
        "description": "Superheated plasma blade that cuts through armour.",
    },
    {
        "name": "Ghost Protocol",
        "item_type": "RELIC",
        "rarity": "rare",
        "gold_cost": 220,
        "chips_bonus": 8,
        "mult_bonus": 2,
        "description": "Illegal stealth module; grants brief optical camouflage.",
    },
    {
        "name": "Reflex Booster",
        "item_type": "ARMOR",
        "rarity": "uncommon",
        "gold_cost": 95,
        "chips_bonus": 0,
        "mult_bonus": 1,
        "description": "Subcutaneous implant that accelerates reaction time.",
    },
    {
        "name": "Overclock Module",
        "item_type": "RELIC",
        "rarity": "rare",
        "gold_cost": 260,
        "chips_bonus": 0,
        "mult_bonus": 3,
        "description": "Overclocks neural processors — devastating but risky.",
    },
    {
        "name": "Apex Core",
        "item_type": "RELIC",
        "rarity": "legendary",
        "gold_cost": 550,
        "chips_bonus": 20,
        "mult_bonus": 5,
        "description": "Black-market AI core of unknown origin; immense destructive potential.",
    },
]

NPCS = [
    {
        "name": "Scratch",
        "role": "MERCHANT",
        "personality_traits": ["paranoid", "chatty", "tech-obsessed"],
        "speech_style": "rapid-fire slang; calls customers 'choom'",
        "faction": "Free Traders Network",
    },
    {
        "name": "Director Vex",
        "role": "QUEST_GIVER",
        "personality_traits": ["cold", "calculating", "ruthless"],
        "speech_style": "corporate jargon; never shows emotion",
        "faction": "Apex-Corp Internal Affairs",
    },
    {
        "name": "Ghost",
        "role": "ALLY",
        "personality_traits": ["loyal", "quiet", "haunted by past"],
        "speech_style": "minimal; lets actions speak; occasional dark humour",
        "faction": None,
    },
    {
        "name": "Nyx",
        "role": "QUEST_GIVER",
        "personality_traits": ["idealistic", "passionate", "reckless"],
        "speech_style": "rallying speeches; heavy street slang",
        "faction": "Neon Liberation Front",
    },
    {
        "name": "The Broker",
        "role": "ANTAGONIST",
        "personality_traits": ["manipulative", "charming", "never directly threatens"],
        "speech_style": "offers wrapped in compliments; always implies power",
        "faction": "Shadow Syndicate",
    },
]

QUESTS = [
    {
        "name": "System Override",
        "quest_type": "MAIN",
        "stages": [
            {
                "stage_number": 1,
                "title": "Signal Breach",
                "description": "A rogue signal in the undercity hints at a massive Apex-Corp data heist in progress.",
                "trigger_room": 1,
                "completion_condition": "clear initial corp guards",
            },
            {
                "stage_number": 2,
                "title": "The Upload",
                "description": "The party discovers the Executive is personally overseeing the theft of citizen biometrics.",
                "trigger_room": 4,
                "completion_condition": "retrieve the data chip",
            },
            {
                "stage_number": 3,
                "title": "Executive Termination",
                "description": "The Mega-Corp Executive must be stopped before the upload completes.",
                "trigger_room": 8,
                "completion_condition": "defeat the Mega-Corp Executive",
            },
        ],
        "reward_gold": 600,
        "reward_item_ids": [],
    },
    {
        "name": "Black Market Burn",
        "quest_type": "SIDE",
        "stages": [
            {
                "stage_number": 1,
                "title": "Track the Fixer",
                "description": "A stolen weapons cache needs recovering before it hits the street.",
                "trigger_room": 2,
                "completion_condition": "defeat the Fixer",
            },
        ],
        "reward_gold": 200,
        "reward_item_ids": [],
    },
    {
        "name": "Rogue Signal",
        "quest_type": "SIDE",
        "stages": [
            {
                "stage_number": 1,
                "title": "Silence the Drone",
                "description": "Recon drones are broadcasting civilian locations to a unknown party.",
                "trigger_room": 3,
                "completion_condition": "destroy the Recon Drone",
            },
        ],
        "reward_gold": 150,
        "reward_item_ids": [],
    },
]


def seed(session: Session) -> None:
    """Insert cyberpunk theme + all presets.  Idempotent via merge."""
    theme = ThemeORM(
        id=uuid.uuid4(),
        name=THEME_NAME,
        tone_descriptor="neon dystopian",
        language_style="slang-heavy street",
        currency_name="Credits",
        health_term="Integrity",
        death_term="flatlined",
        banned_words=["medieval", "goblin", "dragon", "sword", "peasant", "manhwa"],
    )
    session.merge(theme)

    for e in ENEMIES:
        session.merge(
            EnemyPresetORM(
                id=uuid.uuid4(),
                theme_name=THEME_NAME,
                name=e["name"],
                hp=e["hp"],
                die_type=e["die_type"],
                pool_size=e["pool_size"],
                ai_behavior=e["ai_behavior"],
                lore_tags=e["lore_tags"],
            )
        )

    for i in ITEMS:
        session.merge(
            ItemPresetORM(
                id=uuid.uuid4(),
                theme_name=THEME_NAME,
                name=i["name"],
                item_type=i["item_type"],
                rarity=i["rarity"],
                gold_cost=i["gold_cost"],
                chips_bonus=i["chips_bonus"],
                mult_bonus=i["mult_bonus"],
                description=i["description"],
            )
        )

    for n in NPCS:
        session.merge(
            NPCPresetORM(
                id=uuid.uuid4(),
                theme_name=THEME_NAME,
                name=n["name"],
                role=n["role"],
                personality_traits=n["personality_traits"],
                speech_style=n["speech_style"],
                faction=n["faction"],
            )
        )

    for q in QUESTS:
        session.merge(
            QuestTemplateORM(
                id=uuid.uuid4(),
                theme_name=THEME_NAME,
                name=q["name"],
                quest_type=q["quest_type"],
                stages=q["stages"],
                reward_gold=q["reward_gold"],
                reward_item_ids=q["reward_item_ids"],
            )
        )

    session.commit()
    print(
        f"Seeded cyberpunk: {len(ENEMIES)} enemies, {len(ITEMS)} items, "
        f"{len(NPCS)} NPCs, {len(QUESTS)} quests"
    )

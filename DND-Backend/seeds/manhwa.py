"""
Manhwa seed data.

Inserts one Theme row plus the minimum required presets:
  8 enemies, 10 items, 5 NPCs, 3 quests (1 main + 2 side).

Manhwa fantasy archetype: Korean web-novel aesthetics — rank gates, spirit
energy (Chi), monstrous Gates opening in the modern world, hunters ascending
through ranks.
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

THEME_NAME = "manhwa"

ENEMIES = [
    {
        "name": "Gate Imp",
        "hp": 12,
        "die_type": "D8",
        "pool_size": 3,
        "ai_behavior": "AGGRESSIVE",
        "lore_tags": ["demon", "gate", "low-rank"],
    },
    {
        "name": "Stone Golem",
        "hp": 35,
        "die_type": "D10",
        "pool_size": 4,
        "ai_behavior": "AGGRESSIVE",
        "lore_tags": ["construct", "heavy", "slow"],
    },
    {
        "name": "Shadow Stalker",
        "hp": 16,
        "die_type": "D8",
        "pool_size": 4,
        "ai_behavior": "STRATEGIC",
        "lore_tags": ["shadow", "assassin", "ambush"],
    },
    {
        "name": "Cursed Knight",
        "hp": 28,
        "die_type": "D10",
        "pool_size": 5,
        "ai_behavior": "AGGRESSIVE",
        "lore_tags": ["cursed", "undead", "armored"],
    },
    {
        "name": "Spirit Archer",
        "hp": 18,
        "die_type": "D8",
        "pool_size": 4,
        "ai_behavior": "DEFENSIVE",
        "lore_tags": ["spirit", "ranged", "ethereal"],
    },
    {
        "name": "Rank B Hunter (Rogue)",
        "hp": 24,
        "die_type": "D10",
        "pool_size": 4,
        "ai_behavior": "STRATEGIC",
        "lore_tags": ["human", "hunter", "betrayer"],
    },
    {
        "name": "Demon General",
        "hp": 40,
        "die_type": "D12",
        "pool_size": 5,
        "ai_behavior": "STRATEGIC",
        "lore_tags": ["demon", "general", "commander"],
    },
    {
        "name": "Gate Monarch",
        "hp": 80,
        "die_type": "D20",
        "pool_size": 6,
        "ai_behavior": "STRATEGIC",
        "lore_tags": ["boss", "monarch", "gate", "ancient", "S-rank"],
    },
]

ITEMS = [
    {
        "name": "Hunter's Blade",
        "item_type": "WEAPON",
        "rarity": "common",
        "gold_cost": 55,
        "chips_bonus": 5,
        "mult_bonus": 0,
        "description": "Standard-issue blade issued to F-rank hunters.",
    },
    {
        "name": "Spirit Weave Robe",
        "item_type": "ARMOR",
        "rarity": "common",
        "gold_cost": 45,
        "chips_bonus": 0,
        "mult_bonus": 0,
        "description": "Cloth armour infused with low-grade spirit energy.",
    },
    {
        "name": "Chi Stone",
        "item_type": "ACCESSORY",
        "rarity": "common",
        "gold_cost": 30,
        "chips_bonus": 3,
        "mult_bonus": 0,
        "description": "A mana stone that releases a pulse of Chi on impact.",
    },
    {
        "name": "Recovery Pill",
        "item_type": "ACCESSORY",
        "rarity": "common",
        "gold_cost": 25,
        "chips_bonus": 0,
        "mult_bonus": 0,
        "description": "Herbal compound that rapidly restores Chi.",
    },
    {
        "name": "Gate Fragment",
        "item_type": "RELIC",
        "rarity": "uncommon",
        "gold_cost": 115,
        "chips_bonus": 5,
        "mult_bonus": 1,
        "description": "A shard of a collapsed Gate — radiates unstable mana.",
    },
    {
        "name": "Shadow Cloth Armour",
        "item_type": "ARMOR",
        "rarity": "uncommon",
        "gold_cost": 105,
        "chips_bonus": 0,
        "mult_bonus": 1,
        "description": "Armour woven from shadow essence — near-invisible at night.",
    },
    {
        "name": "Spirit Bow",
        "item_type": "WEAPON",
        "rarity": "rare",
        "gold_cost": 210,
        "chips_bonus": 10,
        "mult_bonus": 2,
        "description": "A weapon that fires arrows of condensed spirit energy.",
    },
    {
        "name": "Rank Seal",
        "item_type": "ACCESSORY",
        "rarity": "uncommon",
        "gold_cost": 90,
        "chips_bonus": 5,
        "mult_bonus": 0,
        "description": "The seal of a rank advancement authority; grants status bonuses.",
    },
    {
        "name": "Monarch's Crest",
        "item_type": "RELIC",
        "rarity": "rare",
        "gold_cost": 270,
        "chips_bonus": 0,
        "mult_bonus": 3,
        "description": "A relic left by a fallen Gate Monarch; radiates immense pressure.",
    },
    {
        "name": "System Core",
        "item_type": "RELIC",
        "rarity": "legendary",
        "gold_cost": 600,
        "chips_bonus": 25,
        "mult_bonus": 5,
        "description": "The crystallised will of the System itself — legendary, terrifying.",
    },
]

NPCS = [
    {
        "name": "Association Clerk Jin",
        "role": "MERCHANT",
        "personality_traits": ["meek", "rule-bound", "secretly envious of hunters"],
        "speech_style": "formal bureaucratic; apologises frequently",
        "faction": "Hunter Association",
    },
    {
        "name": "Master Kang",
        "role": "QUEST_GIVER",
        "personality_traits": ["stern", "honourable", "tests before trusting"],
        "speech_style": "sparse, weighted words; expects silence in return",
        "faction": "Kang Guild",
    },
    {
        "name": "Min-Ji",
        "role": "ALLY",
        "personality_traits": ["energetic", "loyal", "comic relief"],
        "speech_style": "enthusiastic; overuses exclamation; cheers party on",
        "faction": None,
    },
    {
        "name": "Shadow Lord's Herald",
        "role": "ANTAGONIST",
        "personality_traits": ["arrogant", "fanatical", "views mortals as insects"],
        "speech_style": "grand proclamations; refers to the Monarch as divine",
        "faction": "Gate Monarch's Host",
    },
    {
        "name": "Elder Soo-Yeon",
        "role": "QUEST_GIVER",
        "personality_traits": ["mystical", "ancient", "speaks in historical allegory"],
        "speech_style": "slow and deliberate; references events centuries past",
        "faction": "Awakened Elders Council",
    },
]

QUESTS = [
    {
        "name": "Ascension Protocol",
        "quest_type": "MAIN",
        "stages": [
            {
                "stage_number": 1,
                "title": "The Gate Opens",
                "description": "A high-rank Gate appears; the party must clear it before it overflows into the city.",
                "trigger_room": 1,
                "completion_condition": "defeat the Gate Imp wave",
            },
            {
                "stage_number": 2,
                "title": "The General's Command",
                "description": "A Demon General is coordinating the monsters — destroying it will weaken the Monarch.",
                "trigger_room": 4,
                "completion_condition": "defeat the Demon General",
            },
            {
                "stage_number": 3,
                "title": "Monarch's Throne",
                "description": "The Gate Monarch itself descends — only a top-rank hunter can survive this fight.",
                "trigger_room": 8,
                "completion_condition": "defeat the Gate Monarch",
            },
        ],
        "reward_gold": 700,
        "reward_item_ids": [],
    },
    {
        "name": "Rogue Hunter Bounty",
        "quest_type": "SIDE",
        "stages": [
            {
                "stage_number": 1,
                "title": "Traitor in the Ranks",
                "description": "A rank B hunter has defected to the Gate Monarch; bring them in.",
                "trigger_room": 2,
                "completion_condition": "defeat the Rank B Hunter",
            },
        ],
        "reward_gold": 200,
        "reward_item_ids": [],
    },
    {
        "name": "Spirit Vein Crisis",
        "quest_type": "SIDE",
        "stages": [
            {
                "stage_number": 1,
                "title": "Disrupted Flow",
                "description": "Spirit archers are disrupting a mana vein; stop them before the area destabilises.",
                "trigger_room": 3,
                "completion_condition": "defeat the Spirit Archer",
            },
        ],
        "reward_gold": 120,
        "reward_item_ids": [],
    },
]


def seed(session: Session) -> None:
    """Insert manhwa theme + all presets.  Idempotent via merge."""
    theme = ThemeORM(
        id=uuid.uuid4(),
        name=THEME_NAME,
        tone_descriptor="high-octane Korean web-novel fantasy",
        language_style="modern Korean drama with power-rank terminology",
        currency_name="Spirit Coins",
        health_term="Chi",
        death_term="dispersed",
        banned_words=["goblin", "dragon", "gold coin", "credits", "neon", "medieval"],
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
        f"Seeded manhwa: {len(ENEMIES)} enemies, {len(ITEMS)} items, "
        f"{len(NPCS)} NPCs, {len(QUESTS)} quests"
    )

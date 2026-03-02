"""
Medieval Fantasy seed data.

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

THEME_NAME = "medieval_fantasy"

ENEMIES = [
    {
        "name": "Goblin Scout",
        "hp": 12,
        "die_type": "D8",
        "pool_size": 3,
        "ai_behavior": "AGGRESSIVE",
        "lore_tags": ["goblin", "scout", "ambush"],
    },
    {
        "name": "Goblin Archer",
        "hp": 10,
        "die_type": "D8",
        "pool_size": 3,
        "ai_behavior": "DEFENSIVE",
        "lore_tags": ["goblin", "ranged"],
    },
    {
        "name": "Orc Warrior",
        "hp": 25,
        "die_type": "D10",
        "pool_size": 4,
        "ai_behavior": "AGGRESSIVE",
        "lore_tags": ["orc", "melee", "berserker"],
    },
    {
        "name": "Skeleton",
        "hp": 15,
        "die_type": "D8",
        "pool_size": 3,
        "ai_behavior": "AGGRESSIVE",
        "lore_tags": ["undead", "skeleton"],
    },
    {
        "name": "Zombie",
        "hp": 20,
        "die_type": "D8",
        "pool_size": 3,
        "ai_behavior": "AGGRESSIVE",
        "lore_tags": ["undead", "zombie", "slow"],
    },
    {
        "name": "Dire Wolf",
        "hp": 18,
        "die_type": "D10",
        "pool_size": 4,
        "ai_behavior": "STRATEGIC",
        "lore_tags": ["beast", "wolf", "pack"],
    },
    {
        "name": "Bandit",
        "hp": 16,
        "die_type": "D8",
        "pool_size": 4,
        "ai_behavior": "STRATEGIC",
        "lore_tags": ["human", "bandit", "thief"],
    },
    {
        "name": "Dragon",
        "hp": 60,
        "die_type": "D20",
        "pool_size": 6,
        "ai_behavior": "STRATEGIC",
        "lore_tags": ["dragon", "boss", "fire", "ancient"],
    },
]

ITEMS = [
    {
        "name": "Iron Sword",
        "item_type": "WEAPON",
        "rarity": "common",
        "gold_cost": 50,
        "chips_bonus": 5,
        "mult_bonus": 0,
        "description": "A dependable iron blade, worn but reliable.",
    },
    {
        "name": "Leather Armor",
        "item_type": "ARMOR",
        "rarity": "common",
        "gold_cost": 40,
        "chips_bonus": 0,
        "mult_bonus": 0,
        "description": "Supple leather that turns aside glancing blows.",
    },
    {
        "name": "Lucky Charm",
        "item_type": "ACCESSORY",
        "rarity": "common",
        "gold_cost": 30,
        "chips_bonus": 2,
        "mult_bonus": 1,
        "description": "A rabbit's foot said to attract fortune.",
    },
    {
        "name": "Healing Potion",
        "item_type": "ACCESSORY",
        "rarity": "common",
        "gold_cost": 25,
        "chips_bonus": 0,
        "mult_bonus": 0,
        "description": "Restores a modest amount of hit points when consumed.",
    },
    {
        "name": "Fire Staff",
        "item_type": "WEAPON",
        "rarity": "uncommon",
        "gold_cost": 120,
        "chips_bonus": 10,
        "mult_bonus": 1,
        "description": "A gnarled staff that crackles with arcane flame.",
    },
    {
        "name": "Chain Mail",
        "item_type": "ARMOR",
        "rarity": "uncommon",
        "gold_cost": 100,
        "chips_bonus": 0,
        "mult_bonus": 0,
        "description": "Interlocked rings of steel that distribute impact evenly.",
    },
    {
        "name": "Shadow Dagger",
        "item_type": "WEAPON",
        "rarity": "rare",
        "gold_cost": 200,
        "chips_bonus": 8,
        "mult_bonus": 2,
        "description": "Forged in darkness; strikes twice when unseen.",
    },
    {
        "name": "Holy Symbol",
        "item_type": "ACCESSORY",
        "rarity": "uncommon",
        "gold_cost": 80,
        "chips_bonus": 5,
        "mult_bonus": 1,
        "description": "A blessed medallion that wards off undead.",
    },
    {
        "name": "Ring of Luck",
        "item_type": "RELIC",
        "rarity": "rare",
        "gold_cost": 250,
        "chips_bonus": 0,
        "mult_bonus": 3,
        "description": "A golden ring that tips fate in the wearer's favour.",
    },
    {
        "name": "Elder Relic",
        "item_type": "RELIC",
        "rarity": "legendary",
        "gold_cost": 500,
        "chips_bonus": 20,
        "mult_bonus": 5,
        "description": "An artefact of immense age whose power defies explanation.",
    },
]

NPCS = [
    {
        "name": "Aldric the Blacksmith",
        "role": "MERCHANT",
        "personality_traits": ["gruff", "honest", "proud of craft"],
        "speech_style": "short declarative sentences; calls everyone 'friend'",
        "faction": "Ironworkers Guild",
    },
    {
        "name": "Elder Seraphine",
        "role": "QUEST_GIVER",
        "personality_traits": ["wise", "cryptic", "weary"],
        "speech_style": "speaks in riddles and ancient proverbs",
        "faction": "Council of Elders",
    },
    {
        "name": "The Stranger in Grey",
        "role": "QUEST_GIVER",
        "personality_traits": ["mysterious", "watchful", "terse"],
        "speech_style": "minimal words; pauses for dramatic effect",
        "faction": None,
    },
    {
        "name": "Mira the Innkeeper",
        "role": "ALLY",
        "personality_traits": ["warm", "gossipy", "protective of patrons"],
        "speech_style": "chatty; shares local rumours freely",
        "faction": "Innkeepers Fellowship",
    },
    {
        "name": "Captain Drevon",
        "role": "ANTAGONIST",
        "personality_traits": ["corrupt", "intimidating", "greedy"],
        "speech_style": "barks orders; uses threats thinly veiled as offers",
        "faction": "City Watch (corrupt)",
    },
]

QUESTS = [
    {
        "name": "The Dark Throne",
        "quest_type": "MAIN",
        "stages": [
            {
                "stage_number": 1,
                "title": "Shadows Stir",
                "description": "Rumours of a dark power resurging in the old fortress reach the party.",
                "trigger_room": 1,
                "completion_condition": "clear rooms 1-3",
            },
            {
                "stage_number": 2,
                "title": "The General's Trail",
                "description": "Evidence points to a warlord commanding the fortress monsters.",
                "trigger_room": 4,
                "completion_condition": "find the warlord's seal",
            },
            {
                "stage_number": 3,
                "title": "The Throne Room",
                "description": "The Dragon waits upon a throne of bones — the true master of the dark army.",
                "trigger_room": 8,
                "completion_condition": "defeat the Dragon boss",
            },
        ],
        "reward_gold": 500,
        "reward_item_ids": [],  # populated after items are inserted
    },
    {
        "name": "Lost Caravan",
        "quest_type": "SIDE",
        "stages": [
            {
                "stage_number": 1,
                "title": "Missing Merchants",
                "description": "A merchant guild paid the party to recover stolen goods from bandit caves.",
                "trigger_room": 2,
                "completion_condition": "defeat the Bandit",
            },
        ],
        "reward_gold": 150,
        "reward_item_ids": [],
    },
    {
        "name": "Missing Villagers",
        "quest_type": "SIDE",
        "stages": [
            {
                "stage_number": 1,
                "title": "Into the Dark",
                "description": "Villagers have vanished near the dungeon entrance; the party investigates.",
                "trigger_room": 3,
                "completion_condition": "find the zombie horde",
            },
        ],
        "reward_gold": 100,
        "reward_item_ids": [],
    },
]


def seed(session: Session) -> None:
    """Insert medieval_fantasy theme + all presets.  Idempotent via merge."""
    theme_id = uuid.uuid4()

    theme = ThemeORM(
        id=theme_id,
        name=THEME_NAME,
        tone_descriptor="gritty dark fantasy",
        language_style="archaic formal",
        currency_name="Gold",
        health_term="Hit Points",
        death_term="slain",
        banned_words=["cyberpunk", "neon", "hacker", "drone", "manhwa"],
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
        f"Seeded medieval_fantasy: {len(ENEMIES)} enemies, {len(ITEMS)} items, "
        f"{len(NPCS)} NPCs, {len(QUESTS)} quests"
    )

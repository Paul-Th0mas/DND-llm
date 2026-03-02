"""
Domain-layer tests for WorldCompiler.

All tests use real domain objects — no mocking, no DB.
"""

import pytest

from app.combat.domain.models import DieType
from app.worlds.domain.models import (
    AIBehavior,
    EnemyPreset,
    ItemPreset,
    ItemType,
    NPCPreset,
    NPCRole,
    QuestStage,
    QuestTemplate,
    QuestType,
    RoomType,
    Theme,
    ThemeName,
    WorldSettings,
)
from app.worlds.domain.repositories import WorldCompilationError
from app.worlds.domain.services import WorldCompiler


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_enemy(name: str, is_boss: bool = False) -> EnemyPreset:
    return EnemyPreset(
        id=f"enemy-{name.lower().replace(' ', '-')}",
        theme=ThemeName.MEDIEVAL_FANTASY,
        name=name,
        hp=20 if not is_boss else 60,
        die_type=DieType.D10 if not is_boss else DieType.D20,
        pool_size=4 if not is_boss else 6,
        ai_behavior=AIBehavior.AGGRESSIVE,
        lore_tags=["test"],
    )


def _make_item(name: str, rarity: str) -> ItemPreset:
    return ItemPreset(
        id=f"item-{name.lower().replace(' ', '-')}",
        theme=ThemeName.MEDIEVAL_FANTASY,
        name=name,
        item_type=ItemType.WEAPON,
        rarity=rarity,
        gold_cost=50,
        chips_bonus=0,
        mult_bonus=0,
        description="Test item",
    )


def _make_quest(name: str, quest_type: QuestType) -> QuestTemplate:
    stage = QuestStage(
        stage_number=1,
        title="Stage 1",
        description="Test stage",
        trigger_room=1,
        completion_condition="defeat boss",
    )
    return QuestTemplate(
        id=f"quest-{name.lower().replace(' ', '-')}",
        theme=ThemeName.MEDIEVAL_FANTASY,
        name=name,
        quest_type=quest_type,
        stages=[stage],
        reward_gold=100,
        reward_item_ids=[],
    )


@pytest.fixture()
def theme() -> Theme:
    return Theme(
        name=ThemeName.MEDIEVAL_FANTASY,
        tone_descriptor="gritty dark fantasy",
        language_style="archaic formal",
        currency_name="Gold",
        health_term="Hit Points",
        death_term="slain",
        banned_words=("cyberpunk",),
    )


@pytest.fixture()
def settings() -> WorldSettings:
    return WorldSettings(
        theme=ThemeName.MEDIEVAL_FANTASY,
        difficulty="normal",
        seed=42,
    )


@pytest.fixture()
def enemies() -> list[EnemyPreset]:
    # 7 normal enemies + 1 boss (last in list, as per WorldCompiler convention)
    return [
        _make_enemy("Goblin Scout"),
        _make_enemy("Goblin Archer"),
        _make_enemy("Orc Warrior"),
        _make_enemy("Skeleton"),
        _make_enemy("Zombie"),
        _make_enemy("Dire Wolf"),
        _make_enemy("Bandit"),
        _make_enemy("Dragon", is_boss=True),
    ]


@pytest.fixture()
def items() -> list[ItemPreset]:
    return [
        _make_item("Iron Sword", "common"),
        _make_item("Leather Armor", "common"),
        _make_item("Fire Staff", "uncommon"),
        _make_item("Chain Mail", "uncommon"),
        _make_item("Shadow Dagger", "rare"),
        _make_item("Ring of Luck", "rare"),
        _make_item("Elder Relic", "legendary"),
        _make_item("Lucky Charm", "common"),
        _make_item("Holy Symbol", "uncommon"),
        _make_item("Healing Potion", "common"),
    ]


@pytest.fixture()
def npcs() -> list[NPCPreset]:
    return [
        NPCPreset(
            id="npc-blacksmith",
            theme=ThemeName.MEDIEVAL_FANTASY,
            name="Blacksmith",
            role=NPCRole.MERCHANT,
            personality_traits=["gruff"],
            speech_style="short sentences",
            faction=None,
        )
    ]


@pytest.fixture()
def quests() -> list[QuestTemplate]:
    return [
        _make_quest("The Dark Throne", QuestType.MAIN),
        _make_quest("Lost Caravan", QuestType.SIDE),
        _make_quest("Missing Villagers", QuestType.SIDE),
    ]


@pytest.fixture()
def compiler() -> WorldCompiler:
    return WorldCompiler()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_compile_produces_10_rooms(
    compiler: WorldCompiler,
    settings: WorldSettings,
    theme: Theme,
    enemies: list[EnemyPreset],
    items: list[ItemPreset],
    npcs: list[NPCPreset],
    quests: list[QuestTemplate],
) -> None:
    skeleton = compiler.compile(settings, theme, enemies, items, npcs, quests)

    assert len(skeleton.room_sequence) == 10


def test_room_10_is_always_boss(
    compiler: WorldCompiler,
    settings: WorldSettings,
    theme: Theme,
    enemies: list[EnemyPreset],
    items: list[ItemPreset],
    npcs: list[NPCPreset],
    quests: list[QuestTemplate],
) -> None:
    skeleton = compiler.compile(settings, theme, enemies, items, npcs, quests)
    last_room = skeleton.room_sequence[-1]

    assert last_room.room_type == RoomType.BOSS


def test_boss_room_has_one_enemy(
    compiler: WorldCompiler,
    settings: WorldSettings,
    theme: Theme,
    enemies: list[EnemyPreset],
    items: list[ItemPreset],
    npcs: list[NPCPreset],
    quests: list[QuestTemplate],
) -> None:
    skeleton = compiler.compile(settings, theme, enemies, items, npcs, quests)
    boss_room = skeleton.room_sequence[-1]

    assert len(boss_room.enemy_preset_ids) == 1


def test_shop_appears_at_room_4(
    compiler: WorldCompiler,
    settings: WorldSettings,
    theme: Theme,
    enemies: list[EnemyPreset],
    items: list[ItemPreset],
    npcs: list[NPCPreset],
    quests: list[QuestTemplate],
) -> None:
    skeleton = compiler.compile(settings, theme, enemies, items, npcs, quests)
    room_4 = skeleton.room_sequence[3]  # index 3 = room number 4

    assert room_4.room_type == RoomType.SHOP


def test_rest_appears_at_room_7(
    compiler: WorldCompiler,
    settings: WorldSettings,
    theme: Theme,
    enemies: list[EnemyPreset],
    items: list[ItemPreset],
    npcs: list[NPCPreset],
    quests: list[QuestTemplate],
) -> None:
    skeleton = compiler.compile(settings, theme, enemies, items, npcs, quests)
    room_7 = skeleton.room_sequence[6]  # index 6 = room number 7

    assert room_7.room_type == RoomType.REST


def test_main_quest_selected(
    compiler: WorldCompiler,
    settings: WorldSettings,
    theme: Theme,
    enemies: list[EnemyPreset],
    items: list[ItemPreset],
    npcs: list[NPCPreset],
    quests: list[QuestTemplate],
) -> None:
    skeleton = compiler.compile(settings, theme, enemies, items, npcs, quests)

    main_quests = [q for q in skeleton.active_quests if q.quest_type == QuestType.MAIN]
    assert len(main_quests) >= 1


def test_raises_on_no_enemies(
    compiler: WorldCompiler,
    settings: WorldSettings,
    theme: Theme,
    items: list[ItemPreset],
    npcs: list[NPCPreset],
    quests: list[QuestTemplate],
) -> None:
    with pytest.raises(WorldCompilationError):
        compiler.compile(settings, theme, [], items, npcs, quests)


def test_raises_on_no_main_quest(
    compiler: WorldCompiler,
    settings: WorldSettings,
    theme: Theme,
    enemies: list[EnemyPreset],
    items: list[ItemPreset],
    npcs: list[NPCPreset],
) -> None:
    # Provide only side quests — no main quest should trigger WorldCompilationError.
    side_only = [_make_quest("Side Quest", QuestType.SIDE)]

    with pytest.raises(WorldCompilationError):
        compiler.compile(settings, theme, enemies, items, npcs, side_only)

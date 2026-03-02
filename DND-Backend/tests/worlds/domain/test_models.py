"""
Domain-layer tests for world model value objects and aggregate invariants.
"""

import uuid
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from app.combat.domain.models import DieType
from app.worlds.domain.models import (
    AIBehavior,
    DungeonRoom,
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
    WorldSkeleton,
)
from app.worlds.domain.repositories import WorldRoomNotFoundError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def theme() -> Theme:
    return Theme(
        name=ThemeName.MEDIEVAL_FANTASY,
        tone_descriptor="gritty dark fantasy",
        language_style="archaic formal",
        currency_name="Gold",
        health_term="Hit Points",
        death_term="slain",
        banned_words=("neon",),
    )


@pytest.fixture()
def dungeon_room() -> DungeonRoom:
    return DungeonRoom(
        room_number=1,
        room_type=RoomType.COMBAT,
        enemy_preset_ids=("enemy-1",),
        npc_preset_id=None,
        lore_seed="Goblins lurk in the dark",
        is_boss_room=False,
    )


@pytest.fixture()
def world_skeleton(theme: Theme) -> WorldSkeleton:
    rooms = [
        DungeonRoom(
            room_number=i,
            room_type=RoomType.COMBAT if i < 10 else RoomType.BOSS,
            enemy_preset_ids=("enemy-1",),
            npc_preset_id=None,
            lore_seed=f"Room {i}",
            is_boss_room=(i == 10),
        )
        for i in range(1, 11)
    ]
    stage = QuestStage(
        stage_number=1,
        title="Test Stage",
        description="A test stage",
        trigger_room=1,
        completion_condition="defeat all",
    )
    quest = QuestTemplate(
        id="quest-main",
        theme=ThemeName.MEDIEVAL_FANTASY,
        name="Test Quest",
        quest_type=QuestType.MAIN,
        stages=[stage],
        reward_gold=100,
        reward_item_ids=[],
    )
    item = ItemPreset(
        id="item-1",
        theme=ThemeName.MEDIEVAL_FANTASY,
        name="Test Sword",
        item_type=ItemType.WEAPON,
        rarity="common",
        gold_cost=50,
        chips_bonus=0,
        mult_bonus=0,
        description="A test sword",
    )
    return WorldSkeleton(
        id=uuid.uuid4(),
        room_id=uuid.uuid4(),
        theme=theme,
        settings=WorldSettings(
            theme=ThemeName.MEDIEVAL_FANTASY, difficulty="normal"
        ),
        room_sequence=rooms,
        active_quests=[quest],
        available_items=[item],
        world_flags={},
        created_at=datetime.now(tz=timezone.utc),
    )


# ---------------------------------------------------------------------------
# Immutability tests
# ---------------------------------------------------------------------------


def test_dungeon_room_frozen(dungeon_room: DungeonRoom) -> None:
    with pytest.raises(FrozenInstanceError):
        dungeon_room.room_number = 99  # type: ignore[misc]


def test_theme_frozen(theme: Theme) -> None:
    with pytest.raises(FrozenInstanceError):
        theme.currency_name = "Credits"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# WorldSkeleton.get_room tests
# ---------------------------------------------------------------------------


def test_world_skeleton_get_room_valid(world_skeleton: WorldSkeleton) -> None:
    room = world_skeleton.get_room(5)

    assert room.room_number == 5


def test_world_skeleton_get_room_invalid(world_skeleton: WorldSkeleton) -> None:
    with pytest.raises(WorldRoomNotFoundError):
        world_skeleton.get_room(99)


def test_world_skeleton_get_room_1(world_skeleton: WorldSkeleton) -> None:
    room = world_skeleton.get_room(1)

    assert room.room_number == 1


def test_world_skeleton_get_room_10(world_skeleton: WorldSkeleton) -> None:
    room = world_skeleton.get_room(10)

    assert room.is_boss_room is True


# ---------------------------------------------------------------------------
# WorldSkeleton.set_flag tests
# ---------------------------------------------------------------------------


def test_world_skeleton_set_flag(world_skeleton: WorldSkeleton) -> None:
    world_skeleton.set_flag("betrayed_faction_a", True)

    assert world_skeleton.world_flags["betrayed_faction_a"] is True


def test_world_skeleton_set_flag_overwrite(world_skeleton: WorldSkeleton) -> None:
    world_skeleton.set_flag("rescued_prisoner", True)
    world_skeleton.set_flag("rescued_prisoner", False)

    assert world_skeleton.world_flags["rescued_prisoner"] is False

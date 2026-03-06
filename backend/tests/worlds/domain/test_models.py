"""
Unit tests for the worlds domain models.

Tests cover:
  - WorldSettings construction and validation
  - Immutability of frozen dataclasses
  - GeneratedWorld structure assertions

No infrastructure or framework imports — domain models are pure Python.
"""

import pytest
from dataclasses import FrozenInstanceError

from app.worlds.domain.exceptions import InvalidWorldSettingsError
from app.worlds.domain.models import (
    Difficulty,
    GeneratedWorld,
    MainQuest,
    NarratedRoom,
    QuestFocus,
    RoomType,
    Theme,
    WorldSettings,
)
from app.worlds.infrastructure.narrator import StubNarrator


# ---------------------------------------------------------------------------
# WorldSettings tests
# ---------------------------------------------------------------------------


def test_world_settings_valid() -> None:
    """Valid settings construct a frozen dataclass without error."""
    settings = WorldSettings(
        theme=Theme.CYBERPUNK,
        difficulty=Difficulty.NORMAL,
        room_count=10,
        quest_focus=QuestFocus.HEIST,
    )

    assert settings.room_count == 10
    assert settings.theme == Theme.CYBERPUNK


def test_world_settings_invalid_room_count_too_high() -> None:
    """validate() raises InvalidWorldSettingsError when room_count exceeds 15."""
    settings = WorldSettings(
        theme=Theme.MEDIEVAL_FANTASY,
        difficulty=Difficulty.HARD,
        room_count=20,
        quest_focus=QuestFocus.EXPLORATION,
    )

    with pytest.raises(InvalidWorldSettingsError):
        settings.validate()


def test_world_settings_invalid_room_count_too_low() -> None:
    """validate() raises InvalidWorldSettingsError when room_count is below 5."""
    settings = WorldSettings(
        theme=Theme.MANHWA,
        difficulty=Difficulty.EASY,
        room_count=2,
        quest_focus=QuestFocus.RESCUE,
    )

    with pytest.raises(InvalidWorldSettingsError):
        settings.validate()


def test_world_settings_valid_does_not_raise() -> None:
    """validate() on valid settings raises no exception."""
    settings = WorldSettings(
        theme=Theme.POST_APOCALYPTIC,
        difficulty=Difficulty.NIGHTMARE,
        room_count=5,
        quest_focus=QuestFocus.ASSASSINATION,
    )

    # Should not raise
    settings.validate()


def test_world_settings_immutable() -> None:
    """Assigning to a WorldSettings field raises FrozenInstanceError."""
    settings = WorldSettings(
        theme=Theme.CYBERPUNK,
        difficulty=Difficulty.NORMAL,
        room_count=8,
        quest_focus=QuestFocus.MYSTERY,
    )

    with pytest.raises(FrozenInstanceError):
        settings.room_count = 12  # type: ignore[misc]


# ---------------------------------------------------------------------------
# GeneratedWorld structure tests (via StubNarrator)
# ---------------------------------------------------------------------------


def _make_settings(
    room_count: int = 8, theme: Theme = Theme.CYBERPUNK
) -> WorldSettings:
    """Helper to build valid WorldSettings for structure tests."""
    return WorldSettings(
        theme=theme,
        difficulty=Difficulty.NORMAL,
        room_count=room_count,
        quest_focus=QuestFocus.HEIST,
    )


def test_generated_world_has_correct_room_count() -> None:
    """The number of rooms in GeneratedWorld matches the requested room_count."""
    settings = _make_settings(room_count=9)
    narrator = StubNarrator()

    world = narrator.generate_world(settings)

    assert len(world.rooms) == 9


def test_generated_world_last_room_is_boss() -> None:
    """The final room in GeneratedWorld always has RoomType.BOSS."""
    settings = _make_settings(room_count=10)
    narrator = StubNarrator()

    world = narrator.generate_world(settings)

    assert world.rooms[-1].room_type == RoomType.BOSS


def test_generated_world_first_room_is_combat() -> None:
    """The first room in GeneratedWorld always has RoomType.COMBAT."""
    settings = _make_settings(room_count=7)
    narrator = StubNarrator()

    world = narrator.generate_world(settings)

    assert world.rooms[0].room_type == RoomType.COMBAT


def test_generated_world_rooms_are_indexed_sequentially() -> None:
    """Each room's index field matches its position in the rooms tuple."""
    settings = _make_settings(room_count=6)
    narrator = StubNarrator()

    world = narrator.generate_world(settings)

    for expected_index, room in enumerate(world.rooms):
        assert room.index == expected_index

"""
Unit tests for the dungeons domain models.

Tests cover:
  - DungeonSettings construction and validation
  - DungeonSettings immutability (frozen dataclass)
  - DungeonRoom and DungeonQuest immutability
  - Domain exception hierarchy
"""

import uuid
from dataclasses import FrozenInstanceError

import pytest

from app.dungeons.domain.exceptions import (
    DungeonGenerationError,
    DungeonNotFoundError,
    InvalidDungeonSettingsError,
)
from app.dungeons.domain.models import (
    DungeonRoom,
    DungeonSettings,
    ROOM_COUNT_MAX,
    ROOM_COUNT_MIN,
    RoomType,
)


# ---------------------------------------------------------------------------
# DungeonSettings validation
# ---------------------------------------------------------------------------


def test_dungeon_settings_valid_construction() -> None:
    """Valid DungeonSettings constructs without error."""
    settings = DungeonSettings(
        campaign_id=uuid.uuid4(),
        room_count=8,
        party_size=4,
    )

    assert settings.room_count == 8
    assert settings.party_size == 4


def test_dungeon_settings_room_count_too_low_raises() -> None:
    """room_count below ROOM_COUNT_MIN raises InvalidDungeonSettingsError."""
    with pytest.raises(InvalidDungeonSettingsError):
        DungeonSettings(
            campaign_id=uuid.uuid4(),
            room_count=ROOM_COUNT_MIN - 1,
            party_size=4,
        )


def test_dungeon_settings_room_count_too_high_raises() -> None:
    """room_count above ROOM_COUNT_MAX raises InvalidDungeonSettingsError."""
    with pytest.raises(InvalidDungeonSettingsError):
        DungeonSettings(
            campaign_id=uuid.uuid4(),
            room_count=ROOM_COUNT_MAX + 1,
            party_size=4,
        )


def test_dungeon_settings_party_size_too_low_raises() -> None:
    """party_size below minimum raises InvalidDungeonSettingsError."""
    with pytest.raises(InvalidDungeonSettingsError):
        DungeonSettings(
            campaign_id=uuid.uuid4(),
            room_count=8,
            party_size=0,
        )


def test_dungeon_settings_party_size_too_high_raises() -> None:
    """party_size above maximum raises InvalidDungeonSettingsError."""
    with pytest.raises(InvalidDungeonSettingsError):
        DungeonSettings(
            campaign_id=uuid.uuid4(),
            room_count=8,
            party_size=9,
        )


def test_dungeon_settings_boundary_room_count_min() -> None:
    """room_count equal to ROOM_COUNT_MIN is valid."""
    settings = DungeonSettings(
        campaign_id=uuid.uuid4(),
        room_count=ROOM_COUNT_MIN,
        party_size=4,
    )

    assert settings.room_count == ROOM_COUNT_MIN


def test_dungeon_settings_boundary_room_count_max() -> None:
    """room_count equal to ROOM_COUNT_MAX is valid."""
    settings = DungeonSettings(
        campaign_id=uuid.uuid4(),
        room_count=ROOM_COUNT_MAX,
        party_size=4,
    )

    assert settings.room_count == ROOM_COUNT_MAX


# ---------------------------------------------------------------------------
# Immutability
# ---------------------------------------------------------------------------


def test_dungeon_settings_is_immutable() -> None:
    """DungeonSettings is a frozen dataclass — mutation raises FrozenInstanceError."""
    settings = DungeonSettings(
        campaign_id=uuid.uuid4(),
        room_count=8,
        party_size=4,
    )

    with pytest.raises(FrozenInstanceError):
        settings.room_count = 10  # type: ignore[misc]


def test_dungeon_room_is_immutable() -> None:
    """DungeonRoom is a frozen dataclass — mutation raises FrozenInstanceError."""
    room = DungeonRoom(
        index=0,
        room_type=RoomType.COMBAT,
        name="Test Room",
        description="A room.",
        enemy_names=("Goblin",),
        npc_names=(),
    )

    with pytest.raises(FrozenInstanceError):
        room.name = "Changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


def test_invalid_dungeon_settings_error_is_dungeon_generation_error() -> None:
    """InvalidDungeonSettingsError is a subclass of DungeonGenerationError."""
    exc = InvalidDungeonSettingsError("bad settings")

    assert isinstance(exc, DungeonGenerationError)


def test_dungeon_not_found_error_is_raised() -> None:
    """DungeonNotFoundError can be raised and caught."""
    with pytest.raises(DungeonNotFoundError):
        raise DungeonNotFoundError("Dungeon abc not found")

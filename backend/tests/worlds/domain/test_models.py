"""
Unit tests for the worlds domain models.

Tests cover:
  - World aggregate construction
  - PresetFaction and PresetBoss immutability (frozen dataclasses)
  - WorldNotFoundError is a domain exception
"""

import uuid
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from app.worlds.domain.exceptions import WorldNotFoundError
from app.worlds.domain.models import PresetBoss, PresetFaction, Theme, World


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_faction(**kwargs: object) -> PresetFaction:
    defaults: dict[str, object] = {
        "name": "Test Faction",
        "description": "A faction",
        "alignment": "neutral",
        "public_reputation": "Unknown",
        "hidden_agenda": "Secret",
    }
    defaults.update(kwargs)
    return PresetFaction(**defaults)  # type: ignore[arg-type]


def _make_boss(**kwargs: object) -> PresetBoss:
    defaults: dict[str, object] = {
        "name": "Test Boss",
        "description": "A boss",
        "challenge_rating": "CR 10",
        "abilities": ("Strike",),
        "lore": "Some lore",
    }
    defaults.update(kwargs)
    return PresetBoss(**defaults)  # type: ignore[arg-type]


def _make_world(**kwargs: object) -> World:
    defaults: dict[str, object] = {
        "id": uuid.uuid4(),
        "name": "Test World",
        "theme": Theme.MEDIEVAL_FANTASY,
        "description": "A test world",
        "lore_summary": "Some lore",
        "factions": (_make_faction(),),
        "bosses": (_make_boss(),),
        "is_active": True,
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    defaults.update(kwargs)
    return World(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# World aggregate tests
# ---------------------------------------------------------------------------


def test_world_construction_succeeds() -> None:
    """A World aggregate can be constructed with valid fields."""
    world = _make_world()

    assert world.name == "Test World"
    assert world.theme == Theme.MEDIEVAL_FANTASY
    assert world.is_active is True


def test_world_stores_factions() -> None:
    """Factions are stored and accessible on the aggregate."""
    faction = _make_faction(name="Iron Crown")
    world = _make_world(factions=(faction,))

    assert len(world.factions) == 1
    assert world.factions[0].name == "Iron Crown"


def test_world_stores_bosses() -> None:
    """Bosses are stored and accessible on the aggregate."""
    boss = _make_boss(name="The Lich")
    world = _make_world(bosses=(boss,))

    assert len(world.bosses) == 1
    assert world.bosses[0].name == "The Lich"


def test_world_inactive_flag() -> None:
    """A world with is_active=False is correctly represented."""
    world = _make_world(is_active=False)

    assert world.is_active is False


# ---------------------------------------------------------------------------
# PresetFaction immutability
# ---------------------------------------------------------------------------


def test_preset_faction_is_immutable() -> None:
    """PresetFaction is a frozen dataclass — mutation raises FrozenInstanceError."""
    faction = _make_faction()

    with pytest.raises(FrozenInstanceError):
        faction.name = "Changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# PresetBoss immutability
# ---------------------------------------------------------------------------


def test_preset_boss_is_immutable() -> None:
    """PresetBoss is a frozen dataclass — mutation raises FrozenInstanceError."""
    boss = _make_boss()

    with pytest.raises(FrozenInstanceError):
        boss.name = "Changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# WorldNotFoundError
# ---------------------------------------------------------------------------


def test_world_not_found_error_is_raised() -> None:
    """WorldNotFoundError can be raised and caught as expected."""
    with pytest.raises(WorldNotFoundError):
        raise WorldNotFoundError("World abc not found")

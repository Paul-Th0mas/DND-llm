"""
Unit tests for the worlds application use cases.

Uses an in-memory stub repository — no database required.
Tests verify orchestration logic: repository calls, exception handling,
and response shape.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.worlds.application.schemas import WorldDetailResponse, WorldSummaryResponse
from app.worlds.application.use_cases import GetWorldByIdUseCase, GetWorldsUseCase
from app.worlds.domain.exceptions import WorldNotFoundError
from app.worlds.domain.models import PresetBoss, PresetFaction, Theme, World
from app.worlds.domain.repositories import WorldRepository


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_world(world_id: uuid.UUID | None = None, is_active: bool = True) -> World:
    """Build a minimal valid World aggregate for use in tests."""
    return World(
        id=world_id or uuid.uuid4(),
        name="Test World",
        theme=Theme.MEDIEVAL_FANTASY,
        description="A world",
        lore_summary="Some lore",
        factions=(
            PresetFaction(
                name="Faction A",
                description="desc",
                alignment="neutral",
                public_reputation="known",
                hidden_agenda="secret",
            ),
        ),
        bosses=(
            PresetBoss(
                name="Boss A",
                description="desc",
                challenge_rating="CR 10",
                abilities=("Strike",),
                lore="lore",
            ),
        ),
        is_active=is_active,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def _stub_repo(worlds: list[World] | None = None) -> WorldRepository:
    """Create a mock WorldRepository with controlled return values."""
    repo = MagicMock(spec=WorldRepository)
    repo.get_all_active.return_value = worlds or []
    return repo


# ---------------------------------------------------------------------------
# GetWorldsUseCase tests
# ---------------------------------------------------------------------------


def test_get_worlds_returns_empty_list_when_no_worlds() -> None:
    """execute() returns an empty list when the repository has no active worlds."""
    repo = _stub_repo(worlds=[])
    use_case = GetWorldsUseCase(repo=repo)

    result = use_case.execute()

    assert result == []


def test_get_worlds_returns_summary_for_each_world() -> None:
    """execute() returns one WorldSummaryResponse per active world."""
    worlds = [_make_world(), _make_world()]
    repo = _stub_repo(worlds=worlds)
    use_case = GetWorldsUseCase(repo=repo)

    result = use_case.execute()

    assert len(result) == 2
    assert all(isinstance(r, WorldSummaryResponse) for r in result)


def test_get_worlds_summary_contains_correct_name() -> None:
    """The returned summary has the correct world name."""
    world = _make_world()
    world.name = "Realm of Valdor"
    repo = _stub_repo(worlds=[world])
    use_case = GetWorldsUseCase(repo=repo)

    result = use_case.execute()

    assert result[0].name == "Realm of Valdor"


def test_get_worlds_calls_repository_once() -> None:
    """execute() calls get_all_active() exactly once."""
    repo = _stub_repo()
    use_case = GetWorldsUseCase(repo=repo)

    use_case.execute()

    repo.get_all_active.assert_called_once()


# ---------------------------------------------------------------------------
# GetWorldByIdUseCase tests
# ---------------------------------------------------------------------------


def test_get_world_by_id_returns_detail_response() -> None:
    """execute() returns a WorldDetailResponse for a valid world_id."""
    world_id = uuid.uuid4()
    world = _make_world(world_id=world_id)
    repo = _stub_repo()
    repo.get_by_id.return_value = world
    use_case = GetWorldByIdUseCase(repo=repo)

    result = use_case.execute(world_id)

    assert isinstance(result, WorldDetailResponse)
    assert result.world_id == world_id


def test_get_world_by_id_raises_when_not_found() -> None:
    """execute() raises WorldNotFoundError when the repository returns None."""
    repo = _stub_repo()
    repo.get_by_id.return_value = None
    use_case = GetWorldByIdUseCase(repo=repo)

    with pytest.raises(WorldNotFoundError):
        use_case.execute(uuid.uuid4())


def test_get_world_by_id_raises_when_inactive() -> None:
    """execute() raises WorldNotFoundError when the world is inactive."""
    world_id = uuid.uuid4()
    world = _make_world(world_id=world_id, is_active=False)
    repo = _stub_repo()
    repo.get_by_id.return_value = world
    use_case = GetWorldByIdUseCase(repo=repo)

    with pytest.raises(WorldNotFoundError):
        use_case.execute(world_id)


def test_get_world_by_id_response_includes_factions() -> None:
    """The detail response contains the world's factions."""
    world_id = uuid.uuid4()
    world = _make_world(world_id=world_id)
    repo = _stub_repo()
    repo.get_by_id.return_value = world
    use_case = GetWorldByIdUseCase(repo=repo)

    result = use_case.execute(world_id)

    assert len(result.factions) == 1
    assert result.factions[0].name == "Faction A"


def test_get_world_by_id_response_includes_bosses() -> None:
    """The detail response contains the world's bosses."""
    world_id = uuid.uuid4()
    world = _make_world(world_id=world_id)
    repo = _stub_repo()
    repo.get_by_id.return_value = world
    use_case = GetWorldByIdUseCase(repo=repo)

    result = use_case.execute(world_id)

    assert len(result.bosses) == 1
    assert result.bosses[0].name == "Boss A"

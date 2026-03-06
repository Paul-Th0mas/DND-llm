"""
Unit tests for the worlds application use cases.

Uses StubNarrator directly — no mocking needed because StubNarrator is
pure infrastructure with no side effects. The use case tests verify
orchestration logic: DTO conversion, domain validation, and response shape.
"""

import pytest

from app.worlds.application.schemas import GeneratedWorldResponse, WorldSettingsRequest
from app.worlds.application.use_cases import GenerateWorldUseCase
from app.worlds.domain.exceptions import InvalidWorldSettingsError
from app.worlds.domain.models import Difficulty, QuestFocus, Theme
from app.worlds.infrastructure.narrator import StubNarrator


def _make_use_case() -> GenerateWorldUseCase:
    """Instantiate the use case with the stub narrator."""
    return GenerateWorldUseCase(narrator=StubNarrator())


def _make_request(
    theme: Theme = Theme.CYBERPUNK,
    difficulty: Difficulty = Difficulty.NORMAL,
    room_count: int = 8,
    quest_focus: QuestFocus = QuestFocus.HEIST,
) -> WorldSettingsRequest:
    """Build a default valid WorldSettingsRequest."""
    return WorldSettingsRequest(
        theme=theme,
        difficulty=difficulty,
        room_count=room_count,
        quest_focus=quest_focus,
    )


# ---------------------------------------------------------------------------
# Happy path tests
# ---------------------------------------------------------------------------


def test_generate_world_returns_response() -> None:
    """execute() returns a GeneratedWorldResponse for valid input."""
    use_case = _make_use_case()
    request = _make_request()

    result = use_case.execute(request)

    assert isinstance(result, GeneratedWorldResponse)


def test_generate_world_cyberpunk_theme() -> None:
    """The theme from the request propagates to the response."""
    use_case = _make_use_case()
    request = _make_request(theme=Theme.CYBERPUNK)

    result = use_case.execute(request)

    assert result.theme == Theme.CYBERPUNK


def test_generate_world_medieval_theme() -> None:
    """MEDIEVAL_FANTASY theme propagates to the response."""
    use_case = _make_use_case()
    request = _make_request(theme=Theme.MEDIEVAL_FANTASY, quest_focus=QuestFocus.RESCUE)

    result = use_case.execute(request)

    assert result.theme == Theme.MEDIEVAL_FANTASY


def test_generate_world_room_count_matches_request() -> None:
    """The number of rooms in the response matches the requested room_count."""
    use_case = _make_use_case()
    request = _make_request(room_count=11)

    result = use_case.execute(request)

    assert len(result.rooms) == 11


def test_generate_world_response_has_main_quest() -> None:
    """The response includes a non-empty main quest with stages."""
    use_case = _make_use_case()
    request = _make_request()

    result = use_case.execute(request)

    assert result.main_quest.name != ""
    assert len(result.main_quest.stages) > 0


def test_generate_world_response_has_factions() -> None:
    """The response includes at least one active faction."""
    use_case = _make_use_case()
    request = _make_request()

    result = use_case.execute(request)

    assert len(result.active_factions) > 0


# ---------------------------------------------------------------------------
# Validation / error path tests
# ---------------------------------------------------------------------------


def test_generate_world_invalid_settings_raises() -> None:
    """execute() raises InvalidWorldSettingsError when domain validation fails.

    Note: Pydantic enforces ge=5, le=15 on the schema field. To test the
    domain validate() path we must construct WorldSettings directly and
    bypass Pydantic. The use case calls validate() after to_domain().
    We test this by calling WorldSettings.validate() on an out-of-bounds value
    constructed without going through the schema (e.g. room_count=3 directly).
    """
    from app.worlds.domain.models import WorldSettings

    settings = WorldSettings(
        theme=Theme.MANHWA,
        difficulty=Difficulty.EASY,
        room_count=3,
        quest_focus=QuestFocus.MYSTERY,
    )

    with pytest.raises(InvalidWorldSettingsError):
        settings.validate()

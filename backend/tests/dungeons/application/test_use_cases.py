"""
Unit tests for the dungeons application use cases.

Uses in-memory stub repositories and the StubDungeonNarrator — no database
or LLM calls. Tests verify orchestration: repository calls, ownership checks,
exception handling, and response shape.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.campaigns.domain.exceptions import CampaignNotFoundError
from app.campaigns.domain.models import (
    Campaign,
    CampaignTone,
    ContentBoundaries,
    LevelRange,
)
from app.dungeons.application.schemas import (
    DungeonCreatedResponse,
    DungeonDetailResponse,
    DungeonSummaryResponse,
    GenerateDungeonRequest,
)
from app.dungeons.application.use_cases import (
    GenerateDungeonUseCase,
    GetDungeonUseCase,
    ListDungeonsUseCase,
)
from app.dungeons.domain.exceptions import DungeonNotFoundError
from app.dungeons.domain.models import (
    Dungeon,
    DungeonQuest,
    DungeonRoom,
    DungeonSettings,
    RoomType,
)
from app.dungeons.domain.repositories import DungeonRepository
from app.dungeons.infrastructure.narrator import StubDungeonNarrator
from app.worlds.domain.models import PresetBoss, PresetFaction, Theme, World


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _dm_id() -> uuid.UUID:
    return uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def _make_world() -> World:
    return World(
        id=uuid.uuid4(),
        name="Test World",
        theme=Theme.MEDIEVAL_FANTASY,
        description="A world",
        lore_summary="Some lore",
        factions=(
            PresetFaction(
                name="Faction",
                description="desc",
                alignment="neutral",
                public_reputation="known",
                hidden_agenda="secret",
            ),
        ),
        bosses=(
            PresetBoss(
                name="Boss",
                description="desc",
                challenge_rating="CR 10",
                abilities=("Strike",),
                lore="lore",
            ),
        ),
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def _make_campaign(dm_id: uuid.UUID, world_id: uuid.UUID) -> Campaign:
    return Campaign(
        id=uuid.uuid4(),
        name="Test Campaign",
        edition="5e-2024",
        tone=CampaignTone.HIGH_FANTASY,
        player_count=4,
        level_range=LevelRange(start=1, end=5),
        themes=("adventure",),
        content_boundaries=ContentBoundaries(lines=()),
        dm_id=dm_id,
        world_id=world_id,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def _make_dungeon(campaign_id: uuid.UUID, world_id: uuid.UUID) -> Dungeon:
    return Dungeon(
        id=uuid.uuid4(),
        campaign_id=campaign_id,
        world_id=world_id,
        name="Test Dungeon",
        premise="A test dungeon.",
        rooms=(
            DungeonRoom(
                index=0,
                room_type=RoomType.COMBAT,
                name="Room 1",
                description="A room.",
                enemy_names=("Goblin",),
                npc_names=(),
            ),
        ),
        quest=DungeonQuest(
            name="Test Quest",
            description="Do things.",
            stages=("Stage 1",),
        ),
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


# ---------------------------------------------------------------------------
# GenerateDungeonUseCase tests
# ---------------------------------------------------------------------------


def test_generate_dungeon_returns_created_response() -> None:
    """execute() returns a DungeonCreatedResponse for a valid campaign."""
    dm_id = _dm_id()
    world = _make_world()
    campaign = _make_campaign(dm_id, world.id)

    campaign_repo = MagicMock()
    campaign_repo.get_by_id.return_value = campaign
    world_repo = MagicMock()
    world_repo.get_by_id.return_value = world
    dungeon_repo = MagicMock(spec=DungeonRepository)
    narrator = StubDungeonNarrator()

    use_case = GenerateDungeonUseCase(
        campaign_repo=campaign_repo,
        world_repo=world_repo,
        dungeon_repo=dungeon_repo,
        narrator=narrator,
    )
    request = GenerateDungeonRequest(room_count=5, party_size=4)

    result = use_case.execute(campaign.id, dm_id, request)

    assert isinstance(result, DungeonCreatedResponse)
    assert result.room_count == 5


def test_generate_dungeon_saves_to_repository() -> None:
    """execute() calls dungeon_repo.save() exactly once."""
    dm_id = _dm_id()
    world = _make_world()
    campaign = _make_campaign(dm_id, world.id)

    campaign_repo = MagicMock()
    campaign_repo.get_by_id.return_value = campaign
    world_repo = MagicMock()
    world_repo.get_by_id.return_value = world
    dungeon_repo = MagicMock(spec=DungeonRepository)
    narrator = StubDungeonNarrator()

    use_case = GenerateDungeonUseCase(
        campaign_repo=campaign_repo,
        world_repo=world_repo,
        dungeon_repo=dungeon_repo,
        narrator=narrator,
    )
    request = GenerateDungeonRequest(room_count=5, party_size=4)
    use_case.execute(campaign.id, dm_id, request)

    dungeon_repo.save.assert_called_once()


def test_generate_dungeon_raises_when_campaign_not_found() -> None:
    """execute() raises CampaignNotFoundError when campaign is missing."""
    campaign_repo = MagicMock()
    campaign_repo.get_by_id.return_value = None
    world_repo = MagicMock()
    dungeon_repo = MagicMock(spec=DungeonRepository)

    use_case = GenerateDungeonUseCase(
        campaign_repo=campaign_repo,
        world_repo=world_repo,
        dungeon_repo=dungeon_repo,
        narrator=StubDungeonNarrator(),
    )
    with pytest.raises(CampaignNotFoundError):
        use_case.execute(uuid.uuid4(), _dm_id(), GenerateDungeonRequest())


def test_generate_dungeon_raises_when_wrong_dm() -> None:
    """execute() raises CampaignNotFoundError when DM does not own the campaign."""
    world = _make_world()
    campaign = _make_campaign(dm_id=uuid.uuid4(), world_id=world.id)  # different DM

    campaign_repo = MagicMock()
    campaign_repo.get_by_id.return_value = campaign
    world_repo = MagicMock()
    dungeon_repo = MagicMock(spec=DungeonRepository)

    use_case = GenerateDungeonUseCase(
        campaign_repo=campaign_repo,
        world_repo=world_repo,
        dungeon_repo=dungeon_repo,
        narrator=StubDungeonNarrator(),
    )
    with pytest.raises(CampaignNotFoundError):
        use_case.execute(campaign.id, _dm_id(), GenerateDungeonRequest())


# ---------------------------------------------------------------------------
# GetDungeonUseCase tests
# ---------------------------------------------------------------------------


def test_get_dungeon_returns_detail_response() -> None:
    """execute() returns a DungeonDetailResponse when dungeon and campaign match."""
    dm_id = _dm_id()
    world = _make_world()
    campaign = _make_campaign(dm_id, world.id)
    dungeon = _make_dungeon(campaign.id, world.id)

    dungeon_repo = MagicMock(spec=DungeonRepository)
    dungeon_repo.get_by_id.return_value = dungeon
    campaign_repo = MagicMock()
    campaign_repo.get_by_id.return_value = campaign

    use_case = GetDungeonUseCase(dungeon_repo=dungeon_repo, campaign_repo=campaign_repo)
    result = use_case.execute(dungeon.id, dm_id)

    assert isinstance(result, DungeonDetailResponse)
    assert result.dungeon_id == dungeon.id


def test_get_dungeon_raises_when_not_found() -> None:
    """execute() raises DungeonNotFoundError when dungeon does not exist."""
    dungeon_repo = MagicMock(spec=DungeonRepository)
    dungeon_repo.get_by_id.return_value = None
    campaign_repo = MagicMock()

    use_case = GetDungeonUseCase(dungeon_repo=dungeon_repo, campaign_repo=campaign_repo)
    with pytest.raises(DungeonNotFoundError):
        use_case.execute(uuid.uuid4(), _dm_id())


def test_get_dungeon_succeeds_for_any_authenticated_user() -> None:
    """
    execute() returns dungeon detail for any authenticated user, not just the
    campaign owner. Players in a session need dungeon content (US-010), so
    GetDungeonUseCase does not enforce DM-only access.
    """
    world = _make_world()
    # Campaign belongs to a different DM than the caller.
    campaign = _make_campaign(dm_id=uuid.uuid4(), world_id=world.id)
    dungeon = _make_dungeon(campaign.id, world.id)

    dungeon_repo = MagicMock(spec=DungeonRepository)
    dungeon_repo.get_by_id.return_value = dungeon
    campaign_repo = MagicMock()
    campaign_repo.get_by_id.return_value = campaign

    use_case = GetDungeonUseCase(dungeon_repo=dungeon_repo, campaign_repo=campaign_repo)
    # Any user id is accepted — ownership is not checked.
    result = use_case.execute(dungeon.id, _dm_id())

    assert isinstance(result, DungeonDetailResponse)
    assert result.dungeon_id == dungeon.id


# ---------------------------------------------------------------------------
# ListDungeonsUseCase tests
# ---------------------------------------------------------------------------


def test_list_dungeons_returns_summaries() -> None:
    """execute() returns one DungeonSummaryResponse per dungeon."""
    dm_id = _dm_id()
    world = _make_world()
    campaign = _make_campaign(dm_id, world.id)
    dungeons = [_make_dungeon(campaign.id, world.id) for _ in range(3)]

    dungeon_repo = MagicMock(spec=DungeonRepository)
    dungeon_repo.list_by_campaign_id.return_value = dungeons
    campaign_repo = MagicMock()
    campaign_repo.get_by_id.return_value = campaign
    room_repo = MagicMock()
    room_repo.get_by_dungeon_id.return_value = None

    use_case = ListDungeonsUseCase(
        dungeon_repo=dungeon_repo,
        campaign_repo=campaign_repo,
        room_repo=room_repo,
    )
    result = use_case.execute(campaign.id, dm_id)

    assert len(result) == 3
    assert all(isinstance(r, DungeonSummaryResponse) for r in result)


def test_list_dungeons_raises_when_campaign_not_found() -> None:
    """execute() raises CampaignNotFoundError when campaign is missing."""
    dungeon_repo = MagicMock(spec=DungeonRepository)
    campaign_repo = MagicMock()
    campaign_repo.get_by_id.return_value = None
    room_repo = MagicMock()

    use_case = ListDungeonsUseCase(
        dungeon_repo=dungeon_repo,
        campaign_repo=campaign_repo,
        room_repo=room_repo,
    )
    with pytest.raises(CampaignNotFoundError):
        use_case.execute(uuid.uuid4(), _dm_id())


def test_list_dungeons_embeds_room_when_found() -> None:
    """execute() includes room status when a room exists for a dungeon."""
    from app.rooms.domain.models import InviteCode
    from app.rooms.domain.models import Room as RoomDomain

    dm_id = _dm_id()
    world = _make_world()
    campaign = _make_campaign(dm_id, world.id)
    dungeon = _make_dungeon(campaign.id, world.id)

    room = RoomDomain(
        id=uuid.uuid4(),
        name="Test Room",
        dm_id=dm_id,
        invite_code=InviteCode(value="ABCD1234"),
        max_players=8,
        is_active=True,
        created_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        dungeon_id=dungeon.id,
    )

    dungeon_repo = MagicMock(spec=DungeonRepository)
    dungeon_repo.list_by_campaign_id.return_value = [dungeon]
    campaign_repo = MagicMock()
    campaign_repo.get_by_id.return_value = campaign
    room_repo = MagicMock()
    room_repo.get_by_dungeon_id.return_value = room

    use_case = ListDungeonsUseCase(
        dungeon_repo=dungeon_repo,
        campaign_repo=campaign_repo,
        room_repo=room_repo,
    )
    result = use_case.execute(campaign.id, dm_id)

    assert len(result) == 1
    assert result[0].room is not None
    assert result[0].room.room_name == "Test Room"
    assert result[0].room.is_active is True


def test_list_dungeons_room_is_none_when_no_room() -> None:
    """execute() sets room to None when no room is linked to the dungeon."""
    dm_id = _dm_id()
    world = _make_world()
    campaign = _make_campaign(dm_id, world.id)
    dungeon = _make_dungeon(campaign.id, world.id)

    dungeon_repo = MagicMock(spec=DungeonRepository)
    dungeon_repo.list_by_campaign_id.return_value = [dungeon]
    campaign_repo = MagicMock()
    campaign_repo.get_by_id.return_value = campaign
    room_repo = MagicMock()
    room_repo.get_by_dungeon_id.return_value = None

    use_case = ListDungeonsUseCase(
        dungeon_repo=dungeon_repo,
        campaign_repo=campaign_repo,
        room_repo=room_repo,
    )
    result = use_case.execute(campaign.id, dm_id)

    assert len(result) == 1
    assert result[0].room is None

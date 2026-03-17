"""
FastAPI dependency providers for the dungeons bounded context.

Wires repositories, use cases, and the narrator via Depends().
Narrator selection:
  - GeminiDungeonNarrator is active in production (uses GEMINI_API_KEY).
  - Swap to StubDungeonNarrator for offline testing by changing get_narrator().
"""

import logging

from fastapi import Depends
from sqlalchemy.orm import Session

from app.campaigns.infrastructure.repositories import SqlAlchemyCampaignRepository
from app.core.config import settings
from app.db.session import get_db
from app.dungeons.application.narrator_port import DungeonNarratorPort
from app.dungeons.application.use_cases import (
    GenerateDungeonUseCase,
    GetDungeonUseCase,
    ListDungeonsUseCase,
)
from app.dungeons.infrastructure.narrator import GeminiDungeonNarrator
from app.dungeons.infrastructure.repositories import SQLAlchemyDungeonRepository
from app.rooms.infrastructure.repositories import SqlAlchemyRoomRepository
from app.worlds.infrastructure.repositories import SQLAlchemyWorldRepository

logger = logging.getLogger(__name__)


def get_dungeon_repository(
    session: Session = Depends(get_db),
) -> SQLAlchemyDungeonRepository:
    """Provide a SQLAlchemyDungeonRepository bound to the current request session."""
    return SQLAlchemyDungeonRepository(session)


def get_campaign_repository(
    session: Session = Depends(get_db),
) -> SqlAlchemyCampaignRepository:
    """Provide a SqlAlchemyCampaignRepository for cross-context reads."""
    return SqlAlchemyCampaignRepository(session)


def get_world_repository(
    session: Session = Depends(get_db),
) -> SQLAlchemyWorldRepository:
    """Provide a SQLAlchemyWorldRepository for cross-context reads."""
    return SQLAlchemyWorldRepository(session)


def get_narrator() -> DungeonNarratorPort:
    """
    Provide the active dungeon narrator implementation.

    Currently wired to GeminiDungeonNarrator. To use the stub narrator for
    offline testing, replace the return value here.
    """
    logger.info("Using GeminiDungeonNarrator for dungeon generation")
    return GeminiDungeonNarrator(api_key=settings.GEMINI_API_KEY)


def get_generate_dungeon_use_case(
    dungeon_repo: SQLAlchemyDungeonRepository = Depends(get_dungeon_repository),
    campaign_repo: SqlAlchemyCampaignRepository = Depends(get_campaign_repository),
    world_repo: SQLAlchemyWorldRepository = Depends(get_world_repository),
    narrator: DungeonNarratorPort = Depends(get_narrator),
) -> GenerateDungeonUseCase:
    """Provide a GenerateDungeonUseCase wired with all dependencies."""
    return GenerateDungeonUseCase(
        campaign_repo=campaign_repo,
        world_repo=world_repo,
        dungeon_repo=dungeon_repo,
        narrator=narrator,
    )


def get_dungeon_use_case(
    dungeon_repo: SQLAlchemyDungeonRepository = Depends(get_dungeon_repository),
    campaign_repo: SqlAlchemyCampaignRepository = Depends(get_campaign_repository),
) -> GetDungeonUseCase:
    """Provide a GetDungeonUseCase wired with its dependencies."""
    return GetDungeonUseCase(dungeon_repo=dungeon_repo, campaign_repo=campaign_repo)


def get_room_repository_for_dungeons(
    session: Session = Depends(get_db),
) -> SqlAlchemyRoomRepository:
    """
    Provide a SqlAlchemyRoomRepository for dungeon list room-status lookups.

    This is a separate provider from the one in app/rooms/api/dependencies.py
    so the dungeons context controls its own wiring without importing from
    the rooms API layer (which would create a cross-context API dependency).
    """
    return SqlAlchemyRoomRepository(session)


def get_list_dungeons_use_case(
    dungeon_repo: SQLAlchemyDungeonRepository = Depends(get_dungeon_repository),
    campaign_repo: SqlAlchemyCampaignRepository = Depends(get_campaign_repository),
    room_repo: SqlAlchemyRoomRepository = Depends(get_room_repository_for_dungeons),
) -> ListDungeonsUseCase:
    """Provide a ListDungeonsUseCase wired with all dependencies."""
    return ListDungeonsUseCase(
        dungeon_repo=dungeon_repo,
        campaign_repo=campaign_repo,
        room_repo=room_repo,
    )

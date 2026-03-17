"""
FastAPI dependency injection for the campaigns bounded context.

Wires the SQLAlchemy repository into the use cases via Depends().
The router never instantiates repositories or use cases directly.

US-018: ListCampaignsUseCase now requires world and dungeon repositories so it
can embed world_name and dungeon_count in the campaign list response.
"""

import logging

from fastapi import Depends
from sqlalchemy.orm import Session

from app.campaigns.application.use_cases import (
    CreateCampaignUseCase,
    GetCampaignUseCase,
    ListCampaignsUseCase,
)
from app.campaigns.infrastructure.repositories import SqlAlchemyCampaignRepository
from app.db.session import get_db
from app.dungeons.infrastructure.repositories import SQLAlchemyDungeonRepository
from app.worlds.infrastructure.repositories import SQLAlchemyWorldRepository

logger = logging.getLogger(__name__)


def get_campaign_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyCampaignRepository:
    """Provide a SqlAlchemyCampaignRepository bound to the current request session."""
    return SqlAlchemyCampaignRepository(session=db)


def get_world_repository_for_campaigns(
    db: Session = Depends(get_db),
) -> SQLAlchemyWorldRepository:
    """
    Provide a SQLAlchemyWorldRepository for campaign list world-name lookups.

    This is a separate provider from the one in the worlds API layer so the
    campaigns context controls its own wiring without importing from other
    context API layers (cross-context API dependency would break DDD).
    """
    return SQLAlchemyWorldRepository(session=db)


def get_dungeon_repository_for_campaigns(
    db: Session = Depends(get_db),
) -> SQLAlchemyDungeonRepository:
    """
    Provide a SQLAlchemyDungeonRepository for campaign list dungeon-count lookups.

    Separate provider for the same DDD isolation reason as world repo above.
    """
    return SQLAlchemyDungeonRepository(session=db)


def get_create_campaign_use_case(
    repo: SqlAlchemyCampaignRepository = Depends(get_campaign_repository),
) -> CreateCampaignUseCase:
    """Provide a CreateCampaignUseCase wired with the current repository."""
    return CreateCampaignUseCase(repo=repo)


def get_campaign_use_case(
    repo: SqlAlchemyCampaignRepository = Depends(get_campaign_repository),
) -> GetCampaignUseCase:
    """Provide a GetCampaignUseCase wired with the current repository."""
    return GetCampaignUseCase(repo=repo)


def get_list_campaigns_use_case(
    repo: SqlAlchemyCampaignRepository = Depends(get_campaign_repository),
    world_repo: SQLAlchemyWorldRepository = Depends(get_world_repository_for_campaigns),
    dungeon_repo: SQLAlchemyDungeonRepository = Depends(
        get_dungeon_repository_for_campaigns
    ),
) -> ListCampaignsUseCase:
    """
    Provide a ListCampaignsUseCase wired with campaign, world, and dungeon repos.

    The world and dungeon repos are used to embed world_name and dungeon_count
    in each campaign summary (US-018) without extra API round-trips from the hub.
    """
    return ListCampaignsUseCase(
        repo=repo,
        world_repo=world_repo,
        dungeon_repo=dungeon_repo,
    )

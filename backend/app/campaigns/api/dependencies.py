"""
FastAPI dependency injection for the campaigns bounded context.

get_narrator() returns StubCampaignNarrator. To use a real LLM narrator,
replace the return value here — no other files need to change.
"""

import logging

from fastapi import Depends
from sqlalchemy.orm import Session

from app.campaigns.application.use_cases import (
    CreateCampaignUseCase,
    GenerateCampaignWorldUseCase,
)
from app.campaigns.infrastructure.narrator import StubCampaignNarrator
from app.campaigns.infrastructure.repositories import (
    SqlAlchemyCampaignRepository,
    SqlAlchemyCampaignWorldRepository,
)
from app.db.session import get_db

logger = logging.getLogger(__name__)


def get_campaign_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyCampaignRepository:
    return SqlAlchemyCampaignRepository(session=db)


def get_campaign_world_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyCampaignWorldRepository:
    return SqlAlchemyCampaignWorldRepository(session=db)


def get_create_campaign_use_case(
    repo: SqlAlchemyCampaignRepository = Depends(get_campaign_repository),
) -> CreateCampaignUseCase:
    return CreateCampaignUseCase(repo=repo)


def get_generate_campaign_world_use_case(
    campaign_repo: SqlAlchemyCampaignRepository = Depends(get_campaign_repository),
    world_repo: SqlAlchemyCampaignWorldRepository = Depends(
        get_campaign_world_repository
    ),
) -> GenerateCampaignWorldUseCase:
    # Swap StubCampaignNarrator for a real narrator here when LLM is ready
    narrator = StubCampaignNarrator()
    return GenerateCampaignWorldUseCase(
        campaign_repo=campaign_repo,
        world_repo=world_repo,
        narrator=narrator,
    )

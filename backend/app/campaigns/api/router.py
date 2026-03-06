"""
FastAPI router for the campaigns bounded context.

Endpoints:
  POST /campaigns           → CampaignResponse (201)
  POST /campaigns/{id}/world → GenerateCampaignWorldResponse (201)

Routers are thin: validate input via Pydantic, delegate to use cases,
return the response. No business logic lives here.
"""

import logging
import uuid

from fastapi import APIRouter, Depends

from app.campaigns.api.dependencies import (
    get_create_campaign_use_case,
    get_generate_campaign_world_use_case,
)
from app.campaigns.application.schemas import (
    CampaignResponse,
    CreateCampaignRequest,
    GenerateCampaignWorldResponse,
)
from app.campaigns.application.use_cases import (
    CreateCampaignUseCase,
    GenerateCampaignWorldUseCase,
)
from app.rooms.api.dependencies import get_dm_user
from app.users.domain.models import User

logger = logging.getLogger(__name__)

campaigns_router = APIRouter()


@campaigns_router.post(
    "",
    response_model=CampaignResponse,
    status_code=201,
    summary="Create a new campaign",
    description=(
        "Captures all DM requirements for a D&D 5e campaign: tone, themes, "
        "content boundaries (Lines & Veils), level range, and house rules. "
        "Returns the campaign ID and the URL for the next pipeline step. "
        "Requires DM role."
    ),
)
def create_campaign(
    request: CreateCampaignRequest,
    current_user: User = Depends(get_dm_user),
    use_case: CreateCampaignUseCase = Depends(get_create_campaign_use_case),
) -> CampaignResponse:
    """
    POST /campaigns

    Delegates entirely to CreateCampaignUseCase. Domain exceptions propagate
    to the global error handlers automatically.
    """
    logger.info(
        "POST /campaigns: name='%s' dm_id=%s",
        request.campaign_name,
        current_user.id,
    )
    return use_case.execute(request, current_user.id)


@campaigns_router.post(
    "/{campaign_id}/world",
    response_model=GenerateCampaignWorldResponse,
    status_code=201,
    summary="Generate world for a campaign",
    description=(
        "Generates a D&D 5e world (settlement, factions, NPCs, hooks) for the "
        "given campaign using the narrator pipeline. Currently uses the stub "
        "narrator (template-based, no LLM). Requires DM role and ownership of "
        "the campaign."
    ),
)
def generate_campaign_world(
    campaign_id: uuid.UUID,
    current_user: User = Depends(get_dm_user),
    use_case: GenerateCampaignWorldUseCase = Depends(
        get_generate_campaign_world_use_case
    ),
) -> GenerateCampaignWorldResponse:
    """
    POST /campaigns/{campaign_id}/world

    Delegates to GenerateCampaignWorldUseCase. Returns 404 if the campaign
    does not exist or belongs to a different DM.
    """
    logger.info("POST /campaigns/%s/world: dm_id=%s", campaign_id, current_user.id)
    return use_case.execute(campaign_id, current_user.id)

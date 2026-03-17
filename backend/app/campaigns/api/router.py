"""
FastAPI router for the campaigns bounded context.

Endpoints:
  POST /campaigns          → CampaignResponse        (201)
  GET  /campaigns          → list[CampaignSummaryResponse] (200)
  GET  /campaigns/{id}     → CampaignDetailResponse  (200)

Routers are thin: validate input via Pydantic, delegate to use cases,
return the response. No business logic lives here.
"""

import logging
import uuid

from fastapi import APIRouter, Depends

from app.campaigns.api.dependencies import (
    get_campaign_use_case,
    get_create_campaign_use_case,
    get_list_campaigns_use_case,
)
from app.campaigns.application.schemas import (
    CampaignDetailResponse,
    CampaignResponse,
    CampaignSummaryResponse,
    CreateCampaignRequest,
)
from app.campaigns.application.use_cases import (
    CreateCampaignUseCase,
    GetCampaignUseCase,
    ListCampaignsUseCase,
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
        "Creates a campaign against a selected world. The request must include a "
        "world_id referencing an active admin-seeded world. Returns the campaign ID "
        "and the URL for dungeon generation. Requires DM role."
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
        "POST /campaigns: name='%s' dm_id=%s world_id=%s",
        request.campaign_name,
        current_user.id,
        request.world_id,
    )
    return use_case.execute(request, current_user.id)


@campaigns_router.get(
    "",
    response_model=list[CampaignSummaryResponse],
    summary="List DM's campaigns",
    description="Returns all campaigns owned by the authenticated DM, newest first.",
)
def list_campaigns(
    current_user: User = Depends(get_dm_user),
    use_case: ListCampaignsUseCase = Depends(get_list_campaigns_use_case),
) -> list[CampaignSummaryResponse]:
    """
    GET /campaigns

    Returns summaries of all campaigns for the current DM.
    """
    logger.info("GET /campaigns: dm_id=%s", current_user.id)
    return use_case.execute(current_user.id)


@campaigns_router.get(
    "/{campaign_id}",
    response_model=CampaignDetailResponse,
    summary="Get campaign detail",
    description=(
        "Returns full campaign detail including world reference, level range, "
        "tone, content boundaries, and themes. Returns 404 if the campaign "
        "does not exist or belongs to a different DM."
    ),
)
def get_campaign(
    campaign_id: uuid.UUID,
    current_user: User = Depends(get_dm_user),
    use_case: GetCampaignUseCase = Depends(get_campaign_use_case),
) -> CampaignDetailResponse:
    """
    GET /campaigns/{campaign_id}

    Returns 404 if the campaign does not exist or is owned by another DM.
    """
    logger.info("GET /campaigns/%s: dm_id=%s", campaign_id, current_user.id)
    return use_case.execute(campaign_id, current_user.id)

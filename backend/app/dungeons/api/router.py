"""
FastAPI router for the dungeons bounded context.

Endpoints:
  POST /campaigns/{campaign_id}/dungeons → DungeonCreatedResponse  (201)
  GET  /campaigns/{campaign_id}/dungeons → list[DungeonSummaryResponse] (200)
  GET  /dungeons/{dungeon_id}            → DungeonDetailResponse   (200)

Routers are thin: validate input via Pydantic, delegate to use cases,
return the response. No business logic lives here.
"""

import logging
import uuid

from fastapi import APIRouter, Depends

from app.dungeons.api.dependencies import (
    get_dungeon_use_case,
    get_generate_dungeon_use_case,
    get_list_dungeons_use_case,
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
from app.rooms.api.dependencies import get_dm_user
from app.users.api.dependencies import get_current_user
from app.users.domain.models import User

logger = logging.getLogger(__name__)

dungeons_router = APIRouter()


@dungeons_router.post(
    "/campaigns/{campaign_id}/dungeons",
    response_model=DungeonCreatedResponse,
    status_code=201,
    summary="Generate a dungeon for a campaign session",
    description=(
        "Generates a dungeon (rooms, encounters, quest) using the campaign's selected "
        "world as narrative context. Requires DM role and ownership of the campaign. "
        "Returns 404 if the campaign does not exist or belongs to another DM."
    ),
)
def generate_dungeon(
    campaign_id: uuid.UUID,
    request: GenerateDungeonRequest,
    current_user: User = Depends(get_dm_user),
    use_case: GenerateDungeonUseCase = Depends(get_generate_dungeon_use_case),
) -> DungeonCreatedResponse:
    """
    POST /campaigns/{campaign_id}/dungeons

    Delegates entirely to GenerateDungeonUseCase. Domain exceptions propagate
    to the global error handlers automatically.
    """
    logger.info(
        "POST /campaigns/%s/dungeons: dm_id=%s rooms=%d",
        campaign_id,
        current_user.id,
        request.room_count,
    )
    return use_case.execute(campaign_id, current_user.id, request)


@dungeons_router.get(
    "/campaigns/{campaign_id}/dungeons",
    response_model=list[DungeonSummaryResponse],
    summary="List dungeons for a campaign",
    description=(
        "Returns all generated dungeons for the given campaign, newest first. "
        "Requires DM role and ownership of the campaign."
    ),
)
def list_dungeons(
    campaign_id: uuid.UUID,
    current_user: User = Depends(get_dm_user),
    use_case: ListDungeonsUseCase = Depends(get_list_dungeons_use_case),
) -> list[DungeonSummaryResponse]:
    """
    GET /campaigns/{campaign_id}/dungeons

    Returns 404 if the campaign does not exist or belongs to another DM.
    """
    logger.info("GET /campaigns/%s/dungeons: dm_id=%s", campaign_id, current_user.id)
    return use_case.execute(campaign_id, current_user.id)


@dungeons_router.get(
    "/dungeons/{dungeon_id}",
    response_model=DungeonDetailResponse,
    summary="Get full dungeon detail",
    description=(
        "Returns the full dungeon including all rooms, quest stages, and metadata. "
        "Accessible by any authenticated user — both DMs reviewing their prepared "
        "content and players viewing the dungeon panel inside a game room (US-010)."
    ),
)
def get_dungeon(
    dungeon_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    use_case: GetDungeonUseCase = Depends(get_dungeon_use_case),
) -> DungeonDetailResponse:
    """
    GET /dungeons/{dungeon_id}

    Returns 404 if the dungeon does not exist. Any authenticated user may call
    this endpoint — no DM role required — so players can load dungeon content
    during a session.
    """
    logger.info("GET /dungeons/%s: user_id=%s", dungeon_id, current_user.id)
    return use_case.execute(dungeon_id, current_user.id)

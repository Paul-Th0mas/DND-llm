"""
FastAPI router for the worlds bounded context.

Endpoints:
  GET /worlds              → list[WorldSummaryResponse]  (200)
  GET /worlds/{world_id}   → WorldDetailResponse         (200)

Routers are thin: validate path/query params, delegate to use cases,
return the response. No business logic lives here.
"""

import logging
import uuid

from fastapi import APIRouter, Depends

from app.worlds.api.dependencies import get_world_by_id_use_case, get_worlds_use_case
from app.worlds.application.schemas import WorldDetailResponse, WorldSummaryResponse
from app.worlds.application.use_cases import GetWorldByIdUseCase, GetWorldsUseCase

logger = logging.getLogger(__name__)

worlds_router = APIRouter()


@worlds_router.get(
    "",
    response_model=list[WorldSummaryResponse],
    summary="List available worlds",
    description=(
        "Returns all active worlds (id, name, theme, description). "
        "Used to populate the world selection screen when a DM creates a campaign. "
        "No authentication required."
    ),
)
def list_worlds(
    use_case: GetWorldsUseCase = Depends(get_worlds_use_case),
) -> list[WorldSummaryResponse]:
    """
    GET /worlds

    No auth required — world list is not sensitive. Domain exceptions
    propagate to the global error handlers automatically.
    """
    logger.info("GET /worlds")
    return use_case.execute()


@worlds_router.get(
    "/{world_id}",
    response_model=WorldDetailResponse,
    summary="Get world detail",
    description=(
        "Returns the full detail of a single world including factions and bosses. "
        "Used on the world detail screen before a DM commits to creating a campaign. "
        "Returns 404 if the world does not exist or is inactive."
    ),
)
def get_world(
    world_id: uuid.UUID,
    use_case: GetWorldByIdUseCase = Depends(get_world_by_id_use_case),
) -> WorldDetailResponse:
    """
    GET /worlds/{world_id}

    No auth required. 404 is returned by the global handler when
    WorldNotFoundError is raised by the use case.
    """
    logger.info("GET /worlds/%s", world_id)
    return use_case.execute(world_id)

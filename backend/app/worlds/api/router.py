"""
FastAPI router for the worlds bounded context.

One endpoint:
  POST /worlds/generate → GeneratedWorldResponse (200)

Routers are thin: validate input via Pydantic, delegate to the use case,
return the response. No business logic lives here.
"""

import logging

from fastapi import APIRouter, Depends

from app.worlds.api.dependencies import get_generate_world_use_case
from app.worlds.application.schemas import (
    GeneratedWorldResponse,
    WorldOptionsResponse,
    WorldSettingsRequest,
)
from app.worlds.domain.models import Theme
from app.worlds.application.use_cases import GenerateWorldUseCase

logger = logging.getLogger(__name__)

worlds_router = APIRouter()


@worlds_router.get(
    "/options",
    response_model=WorldOptionsResponse,
    summary="Get world generation options",
    description=(
        "Returns all valid enum values for theme, difficulty, quest focus, and room type, "
        "plus the allowed room_count range. Use this to populate form dropdowns dynamically "
        "instead of hardcoding values on the client."
    ),
)
def get_world_options(theme: Theme | None = None) -> WorldOptionsResponse:
    """
    GET /worlds/options?theme=<Theme>

    No auth required — enum values are not sensitive.
    The optional theme query param is forwarded to from_domain() for future
    theme-specific filtering; currently all options are returned regardless.
    FastAPI reads theme directly from the query string and validates it against
    the Theme enum — an invalid value returns 422 automatically.
    """
    logger.info("GET /worlds/options: theme=%s", theme)
    return WorldOptionsResponse.from_domain(theme=theme)


@worlds_router.post(
    "/generate",
    response_model=GeneratedWorldResponse,
    summary="Generate a new world",
    description=(
        "Accepts world settings from the DM and returns a fully generated dungeon world "
        "including rooms, main quest, and active factions. "
        "Currently uses the StubNarrator (template-based, no LLM)."
    ),
)
def generate_world(
    request: WorldSettingsRequest,
    use_case: GenerateWorldUseCase = Depends(get_generate_world_use_case),
) -> GeneratedWorldResponse:
    """
    POST /worlds/generate

    Delegates entirely to GenerateWorldUseCase. Domain exceptions propagate
    to the global error handlers automatically — no HTTPException raising here.
    """
    logger.info(
        "POST /worlds/generate: theme=%s rooms=%d",
        request.theme,
        request.room_count,
    )
    return use_case.execute(request)

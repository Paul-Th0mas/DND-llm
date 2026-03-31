"""
FastAPI router for the character_options bounded context.

Endpoints:
  GET /character-options/classes                → CharacterClassListResponse  (200)
  GET /character-options/classes/{class_id}     → CharacterClassResponse      (200)
  GET /character-options/species                → CharacterSpeciesListResponse (200)
  GET /character-options/species/{species_id}   → CharacterSpeciesResponse    (200)

All endpoints are public (no auth required) — players need to browse options
before they are logged in to start character creation.
"""

import logging
import uuid

from fastapi import APIRouter, Depends

from app.character_options.api.dependencies import (
    get_class_use_case,
    get_list_classes_use_case,
    get_list_species_use_case,
    get_species_use_case,
)
from app.character_options.application.schemas import (
    CharacterClassListResponse,
    CharacterClassResponse,
    CharacterSpeciesListResponse,
    CharacterSpeciesResponse,
)
from app.character_options.application.use_cases import (
    GetClassUseCase,
    GetSpeciesUseCase,
    ListClassesUseCase,
    ListSpeciesUseCase,
)

logger = logging.getLogger(__name__)

character_options_router = APIRouter()


@character_options_router.get(
    "/classes",
    response_model=CharacterClassListResponse,
    summary="List character classes by theme",
    description=(
        "Returns all playable classes available for the given world theme. "
        "The theme query parameter must match a valid Theme enum value "
        "(e.g. MEDIEVAL_FANTASY, CYBERPUNK, POST_APOCALYPTIC)."
    ),
)
def list_classes(
    theme: str,
    use_case: ListClassesUseCase = Depends(get_list_classes_use_case),
) -> CharacterClassListResponse:
    """
    GET /character-options/classes?theme={theme}

    Returns an empty list if no classes are seeded for the given theme.
    """
    logger.info("GET /character-options/classes: theme=%s", theme)
    return use_case.execute(theme)


@character_options_router.get(
    "/classes/{class_id}",
    response_model=CharacterClassResponse,
    summary="Get a character class by ID",
    description="Returns a single character class by its UUID. Returns 404 if not found.",
)
def get_class(
    class_id: uuid.UUID,
    use_case: GetClassUseCase = Depends(get_class_use_case),
) -> CharacterClassResponse:
    """
    GET /character-options/classes/{class_id}

    Domain exceptions propagate to the global error handler automatically.
    """
    logger.info("GET /character-options/classes/%s", class_id)
    return use_case.execute(class_id)


@character_options_router.get(
    "/species",
    response_model=CharacterSpeciesListResponse,
    summary="List character species by theme",
    description=(
        "Returns all playable species available for the given world theme. "
        "The theme query parameter must match a valid Theme enum value."
    ),
)
def list_species(
    theme: str,
    use_case: ListSpeciesUseCase = Depends(get_list_species_use_case),
) -> CharacterSpeciesListResponse:
    """
    GET /character-options/species?theme={theme}

    Returns an empty list if no species are seeded for the given theme.
    """
    logger.info("GET /character-options/species: theme=%s", theme)
    return use_case.execute(theme)


@character_options_router.get(
    "/species/{species_id}",
    response_model=CharacterSpeciesResponse,
    summary="Get a character species by ID",
    description="Returns a single character species by its UUID. Returns 404 if not found.",
)
def get_species(
    species_id: uuid.UUID,
    use_case: GetSpeciesUseCase = Depends(get_species_use_case),
) -> CharacterSpeciesResponse:
    """
    GET /character-options/species/{species_id}

    Domain exceptions propagate to the global error handler automatically.
    """
    logger.info("GET /character-options/species/%s", species_id)
    return use_case.execute(species_id)

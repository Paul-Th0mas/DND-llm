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
    get_class_skill_proficiencies_use_case,
    get_class_spell_options_use_case,
    get_class_starting_equipment_use_case,
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
    ClassSkillProficienciesResponse,
    ClassSpellOptionsResponse,
    ClassStartingEquipmentResponse,
)
from app.character_options.application.use_cases import (
    GetClassSkillProficienciesUseCase,
    GetClassSpellOptionsUseCase,
    GetClassStartingEquipmentUseCase,
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
    "/classes/{class_id}/skill-proficiencies",
    response_model=ClassSkillProficienciesResponse,
    summary="Get selectable skills for a class",
    description=(
        "Returns the list of skills a player may choose from and how many "
        "to select when creating a character of this class."
    ),
)
def get_class_skill_proficiencies(
    class_id: uuid.UUID,
    use_case: GetClassSkillProficienciesUseCase = Depends(
        get_class_skill_proficiencies_use_case
    ),
) -> ClassSkillProficienciesResponse:
    """GET /character-options/classes/{class_id}/skill-proficiencies"""
    logger.info("GET /character-options/classes/%s/skill-proficiencies", class_id)
    return use_case.execute(class_id)


@character_options_router.get(
    "/classes/{class_id}/starting-equipment",
    response_model=ClassStartingEquipmentResponse,
    summary="Get starting equipment for a class",
    description="Returns the starting equipment items granted to this class.",
)
def get_class_starting_equipment(
    class_id: uuid.UUID,
    use_case: GetClassStartingEquipmentUseCase = Depends(
        get_class_starting_equipment_use_case
    ),
) -> ClassStartingEquipmentResponse:
    """GET /character-options/classes/{class_id}/starting-equipment"""
    logger.info("GET /character-options/classes/%s/starting-equipment", class_id)
    return use_case.execute(class_id)


@character_options_router.get(
    "/classes/{class_id}/spells",
    response_model=ClassSpellOptionsResponse,
    summary="Get spell options for a class",
    description=(
        "Returns the spell sections and spells available for selection. "
        "Non-caster classes return an empty sections list."
    ),
)
def get_class_spell_options(
    class_id: uuid.UUID,
    use_case: GetClassSpellOptionsUseCase = Depends(get_class_spell_options_use_case),
) -> ClassSpellOptionsResponse:
    """GET /character-options/classes/{class_id}/spells"""
    logger.info("GET /character-options/classes/%s/spells", class_id)
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

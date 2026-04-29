"""
FastAPI router for the characters bounded context.

Endpoints:
  POST   /characters                                   → CharacterResponse (201)
  GET    /characters                                   → ListMyCharactersResponse (200)
  GET    /characters/{character_id}                    → CharacterSheetResponse (200)
  POST   /campaigns/{campaign_id}/characters           → LinkCharacterResponse (201)
  DELETE /campaigns/{campaign_id}/characters/{char_id} → 204 (no body)
  GET    /campaigns/{campaign_id}/characters           → CampaignRosterResponse (200)

Routers are thin: validate input via Pydantic, delegate to use cases,
return the response. No business logic lives here.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, Response, status

from app.characters.api.dependencies import (
    get_campaign_roster_use_case,
    get_character_use_case,
    get_create_character_use_case,
    get_link_character_use_case,
    get_list_my_characters_use_case,
    get_unlink_character_use_case,
)
from app.characters.application.schemas import (
    CampaignRosterResponse,
    CharacterResponse,
    CharacterSheetResponse,
    CreateCharacterRequest,
    LinkCharacterRequest,
    LinkCharacterResponse,
    ListMyCharactersResponse,
)
from app.characters.application.use_cases import (
    CreateCharacterUseCase,
    GetCampaignRosterUseCase,
    GetCharacterUseCase,
    LinkCharacterUseCase,
    ListMyCharactersUseCase,
    UnlinkCharacterUseCase,
)
from app.rooms.api.dependencies import get_dm_user
from app.users.api.dependencies import get_current_user
from app.users.domain.models import User

logger = logging.getLogger(__name__)

characters_router = APIRouter()


@characters_router.post(
    "/characters",
    response_model=CharacterResponse,
    status_code=201,
    summary="Create a new character",
    description=(
        "Creates a character for the authenticated user. "
        "class_id and species_id must reference valid options for the given world's theme. "
        "Requires authentication (player or DM role)."
    ),
)
def create_character(
    request: CreateCharacterRequest,
    current_user: User = Depends(get_current_user),
    use_case: CreateCharacterUseCase = Depends(get_create_character_use_case),
) -> CharacterResponse:
    """
    POST /characters

    Validates class and species exist, enforces domain invariants via
    Character.create(), and persists the character.
    """
    logger.info(
        "POST /characters: name='%s' owner_id=%s world_id=%s",
        request.name,
        current_user.id,
        request.world_id,
    )
    return use_case.execute(
        name=request.name,
        owner_id=current_user.id,
        world_id=request.world_id,
        class_id=request.class_id,
        species_id=request.species_id,
        background=request.background,
        ability_scores=request.ability_scores.to_domain(),
        skill_proficiencies=request.skill_proficiencies,
        starting_equipment=request.starting_equipment,
        spells=request.spells,
    )


@characters_router.get(
    "/characters",
    response_model=ListMyCharactersResponse,
    summary="List my characters",
    description=(
        "Returns all characters owned by the authenticated user, with resolved "
        "world_name, class_name, and species_name. "
        "Requires authentication."
    ),
)
def list_my_characters(
    current_user: User = Depends(get_current_user),
    use_case: ListMyCharactersUseCase = Depends(get_list_my_characters_use_case),
) -> ListMyCharactersResponse:
    """
    GET /characters

    Returns an empty list (not 404) if the user has no characters.
    """
    logger.info("GET /characters: owner_id=%s", current_user.id)
    return use_case.execute(owner_id=current_user.id)


@characters_router.get(
    "/characters/{character_id}",
    response_model=CharacterSheetResponse,
    summary="Get character sheet",
    description=(
        "Returns the full character sheet for the authenticated owner. "
        "Returns 404 if the character does not exist or belongs to another user."
    ),
)
def get_character(
    character_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    use_case: GetCharacterUseCase = Depends(get_character_use_case),
) -> CharacterSheetResponse:
    """
    GET /characters/{character_id}

    The requester must own the character — otherwise 404 is returned
    to avoid leaking the existence of other players' characters.
    """
    logger.info("GET /characters/%s: requester=%s", character_id, current_user.id)
    return use_case.execute(character_id=character_id, requester_id=current_user.id)


@characters_router.post(
    "/campaigns/{campaign_id}/characters",
    response_model=LinkCharacterResponse,
    status_code=201,
    summary="Link a character to a campaign",
    description=(
        "Links an existing character owned by the authenticated player to a campaign. "
        "The character's world must match the campaign's world. "
        "Returns 409 if the player already has a character in this campaign."
    ),
)
def link_character(
    campaign_id: uuid.UUID,
    request: LinkCharacterRequest,
    current_user: User = Depends(get_current_user),
    use_case: LinkCharacterUseCase = Depends(get_link_character_use_case),
) -> LinkCharacterResponse:
    """
    POST /campaigns/{campaign_id}/characters

    Enforces: player owns the character, world matches, no duplicate link.
    """
    logger.info(
        "POST /campaigns/%s/characters: character=%s requester=%s",
        campaign_id,
        request.character_id,
        current_user.id,
    )
    return use_case.execute(
        campaign_id=campaign_id,
        character_id=request.character_id,
        requester_id=current_user.id,
    )


@characters_router.delete(
    "/campaigns/{campaign_id}/characters/{character_id}",
    status_code=204,
    summary="Unlink a character from a campaign",
    description=(
        "Removes the campaign link from a character. "
        "The authenticated user must own the character."
    ),
)
def unlink_character(
    campaign_id: uuid.UUID,
    character_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    use_case: UnlinkCharacterUseCase = Depends(get_unlink_character_use_case),
) -> Response:
    """
    DELETE /campaigns/{campaign_id}/characters/{character_id}

    Returns 204 with no body on success.
    """
    logger.info(
        "DELETE /campaigns/%s/characters/%s: requester=%s",
        campaign_id,
        character_id,
        current_user.id,
    )
    use_case.execute(
        campaign_id=campaign_id,
        character_id=character_id,
        requester_id=current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@characters_router.get(
    "/campaigns/{campaign_id}/characters",
    response_model=CampaignRosterResponse,
    summary="Get campaign party roster",
    description=(
        "Returns all characters linked to a campaign. DM-only. "
        "Returns 404 if the campaign does not exist or belongs to another DM."
    ),
)
def get_campaign_roster(
    campaign_id: uuid.UUID,
    current_user: User = Depends(get_dm_user),
    use_case: GetCampaignRosterUseCase = Depends(get_campaign_roster_use_case),
) -> CampaignRosterResponse:
    """
    GET /campaigns/{campaign_id}/characters

    Only the DM who owns the campaign can access this endpoint.
    """
    logger.info("GET /campaigns/%s/characters: dm_id=%s", campaign_id, current_user.id)
    return use_case.execute(campaign_id=campaign_id, dm_id=current_user.id)

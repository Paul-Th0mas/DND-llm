"""
Application services (use cases) for the characters bounded context.

CreateCharacterUseCase      — POST /characters
GetCharacterUseCase         — GET /characters/{character_id}
ListMyCharactersUseCase     — GET /characters (US-046)
LinkCharacterUseCase        — POST /campaigns/{campaign_id}/characters (US-029)
UnlinkCharacterUseCase      — DELETE /campaigns/{campaign_id}/characters/{character_id}
GetCampaignRosterUseCase    — GET /campaigns/{campaign_id}/characters (US-031)

Use cases orchestrate domain objects and repositories.
They contain no business logic — invariants live in domain aggregates.
"""

import logging
import uuid
from datetime import datetime, timezone

from app.characters.application.schemas import (
    CampaignRosterResponse,
    CharacterResponse,
    CharacterRosterEntry,
    CharacterSheetResponse,
    CharacterSummaryResponse,
    LinkCharacterResponse,
    ListMyCharactersResponse,
)
from app.characters.domain.exceptions import (
    CampaignCharacterThemeMismatchError,
    CharacterAccessDeniedError,
    CharacterAlreadyLinkedError,
    CharacterNotFoundError,
)
from app.characters.domain.models import AbilityScores, Character
from app.characters.domain.repositories import CharacterRepository

# Cross-context repository interfaces — abstract ABCs only, no ORM imports.
from app.character_options.domain.repositories import (
    CharacterClassRepository,
    CharacterSpeciesRepository,
)
from app.campaigns.domain.repositories import CampaignRepository
from app.campaigns.domain.exceptions import CampaignNotFoundError
from app.users.domain.repositories import UserRepository
from app.worlds.domain.repositories import WorldRepository
from app.character_options.domain.exceptions import (
    CharacterClassNotFoundError,
    CharacterSpeciesNotFoundError,
)

logger = logging.getLogger(__name__)


class CreateCharacterUseCase:
    """
    Handles POST /characters.

    Validates that the class and species belong to the world's theme,
    then persists the character.
    """

    def __init__(
        self,
        character_repo: CharacterRepository,
        class_repo: CharacterClassRepository,
        species_repo: CharacterSpeciesRepository,
    ) -> None:
        self._character_repo = character_repo
        self._class_repo = class_repo
        self._species_repo = species_repo

    def execute(
        self,
        name: str,
        owner_id: uuid.UUID,
        world_id: uuid.UUID,
        class_id: uuid.UUID,
        species_id: uuid.UUID,
        background: str,
        ability_scores: AbilityScores,
    ) -> CharacterResponse:
        """
        Create and persist a new Character.

        Validates class/species existence; theme validation requires the
        caller to ensure theme consistency (the world entity carries the theme).
        Raises CharacterClassNotFoundError / CharacterSpeciesNotFoundError
        if either referenced option does not exist.

        @param name           - Character display name.
        @param owner_id       - UUID of the authenticated user.
        @param world_id       - UUID of the world this character belongs to.
        @param class_id       - UUID of the chosen CharacterClass.
        @param species_id     - UUID of the chosen CharacterSpecies.
        @param background     - Character backstory text.
        @param ability_scores - AbilityScores value object.
        @returns CharacterResponse DTO.
        """
        logger.info(
            "CreateCharacterUseCase.execute: name=%s owner=%s world=%s",
            name,
            owner_id,
            world_id,
        )

        # Validate class and species exist (NotFoundError → 404).
        cls = self._class_repo.get_by_id(class_id)
        if cls is None:
            raise CharacterClassNotFoundError(f"Class {class_id} not found")

        sp = self._species_repo.get_by_id(species_id)
        if sp is None:
            raise CharacterSpeciesNotFoundError(f"Species {species_id} not found")

        character = Character.create(
            name=name,
            owner_id=owner_id,
            world_id=world_id,
            class_id=class_id,
            species_id=species_id,
            background=background,
            ability_scores=ability_scores,
        )
        self._character_repo.save(character)
        return CharacterResponse.from_domain(character)


class GetCharacterUseCase:
    """
    Handles GET /characters/{character_id}.

    Returns the full character sheet for the authenticated owner.
    Raises CharacterNotFoundError (→ 404) if the character does not exist
    or belongs to a different user.
    """

    def __init__(
        self,
        character_repo: CharacterRepository,
        class_repo: CharacterClassRepository,
        species_repo: CharacterSpeciesRepository,
    ) -> None:
        self._character_repo = character_repo
        self._class_repo = class_repo
        self._species_repo = species_repo

    def execute(
        self, character_id: uuid.UUID, requester_id: uuid.UUID
    ) -> CharacterSheetResponse:
        """
        Fetch a character sheet for the requesting owner.

        @param character_id  - UUID of the character to fetch.
        @param requester_id  - UUID of the authenticated user.
        @returns CharacterSheetResponse DTO.
        @raises CharacterNotFoundError if not found or owned by another user.
        """
        logger.debug("GetCharacterUseCase.execute: character_id=%s", character_id)
        character = self._character_repo.get_by_id(character_id)
        if character is None:
            raise CharacterNotFoundError(f"Character {character_id} not found")
        if character.owner_id != requester_id:
            # Return 404 to avoid leaking existence of other players' characters.
            raise CharacterAccessDeniedError(f"Character {character_id} not found")

        # Resolve class and species — raise 404 if they were deleted.
        cls = self._class_repo.get_by_id(character.class_id)
        if cls is None:
            raise CharacterClassNotFoundError(f"Class {character.class_id} not found")

        sp = self._species_repo.get_by_id(character.species_id)
        if sp is None:
            raise CharacterSpeciesNotFoundError(
                f"Species {character.species_id} not found"
            )

        return CharacterSheetResponse.from_domain(character, cls, sp)


class ListMyCharactersUseCase:
    """
    Handles GET /characters (US-046).

    Returns all characters owned by the authenticated user with resolved
    world_name, class_name, and species_name.
    """

    def __init__(
        self,
        character_repo: CharacterRepository,
        class_repo: CharacterClassRepository,
        species_repo: CharacterSpeciesRepository,
        world_repo: WorldRepository,
    ) -> None:
        self._character_repo = character_repo
        self._class_repo = class_repo
        self._species_repo = species_repo
        self._world_repo = world_repo

    def execute(
        self,
        owner_id: uuid.UUID,
    ) -> ListMyCharactersResponse:
        """
        List all characters for the authenticated user with enrichment.

        world_name, class_name, species_name are None if the referenced records
        have been deleted — the response degrades gracefully rather than 500-ing.

        @param owner_id   - UUID of the authenticated user.
        @returns ListMyCharactersResponse DTO.
        """
        logger.debug("ListMyCharactersUseCase.execute: owner_id=%s", owner_id)
        characters = self._character_repo.list_by_owner_id(owner_id)
        logger.info(
            "ListMyCharactersUseCase: found %d characters for owner=%s",
            len(characters),
            owner_id,
        )

        result: list[CharacterSummaryResponse] = []
        for character in characters:
            # Resolve world name — warn if world was deleted.
            world_name: str | None = None
            world = self._world_repo.get_by_id(character.world_id)
            if world is not None:
                world_name = world.name
            else:
                logger.warning(
                    "ListMyCharactersUseCase: world %s not found for character %s",
                    character.world_id,
                    character.id,
                )

            # Resolve class name — None if deleted.
            cls = self._class_repo.get_by_id(character.class_id)
            class_name: str | None = cls.display_name if cls is not None else None

            # Resolve species name — None if deleted.
            sp = self._species_repo.get_by_id(character.species_id)
            species_name: str | None = sp.display_name if sp is not None else None

            result.append(
                CharacterSummaryResponse(
                    id=character.id,
                    name=character.name,
                    world_id=character.world_id,
                    world_name=world_name,
                    class_name=class_name,
                    species_name=species_name,
                    created_at=character.created_at,
                )
            )

        return ListMyCharactersResponse(characters=result)


class LinkCharacterUseCase:
    """
    Handles POST /campaigns/{campaign_id}/characters (US-029).

    Links an existing character to a campaign.
    Enforces: player owns the character, character theme matches campaign world
    theme, player has not already linked another character to this campaign.
    """

    def __init__(
        self,
        character_repo: CharacterRepository,
        campaign_repo: CampaignRepository,
        class_repo: CharacterClassRepository,
        species_repo: CharacterSpeciesRepository,
    ) -> None:
        self._character_repo = character_repo
        self._campaign_repo = campaign_repo
        self._class_repo = class_repo
        self._species_repo = species_repo

    def execute(
        self,
        campaign_id: uuid.UUID,
        character_id: uuid.UUID,
        requester_id: uuid.UUID,
    ) -> LinkCharacterResponse:
        """
        Link a character to a campaign.

        @param campaign_id   - UUID of the target campaign.
        @param character_id  - UUID of the character to link.
        @param requester_id  - UUID of the authenticated player.
        @returns LinkCharacterResponse (201).
        @raises CampaignNotFoundError if campaign not found.
        @raises CharacterNotFoundError if character not found or not owned.
        @raises CharacterAlreadyLinkedError if player already has a character in this campaign.
        @raises CampaignCharacterThemeMismatchError if theme does not match.
        """
        logger.info(
            "LinkCharacterUseCase.execute: campaign=%s character=%s requester=%s",
            campaign_id,
            character_id,
            requester_id,
        )

        # Fetch campaign — raises CampaignNotFoundError if not found.
        campaign = self._campaign_repo.get_by_id(campaign_id)
        if campaign is None:
            raise CampaignNotFoundError(f"Campaign {campaign_id} not found")

        # Fetch character — enforce ownership.
        character = self._character_repo.get_by_id(character_id)
        if character is None or character.owner_id != requester_id:
            raise CharacterNotFoundError(
                f"Character {character_id} not found or not owned by requester"
            )

        # Enforce one character per player per campaign.
        existing = self._character_repo.get_by_campaign_and_owner(
            campaign_id, requester_id
        )
        if existing is not None and existing.id != character_id:
            raise CharacterAlreadyLinkedError(
                "You already have a character linked to this campaign"
            )

        # A character is created for a specific world. Linking it to a campaign
        # that belongs to a different world is a theme mismatch by definition.
        if character.world_id != campaign.world_id:
            raise CampaignCharacterThemeMismatchError(
                "Character does not belong to the same world as the campaign"
            )

        # Persist the link.
        character.link_to_campaign(campaign_id)
        self._character_repo.save(character)

        now = datetime.now(tz=timezone.utc)
        logger.info(
            "LinkCharacterUseCase: linked character=%s to campaign=%s",
            character_id,
            campaign_id,
        )
        return LinkCharacterResponse(
            campaign_id=campaign_id,
            character_id=character_id,
            player_id=requester_id,
            linked_at=now,
        )


class UnlinkCharacterUseCase:
    """
    Handles DELETE /campaigns/{campaign_id}/characters/{character_id}.

    Removes the campaign link from a character.
    """

    def __init__(
        self,
        character_repo: CharacterRepository,
    ) -> None:
        self._character_repo = character_repo

    def execute(
        self,
        campaign_id: uuid.UUID,
        character_id: uuid.UUID,
        requester_id: uuid.UUID,
    ) -> None:
        """
        Unlink a character from a campaign.

        @param campaign_id   - UUID of the campaign.
        @param character_id  - UUID of the character to unlink.
        @param requester_id  - UUID of the authenticated user.
        @raises CharacterNotFoundError if character not found or not owned.
        """
        logger.info(
            "UnlinkCharacterUseCase.execute: campaign=%s character=%s requester=%s",
            campaign_id,
            character_id,
            requester_id,
        )
        character = self._character_repo.get_by_id(character_id)
        if character is None or character.owner_id != requester_id:
            raise CharacterNotFoundError(
                f"Character {character_id} not found or not owned by requester"
            )
        character.unlink_from_campaign()
        self._character_repo.save(character)
        logger.info("UnlinkCharacterUseCase: character=%s unlinked", character_id)


class GetCampaignRosterUseCase:
    """
    Handles GET /campaigns/{campaign_id}/characters (US-031).

    Returns the full party roster for a campaign. DM-only.
    """

    def __init__(
        self,
        character_repo: CharacterRepository,
        campaign_repo: CampaignRepository,
        class_repo: CharacterClassRepository,
        species_repo: CharacterSpeciesRepository,
        user_repo: UserRepository,
    ) -> None:
        self._character_repo = character_repo
        self._campaign_repo = campaign_repo
        self._class_repo = class_repo
        self._species_repo = species_repo
        self._user_repo = user_repo

    def execute(
        self, campaign_id: uuid.UUID, dm_id: uuid.UUID
    ) -> CampaignRosterResponse:
        """
        Return all characters linked to a campaign (DM only).

        @param campaign_id - UUID of the campaign.
        @param dm_id       - UUID of the authenticated DM.
        @returns CampaignRosterResponse DTO.
        @raises CampaignNotFoundError if campaign not found or not owned by DM.
        """
        logger.info(
            "GetCampaignRosterUseCase.execute: campaign=%s dm=%s",
            campaign_id,
            dm_id,
        )
        campaign = self._campaign_repo.get_by_id(campaign_id)
        if campaign is None or campaign.dm_id != dm_id:
            raise CampaignNotFoundError(f"Campaign {campaign_id} not found")

        characters = self._character_repo.list_by_campaign_id(campaign_id)
        logger.info(
            "GetCampaignRosterUseCase: found %d characters for campaign=%s",
            len(characters),
            campaign_id,
        )

        entries: list[CharacterRosterEntry] = []
        for character in characters:
            cls = self._class_repo.get_by_id(character.class_id)
            sp = self._species_repo.get_by_id(character.species_id)
            user = self._user_repo.get_by_id(character.owner_id)

            # If class or species has been deleted, skip the entry with a warning
            # rather than failing the entire roster request.
            if cls is None:
                logger.warning(
                    "GetCampaignRosterUseCase: class %s not found for character %s — skipping",
                    character.class_id,
                    character.id,
                )
                continue
            if sp is None:
                logger.warning(
                    "GetCampaignRosterUseCase: species %s not found for character %s — skipping",
                    character.species_id,
                    character.id,
                )
                continue

            player_username = user.name if user is not None else "Unknown Player"
            player_id = character.owner_id

            entries.append(
                CharacterRosterEntry.from_domain(
                    character=character,
                    character_class=cls,
                    species=sp,
                    player_id=player_id,
                    player_username=player_username,
                )
            )

        return CampaignRosterResponse(characters=entries)

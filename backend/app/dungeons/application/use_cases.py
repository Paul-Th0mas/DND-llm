"""
Application services (use cases) for the dungeons bounded context.

GenerateDungeonUseCase  — calls the narrator with World + Campaign context,
                          persists the result.
GetDungeonUseCase       — loads a single dungeon, verifies DM ownership.
ListDungeonsUseCase     — lists all dungeons for a campaign owned by the DM.

Use cases may read from sibling contexts (campaigns, worlds) to assemble
the data needed for generation. They contain no business logic — invariants
live in the domain layer.
"""

import logging
import uuid

from app.campaigns.domain.repositories import CampaignRepository
from app.dungeons.application.narrator_port import DungeonNarratorPort
from app.dungeons.application.schemas import (
    DungeonCreatedResponse,
    DungeonDetailResponse,
    DungeonSummaryResponse,
    GenerateDungeonRequest,
)
from app.dungeons.domain.exceptions import DungeonNotFoundError
from app.dungeons.domain.repositories import DungeonRepository
from app.campaigns.domain.exceptions import CampaignNotFoundError
from app.rooms.domain.repositories import RoomRepository
from app.worlds.domain.exceptions import WorldNotFoundError
from app.worlds.domain.repositories import WorldRepository

logger = logging.getLogger(__name__)


class GenerateDungeonUseCase:
    """
    Handles POST /campaigns/{campaign_id}/dungeons.

    Pipeline:
      1. Load Campaign — 404 if not found or not owned by dm_id
      2. Load World from campaign.world_id — 404 if missing
      3. Build DungeonSettings from request (validates room_count, party_size)
      4. Call narrator with World + Campaign as context
      5. Persist the Dungeon
      6. Return creation response
    """

    def __init__(
        self,
        campaign_repo: CampaignRepository,
        world_repo: WorldRepository,
        dungeon_repo: DungeonRepository,
        narrator: DungeonNarratorPort,
    ) -> None:
        self._campaign_repo = campaign_repo
        self._world_repo = world_repo
        self._dungeon_repo = dungeon_repo
        self._narrator = narrator

    def execute(
        self,
        campaign_id: uuid.UUID,
        dm_id: uuid.UUID,
        request: GenerateDungeonRequest,
    ) -> DungeonCreatedResponse:
        """
        Generate and persist a dungeon for the given campaign.

        @param campaign_id - UUID of the Campaign to generate a dungeon for.
        @param dm_id       - UUID of the authenticated DM making the request.
        @param request     - Validated inbound DTO with room_count, party_size, etc.
        @returns DungeonCreatedResponse ready for HTTP serialization.
        @raises CampaignNotFoundError if campaign does not exist or belongs to
                another DM (404 to avoid leaking existence).
        @raises WorldNotFoundError if the campaign's world is missing.
        @raises InvalidDungeonSettingsError if settings fail domain validation.
        """
        logger.info(
            "GenerateDungeonUseCase.execute: campaign_id=%s dm_id=%s rooms=%d",
            campaign_id,
            dm_id,
            request.room_count,
        )

        # Step 1: Load campaign and verify ownership
        campaign = self._campaign_repo.get_by_id(campaign_id)
        if campaign is None or campaign.dm_id != dm_id:
            logger.warning(
                "GenerateDungeonUseCase: campaign not found or wrong DM: "
                "campaign_id=%s dm_id=%s",
                campaign_id,
                dm_id,
            )
            raise CampaignNotFoundError(f"Campaign {campaign_id} not found")

        # Step 2: Load the world linked to this campaign
        world = self._world_repo.get_by_id(campaign.world_id)
        if world is None:
            logger.error(
                "GenerateDungeonUseCase: world %s not found for campaign %s",
                campaign.world_id,
                campaign_id,
            )
            raise WorldNotFoundError(
                f"World {campaign.world_id} not found for campaign {campaign_id}"
            )

        # Step 3: Build DungeonSettings (validates room_count and party_size)
        settings = request.to_domain(campaign_id)

        # Step 4: Generate via narrator (infrastructure seam)
        dungeon = self._narrator.generate_dungeon(settings, world, campaign)

        # Step 5: Persist
        self._dungeon_repo.save(dungeon)
        logger.info(
            "Dungeon generated and saved: id=%s campaign_id=%s name='%s' rooms=%d",
            dungeon.id,
            campaign_id,
            dungeon.name,
            len(dungeon.rooms),
        )

        return DungeonCreatedResponse.from_domain(dungeon)


class GetDungeonUseCase:
    """
    Handles GET /dungeons/{dungeon_id}.

    Loads the dungeon and verifies DM ownership via the linked campaign.
    Returns 404 for both missing dungeons and ownership mismatches.
    """

    def __init__(
        self,
        dungeon_repo: DungeonRepository,
        campaign_repo: CampaignRepository,
    ) -> None:
        self._dungeon_repo = dungeon_repo
        self._campaign_repo = campaign_repo

    def execute(
        self, dungeon_id: uuid.UUID, user_id: uuid.UUID
    ) -> DungeonDetailResponse:
        """
        Fetch a dungeon by ID. Any authenticated user may read dungeon detail —
        both the DM who created it and players participating in the room.

        Ownership is verified only to the extent that the parent campaign must
        exist (guards against orphaned data). Role-based restrictions are not
        applied here because players legitimately need dungeon content during a
        session (US-010).

        @param dungeon_id - UUID of the dungeon to fetch.
        @param user_id    - UUID of the authenticated user making the request.
        @returns DungeonDetailResponse ready for HTTP serialization.
        @raises DungeonNotFoundError if the dungeon or its parent campaign is missing.
        """
        logger.debug(
            "GetDungeonUseCase.execute: dungeon_id=%s user_id=%s",
            dungeon_id,
            user_id,
        )
        dungeon = self._dungeon_repo.get_by_id(dungeon_id)
        if dungeon is None:
            raise DungeonNotFoundError(f"Dungeon {dungeon_id} not found")

        # Confirm the parent campaign still exists (guards orphaned dungeon rows).
        # We do NOT restrict by campaign.dm_id — players need read access too.
        campaign = self._campaign_repo.get_by_id(dungeon.campaign_id)
        if campaign is None:
            logger.warning(
                "GetDungeonUseCase: dungeon %s has no parent campaign", dungeon_id
            )
            raise DungeonNotFoundError(f"Dungeon {dungeon_id} not found")

        return DungeonDetailResponse.from_domain(dungeon)


class ListDungeonsUseCase:
    """
    Handles GET /campaigns/{campaign_id}/dungeons.

    Returns all dungeons for a campaign owned by the requesting DM, newest first.
    Each summary includes the most recently created room linked to that dungeon
    (if any) so the frontend can display Active / Closed / No Room status without
    additional API calls (US-014).
    """

    def __init__(
        self,
        dungeon_repo: DungeonRepository,
        campaign_repo: CampaignRepository,
        room_repo: RoomRepository,
    ) -> None:
        self._dungeon_repo = dungeon_repo
        self._campaign_repo = campaign_repo
        # room_repo is used only for cross-context reads — we call it through
        # the abstract RoomRepository interface so the dungeons context never
        # imports rooms infrastructure (ORM, SQLAlchemy).
        self._room_repo = room_repo

    def execute(
        self, campaign_id: uuid.UUID, dm_id: uuid.UUID
    ) -> list[DungeonSummaryResponse]:
        """
        List all dungeons for a campaign owned by the given DM.

        For each dungeon, performs one additional query to find its linked room.
        One query per dungeon is acceptable at current scale (campaigns typically
        have fewer than 20 dungeons).

        @param campaign_id - UUID of the campaign.
        @param dm_id       - UUID of the authenticated DM.
        @returns List of DungeonSummaryResponse DTOs with embedded room status.
        @raises CampaignNotFoundError if campaign not found or not owned by DM.
        """
        logger.debug(
            "ListDungeonsUseCase.execute: campaign_id=%s dm_id=%s",
            campaign_id,
            dm_id,
        )
        campaign = self._campaign_repo.get_by_id(campaign_id)
        if campaign is None or campaign.dm_id != dm_id:
            raise CampaignNotFoundError(f"Campaign {campaign_id} not found")

        dungeons = self._dungeon_repo.list_by_campaign_id(campaign_id)
        logger.info(
            "ListDungeonsUseCase: found %d dungeons for campaign_id=%s",
            len(dungeons),
            campaign_id,
        )
        result = []
        for dungeon in dungeons:
            # Look up the most recently created room for this dungeon.
            room = self._room_repo.get_by_dungeon_id(dungeon.id)
            result.append(DungeonSummaryResponse.from_domain(dungeon, room=room))
        return result

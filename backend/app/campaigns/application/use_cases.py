"""
Application services (use cases) for the campaigns bounded context.

CreateCampaignUseCase  — stores the DM's campaign requirements.
GetCampaignUseCase     — loads a single campaign owned by the DM.
ListCampaignsUseCase   — lists all campaigns owned by the DM.

Use cases orchestrate domain objects and repositories. They contain no
business logic — invariants live in the domain aggregates.
"""

import logging
import uuid

from app.campaigns.application.schemas import (
    CampaignDetailResponse,
    CampaignResponse,
    CampaignSummaryResponse,
    CreateCampaignRequest,
)
from app.campaigns.domain.exceptions import CampaignNotFoundError
from app.campaigns.domain.repositories import CampaignRepository

# Cross-context repository interfaces — abstract ABCs only, no ORM imports.
from app.dungeons.domain.repositories import DungeonRepository
from app.worlds.domain.repositories import WorldRepository

logger = logging.getLogger(__name__)


class CreateCampaignUseCase:
    """
    Handles POST /campaigns.

    Converts the request DTO to a Campaign aggregate, persists it, and
    returns the summary response with the next-step URL for dungeon generation.
    """

    def __init__(self, repo: CampaignRepository) -> None:
        self._repo = repo

    def execute(
        self, request: CreateCampaignRequest, dm_id: uuid.UUID
    ) -> CampaignResponse:
        """
        Create and persist a new Campaign.

        @param request - Validated inbound Pydantic DTO (includes world_id).
        @param dm_id   - UUID of the authenticated DM creating this campaign.
        @returns CampaignResponse ready for HTTP serialization.
        @raises InvalidCampaignError if domain validation fails.
        """
        logger.info(
            "CreateCampaignUseCase.execute: name='%s' dm_id=%s world_id=%s",
            request.campaign_name,
            dm_id,
            request.world_id,
        )
        # to_domain() calls Campaign.create() which enforces invariants
        campaign = request.to_domain(dm_id)
        self._repo.save(campaign)
        logger.info("Campaign saved: id=%s world_id=%s", campaign.id, campaign.world_id)
        return CampaignResponse.from_domain(campaign)


class GetCampaignUseCase:
    """
    Handles GET /campaigns/{id}.

    Loads a campaign by ID and verifies the requesting DM owns it.
    Returns 404 for both missing and foreign campaigns to avoid leaking existence.
    """

    def __init__(self, repo: CampaignRepository) -> None:
        self._repo = repo

    def execute(
        self, campaign_id: uuid.UUID, dm_id: uuid.UUID
    ) -> CampaignDetailResponse:
        """
        Fetch a campaign owned by the given DM.

        @param campaign_id - UUID of the campaign to fetch.
        @param dm_id       - UUID of the authenticated DM making the request.
        @returns CampaignDetailResponse ready for HTTP serialization.
        @raises CampaignNotFoundError if not found or owned by a different DM.
        """
        logger.debug("GetCampaignUseCase.execute: campaign_id=%s", campaign_id)
        campaign = self._repo.get_by_id(campaign_id)
        if campaign is None or campaign.dm_id != dm_id:
            raise CampaignNotFoundError(f"Campaign {campaign_id} not found")
        return CampaignDetailResponse.from_domain(campaign)


class ListCampaignsUseCase:
    """
    Handles GET /campaigns.

    Returns all campaigns owned by the requesting DM, newest first.
    Each summary embeds the world name and dungeon count (US-018) so the
    campaign hub page can render cards without additional API round-trips.
    """

    def __init__(
        self,
        repo: CampaignRepository,
        world_repo: WorldRepository,
        dungeon_repo: DungeonRepository,
    ) -> None:
        self._repo = repo
        # world_repo and dungeon_repo are abstract interfaces — the campaigns
        # context reads through them without importing worlds/dungeons ORM code.
        self._world_repo = world_repo
        self._dungeon_repo = dungeon_repo

    def execute(self, dm_id: uuid.UUID) -> list[CampaignSummaryResponse]:
        """
        List all campaigns for the given DM with embedded world name and
        dungeon count.

        For each campaign:
          - Calls world_repo.get_by_id to resolve the world name. Passes
            world_name=None if the world has been deleted.
          - Calls dungeon_repo.list_by_campaign_id and counts the results.

        One query per campaign for world and dungeon lookups is acceptable at
        current scale (DMs typically own fewer than 20 campaigns).

        @param dm_id - UUID of the authenticated DM.
        @returns List of CampaignSummaryResponse DTOs with embedded enrichment.
        """
        logger.debug("ListCampaignsUseCase.execute: dm_id=%s", dm_id)
        campaigns = self._repo.list_by_dm_id(dm_id)
        logger.info("Listed %d campaigns for dm_id=%s", len(campaigns), dm_id)

        result: list[CampaignSummaryResponse] = []
        for campaign in campaigns:
            # Resolve world name — warn (not error) if world was deleted.
            world = self._world_repo.get_by_id(campaign.world_id)
            if world is None:
                logger.warning(
                    "ListCampaignsUseCase: world %s not found for campaign %s",
                    campaign.world_id,
                    campaign.id,
                )
                world_name: str | None = None
            else:
                world_name = world.name

            # Count dungeons generated for this campaign.
            dungeons = self._dungeon_repo.list_by_campaign_id(campaign.id)
            dungeon_count = len(dungeons)
            logger.debug(
                "ListCampaignsUseCase: campaign %s world_name=%s dungeon_count=%d",
                campaign.id,
                world_name,
                dungeon_count,
            )

            result.append(
                CampaignSummaryResponse.from_domain(
                    campaign,
                    world_name=world_name,
                    dungeon_count=dungeon_count,
                )
            )
        return result

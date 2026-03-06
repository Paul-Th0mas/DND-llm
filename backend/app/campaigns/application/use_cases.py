"""
Application services (use cases) for the campaigns bounded context.

CreateCampaignUseCase         — stores the DM's campaign requirements.
GenerateCampaignWorldUseCase  — calls the narrator and saves the world.

Use cases orchestrate domain objects and repositories. They contain no
business logic — invariants live in the domain aggregates.
"""

import logging
import uuid

from app.campaigns.application.narrator_port import CampaignNarratorPort
from app.campaigns.application.schemas import (
    CampaignResponse,
    CreateCampaignRequest,
    GenerateCampaignWorldResponse,
)
from app.campaigns.domain.exceptions import CampaignNotFoundError
from app.campaigns.domain.repositories import (
    CampaignRepository,
    CampaignWorldRepository,
)

logger = logging.getLogger(__name__)


class CreateCampaignUseCase:
    """
    Handles POST /campaigns.

    Converts the request DTO to a Campaign aggregate, persists it, and
    returns the summary response with the next-step URL.
    """

    def __init__(self, repo: CampaignRepository) -> None:
        self._repo = repo

    def execute(
        self, request: CreateCampaignRequest, dm_id: uuid.UUID
    ) -> CampaignResponse:
        """
        Create and persist a new Campaign.

        @param request - Validated inbound Pydantic DTO.
        @param dm_id   - UUID of the authenticated DM creating this campaign.
        @returns CampaignResponse ready for HTTP serialization.
        @raises InvalidCampaignError if domain validation fails.
        """
        logger.info(
            "CreateCampaignUseCase.execute: name='%s' dm_id=%s",
            request.campaign_name,
            dm_id,
        )
        # to_domain() calls Campaign.create() which enforces invariants
        campaign = request.to_domain(dm_id)
        self._repo.save(campaign)
        logger.info("Campaign saved: id=%s", campaign.id)
        return CampaignResponse.from_domain(campaign)


class GenerateCampaignWorldUseCase:
    """
    Handles POST /campaigns/{id}/world.

    Loads the campaign, calls the narrator to generate a world, persists both,
    and returns the world summary response.
    """

    def __init__(
        self,
        campaign_repo: CampaignRepository,
        world_repo: CampaignWorldRepository,
        narrator: CampaignNarratorPort,
    ) -> None:
        self._campaign_repo = campaign_repo
        self._world_repo = world_repo
        self._narrator = narrator

    def execute(
        self,
        campaign_id: uuid.UUID,
        dm_id: uuid.UUID,
    ) -> GenerateCampaignWorldResponse:
        """
        Generate and persist a world for the given campaign.

        The requesting DM must be the one who created the campaign — the
        same ID check that prevents DMs from generating worlds for other DMs'
        campaigns. We reuse CampaignNotFoundError (→ 404) rather than a 403
        so we don't reveal whether a campaign exists.

        @param campaign_id - UUID of the Campaign to generate a world for.
        @param dm_id       - UUID of the authenticated DM making the request.
        @returns GenerateCampaignWorldResponse ready for HTTP serialization.
        @raises CampaignNotFoundError if the campaign does not exist or belongs
                to a different DM.
        @raises InvalidCampaignError if a world is already attached.
        """
        logger.info(
            "GenerateCampaignWorldUseCase.execute: campaign_id=%s dm_id=%s",
            campaign_id,
            dm_id,
        )

        # Step 1: Load the campaign
        campaign = self._campaign_repo.get_by_id(campaign_id)
        if campaign is None:
            raise CampaignNotFoundError(f"Campaign {campaign_id} not found")

        # Step 2: Verify ownership — return 404 not 403 to avoid leaking existence
        if campaign.dm_id != dm_id:
            logger.warning(
                "DM %s attempted to generate world for campaign %s owned by DM %s",
                dm_id,
                campaign_id,
                campaign.dm_id,
            )
            raise CampaignNotFoundError(f"Campaign {campaign_id} not found")

        # Step 3: Generate world via narrator (infrastructure seam)
        world = self._narrator.generate_world(campaign)

        # Step 4: Persist world, then link campaign → world (order matters:
        # world must exist before campaign FK is set)
        self._world_repo.save(world)
        campaign.attach_world(world.world_id)
        self._campaign_repo.save(campaign)

        logger.info(
            "Campaign world generated: campaign_id=%s world_id=%s world_name=%s",
            campaign_id,
            world.world_id,
            world.world_name,
        )
        return GenerateCampaignWorldResponse.from_domain(world)

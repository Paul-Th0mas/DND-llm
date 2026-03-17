"""
Pydantic DTOs for the campaigns bounded context.

These are Data Transfer Objects — they live at the application layer boundary
between the API (HTTP) and the domain. They are NOT domain models.

Inbound:  CreateCampaignRequest  → converted to Campaign domain aggregate
Outbound: CampaignResponse       ← converted from Campaign domain aggregate
          CampaignDetailResponse ← full campaign detail
          CampaignSummaryResponse ← list item
"""

import logging
import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.campaigns.domain.models import (
    LEVEL_MAX,
    LEVEL_MIN,
    PLAYER_COUNT_MAX,
    PLAYER_COUNT_MIN,
    Campaign,
    CampaignTone,
    ContentBoundaries,
    LevelRange,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Inbound DTOs
# ---------------------------------------------------------------------------


class LevelRangeRequest(BaseModel):
    """Inbound representation of a campaign level range."""

    start: int = Field(ge=LEVEL_MIN, le=LEVEL_MAX)
    end: int = Field(ge=LEVEL_MIN, le=LEVEL_MAX)


class ContentBoundariesRequest(BaseModel):
    """Inbound representation of campaign content boundaries (Lines only)."""

    lines: list[str] = Field(default_factory=list)


class CreateCampaignRequest(BaseModel):
    """
    Inbound DTO for POST /campaigns.

    world_id is required — DM must select a world before creating a campaign.
    Pydantic enforces field-level constraints; domain-level invariants
    (e.g. start <= end for level_range) are enforced in the domain models
    after to_domain() is called.
    """

    campaign_name: str = Field(min_length=1, max_length=200)
    world_id: uuid.UUID
    edition: str = Field(default="5e-2024", max_length=20)
    tone: CampaignTone
    player_count: int = Field(ge=PLAYER_COUNT_MIN, le=PLAYER_COUNT_MAX)
    level_range: LevelRangeRequest
    themes: list[str] = Field(default_factory=list, max_length=10)
    content_boundaries: ContentBoundariesRequest = Field(
        default_factory=ContentBoundariesRequest
    )

    def to_domain(self, dm_id: uuid.UUID) -> Campaign:
        """Convert this request DTO into a Campaign aggregate."""
        logger.debug(
            "Converting CreateCampaignRequest to domain: name='%s' dm_id=%s world_id=%s",
            self.campaign_name,
            dm_id,
            self.world_id,
        )
        level_range = LevelRange(
            start=self.level_range.start,
            end=self.level_range.end,
        )
        boundaries = ContentBoundaries(
            lines=tuple(self.content_boundaries.lines),
        )
        return Campaign.create(
            name=self.campaign_name,
            edition=self.edition,
            tone=self.tone,
            player_count=self.player_count,
            level_range=level_range,
            themes=tuple(self.themes),
            content_boundaries=boundaries,
            dm_id=dm_id,
            world_id=self.world_id,
        )


# ---------------------------------------------------------------------------
# Outbound DTOs
# ---------------------------------------------------------------------------


class CampaignResponse(BaseModel):
    """
    Outbound DTO for POST /campaigns.

    Returns the new campaign ID and the URL for the next step — dungeon
    generation — following the pipeline design from the architecture spec.
    """

    campaign_id: uuid.UUID
    status: str
    next_step: str

    @classmethod
    def from_domain(cls, campaign: Campaign) -> "CampaignResponse":
        """Convert a Campaign aggregate into this response DTO."""
        return cls(
            campaign_id=campaign.id,
            status="created",
            next_step=f"/api/v1/campaigns/{campaign.id}/dungeons",
        )


class LevelRangeResponse(BaseModel):
    """Outbound representation of a campaign level range."""

    start: int
    end: int


class ContentBoundariesResponse(BaseModel):
    """Outbound representation of campaign content boundaries."""

    lines: list[str]


class CampaignDetailResponse(BaseModel):
    """
    Full campaign detail for GET /campaigns/{id}.

    Returns all stored fields so the frontend can display the campaign
    requirements alongside the world it was built against.
    """

    campaign_id: uuid.UUID
    name: str
    edition: str
    tone: str
    player_count: int
    level_range: LevelRangeResponse
    themes: list[str]
    content_boundaries: ContentBoundariesResponse
    dm_id: uuid.UUID
    world_id: uuid.UUID
    created_at: datetime

    @classmethod
    def from_domain(cls, campaign: Campaign) -> "CampaignDetailResponse":
        """Convert a Campaign aggregate into this detailed response DTO."""
        return cls(
            campaign_id=campaign.id,
            name=campaign.name,
            edition=campaign.edition,
            tone=campaign.tone.value,
            player_count=campaign.player_count,
            level_range=LevelRangeResponse(
                start=campaign.level_range.start,
                end=campaign.level_range.end,
            ),
            themes=list(campaign.themes),
            content_boundaries=ContentBoundariesResponse(
                lines=list(campaign.content_boundaries.lines),
            ),
            dm_id=campaign.dm_id,
            world_id=campaign.world_id,
            created_at=campaign.created_at,
        )


class CampaignSummaryResponse(BaseModel):
    """
    Minimal campaign entry for GET /campaigns list.

    Used in list responses where the full detail is not needed.
    Extended (US-018) to embed world_name and dungeon_count so the campaign
    hub can render cards without N+1 API calls from the frontend.
    """

    campaign_id: uuid.UUID
    name: str
    tone: str
    player_count: int
    world_id: uuid.UUID
    # world_name is null when the linked world has been deleted by an admin.
    world_name: str | None
    # dungeon_count is 0 when no dungeons have been generated for this campaign.
    dungeon_count: int
    created_at: datetime

    @classmethod
    def from_domain(
        cls,
        campaign: Campaign,
        *,
        world_name: str | None,
        dungeon_count: int,
    ) -> "CampaignSummaryResponse":
        """
        Convert a Campaign aggregate into a summary DTO.

        @param campaign      - The Campaign aggregate to convert.
        @param world_name    - The name of the linked world, or None if deleted.
        @param dungeon_count - Number of dungeons generated for this campaign.
        """
        return cls(
            campaign_id=campaign.id,
            name=campaign.name,
            tone=campaign.tone.value,
            player_count=campaign.player_count,
            world_id=campaign.world_id,
            world_name=world_name,
            dungeon_count=dungeon_count,
            created_at=campaign.created_at,
        )

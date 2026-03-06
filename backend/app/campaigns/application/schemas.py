"""
Pydantic DTOs for the campaigns bounded context.

These are Data Transfer Objects — they live at the application layer boundary
between the API (HTTP) and the domain. They are NOT domain models.

Inbound:  CreateCampaignRequest  → converted to Campaign domain aggregate
Outbound: CampaignResponse       ← converted from Campaign domain aggregate
          GenerateCampaignWorldResponse ← converted from CampaignWorld aggregate
"""

import logging
import uuid

from pydantic import BaseModel, Field

from app.campaigns.domain.models import (
    LEVEL_MAX,
    LEVEL_MIN,
    PLAYER_COUNT_MAX,
    PLAYER_COUNT_MIN,
    SESSION_COUNT_MAX,
    SESSION_COUNT_MIN,
    Campaign,
    CampaignTone,
    ContentBoundaries,
    LevelRange,
    SettingPreference,
)
from app.campaigns.domain.world_models import (
    AdventureHook,
    CampaignWorld,
    Settlement,
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
    """Inbound representation of campaign content boundaries (Lines & Veils)."""

    lines: list[str] = Field(default_factory=list)
    veils: list[str] = Field(default_factory=list)


class CreateCampaignRequest(BaseModel):
    """
    Inbound DTO for POST /campaigns.

    Captures all DM requirements for a new campaign. Pydantic enforces
    field-level constraints; domain-level invariants (e.g. start <= end for
    level_range) are enforced in the domain models after to_domain() is called.
    """

    campaign_name: str = Field(min_length=1, max_length=200)
    edition: str = Field(default="5e-2024", max_length=20)
    tone: CampaignTone
    player_count: int = Field(ge=PLAYER_COUNT_MIN, le=PLAYER_COUNT_MAX)
    level_range: LevelRangeRequest
    session_count_estimate: int = Field(ge=SESSION_COUNT_MIN, le=SESSION_COUNT_MAX)
    setting_preference: SettingPreference = SettingPreference.HOMEBREW
    themes: list[str] = Field(default_factory=list, max_length=10)
    content_boundaries: ContentBoundariesRequest = Field(
        default_factory=ContentBoundariesRequest
    )
    homebrew_rules: list[str] = Field(default_factory=list, max_length=20)
    inspirations: str | None = None

    def to_domain(self, dm_id: uuid.UUID) -> Campaign:
        """Convert this request DTO into a Campaign aggregate."""
        logger.debug(
            "Converting CreateCampaignRequest to domain: name='%s' dm_id=%s",
            self.campaign_name,
            dm_id,
        )
        level_range = LevelRange(
            start=self.level_range.start,
            end=self.level_range.end,
        )
        boundaries = ContentBoundaries(
            lines=tuple(self.content_boundaries.lines),
            veils=tuple(self.content_boundaries.veils),
        )
        return Campaign.create(
            name=self.campaign_name,
            edition=self.edition,
            tone=self.tone,
            player_count=self.player_count,
            level_range=level_range,
            session_count_estimate=self.session_count_estimate,
            setting_preference=self.setting_preference,
            themes=tuple(self.themes),
            content_boundaries=boundaries,
            homebrew_rules=tuple(self.homebrew_rules),
            inspirations=self.inspirations,
            dm_id=dm_id,
        )


# ---------------------------------------------------------------------------
# Outbound DTOs
# ---------------------------------------------------------------------------


class CampaignResponse(BaseModel):
    """
    Outbound DTO for POST /campaigns.

    Returns the new campaign ID, its status, and the URL for the next step
    (world generation), following the API design from the pipeline spec.
    """

    campaign_id: uuid.UUID
    status: str
    next_step: str

    @classmethod
    def from_domain(cls, campaign: Campaign) -> "CampaignResponse":
        """Convert a Campaign aggregate into this response DTO."""
        return cls(
            campaign_id=campaign.id,
            status="requirements_captured",
            next_step=f"/api/v1/campaigns/{campaign.id}/world",
        )


class SettlementResponse(BaseModel):
    """Output DTO for the starting settlement within a campaign world."""

    name: str
    population: int
    governance: str
    description: str

    @classmethod
    def from_domain(cls, settlement: Settlement) -> "SettlementResponse":
        """Convert a Settlement value object into this response DTO."""
        return cls(
            name=settlement.name,
            population=settlement.population,
            governance=settlement.governance,
            description=settlement.description,
        )


class AdventureHookResponse(BaseModel):
    """Output DTO for a single adventure hook."""

    pillar: str
    hook: str
    connected_npc: str | None

    @classmethod
    def from_domain(cls, hook: AdventureHook) -> "AdventureHookResponse":
        """Convert an AdventureHook value object into this response DTO."""
        return cls(
            pillar=hook.pillar,
            hook=hook.hook,
            connected_npc=hook.connected_npc,
        )


class GenerateCampaignWorldResponse(BaseModel):
    """
    Outbound DTO for POST /campaigns/{id}/world.

    Returns a summary of the generated world. The full world data (NPCs,
    factions, hidden agendas) is stored in the database and served via
    separate endpoints in later pipeline steps.
    """

    world_id: uuid.UUID
    world_name: str
    premise: str
    starting_settlement: SettlementResponse
    npcs_generated: int
    factions_generated: int
    hooks_generated: int

    @classmethod
    def from_domain(cls, world: CampaignWorld) -> "GenerateCampaignWorldResponse":
        """Convert a CampaignWorld aggregate into this response DTO."""
        logger.debug(
            "Converting CampaignWorld to response DTO: world_id=%s name=%s",
            world.world_id,
            world.world_name,
        )
        return cls(
            world_id=world.world_id,
            world_name=world.world_name,
            premise=world.premise,
            starting_settlement=SettlementResponse.from_domain(
                world.starting_settlement
            ),
            npcs_generated=len(world.key_npcs),
            factions_generated=len(world.factions),
            hooks_generated=len(world.adventure_hooks),
        )

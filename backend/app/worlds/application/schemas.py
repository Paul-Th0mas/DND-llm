"""
Pydantic DTOs for the worlds bounded context.

These are Data Transfer Objects — they live at the application layer boundary
between the API (HTTP) and the domain. They are NOT domain models.

Outbound:
  WorldSummaryResponse  — used for GET /worlds (list, no factions/bosses)
  WorldDetailResponse   — used for GET /worlds/{id} (full detail)

hidden_agenda on factions is intentionally excluded from all response schemas.
It is DM-only lore stored in the domain but never surfaced to the API.
"""

import logging
import uuid

from pydantic import BaseModel

from app.worlds.domain.models import PresetBoss, PresetFaction, Theme, World

logger = logging.getLogger(__name__)


class PresetFactionResponse(BaseModel):
    """
    Outbound DTO for a single faction.

    hidden_agenda is omitted — DM-facing detail available only in
    the narrative context passed to the LLM narrator.
    """

    name: str
    description: str
    alignment: str
    public_reputation: str

    @classmethod
    def from_domain(cls, faction: PresetFaction) -> "PresetFactionResponse":
        """Convert a PresetFaction domain value object into this response DTO."""
        return cls(
            name=faction.name,
            description=faction.description,
            alignment=faction.alignment,
            public_reputation=faction.public_reputation,
        )


class PresetBossResponse(BaseModel):
    """Outbound DTO for a single preset boss."""

    name: str
    description: str
    challenge_rating: str
    abilities: list[str]
    lore: str

    @classmethod
    def from_domain(cls, boss: PresetBoss) -> "PresetBossResponse":
        """Convert a PresetBoss domain value object into this response DTO."""
        return cls(
            name=boss.name,
            description=boss.description,
            challenge_rating=boss.challenge_rating,
            abilities=list(boss.abilities),
            lore=boss.lore,
        )


class WorldSummaryResponse(BaseModel):
    """
    Outbound DTO for GET /worlds (list view).

    Returns only the fields needed for a DM to choose a world.
    Factions and bosses are excluded — see WorldDetailResponse for full data.
    """

    world_id: uuid.UUID
    name: str
    theme: Theme
    description: str

    @classmethod
    def from_domain(cls, world: World) -> "WorldSummaryResponse":
        """Convert a World aggregate into a summary response DTO."""
        logger.debug(
            "WorldSummaryResponse.from_domain: id=%s name='%s'", world.id, world.name
        )
        return cls(
            world_id=world.id,
            name=world.name,
            theme=world.theme,
            description=world.description,
        )


class WorldDetailResponse(BaseModel):
    """
    Outbound DTO for GET /worlds/{world_id} (detail view).

    Includes full faction and boss lists for DM review before campaign creation.
    """

    world_id: uuid.UUID
    name: str
    theme: Theme
    description: str
    lore_summary: str
    factions: list[PresetFactionResponse]
    bosses: list[PresetBossResponse]

    @classmethod
    def from_domain(cls, world: World) -> "WorldDetailResponse":
        """Convert a World aggregate into a full detail response DTO."""
        logger.debug(
            "WorldDetailResponse.from_domain: id=%s name='%s'", world.id, world.name
        )
        return cls(
            world_id=world.id,
            name=world.name,
            theme=world.theme,
            description=world.description,
            lore_summary=world.lore_summary,
            factions=[PresetFactionResponse.from_domain(f) for f in world.factions],
            bosses=[PresetBossResponse.from_domain(b) for b in world.bosses],
        )

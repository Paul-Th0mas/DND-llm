"""
Application services (use cases) for the worlds bounded context.

Each class handles exactly one use case. Use cases orchestrate the repository
and schema conversion but contain no business logic — invariants live in the
domain layer.
"""

import logging
import uuid

from app.worlds.application.schemas import WorldDetailResponse, WorldSummaryResponse
from app.worlds.domain.exceptions import WorldNotFoundError
from app.worlds.domain.repositories import WorldRepository

logger = logging.getLogger(__name__)


class GetWorldsUseCase:
    """
    Returns a summary list of all active worlds.

    Used to populate the world selection screen when a DM creates a campaign.
    """

    def __init__(self, repo: WorldRepository) -> None:
        self._repo = repo

    def execute(self) -> list[WorldSummaryResponse]:
        """
        Fetch all active worlds and return summary DTOs.

        @returns A list of WorldSummaryResponse — may be empty if no worlds are seeded.
        """
        logger.info("GetWorldsUseCase.execute")
        worlds = self._repo.get_all_active()
        logger.info("GetWorldsUseCase: returning %d worlds", len(worlds))
        return [WorldSummaryResponse.from_domain(w) for w in worlds]


class GetWorldByIdUseCase:
    """
    Returns the full detail of a single world by id.

    Used on the world detail screen before a DM commits to creating a campaign.
    """

    def __init__(self, repo: WorldRepository) -> None:
        self._repo = repo

    def execute(self, world_id: uuid.UUID) -> WorldDetailResponse:
        """
        Fetch one world by id and return the full detail DTO.

        @param world_id - The UUID of the world to fetch.
        @returns WorldDetailResponse with factions and bosses.
        @raises WorldNotFoundError if the world does not exist or is inactive.
        """
        logger.info("GetWorldByIdUseCase.execute: world_id=%s", world_id)
        world = self._repo.get_by_id(world_id)
        if world is None or not world.is_active:
            logger.warning("GetWorldByIdUseCase: world not found id=%s", world_id)
            raise WorldNotFoundError(f"World {world_id} not found")
        return WorldDetailResponse.from_domain(world)

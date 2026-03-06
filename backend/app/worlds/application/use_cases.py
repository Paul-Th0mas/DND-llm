"""
Application services (use cases) for the worlds bounded context.

Each class handles exactly one use case. Use cases orchestrate the narrator
port and domain objects but contain no business logic — invariants live in
the domain layer (WorldSettings.validate).
"""

import logging

from app.worlds.application.narrator_port import NarratorPort
from app.worlds.application.schemas import GeneratedWorldResponse, WorldSettingsRequest

logger = logging.getLogger(__name__)


class GenerateWorldUseCase:
    """
    Orchestrates world generation from a DM's settings request.

    Flow:
      1. Convert request DTO → domain value object (WorldSettings)
      2. Ask the domain to validate its own invariants
      3. Delegate generation to the NarratorPort (infrastructure seam)
      4. Convert the domain aggregate → response DTO

    The use case never contains business logic. It is a coordinator only.
    """

    def __init__(self, narrator: NarratorPort) -> None:
        self._narrator = narrator

    def execute(self, request: WorldSettingsRequest) -> GeneratedWorldResponse:
        """
        Run the world generation pipeline.

        @param request - Validated inbound Pydantic DTO from the router.
        @returns GeneratedWorldResponse ready for HTTP serialization.
        @raises InvalidWorldSettingsError if domain validation fails.
        """
        logger.info(
            "GenerateWorldUseCase.execute: theme=%s difficulty=%s rooms=%d",
            request.theme,
            request.difficulty,
            request.room_count,
        )

        # Step 1: Convert DTO → domain value object
        settings = request.to_domain()

        # Step 2: Let the domain enforce its invariants
        settings.validate()

        # Step 3: Generate the world via the narrator (infrastructure seam)
        world = self._narrator.generate_world(settings)

        logger.info(
            "World generated: name=%s rooms=%d",
            world.world_name,
            len(world.rooms),
        )

        # Step 4: Convert domain aggregate → response DTO
        return GeneratedWorldResponse.from_domain(world)

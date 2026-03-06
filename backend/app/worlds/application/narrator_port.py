"""
NarratorPort — the application-layer interface for world narration.

This is the seam between the application layer (use cases) and the
infrastructure layer (LLM clients, stub narrators, etc.).

By depending on this ABC, GenerateWorldUseCase never imports any LLM SDK
or sees any HTTP client. Infrastructure implements the interface; the
application layer stays pure.

Dependency rule: application → domain. Never application → infrastructure.
"""

import logging
from abc import ABC, abstractmethod

from app.worlds.domain.models import GeneratedWorld, WorldSettings

logger = logging.getLogger(__name__)


class NarratorPort(ABC):
    """
    Abstract narrator interface.

    Any class that generates a world must implement this port.
    Current implementations:
      - StubNarrator  (infrastructure/narrator.py) — deterministic template output
    Future implementations:
      - ClaudeNarrator — real LLM call via Anthropic SDK
    """

    @abstractmethod
    def generate_world(self, settings: WorldSettings) -> GeneratedWorld:
        """
        Generate a complete world from the given settings.

        @param settings - Validated WorldSettings value object from the domain.
        @returns A fully populated GeneratedWorld aggregate.
        """
        ...

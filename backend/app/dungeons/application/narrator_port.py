"""
DungeonNarratorPort — the application-layer interface for dungeon generation.

This is the seam between the application layer (use cases) and the
infrastructure layer (LLM clients, stub narrators, etc.).

The narrator receives both the World (lore, factions, bosses) and Campaign
(tone, themes, level_range, content_boundaries) so it has full context for
producing narratively consistent dungeon content.

Dependency rule: application → domain. Never application → infrastructure.
Importing World and Campaign from sibling contexts is allowed at the
application layer in a monolith — dungeons orchestrate data from both.
"""

import logging
from abc import ABC, abstractmethod

from app.campaigns.domain.models import Campaign
from app.dungeons.domain.models import Dungeon, DungeonSettings
from app.worlds.domain.models import World

logger = logging.getLogger(__name__)


class DungeonNarratorPort(ABC):
    """
    Abstract narrator interface for dungeon generation.

    Any class that generates a dungeon must implement this port.
    Implementations:
      - StubDungeonNarrator  — deterministic template output, keyed by CampaignTone
      - GeminiDungeonNarrator — calls Gemini API with world + campaign context
    """

    @abstractmethod
    def generate_dungeon(
        self,
        settings: DungeonSettings,
        world: World,
        campaign: Campaign,
    ) -> Dungeon:
        """
        Generate a complete dungeon from the given context.

        @param settings  - Validated DungeonSettings (room_count, party_size, notes).
        @param world     - The admin-seeded World with lore, factions, and bosses.
        @param campaign  - The Campaign with tone, themes, and content boundaries.
        @returns A fully populated Dungeon aggregate ready for persistence.
        """
        ...

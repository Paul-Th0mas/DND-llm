"""
Port (interface) for campaign world narration.

The application layer depends on this ABC; the infrastructure layer provides
the concrete implementation (StubCampaignNarrator, or a future LLM narrator).
Swap the implementation in api/dependencies.py — no other files change.
"""

import abc

from app.campaigns.domain.models import Campaign
from app.campaigns.domain.world_models import CampaignWorld


class CampaignNarratorPort(abc.ABC):
    """
    Generates a D&D 5e world from a Campaign's requirements.

    Implementations may call a stub template, a local LLM, or an external
    API (OpenAI, Gemini, Anthropic). The use case only sees this interface.
    """

    @abc.abstractmethod
    def generate_world(self, campaign: Campaign) -> CampaignWorld:
        """
        Generate a CampaignWorld from the given Campaign requirements.

        @param campaign - The Campaign aggregate with DM requirements.
        @returns A fully populated CampaignWorld ready for persistence.
        """

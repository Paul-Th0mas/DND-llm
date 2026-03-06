"""
Abstract repository interfaces for the campaigns bounded context.

The domain defines the interface; the infrastructure layer implements it.
This keeps the domain free of SQLAlchemy — only pure Python ABCs here.
"""

import abc
import uuid

from app.campaigns.domain.models import Campaign
from app.campaigns.domain.world_models import CampaignWorld


class CampaignRepository(abc.ABC):
    """Persistence interface for Campaign aggregates."""

    @abc.abstractmethod
    def save(self, campaign: Campaign) -> None:
        """Insert or update a Campaign in the store."""

    @abc.abstractmethod
    def get_by_id(self, campaign_id: uuid.UUID) -> Campaign | None:
        """Return a Campaign by its UUID, or None if not found."""


class CampaignWorldRepository(abc.ABC):
    """Persistence interface for CampaignWorld aggregates."""

    @abc.abstractmethod
    def save(self, world: CampaignWorld) -> None:
        """Insert or update a CampaignWorld in the store."""

    @abc.abstractmethod
    def get_by_campaign_id(self, campaign_id: uuid.UUID) -> CampaignWorld | None:
        """Return the world linked to a campaign, or None if not generated yet."""

"""
Abstract repository interface for the campaigns bounded context.

The domain defines what it needs from persistence. The infrastructure layer
implements it. This keeps the domain free of any SQLAlchemy dependency.
"""

import abc
import uuid

from app.campaigns.domain.models import Campaign


class CampaignRepository(abc.ABC):
    """Persistence interface for Campaign aggregates."""

    @abc.abstractmethod
    def save(self, campaign: Campaign) -> None:
        """
        Insert or update a Campaign in the store.

        @param campaign - The Campaign aggregate to persist.
        """

    @abc.abstractmethod
    def get_by_id(self, campaign_id: uuid.UUID) -> Campaign | None:
        """
        Return a Campaign by its UUID, or None if not found.

        @param campaign_id - The UUID of the campaign to fetch.
        """

    @abc.abstractmethod
    def list_by_dm_id(self, dm_id: uuid.UUID) -> list[Campaign]:
        """
        Return all campaigns owned by the given DM, newest first.

        @param dm_id - The UUID of the DM whose campaigns to list.
        """

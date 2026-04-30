"""
Abstract repository interface for the dungeons bounded context.

The domain defines what it needs from persistence. The infrastructure layer
implements it. This keeps the domain free of any SQLAlchemy dependency.
"""

import uuid
from abc import ABC, abstractmethod

from app.dungeons.domain.models import Dungeon


class DungeonRepository(ABC):
    """Persistence interface for Dungeon aggregates."""

    @abstractmethod
    def save(self, dungeon: Dungeon) -> None:
        """
        Insert or update a Dungeon aggregate in the store.

        @param dungeon - The Dungeon aggregate to persist.
        """
        ...

    @abstractmethod
    def get_by_id(self, dungeon_id: uuid.UUID) -> Dungeon | None:
        """
        Return a Dungeon by its UUID, or None if not found.

        @param dungeon_id - The UUID of the dungeon to fetch.
        """
        ...

    @abstractmethod
    def list_by_campaign_id(self, campaign_id: uuid.UUID) -> list[Dungeon]:
        """
        Return all dungeons for the given campaign, newest first.

        @param campaign_id - The UUID of the campaign.
        """
        ...

    @abstractmethod
    def update_room_index(
        self, dungeon_id: uuid.UUID, room_index: int
    ) -> Dungeon | None:
        """
        Set current_room_index on the dungeon and return the updated aggregate.

        Returns None if the dungeon does not exist.
        """
        ...

    @abstractmethod
    def complete_quest_stage(
        self, dungeon_id: uuid.UUID, stage_index: int
    ) -> Dungeon | None:
        """
        Append stage_index to completed_stage_indices and return the updated aggregate.

        Idempotent -- calling with the same stage_index twice is safe.
        Returns None if the dungeon does not exist.
        """
        ...

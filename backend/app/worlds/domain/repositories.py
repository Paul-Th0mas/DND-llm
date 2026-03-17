"""
Abstract repository interface for the worlds bounded context.

The domain defines what it needs from persistence. The infrastructure layer
implements it. This keeps the domain free of any SQLAlchemy dependency.
"""

import uuid
from abc import ABC, abstractmethod

from app.worlds.domain.models import World


class WorldRepository(ABC):
    """
    Persistence interface for World aggregates.

    Only read operations are needed — worlds are seeded by admin, not
    created via the API.
    """

    @abstractmethod
    def get_all_active(self) -> list[World]:
        """
        Return all worlds where is_active is True.

        @returns A list of World aggregates. Empty list if none exist.
        """
        ...

    @abstractmethod
    def get_by_id(self, world_id: uuid.UUID) -> World | None:
        """
        Return the world with the given id, or None if not found.

        @param world_id - The UUID of the world to fetch.
        @returns The World aggregate, or None.
        """
        ...

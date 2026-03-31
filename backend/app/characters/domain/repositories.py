"""
Abstract repository interfaces for the characters bounded context.

The domain defines what it needs from persistence; the infrastructure layer
provides the concrete implementation.
"""

import logging
import uuid
from abc import ABC, abstractmethod

from app.characters.domain.models import Character

logger = logging.getLogger(__name__)


class CharacterRepository(ABC):
    """Abstract repository for Character aggregates."""

    @abstractmethod
    def save(self, character: Character) -> None:
        """Insert or update a Character aggregate."""
        ...

    @abstractmethod
    def get_by_id(self, character_id: uuid.UUID) -> Character | None:
        """Return a Character by UUID, or None if not found."""
        ...

    @abstractmethod
    def list_by_owner_id(self, owner_id: uuid.UUID) -> list[Character]:
        """Return all characters owned by the given user."""
        ...

    @abstractmethod
    def list_by_campaign_id(self, campaign_id: uuid.UUID) -> list[Character]:
        """Return all characters linked to the given campaign."""
        ...

    @abstractmethod
    def get_by_campaign_and_owner(
        self, campaign_id: uuid.UUID, owner_id: uuid.UUID
    ) -> Character | None:
        """
        Return the character owned by owner_id that is linked to campaign_id,
        or None if no such character exists.
        """
        ...

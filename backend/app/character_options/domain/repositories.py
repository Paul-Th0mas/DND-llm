"""
Abstract repository interfaces for the character_options bounded context.

The domain defines what it needs from persistence; the infrastructure layer
provides the concrete implementation. This keeps the domain free of ORM deps.
"""

import logging
import uuid
from abc import ABC, abstractmethod

from app.character_options.domain.models import CharacterClass, CharacterSpecies

logger = logging.getLogger(__name__)


class CharacterClassRepository(ABC):
    """Abstract repository for CharacterClass reference data."""

    @abstractmethod
    def list_by_theme(self, theme: str) -> list[CharacterClass]:
        """Return all classes for the given world theme."""
        ...

    @abstractmethod
    def get_by_id(self, class_id: uuid.UUID) -> CharacterClass | None:
        """Return a single class by UUID, or None if not found."""
        ...


class CharacterSpeciesRepository(ABC):
    """Abstract repository for CharacterSpecies reference data."""

    @abstractmethod
    def list_by_theme(self, theme: str) -> list[CharacterSpecies]:
        """Return all species for the given world theme."""
        ...

    @abstractmethod
    def get_by_id(self, species_id: uuid.UUID) -> CharacterSpecies | None:
        """Return a single species by UUID, or None if not found."""
        ...

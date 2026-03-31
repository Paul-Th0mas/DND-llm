"""
Application services (use cases) for the character_options bounded context.

ListClassesUseCase    — returns all classes for a given world theme.
GetClassUseCase       — returns a single class by ID.
ListSpeciesUseCase    — returns all species for a given world theme.
GetSpeciesUseCase     — returns a single species by ID.

Use cases orchestrate domain objects and repositories. They contain no
business logic — invariants live in the domain models.
"""

import logging
import uuid

from app.character_options.application.schemas import (
    CharacterClassListResponse,
    CharacterClassResponse,
    CharacterSpeciesListResponse,
    CharacterSpeciesResponse,
)
from app.character_options.domain.exceptions import (
    CharacterClassNotFoundError,
    CharacterSpeciesNotFoundError,
)
from app.character_options.domain.repositories import (
    CharacterClassRepository,
    CharacterSpeciesRepository,
)

logger = logging.getLogger(__name__)


class ListClassesUseCase:
    """Handles GET /character-options/classes?theme={theme}."""

    def __init__(self, repo: CharacterClassRepository) -> None:
        self._repo = repo

    def execute(self, theme: str) -> CharacterClassListResponse:
        """
        Return all classes for the given world theme.

        @param theme - The world theme string (e.g. "MEDIEVAL_FANTASY").
        @returns CharacterClassListResponse ready for HTTP serialization.
        """
        logger.info("ListClassesUseCase.execute: theme=%s", theme)
        classes = self._repo.list_by_theme(theme)
        return CharacterClassListResponse(
            classes=[CharacterClassResponse.from_domain(c) for c in classes]
        )


class GetClassUseCase:
    """Handles GET /character-options/classes/{class_id}."""

    def __init__(self, repo: CharacterClassRepository) -> None:
        self._repo = repo

    def execute(self, class_id: uuid.UUID) -> CharacterClassResponse:
        """
        Return a single class by UUID.

        @param class_id - UUID of the class to fetch.
        @returns CharacterClassResponse ready for HTTP serialization.
        @raises CharacterClassNotFoundError if not found.
        """
        logger.debug("GetClassUseCase.execute: class_id=%s", class_id)
        cls = self._repo.get_by_id(class_id)
        if cls is None:
            raise CharacterClassNotFoundError(f"Class {class_id} not found")
        return CharacterClassResponse.from_domain(cls)


class ListSpeciesUseCase:
    """Handles GET /character-options/species?theme={theme}."""

    def __init__(self, repo: CharacterSpeciesRepository) -> None:
        self._repo = repo

    def execute(self, theme: str) -> CharacterSpeciesListResponse:
        """
        Return all species for the given world theme.

        @param theme - The world theme string (e.g. "MEDIEVAL_FANTASY").
        @returns CharacterSpeciesListResponse ready for HTTP serialization.
        """
        logger.info("ListSpeciesUseCase.execute: theme=%s", theme)
        species = self._repo.list_by_theme(theme)
        return CharacterSpeciesListResponse(
            species=[CharacterSpeciesResponse.from_domain(s) for s in species]
        )


class GetSpeciesUseCase:
    """Handles GET /character-options/species/{species_id}."""

    def __init__(self, repo: CharacterSpeciesRepository) -> None:
        self._repo = repo

    def execute(self, species_id: uuid.UUID) -> CharacterSpeciesResponse:
        """
        Return a single species by UUID.

        @param species_id - UUID of the species to fetch.
        @returns CharacterSpeciesResponse ready for HTTP serialization.
        @raises CharacterSpeciesNotFoundError if not found.
        """
        logger.debug("GetSpeciesUseCase.execute: species_id=%s", species_id)
        sp = self._repo.get_by_id(species_id)
        if sp is None:
            raise CharacterSpeciesNotFoundError(f"Species {species_id} not found")
        return CharacterSpeciesResponse.from_domain(sp)

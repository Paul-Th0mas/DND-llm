"""
Domain exceptions for the character_options bounded context.

All exceptions inherit from core domain exceptions so the global error
handlers can map them to the correct HTTP status codes automatically.
"""

from app.core.exceptions import NotFoundError


class CharacterClassNotFoundError(NotFoundError):
    """Raised when a requested CharacterClass does not exist."""


class CharacterSpeciesNotFoundError(NotFoundError):
    """Raised when a requested CharacterSpecies does not exist."""

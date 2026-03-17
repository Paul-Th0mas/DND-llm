"""
Domain exceptions for the dungeons bounded context.

All inherit from the core exception hierarchy so the global handler
automatically maps them to the correct HTTP status codes.

No HTTP knowledge belongs here — just semantic error types.
"""

from app.core.exceptions import DomainError, NotFoundError


class DungeonNotFoundError(NotFoundError):
    """Raised when a requested dungeon does not exist. Maps to HTTP 404."""


class DungeonGenerationError(DomainError):
    """Raised when the narrator fails to generate a dungeon. Maps to HTTP 400."""


class InvalidDungeonSettingsError(DungeonGenerationError):
    """Raised when DungeonSettings fail domain validation. Maps to HTTP 400."""

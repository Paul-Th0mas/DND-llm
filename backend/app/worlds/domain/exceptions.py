"""
Domain exceptions for the worlds bounded context.

All inherit from the core exception hierarchy so the global handler
automatically maps them to the correct HTTP status codes.

No HTTP knowledge belongs here — just semantic error types.
"""

from app.core.exceptions import DomainError


class WorldGenerationError(DomainError):
    """Base for all world generation errors. Maps to HTTP 400."""


class InvalidWorldSettingsError(WorldGenerationError):
    """Raised when the DM's world settings fail domain validation. Maps to HTTP 400."""

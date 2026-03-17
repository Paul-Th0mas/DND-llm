"""
Domain exceptions for the worlds bounded context.

All inherit from the core exception hierarchy so the global handler
automatically maps them to the correct HTTP status codes.

No HTTP knowledge belongs here — just semantic error types.
"""

from app.core.exceptions import NotFoundError


class WorldNotFoundError(NotFoundError):
    """Raised when a requested world does not exist or is inactive. Maps to HTTP 404."""

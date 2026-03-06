"""
Domain exceptions for the campaigns bounded context.

These inherit from the core hierarchy so the global error handlers
in app/core/error_handlers.py automatically map them to HTTP responses:
  CampaignNotFoundError  → 404
  InvalidCampaignError   → 400
"""

from app.core.exceptions import DomainError, NotFoundError


class CampaignNotFoundError(NotFoundError):
    """Raised when a Campaign with the given ID does not exist."""


class InvalidCampaignError(DomainError):
    """Raised when campaign fields violate a domain invariant."""

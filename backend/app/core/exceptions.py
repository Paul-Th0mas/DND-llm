"""
Base domain exception hierarchy.

These exceptions carry semantic meaning only — no HTTP knowledge lives here.
The API layer (error_handlers.py) maps these to HTTP status codes.

Keeping HTTP concerns out of the domain layer is a DDD principle: the domain
should not know or care how it is exposed (HTTP, CLI, message queue, etc.).
"""


class DomainError(Exception):
    """Root for all domain-specific errors. Maps to HTTP 400 (bad request)."""


class NotFoundError(DomainError):
    """Raised when a requested aggregate or entity does not exist. Maps to HTTP 404."""


class AuthenticationError(DomainError):
    """Raised when authentication fails (bad token, OAuth failure). Maps to HTTP 401."""


class ConflictError(DomainError):
    """
    Raised when an operation conflicts with existing state (e.g. duplicate).
    Maps to HTTP 409.
    """


class ForbiddenError(DomainError):
    """
    Raised when an authenticated user lacks permission for an action
    (e.g. wrong password, wrong role). Maps to HTTP 403.
    """


class GoneError(DomainError):
    """
    Raised when a resource existed but is no longer available
    (e.g. a closed room). Maps to HTTP 410.
    """

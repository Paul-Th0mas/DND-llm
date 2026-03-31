"""
Domain exceptions for the characters bounded context.

All exceptions inherit from core domain exceptions so the global error
handlers can map them to the correct HTTP status codes automatically.
"""

from app.core.exceptions import ConflictError, DomainError, NotFoundError


class InvalidCharacterError(DomainError):
    """Raised when a character violates a domain invariant (e.g. name too long)."""


class CharacterNotFoundError(NotFoundError):
    """Raised when a requested Character does not exist."""


class CharacterAccessDeniedError(NotFoundError):
    """
    Raised when a player tries to access a character they do not own.

    We deliberately inherit from NotFoundError (→ 404) rather than
    DomainError (→ 400) to avoid leaking the existence of other players'
    characters. The API should return 404 not 403 per the spec.
    """


class CharacterAlreadyLinkedError(ConflictError):
    """
    Raised when a player tries to link a second character to the same campaign.
    Maps to HTTP 409.
    """


class CampaignCharacterThemeMismatchError(DomainError):
    """
    Raised when a character's world does not match the campaign's world.
    Maps to HTTP 400.
    """


class DuplicateCharacterNameError(ConflictError):
    """
    Raised when a character name already exists in the same campaign.
    Maps to HTTP 409.
    """

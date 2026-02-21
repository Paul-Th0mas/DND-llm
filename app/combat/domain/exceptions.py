"""
Domain exceptions for the combat bounded context.

All inherit from the core exception hierarchy so the global handler
automatically maps them to the correct HTTP status codes.
"""

from app.core.exceptions import DomainError, NotFoundError


class CombatNotFoundError(NotFoundError):
    """Raised when a requested CombatEncounter does not exist. HTTP 404."""


class InvalidActionError(DomainError):
    """Raised when the action is illegal — wrong hand type or invalid indices. HTTP 400."""


class InsufficientDiceError(DomainError):
    """Raised when the dice pool lacks enough dice to form the required hand. HTTP 400."""


class CombatAlreadyEndedError(DomainError):
    """Raised when an action is attempted on a finished encounter. HTTP 400."""


class NotYourTurnError(DomainError):
    """Raised when actor_id does not match the current-turn combatant. HTTP 400."""

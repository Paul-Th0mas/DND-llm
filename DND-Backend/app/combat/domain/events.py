"""
Domain events for the combat bounded context.

Events are immutable records of something meaningful that happened.
They are raised by aggregates and may be handled by application services
to trigger side effects (notifications, persistence, etc.).
"""

import uuid
from dataclasses import dataclass
from datetime import datetime

from app.combat.domain.models import ActionType, CombatStatus, HandType


@dataclass(frozen=True)
class CombatStarted:
    """Fired when a new CombatEncounter is created and turn order is set."""

    encounter_id: uuid.UUID
    # tuple so the event remains fully immutable (list would allow mutation).
    turn_order: tuple[uuid.UUID, ...]
    occurred_at: datetime


@dataclass(frozen=True)
class ActionTaken:
    """Fired after an actor successfully resolves an action."""

    encounter_id: uuid.UUID
    actor_id: uuid.UUID
    action_type: ActionType
    hand_type: HandType | None  # None for non-hand actions like FLEE/REST
    score: int
    occurred_at: datetime


@dataclass(frozen=True)
class CombatantDowned:
    """Fired when a combatant reaches 0 HP."""

    encounter_id: uuid.UUID
    combatant_id: uuid.UUID
    occurred_at: datetime


@dataclass(frozen=True)
class CombatEnded:
    """Fired when the encounter resolves to VICTORY, DEFEAT, or FLED."""

    encounter_id: uuid.UUID
    status: CombatStatus
    rounds_elapsed: int
    occurred_at: datetime

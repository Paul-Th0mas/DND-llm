"""
Tests for combat domain events.

Verifies that each event can be constructed and that its fields are
correctly set and immutable.
"""

import uuid
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from app.combat.domain.events import (
    ActionTaken,
    CombatEnded,
    CombatStarted,
    CombatantDowned,
)
from app.combat.domain.models import ActionType, CombatStatus, HandType


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def test_combat_started_fields() -> None:
    enc_id = uuid.uuid4()
    c1, c2 = uuid.uuid4(), uuid.uuid4()
    now = _now()

    event = CombatStarted(
        encounter_id=enc_id,
        turn_order=(c1, c2),
        occurred_at=now,
    )

    assert event.encounter_id == enc_id
    assert event.turn_order == (c1, c2)
    assert event.occurred_at == now


def test_combat_started_is_immutable() -> None:
    event = CombatStarted(
        encounter_id=uuid.uuid4(),
        turn_order=(uuid.uuid4(),),
        occurred_at=_now(),
    )

    # Frozen dataclasses raise FrozenInstanceError on direct attribute assignment.
    with pytest.raises(FrozenInstanceError):
        event.encounter_id = uuid.uuid4()  # type: ignore[misc]


def test_action_taken_fields() -> None:
    enc_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    now = _now()

    event = ActionTaken(
        encounter_id=enc_id,
        actor_id=actor_id,
        action_type=ActionType.QUICK_STRIKE,
        hand_type=HandType.PAIR,
        score=42,
        occurred_at=now,
    )

    assert event.encounter_id == enc_id
    assert event.actor_id == actor_id
    assert event.action_type == ActionType.QUICK_STRIKE
    assert event.hand_type == HandType.PAIR
    assert event.score == 42


def test_action_taken_hand_type_can_be_none() -> None:
    """FLEE and REST actions have no associated hand."""
    event = ActionTaken(
        encounter_id=uuid.uuid4(),
        actor_id=uuid.uuid4(),
        action_type=ActionType.FLEE,
        hand_type=None,
        score=0,
        occurred_at=_now(),
    )

    assert event.hand_type is None


def test_combatant_downed_fields() -> None:
    enc_id = uuid.uuid4()
    comb_id = uuid.uuid4()
    now = _now()

    event = CombatantDowned(
        encounter_id=enc_id,
        combatant_id=comb_id,
        occurred_at=now,
    )

    assert event.encounter_id == enc_id
    assert event.combatant_id == comb_id


def test_combat_ended_fields() -> None:
    enc_id = uuid.uuid4()
    now = _now()

    event = CombatEnded(
        encounter_id=enc_id,
        status=CombatStatus.VICTORY,
        rounds_elapsed=3,
        occurred_at=now,
    )

    assert event.encounter_id == enc_id
    assert event.status == CombatStatus.VICTORY
    assert event.rounds_elapsed == 3


def test_combat_ended_is_immutable() -> None:
    event = CombatEnded(
        encounter_id=uuid.uuid4(),
        status=CombatStatus.DEFEAT,
        rounds_elapsed=1,
        occurred_at=_now(),
    )

    with pytest.raises(FrozenInstanceError):
        event.rounds_elapsed = 999  # type: ignore[misc]

"""
Pydantic DTOs for the combat bounded context.

These schemas are the API contract: request bodies coming in and response
bodies going out. They are distinct from domain models (Combatant,
CombatEncounter) and ORM models. FastAPI uses these for validation and
serialisation.
"""

import uuid
from typing import Any

from pydantic import BaseModel

from app.combat.domain.models import ActionType, ClassType, CombatantType, DieType


# ---------------------------------------------------------------------------
# Request DTOs
# ---------------------------------------------------------------------------


class CombatantConfig(BaseModel):
    """Configuration for a single combatant when starting a new encounter."""

    name: str
    combatant_type: CombatantType
    class_type: ClassType | None = None
    die_type: DieType
    max_pool_size: int
    hp: int
    # weapon / armor / accessory — use None to leave a slot empty.
    equipment: dict[str, str | None] = {}
    relics: list[str] = []


class StartCombatRequest(BaseModel):
    room_id: uuid.UUID | None = None
    combatants: list[CombatantConfig]


class TakeActionRequest(BaseModel):
    actor_id: uuid.UUID
    action_type: ActionType
    # Indices into the actor's current pool that will be spent/used for the hand.
    dice_indices: list[int]
    # One or more target combatant IDs (empty is valid for self-targeting actions).
    target_ids: list[uuid.UUID] = []
    # Barbarian class ability: skip hand detection, use Rage Strike fixed scoring.
    rage_strike: bool = False
    # Wizard Wild Tokens: map pool index → forced die value. Consumes wild tokens.
    wild_token_overrides: dict[int, int] | None = None
    # Rogue Twin Strike: provide a second set of dice indices to resolve a second Pair action.
    twin_strike_indices: list[int] | None = None


class RerollRequest(BaseModel):
    actor_id: uuid.UUID
    # Up to 3 pool indices to reroll.
    dice_indices: list[int]


# ---------------------------------------------------------------------------
# Response DTOs
# ---------------------------------------------------------------------------


class StatusEffectResponse(BaseModel):
    effect_type: str
    duration: int


class CombatantResponse(BaseModel):
    id: uuid.UUID
    name: str
    combatant_type: str
    class_type: str | None
    hp: int
    max_hp: int
    temp_hp: int
    pool: list[int]
    discard: list[int]
    max_pool_size: int
    status_effects: list[StatusEffectResponse]
    initiative: int
    wild_tokens: int
    is_downed: bool
    is_exhausted: bool


class CombatStateResponse(BaseModel):
    encounter_id: uuid.UUID
    status: str
    round: int
    current_actor_id: uuid.UUID | None
    combatants: list[CombatantResponse]


class ActionResultResponse(BaseModel):
    action_type: str
    hand_type: str | None
    score: int
    damage_dealt: dict[str, int]
    healing_done: dict[str, int]
    temp_hp_gained: int
    messages: list[str]
    updated_state: CombatStateResponse


# ---------------------------------------------------------------------------
# Mapping helpers (domain → response DTO)
# ---------------------------------------------------------------------------


def combatant_to_response(c: Any) -> CombatantResponse:
    """
    Convert a domain Combatant to its response DTO.
    Using Any here avoids a circular import between schemas and domain models
    at the type annotation level; runtime values are always Combatant instances.
    """
    return CombatantResponse(
        id=c.id,
        name=c.name,
        combatant_type=c.combatant_type.name,
        class_type=c.class_type.name if c.class_type else None,
        hp=c.hp,
        max_hp=c.max_hp,
        temp_hp=c.temp_hp,
        pool=list(c.pool),
        discard=list(c.discard),
        max_pool_size=c.max_pool_size,
        status_effects=[
            StatusEffectResponse(effect_type=e.effect_type.name, duration=e.duration)
            for e in c.status_effects
        ],
        initiative=c.initiative,
        wild_tokens=c.wild_tokens,
        is_downed=c.is_downed(),
        is_exhausted=c.is_exhausted(),
    )


def encounter_to_state_response(enc: Any) -> CombatStateResponse:
    """Convert a domain CombatEncounter to its state response DTO."""
    from app.combat.domain.models import CombatStatus

    current_actor_id: uuid.UUID | None = None
    if enc.status == CombatStatus.ACTIVE and enc.turn_order:
        current_actor_id = enc.turn_order[enc.current_turn_index]

    return CombatStateResponse(
        encounter_id=enc.id,
        status=enc.status.name,
        round=enc.round,
        current_actor_id=current_actor_id,
        combatants=[combatant_to_response(c) for c in enc.combatants],
    )

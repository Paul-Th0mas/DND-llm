"""
FastAPI router for the combat bounded context.

Four endpoints:
  POST   /combat/start                  → CombatStateResponse  (201)
  GET    /combat/{encounter_id}         → CombatStateResponse  (200)
  POST   /combat/{encounter_id}/action  → ActionResultResponse (200)
  POST   /combat/{encounter_id}/reroll  → ActionResultResponse (200)

Routers are thin: validate input via Pydantic, delegate to a use case,
return the response. No business logic lives here.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, status

from app.combat.api.dependencies import get_combat_repository, get_dice_roller
from app.combat.application.schemas import (
    ActionResultResponse,
    CombatStateResponse,
    RerollRequest,
    StartCombatRequest,
    TakeActionRequest,
)
from app.combat.application.use_cases import (
    GetCombatStateUseCase,
    RerollDiceUseCase,
    StartCombatUseCase,
    TakeActionUseCase,
)
from app.combat.domain.repositories import CombatRepository
from app.combat.domain.services import ActionResolver, HandRecognizer
from app.combat.infrastructure.dice import RandomDiceRoller

logger = logging.getLogger(__name__)

combat_router = APIRouter(prefix="/combat", tags=["combat"])


@combat_router.post(
    "/start",
    response_model=CombatStateResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_combat(
    body: StartCombatRequest,
    repo: CombatRepository = Depends(get_combat_repository),
    roller: RandomDiceRoller = Depends(get_dice_roller),
) -> CombatStateResponse:
    """
    Create a new combat encounter.

    Rolls initial dice pools and initiative for every combatant, determines
    turn order (initiative descending), and returns the starting state.
    """
    logger.info("POST /combat/start combatants=%d", len(body.combatants))
    use_case = StartCombatUseCase(combat_repo=repo, dice_roller=roller)
    return use_case.execute(room_id=body.room_id, combatant_configs=body.combatants)


@combat_router.get(
    "/{encounter_id}",
    response_model=CombatStateResponse,
    status_code=status.HTTP_200_OK,
)
def get_combat_state(
    encounter_id: uuid.UUID,
    repo: CombatRepository = Depends(get_combat_repository),
) -> CombatStateResponse:
    """Return the current state of an encounter."""
    logger.info("GET /combat/%s", encounter_id)
    use_case = GetCombatStateUseCase(combat_repo=repo)
    return use_case.execute(encounter_id=encounter_id)


@combat_router.post(
    "/{encounter_id}/action",
    response_model=ActionResultResponse,
    status_code=status.HTTP_200_OK,
)
def take_action(
    encounter_id: uuid.UUID,
    body: TakeActionRequest,
    repo: CombatRepository = Depends(get_combat_repository),
    roller: RandomDiceRoller = Depends(get_dice_roller),
) -> ActionResultResponse:
    """
    Declare and resolve an action for the current-turn combatant.

    The actor_id must match the combatant whose turn it is.
    dice_indices selects which pool dice to spend for the hand.
    """
    logger.info(
        "POST /combat/%s/action actor=%s action=%s",
        encounter_id,
        body.actor_id,
        body.action_type.name,
    )
    use_case = TakeActionUseCase(
        combat_repo=repo,
        dice_roller=roller,
        hand_recognizer=HandRecognizer(),
        action_resolver=ActionResolver(),
    )
    return use_case.execute(
        encounter_id=encounter_id,
        actor_id=body.actor_id,
        action_type=body.action_type,
        dice_indices=body.dice_indices,
        target_ids=body.target_ids,
        rage_strike=body.rage_strike,
        wild_token_overrides=body.wild_token_overrides,
        twin_strike_indices=body.twin_strike_indices,
    )


@combat_router.post(
    "/{encounter_id}/reroll",
    response_model=ActionResultResponse,
    status_code=status.HTTP_200_OK,
)
def reroll_dice(
    encounter_id: uuid.UUID,
    body: RerollRequest,
    repo: CombatRepository = Depends(get_combat_repository),
    roller: RandomDiceRoller = Depends(get_dice_roller),
) -> ActionResultResponse:
    """
    Reroll up to 3 pool dice for the current-turn combatant.

    This consumes their action for the turn (turn advances after reroll).
    """
    logger.info(
        "POST /combat/%s/reroll actor=%s indices=%s",
        encounter_id,
        body.actor_id,
        body.dice_indices,
    )
    use_case = RerollDiceUseCase(combat_repo=repo, dice_roller=roller)
    return use_case.execute(
        encounter_id=encounter_id,
        actor_id=body.actor_id,
        dice_indices=body.dice_indices,
    )

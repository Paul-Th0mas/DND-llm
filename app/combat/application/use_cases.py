"""
Application services (use cases) for the combat bounded context.

Each class handles exactly one use case. They orchestrate domain objects,
repositories, and services but contain no business logic themselves — all
invariants live in the domain layer.
"""

import logging
import uuid
from datetime import datetime, timezone

from app.combat.application.schemas import (
    ActionResultResponse,
    CombatStateResponse,
    CombatantConfig,
    encounter_to_state_response,
)
from app.combat.domain.exceptions import (
    CombatAlreadyEndedError,
    CombatNotFoundError,
    InsufficientDiceError,
    InvalidActionError,
    NotYourTurnError,
)
from app.combat.domain.models import (
    ACTION_HAND_REQUIREMENTS,
    HAND_SCORING,
    ActionResult,
    ActionType,
    ClassType,
    CombatEncounter,
    CombatStatus,
    Combatant,
    CombatantType,
    Equipment,
    Hand,
    HandType,
    StatusEffectType,
)
from app.combat.domain.repositories import CombatRepository
from app.combat.domain.services import ActionResolver, DiceRoller, HandRecognizer

logger = logging.getLogger(__name__)


class StartCombatUseCase:
    """
    Creates a new CombatEncounter, rolls initial dice pools, determines
    initiative order, and persists it.

    Initiative is rolled as a single die of the combatant's die_type. Ties
    are broken by the order combatants appear in the request.
    """

    def __init__(
        self,
        combat_repo: CombatRepository,
        dice_roller: DiceRoller,
    ) -> None:
        self._repo = combat_repo
        self._roller = dice_roller

    def execute(
        self,
        room_id: uuid.UUID | None,
        combatant_configs: list[CombatantConfig],
    ) -> CombatStateResponse:
        logger.debug(
            "StartCombatUseCase: room_id=%s configs=%d", room_id, len(combatant_configs)
        )

        combatants: list[Combatant] = []
        for cfg in combatant_configs:
            equipment = Equipment(
                weapon=cfg.equipment.get("weapon"),
                armor=cfg.equipment.get("armor"),
                accessory=cfg.equipment.get("accessory"),
            )
            # Roll the starting pool.
            pool = self._roller.roll_many(cfg.die_type, cfg.max_pool_size)
            # Roll initiative as one die of the combatant's type.
            initiative = self._roller.roll(cfg.die_type)

            combatant = Combatant(
                id=uuid.uuid4(),
                name=cfg.name,
                combatant_type=cfg.combatant_type,
                class_type=cfg.class_type,
                die_type=cfg.die_type,
                max_pool_size=cfg.max_pool_size,
                hp=cfg.hp,
                max_hp=cfg.hp,
                temp_hp=0,
                pool=pool,
                discard=[],
                status_effects=[],
                initiative=initiative,
                equipment=equipment,
                # Wizards start with 3 wild tokens per encounter.
                wild_tokens=3 if cfg.class_type == ClassType.WIZARD else 0,
                relics=list(cfg.relics),
                free_reroll_used=False,
                second_wind_used=False,
                case_joint_used=False,
                sanctuary_used=False,
                discordant_used=False,
                fury_bonus_active=False,
                fury_chips_bonus=0,
                fury_mult_bonus=0,
                escalation_count=0,
                last_hand_type=None,
                trap_dice=[],
                trap_trigger="",
                inspire_given=False,
            )
            combatants.append(combatant)
            logger.info(
                "StartCombat: created combatant '%s' id=%s initiative=%d",
                combatant.name,
                combatant.id,
                initiative,
            )

        # Sort by initiative descending; stable sort preserves request order on ties.
        combatants.sort(key=lambda c: c.initiative, reverse=True)
        turn_order = [c.id for c in combatants]

        encounter = CombatEncounter(
            id=uuid.uuid4(),
            room_id=room_id,
            combatants=combatants,
            round=1,
            turn_order=turn_order,
            current_turn_index=0,
            status=CombatStatus.ACTIVE,
        )

        self._repo.save(encounter)
        logger.info(
            "StartCombat: encounter id=%s created with %d combatants",
            encounter.id,
            len(combatants),
        )

        return encounter_to_state_response(encounter)


class GetCombatStateUseCase:
    """Returns the current state of an encounter as a response DTO."""

    def __init__(self, combat_repo: CombatRepository) -> None:
        self._repo = combat_repo

    def execute(self, encounter_id: uuid.UUID) -> CombatStateResponse:
        logger.debug("GetCombatStateUseCase: encounter_id=%s", encounter_id)
        encounter = self._repo.get_by_id(encounter_id)
        if encounter is None:
            raise CombatNotFoundError(f"Combat encounter {encounter_id} not found")
        return encounter_to_state_response(encounter)


class TakeActionUseCase:
    """
    Validates and resolves a single action taken by a combatant.

    Pipeline:
      1. Load encounter; assert ACTIVE.
      2. Assert actor is the current turn combatant.
      3. Apply Wild Token overrides (Wizard).
      4. Validate dice_indices form a hand meeting the action's minimum.
      5. Call ActionResolver.resolve().
      6. Handle Rogue Twin Strike (second resolve).
      7. Handle Cleric Blessed Hands dice recovery.
      8. Advance turn; check end conditions.
      9. Save and return ActionResultResponse.
    """

    def __init__(
        self,
        combat_repo: CombatRepository,
        dice_roller: DiceRoller,
        hand_recognizer: HandRecognizer,
        action_resolver: ActionResolver,
    ) -> None:
        self._repo = combat_repo
        self._roller = dice_roller
        self._recognizer = hand_recognizer
        self._resolver = action_resolver

    def execute(
        self,
        encounter_id: uuid.UUID,
        actor_id: uuid.UUID,
        action_type: ActionType,
        dice_indices: list[int],
        target_ids: list[uuid.UUID],
        rage_strike: bool = False,
        wild_token_overrides: dict[int, int] | None = None,
        twin_strike_indices: list[int] | None = None,
    ) -> ActionResultResponse:
        logger.debug(
            "TakeActionUseCase: encounter=%s actor=%s action=%s",
            encounter_id,
            actor_id,
            action_type.name,
        )

        encounter = self._load_active_encounter(encounter_id)
        actor = self._validate_turn(encounter, actor_id)
        targets = [encounter.get_combatant(tid) for tid in target_ids]

        # Apply start-of-turn status effects (burning, poison tick, etc.).
        sot_messages = encounter.apply_start_of_turn_effects()

        # Wizard Wild Token overrides: force pool positions to specific values.
        if wild_token_overrides and actor.class_type == ClassType.WIZARD:
            self._apply_wild_tokens(actor, wild_token_overrides)

        # Resolve the primary action.
        hand, result = self._resolve_action(
            encounter, actor, action_type, dice_indices, targets, rage_strike
        )
        all_messages = sot_messages + result.messages

        # Rogue Twin Strike: resolve a second Pair action in the same turn.
        if twin_strike_indices and actor.class_type == ClassType.ROGUE:
            twin_hand = self._recognizer.identify_from_indices(
                actor.pool, twin_strike_indices
            )
            if twin_hand and twin_hand.hand_type.value >= HandType.PAIR.value:
                actor.spend_dice(twin_strike_indices)
                twin_result = self._resolver.resolve(
                    ActionType.QUICK_STRIKE,
                    twin_hand,
                    actor,
                    targets,
                    encounter,
                )
                # Merge twin strike results.
                for cid, dmg in twin_result.damage_dealt.items():
                    result.damage_dealt[cid] = result.damage_dealt.get(cid, 0) + dmg
                all_messages.extend(twin_result.messages)
                logger.info("Rogue Twin Strike resolved score=%d", twin_result.score)

        # Cleric Blessed Hands: recover 1 extra die from pool if flagged.
        if result.dice_recovered > 0 and actor.class_type == ClassType.CLERIC:
            recovered_vals = self._roller.roll_many(
                actor.die_type, result.dice_recovered
            )
            actor.recover_dice(recovered_vals)
            all_messages.append(
                f"{actor.name} recovers {result.dice_recovered} die — "
                f"Blessed Hands: {recovered_vals}"
            )

        # Check if any combatant was downed this action.
        for target in targets:
            if target.is_downed():
                logger.info(
                    "TakeAction: combatant '%s' downed in encounter %s",
                    target.name,
                    encounter_id,
                )

        encounter.check_end_conditions()

        if encounter.status == CombatStatus.ACTIVE:
            encounter.advance_turn()

        self._repo.save(encounter)
        logger.info(
            "TakeAction: action=%s score=%d encounter=%s",
            action_type.name,
            result.score,
            encounter_id,
        )

        return ActionResultResponse(
            action_type=result.action_type.name,
            hand_type=result.hand_type.name if result.hand_type else None,
            score=result.score,
            damage_dealt=result.damage_dealt,
            healing_done=result.healing_done,
            temp_hp_gained=result.temp_hp_gained,
            messages=all_messages,
            updated_state=encounter_to_state_response(encounter),
        )

    def _load_active_encounter(self, encounter_id: uuid.UUID) -> CombatEncounter:
        encounter = self._repo.get_by_id(encounter_id)
        if encounter is None:
            raise CombatNotFoundError(f"Combat encounter {encounter_id} not found")
        if encounter.status != CombatStatus.ACTIVE:
            raise CombatAlreadyEndedError(
                f"Combat encounter {encounter_id} has already ended ({encounter.status.name})"
            )
        return encounter

    def _validate_turn(
        self, encounter: CombatEncounter, actor_id: uuid.UUID
    ) -> Combatant:
        current = encounter.get_current_actor()
        if current.id != actor_id:
            raise NotYourTurnError(f"It is {current.name}'s turn, not actor {actor_id}")
        return current

    def _apply_wild_tokens(self, actor: Combatant, overrides: dict[int, int]) -> None:
        """
        Wizard Wild Tokens: force specific dice to specific values.
        Each override costs 1 wild token. Stops when tokens run out.
        """
        for idx, forced_val in overrides.items():
            if actor.wild_tokens <= 0:
                logger.warning("Wizard %s has no wild tokens left", actor.name)
                break
            if 0 <= idx < len(actor.pool):
                actor.pool[idx] = forced_val
                actor.wild_tokens -= 1
                logger.debug(
                    "Wild token: %s pool[%d] → %d (tokens left=%d)",
                    actor.name,
                    idx,
                    forced_val,
                    actor.wild_tokens,
                )

    def _resolve_action(
        self,
        encounter: CombatEncounter,
        actor: Combatant,
        action_type: ActionType,
        dice_indices: list[int],
        targets: list[Combatant],
        rage_strike: bool,
    ) -> tuple[Hand, ActionResult]:
        """
        Validate dice and resolve the action. Returns (hand, ActionResult).
        For actions without a hand requirement (FLEE, REST, REROLL) a dummy
        high-die hand is constructed from the highest die in the pool.
        """

        free_actions = {ActionType.FLEE, ActionType.REST, ActionType.REROLL}
        if action_type in free_actions:
            # Build a minimal dummy hand so the resolver has something to work with.
            dummy_pool = actor.pool if actor.pool else [0]
            dummy_hand = Hand(
                hand_type=HandType.HIGH_DIE,
                scoring_indices=(0,),
                scoring_values=(dummy_pool[0],),
                base_chips=HAND_SCORING[HandType.HIGH_DIE][0],
                mult=HAND_SCORING[HandType.HIGH_DIE][1],
            )
            result = self._resolver.resolve(
                action_type, dummy_hand, actor, targets, encounter
            )
            return dummy_hand, result

        # Validate dice indices.
        if not dice_indices:
            raise InsufficientDiceError("No dice indices provided")
        if max(dice_indices) >= len(actor.pool) or min(dice_indices) < 0:
            raise InvalidActionError(
                f"Dice indices {dice_indices} are out of range for pool size {len(actor.pool)}"
            )

        # Barbarian Rage Strike skips normal hand detection.
        if rage_strike and actor.class_type == ClassType.BARBARIAN:
            rage_values = tuple(actor.pool[i] for i in dice_indices[:3])
            rage_hand = Hand(
                hand_type=HandType.THREE_OF_A_KIND,  # placeholder type for rage
                scoring_indices=tuple(dice_indices[:3]),
                scoring_values=rage_values,
                base_chips=15,
                mult=2,
            )
            actor.spend_dice(list(dice_indices[:3]))
            rage_result = self._resolver.resolve(
                action_type, rage_hand, actor, targets, encounter, rage_strike=True
            )
            return rage_hand, rage_result

        # Normal hand detection from provided indices.
        hand: Hand | None = self._recognizer.identify_from_indices(
            actor.pool, dice_indices
        )
        if hand is None:
            raise InsufficientDiceError(
                f"Dice at indices {dice_indices} do not form any recognisable hand"
            )

        # Validate the hand meets the action's minimum requirement.
        required = from_action_requirement(action_type)
        if required is not None and hand.hand_type.value < required.value:
            raise InvalidActionError(
                f"{action_type.name} requires at least {required.name}, "
                f"but dice form only {hand.hand_type.name}"
            )

        # Spend the dice used for the hand.
        actor.spend_dice(list(hand.scoring_indices))

        result = self._resolver.resolve(
            action_type, hand, actor, targets, encounter, rage_strike=False
        )
        return hand, result


class RerollDiceUseCase:
    """
    Rerolls up to 3 of the actor's pool dice, consuming their turn action.
    Fighter's free reroll (once per turn) is tracked separately and does not
    consume their main action.
    """

    def __init__(
        self,
        combat_repo: CombatRepository,
        dice_roller: DiceRoller,
    ) -> None:
        self._repo = combat_repo
        self._roller = dice_roller

    def execute(
        self,
        encounter_id: uuid.UUID,
        actor_id: uuid.UUID,
        dice_indices: list[int],
    ) -> ActionResultResponse:
        logger.debug(
            "RerollDiceUseCase: encounter=%s actor=%s indices=%s",
            encounter_id,
            actor_id,
            dice_indices,
        )

        encounter = self._repo.get_by_id(encounter_id)
        if encounter is None:
            raise CombatNotFoundError(f"Combat encounter {encounter_id} not found")
        if encounter.status != CombatStatus.ACTIVE:
            raise CombatAlreadyEndedError(f"Combat {encounter_id} has already ended")

        current = encounter.get_current_actor()
        if current.id != actor_id:
            raise NotYourTurnError(f"It is {current.name}'s turn, not {actor_id}")

        if len(dice_indices) > 3:
            raise InvalidActionError("Cannot reroll more than 3 dice at once")

        if dice_indices:
            if max(dice_indices) >= len(current.pool) or min(dice_indices) < 0:
                raise InvalidActionError(
                    f"Dice indices {dice_indices} are out of range"
                )
            new_values = self._roller.roll_many(current.die_type, len(dice_indices))
            current.reroll_dice(dice_indices, new_values)
            logger.info(
                "RerollDice: %s rerolled %s → %s",
                current.name,
                dice_indices,
                new_values,
            )

        encounter.advance_turn()
        self._repo.save(encounter)

        return ActionResultResponse(
            action_type=ActionType.REROLL.name,
            hand_type=None,
            score=0,
            damage_dealt={},
            healing_done={},
            temp_hp_gained=0,
            messages=[f"{current.name} rerolled {len(dice_indices)} dice"],
            updated_state=encounter_to_state_response(encounter),
        )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def from_action_requirement(action: ActionType) -> HandType | None:
    """Look up the minimum HandType for an action (None = no requirement)."""
    return ACTION_HAND_REQUIREMENTS.get(action)

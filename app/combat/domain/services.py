"""
Domain services for the combat bounded context.

Contains:
  DiceRoller   — Protocol for injectable die rolling (real vs. test seeded).
  HandRecognizer — Stateless hand detection from a dice pool.
  ActionResolver — Applies a resolved hand against combatants and returns
                   an ActionResult with damage, healing, and log messages.
"""

import logging
from typing import Callable, Protocol

from app.combat.domain.exceptions import InvalidActionError, InsufficientDiceError
from app.combat.domain.models import (
    ACTION_HAND_REQUIREMENTS,
    HAND_SCORING,
    ActionResult,
    ActionType,
    ClassType,
    CombatEncounter,
    CombatStatus,
    Combatant,
    DieType,
    Hand,
    HandType,
    StatusEffect,
    StatusEffectType,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DiceRoller protocol
# ---------------------------------------------------------------------------


class DiceRoller(Protocol):
    """
    Interface for rolling dice. Using a Protocol (structural subtyping)
    rather than ABC means the concrete RandomDiceRoller does not have to
    explicitly inherit from anything — it just needs the right method shapes.
    This also makes test doubles trivial to write.
    """

    def roll(self, die_type: DieType) -> int: ...

    def roll_many(self, die_type: DieType, count: int) -> list[int]: ...


# ---------------------------------------------------------------------------
# HandRecognizer
# ---------------------------------------------------------------------------


class HandRecognizer:
    """
    Stateless service that detects the best poker-style hand from a pool
    of integer die values.

    Detection checks from highest rank to lowest so the first match wins.
    Scoring metadata (base_chips, mult) is pre-populated from HAND_SCORING
    so callers receive a complete Hand value object.
    """

    def identify_best_hand(self, pool: list[int]) -> Hand | None:
        """
        Return the highest-ranking Hand that can be formed from `pool`,
        or None if no recognisable hand exists (can happen with an empty pool
        or a single die).
        """
        logger.debug("identify_best_hand pool=%s", pool)
        if not pool:
            return None

        # Detection in descending rank order so the first hit is the best.
        # Explicit type annotation is required so mypy knows the lambda return type.
        _D = Callable[[list[int]], tuple[list[int], list[int]] | None]
        detectors: list[tuple[HandType, _D]] = [
            (HandType.FIVE_OF_A_KIND, lambda p: self._detect_n_of_a_kind(p, 5)),
            (HandType.FOUR_OF_A_KIND, lambda p: self._detect_n_of_a_kind(p, 4)),
            (HandType.RUN_5, lambda p: self._detect_run(p, 5)),
            (HandType.FULL_HOUSE, lambda p: self._detect_full_house(p)),
            (HandType.RUN_4, lambda p: self._detect_run(p, 4)),
            (HandType.THREE_OF_A_KIND, lambda p: self._detect_n_of_a_kind(p, 3)),
            (HandType.TWO_PAIR, lambda p: self._detect_two_pair(p)),
            (HandType.RUN_3, lambda p: self._detect_run(p, 3)),
            (HandType.PAIR, lambda p: self._detect_n_of_a_kind(p, 2)),
            (HandType.HIGH_DIE, lambda p: self._detect_high_die(p)),
        ]

        for hand_type, detector in detectors:
            result = detector(pool)
            if result is not None:
                indices, values = result
                base_chips, mult = HAND_SCORING[hand_type]
                hand = Hand(
                    hand_type=hand_type,
                    scoring_indices=tuple(indices),
                    scoring_values=tuple(values),
                    base_chips=base_chips,
                    mult=mult,
                )
                logger.debug("identify_best_hand found %s: %s", hand_type.name, hand)
                return hand

        return None

    def identify_from_indices(self, pool: list[int], indices: list[int]) -> Hand | None:
        """
        Identify the best hand formed by the dice at the specified pool
        indices (sub-pool selection). Returns None if no hand is found.
        """
        logger.debug("identify_from_indices pool=%s indices=%s", pool, indices)
        if not indices:
            return None
        sub_pool = [pool[i] for i in indices]
        # Identify hand on sub_pool, then remap indices back to the full pool.
        hand = self.identify_best_hand(sub_pool)
        if hand is None:
            return None
        # scoring_indices in the result are relative to sub_pool; map back.
        full_indices = tuple(indices[i] for i in hand.scoring_indices)
        return Hand(
            hand_type=hand.hand_type,
            scoring_indices=full_indices,
            scoring_values=hand.scoring_values,
            base_chips=hand.base_chips,
            mult=hand.mult,
        )

    def find_all_valid_hands(self, pool: list[int]) -> list[Hand]:
        """Return all Hand types that can be formed from the pool."""
        logger.debug("find_all_valid_hands pool=%s", pool)
        results: list[Hand] = []
        _D = Callable[[list[int]], tuple[list[int], list[int]] | None]
        detectors: list[tuple[HandType, _D]] = [
            (HandType.FIVE_OF_A_KIND, lambda p: self._detect_n_of_a_kind(p, 5)),
            (HandType.FOUR_OF_A_KIND, lambda p: self._detect_n_of_a_kind(p, 4)),
            (HandType.RUN_5, lambda p: self._detect_run(p, 5)),
            (HandType.FULL_HOUSE, lambda p: self._detect_full_house(p)),
            (HandType.RUN_4, lambda p: self._detect_run(p, 4)),
            (HandType.THREE_OF_A_KIND, lambda p: self._detect_n_of_a_kind(p, 3)),
            (HandType.TWO_PAIR, lambda p: self._detect_two_pair(p)),
            (HandType.RUN_3, lambda p: self._detect_run(p, 3)),
            (HandType.PAIR, lambda p: self._detect_n_of_a_kind(p, 2)),
            (HandType.HIGH_DIE, lambda p: self._detect_high_die(p)),
        ]
        for hand_type, detector in detectors:
            result = detector(pool)
            if result is not None:
                indices, values = result
                base_chips, mult = HAND_SCORING[hand_type]
                results.append(
                    Hand(
                        hand_type=hand_type,
                        scoring_indices=tuple(indices),
                        scoring_values=tuple(values),
                        base_chips=base_chips,
                        mult=mult,
                    )
                )
        return results

    def can_form_hand_for_action(self, pool: list[int], action: ActionType) -> bool:
        """
        Check whether the pool contains sufficient dice to satisfy the
        minimum hand requirement for the given action.
        REROLL, FLEE, REST always return True (no hand needed).
        BLOCK requires at least 2 dice (no specific hand pattern).
        """
        required = ACTION_HAND_REQUIREMENTS.get(action)
        if required is None:
            # Free actions: REROLL, FLEE, REST.
            return True
        if action == ActionType.BLOCK:
            return len(pool) >= 2
        hand = self.identify_best_hand(pool)
        if hand is None:
            return False
        return hand.hand_type.value >= required.value

    # ------------------------------------------------------------------
    # Private detection helpers
    # Each returns (indices, values) or None.
    # indices are positions in the supplied pool list.
    # ------------------------------------------------------------------

    def _detect_n_of_a_kind(
        self, pool: list[int], n: int
    ) -> tuple[list[int], list[int]] | None:
        """Find a group of at least n dice with the same face value."""
        from collections import defaultdict

        groups: dict[int, list[int]] = defaultdict(list)
        for idx, val in enumerate(pool):
            groups[val].append(idx)

        # Pick the group with the highest value when multiple qualify.
        best_val = -1
        best_indices: list[int] = []
        for val, idxs in groups.items():
            if len(idxs) >= n and val > best_val:
                best_val = val
                best_indices = idxs[:n]

        if best_val == -1:
            return None
        values = [pool[i] for i in best_indices]
        return best_indices, values

    def _detect_run(
        self, pool: list[int], length: int
    ) -> tuple[list[int], list[int]] | None:
        """
        Find a run (straight) of `length` consecutive unique values.
        Uses the first occurrence of each value in the pool (lowest index).
        Returns the highest-value run when multiple are possible.
        """
        # Map each unique value to its first index in the pool.
        seen: dict[int, int] = {}
        for idx, val in enumerate(pool):
            if val not in seen:
                seen[val] = idx

        unique_sorted = sorted(seen.keys())
        best: tuple[list[int], list[int]] | None = None

        # Slide a window of `length` over the sorted unique values.
        for start in range(len(unique_sorted) - length + 1):
            window = unique_sorted[start : start + length]
            # Check that the window is truly consecutive (no gaps).
            if window[-1] - window[0] != length - 1:
                continue
            indices = [seen[v] for v in window]
            values = window
            # Keep the highest-starting run (last valid window wins).
            best = (indices, values)

        return best

    def _detect_full_house(self, pool: list[int]) -> tuple[list[int], list[int]] | None:
        """
        Three of a kind + pair from (at least) 5 dice.
        Returns 5 indices total: the 3-of-a-kind indices first, then the pair.
        """
        from collections import defaultdict

        groups: dict[int, list[int]] = defaultdict(list)
        for idx, val in enumerate(pool):
            groups[val].append(idx)

        threes: list[tuple[int, list[int]]] = [
            (v, idxs) for v, idxs in groups.items() if len(idxs) >= 3
        ]
        pairs: list[tuple[int, list[int]]] = [
            (v, idxs) for v, idxs in groups.items() if len(idxs) >= 2
        ]

        if not threes:
            return None

        # Pick the highest three-value; then a pair from a different value.
        threes.sort(key=lambda x: x[0], reverse=True)
        for three_val, three_idxs in threes:
            pair_candidates = [(v, idxs) for v, idxs in pairs if v != three_val]
            if not pair_candidates:
                continue
            pair_candidates.sort(key=lambda x: x[0], reverse=True)
            pair_val, pair_idxs = pair_candidates[0]
            indices = three_idxs[:3] + pair_idxs[:2]
            values = [three_val] * 3 + [pair_val] * 2
            return indices, values

        return None

    def _detect_two_pair(self, pool: list[int]) -> tuple[list[int], list[int]] | None:
        """
        Two distinct pairs from (at least) 4 dice.
        Returns 4 indices: first pair then second pair, highest values first.
        """
        from collections import defaultdict

        groups: dict[int, list[int]] = defaultdict(list)
        for idx, val in enumerate(pool):
            groups[val].append(idx)

        pairs = sorted(
            [(v, idxs) for v, idxs in groups.items() if len(idxs) >= 2],
            key=lambda x: x[0],
            reverse=True,
        )

        if len(pairs) < 2:
            return None

        (v1, idxs1), (v2, idxs2) = pairs[0], pairs[1]
        indices = idxs1[:2] + idxs2[:2]
        values = [v1, v1, v2, v2]
        return indices, values

    def _detect_high_die(self, pool: list[int]) -> tuple[list[int], list[int]] | None:
        """Single highest die — always matches if pool is non-empty."""
        if not pool:
            return None
        best_idx = max(range(len(pool)), key=lambda i: pool[i])
        return [best_idx], [pool[best_idx]]


# ---------------------------------------------------------------------------
# ActionResolver
# ---------------------------------------------------------------------------


class ActionResolver:
    """
    Resolves a declared action into an ActionResult.

    Modifier pipeline (applied in order):
      1. Base chips/mult from hand
      2. Equipment modifiers (weapon chips, armor effects)
      3. Status effect modifiers (Cursed -1 mult, Blessed +1 mult, Inspired +10 chips)
      4. Class ability modifiers (Barbarian Rage, Wizard Overcharge, etc.)
      5. Compute score
      6. Apply action effect (damage/healing/status)
    """

    def resolve(
        self,
        action: ActionType,
        hand: Hand,
        actor: Combatant,
        targets: list[Combatant],
        encounter: CombatEncounter,
        *,
        rage_strike: bool = False,
    ) -> ActionResult:
        """
        Resolve `action` for `actor` against `targets` inside `encounter`.

        `rage_strike=True` activates the Barbarian Rage Strike alternative
        scoring (chips=15, mult=2) and skips the normal hand evaluation.
        """
        logger.debug(
            "ActionResolver.resolve: action=%s actor=%s rage_strike=%s",
            action.name,
            actor.name,
            rage_strike,
        )

        chips, mult = self._base_scoring(hand, rage_strike)
        chips, mult = self._apply_equipment_modifiers(chips, mult, actor, action)
        chips, mult = self._apply_status_modifiers(chips, mult, actor)
        chips, mult = self._apply_class_modifiers(chips, mult, actor, hand, action)

        score = (chips + sum(hand.scoring_values)) * mult
        logger.debug("ActionResolver: chips=%d mult=%d score=%d", chips, mult, score)

        messages: list[str] = []
        damage_dealt: dict[str, int] = {}
        healing_done: dict[str, int] = {}
        temp_hp_gained = 0
        dice_recovered = 0

        # Apply the action's effect based on its category.
        if action in (
            ActionType.QUICK_STRIKE,
            ActionType.HEAVY_STRIKE,
            ActionType.PRECISION_STRIKE,
            ActionType.DEVASTATING_BLOW,
            ActionType.CATACLYSM,
        ):
            damage_dealt, messages = self._apply_damage(score, actor, targets)

        elif action == ActionType.BLOCK:
            # BLOCK provides temp HP equal to the score.
            actor.gain_temp_hp(score)
            temp_hp_gained = score
            messages.append(f"{actor.name} blocks — gains {score} temp HP")

        elif action == ActionType.DODGE:
            # DODGE halves incoming damage until next turn; represented as a
            # short-lived status (duration=1 means it expires at their next tick).
            actor.apply_status(StatusEffect(StatusEffectType.BLESSED, duration=1))
            messages.append(f"{actor.name} dodges — BLESSED for 1 turn")

        elif action == ActionType.BRACE:
            # BRACE provides a large temp HP buffer.
            actor.gain_temp_hp(score)
            temp_hp_gained = score
            messages.append(f"{actor.name} braces — gains {score} temp HP")

        elif action == ActionType.HEAL:
            heal_amount = score
            actor.heal(heal_amount)
            healing_done[str(actor.id)] = heal_amount
            messages.append(f"{actor.name} heals for {heal_amount} HP")

        elif action == ActionType.AID:
            # AID heals a target.
            for target in targets:
                target.heal(score)
                healing_done[str(target.id)] = score
                messages.append(f"{actor.name} aids {target.name} for {score} HP")

        elif action == ActionType.RALLY:
            # RALLY heals all player combatants for a smaller amount.
            rally_amount = score // max(1, len(targets))
            for target in targets:
                target.heal(rally_amount)
                healing_done[str(target.id)] = rally_amount
                messages.append(
                    f"{actor.name} rallies {target.name} for {rally_amount} HP"
                )

        elif action == ActionType.CAST_SPELL:
            damage_dealt, messages = self._apply_damage(score, actor, targets)
            # Barbarian Fury: if their fury_bonus_active was triggered pre-call,
            # it is already baked into chips/mult above.

        elif action == ActionType.DISRUPT:
            # DISRUPT deals half score as damage and applies CURSED to one target.
            for target in targets:
                dmg = score // 2
                target.take_damage(dmg)
                damage_dealt[str(target.id)] = dmg
                target.apply_status(StatusEffect(StatusEffectType.CURSED, duration=2))
                messages.append(
                    f"{actor.name} disrupts {target.name} for {dmg} dmg and CURSED 2 turns"
                )

        elif action == ActionType.FLEE:
            encounter.status = CombatStatus.FLED
            messages.append(f"{actor.name} flees — combat ends")

        elif action == ActionType.REST:
            # REST recovers 3 dice from discard.
            recover_count = min(3, len(actor.discard))
            recovered = actor.discard[-recover_count:]
            actor.discard = (
                actor.discard[:-recover_count] if recover_count else actor.discard
            )
            actor.recover_dice(recovered)
            dice_recovered = recover_count
            messages.append(f"{actor.name} rests — recovers {recover_count} dice")

        # Cleric Blessed Hands: any hand containing a Pair recovers 1 extra die.
        if (
            actor.class_type == ClassType.CLERIC
            and hand.hand_type is not None
            and hand.hand_type.value >= HandType.PAIR.value
        ):
            dice_recovered += 1
            messages.append(f"{actor.name} Blessed Hands — will recover 1 extra die")

        # Update actor's last_hand_type for Escalation Die relic.
        actor.last_hand_type = hand.hand_type

        return ActionResult(
            action_type=action,
            hand_type=hand.hand_type,
            score=score,
            damage_dealt=damage_dealt,
            healing_done=healing_done,
            temp_hp_gained=temp_hp_gained,
            messages=messages,
            dice_recovered=dice_recovered,
        )

    # ------------------------------------------------------------------
    # Private modifier helpers
    # ------------------------------------------------------------------

    def _base_scoring(self, hand: Hand, rage_strike: bool) -> tuple[int, int]:
        """Return (chips, mult). Rage Strike overrides hand values."""
        if rage_strike:
            # Barbarian Rage Strike: fixed chips=15, mult=2 regardless of hand.
            return 15, 2
        return hand.base_chips, hand.mult

    def _apply_equipment_modifiers(
        self,
        chips: int,
        mult: int,
        actor: Combatant,
        action: ActionType,
    ) -> tuple[int, int]:
        """
        Apply weapon/armor/accessory bonuses.
        Items are identified by name string; each known item grants a bonus.
        Only attack actions benefit from weapon chips.
        """
        attack_actions = {
            ActionType.QUICK_STRIKE,
            ActionType.HEAVY_STRIKE,
            ActionType.PRECISION_STRIKE,
            ActionType.DEVASTATING_BLOW,
            ActionType.CATACLYSM,
            ActionType.CAST_SPELL,
        }

        weapon = actor.equipment.weapon
        if weapon and action in attack_actions:
            bonus = _WEAPON_CHIPS.get(weapon, 0)
            chips += bonus
            if bonus:
                logger.debug("Equipment weapon '%s' +%d chips", weapon, bonus)

        accessory = actor.equipment.accessory
        if accessory:
            acc_chips, acc_mult = _ACCESSORY_BONUSES.get(accessory, (0, 0))
            chips += acc_chips
            mult += acc_mult
            if acc_chips or acc_mult:
                logger.debug(
                    "Equipment accessory '%s' +%d chips +%d mult",
                    accessory,
                    acc_chips,
                    acc_mult,
                )

        return chips, mult

    def _apply_status_modifiers(
        self, chips: int, mult: int, actor: Combatant
    ) -> tuple[int, int]:
        """CURSED: -1 mult. BLESSED: +1 mult. INSPIRED: +10 chips."""
        for effect in actor.status_effects:
            if effect.effect_type == StatusEffectType.CURSED:
                mult = max(1, mult - 1)
                logger.debug("Status CURSED -1 mult → %d", mult)
            elif effect.effect_type == StatusEffectType.BLESSED:
                mult += 1
                logger.debug("Status BLESSED +1 mult → %d", mult)
            elif effect.effect_type == StatusEffectType.INSPIRED:
                chips += 10
                logger.debug("Status INSPIRED +10 chips → %d", chips)
        return chips, mult

    def _apply_class_modifiers(
        self,
        chips: int,
        mult: int,
        actor: Combatant,
        hand: Hand,
        action: ActionType,
    ) -> tuple[int, int]:
        """Apply class-specific passive bonuses that affect the score."""
        if actor.class_type == ClassType.WIZARD:
            # Overcharge: Five of a Kind doubles the final mult.
            if hand.hand_type == HandType.FIVE_OF_A_KIND:
                mult *= 2
                logger.debug("Wizard Overcharge Five-of-a-Kind ×2 mult → %d", mult)

        if actor.class_type == ClassType.BARBARIAN and actor.fury_bonus_active:
            # Fury bonus accumulated from prior Spell actions.
            chips += actor.fury_chips_bonus
            mult += actor.fury_mult_bonus
            logger.debug(
                "Barbarian Fury +%d chips +%d mult",
                actor.fury_chips_bonus,
                actor.fury_mult_bonus,
            )

        return chips, mult

    def _apply_damage(
        self,
        score: int,
        actor: Combatant,
        targets: list[Combatant],
    ) -> tuple[dict[str, int], list[str]]:
        """Deal score damage split evenly across targets (floor division)."""
        damage_dealt: dict[str, int] = {}
        messages: list[str] = []
        if not targets:
            return damage_dealt, messages
        dmg = score // len(targets)
        for target in targets:
            target.take_damage(dmg)
            damage_dealt[str(target.id)] = dmg
            messages.append(f"{actor.name} deals {dmg} to {target.name}")
        return damage_dealt, messages


# ---------------------------------------------------------------------------
# Equipment lookup tables
# These define the numeric effects of named items.
# New items can be added here without changing any resolver logic.
# ---------------------------------------------------------------------------

_WEAPON_CHIPS: dict[str, int] = {
    "Iron Sword": 5,
    "Silver Blade": 10,
    "Cursed Dagger": 8,
    "Battle Axe": 12,
    "Staff of Sparks": 7,
}

_ACCESSORY_BONUSES: dict[str, tuple[int, int]] = {
    # name → (chips_bonus, mult_bonus)
    "Lucky Charm": (5, 0),
    "Power Ring": (0, 1),
    "Blood Pact Pendant": (10, 0),
    "Glass Cannon Amulet": (15, -1),
}

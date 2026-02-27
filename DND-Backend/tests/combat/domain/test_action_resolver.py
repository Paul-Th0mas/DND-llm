"""
Tests for ActionResolver — scoring formula, equipment modifiers,
class ability hooks, and correct exception raising.
"""

import uuid

import pytest

from app.combat.domain.exceptions import InvalidActionError
from app.combat.domain.models import (
    HAND_SCORING,
    ActionResult,
    ActionType,
    ClassType,
    CombatEncounter,
    CombatStatus,
    Combatant,
    CombatantType,
    DieType,
    Equipment,
    Hand,
    HandType,
    StatusEffect,
    StatusEffectType,
)
from app.combat.domain.services import ActionResolver


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_combatant(
    class_type: ClassType | None = None,
    hp: int = 50,
    equipment: Equipment | None = None,
    status_effects: list[StatusEffect] | None = None,
) -> Combatant:
    return Combatant(
        id=uuid.uuid4(),
        name="Actor",
        combatant_type=CombatantType.PLAYER,
        class_type=class_type,
        die_type=DieType.D10,
        max_pool_size=5,
        hp=hp,
        max_hp=hp,
        temp_hp=0,
        pool=[5, 5, 5, 5, 5],
        discard=[],
        status_effects=status_effects or [],
        initiative=10,
        equipment=equipment or Equipment(),
        wild_tokens=0,
        relics=[],
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


def _make_enemy(hp: int = 30) -> Combatant:
    return Combatant(
        id=uuid.uuid4(),
        name="Goblin",
        combatant_type=CombatantType.ENEMY,
        class_type=None,
        die_type=DieType.D8,
        max_pool_size=4,
        hp=hp,
        max_hp=hp,
        temp_hp=0,
        pool=[3, 3, 3, 3],
        discard=[],
        status_effects=[],
        initiative=5,
        equipment=Equipment(),
        wild_tokens=0,
        relics=[],
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


def _make_encounter(actor: Combatant, enemy: Combatant) -> CombatEncounter:
    return CombatEncounter(
        id=uuid.uuid4(),
        room_id=None,
        combatants=[actor, enemy],
        round=1,
        turn_order=[actor.id, enemy.id],
        current_turn_index=0,
        status=CombatStatus.ACTIVE,
    )


def _pair_hand(values: tuple[int, int] = (5, 5)) -> Hand:
    base_chips, mult = HAND_SCORING[HandType.PAIR]
    return Hand(
        hand_type=HandType.PAIR,
        scoring_indices=(0, 1),
        scoring_values=values,
        base_chips=base_chips,
        mult=mult,
    )


def _five_of_a_kind_hand(value: int = 8) -> Hand:
    base_chips, mult = HAND_SCORING[HandType.FIVE_OF_A_KIND]
    return Hand(
        hand_type=HandType.FIVE_OF_A_KIND,
        scoring_indices=(0, 1, 2, 3, 4),
        scoring_values=(value,) * 5,
        base_chips=base_chips,
        mult=mult,
    )


# ---------------------------------------------------------------------------
# Scoring formula
# ---------------------------------------------------------------------------


def test_score_formula_pair() -> None:
    """Score = (base_chips + sum(scoring_values)) * mult."""
    resolver = ActionResolver()
    actor = _make_combatant()
    enemy = _make_enemy()
    encounter = _make_encounter(actor, enemy)
    hand = _pair_hand((6, 6))

    result = resolver.resolve(ActionType.QUICK_STRIKE, hand, actor, [enemy], encounter)

    expected_score = (10 + 6 + 6) * 2
    assert result.score == expected_score


def test_damage_dealt_equals_score_for_single_target() -> None:
    resolver = ActionResolver()
    actor = _make_combatant()
    enemy = _make_enemy(hp=100)
    encounter = _make_encounter(actor, enemy)
    hand = _pair_hand((5, 5))

    result = resolver.resolve(ActionType.QUICK_STRIKE, hand, actor, [enemy], encounter)

    assert result.damage_dealt[str(enemy.id)] == result.score


# ---------------------------------------------------------------------------
# Equipment chip bonus
# ---------------------------------------------------------------------------


def test_weapon_chips_added_on_attack() -> None:
    resolver = ActionResolver()
    actor_no_weapon = _make_combatant()
    actor_with_weapon = _make_combatant(equipment=Equipment(weapon="Iron Sword"))
    enemy1 = _make_enemy(hp=200)
    enemy2 = _make_enemy(hp=200)
    enc1 = _make_encounter(actor_no_weapon, enemy1)
    enc2 = _make_encounter(actor_with_weapon, enemy2)
    hand = _pair_hand((5, 5))

    result_plain = resolver.resolve(
        ActionType.QUICK_STRIKE, hand, actor_no_weapon, [enemy1], enc1
    )
    result_weapon = resolver.resolve(
        ActionType.QUICK_STRIKE, hand, actor_with_weapon, [enemy2], enc2
    )

    # Iron Sword adds +5 chips so score should be higher.
    assert result_weapon.score > result_plain.score


# ---------------------------------------------------------------------------
# Status effect modifiers
# ---------------------------------------------------------------------------


def test_cursed_reduces_mult() -> None:
    resolver = ActionResolver()
    # Pair mult is 2; CURSED makes it max(1, 2-1)=1
    cursed_effect = StatusEffect(effect_type=StatusEffectType.CURSED, duration=2)
    actor = _make_combatant(status_effects=[cursed_effect])
    enemy = _make_enemy(hp=200)
    encounter = _make_encounter(actor, enemy)
    hand = _pair_hand((5, 5))

    result = resolver.resolve(ActionType.QUICK_STRIKE, hand, actor, [enemy], encounter)

    # With CURSED: (10 + 10) * 1 = 20
    assert result.score == (10 + 5 + 5) * 1


def test_blessed_increases_mult() -> None:
    resolver = ActionResolver()
    blessed_effect = StatusEffect(effect_type=StatusEffectType.BLESSED, duration=1)
    actor = _make_combatant(status_effects=[blessed_effect])
    enemy = _make_enemy(hp=200)
    encounter = _make_encounter(actor, enemy)
    hand = _pair_hand((5, 5))

    result = resolver.resolve(ActionType.QUICK_STRIKE, hand, actor, [enemy], encounter)

    # BLESSED +1 mult: (10 + 10) * 3 = 60
    assert result.score == (10 + 5 + 5) * 3


# ---------------------------------------------------------------------------
# Barbarian Rage Strike
# ---------------------------------------------------------------------------


def test_rage_strike_uses_fixed_chips_mult() -> None:
    """Rage Strike overrides scoring to chips=15, mult=2 regardless of hand."""
    resolver = ActionResolver()
    actor = _make_combatant(class_type=ClassType.BARBARIAN)
    enemy = _make_enemy(hp=200)
    encounter = _make_encounter(actor, enemy)
    # Provide a THREE_OF_A_KIND hand as placeholder (values used in score calc).
    base, mult = HAND_SCORING[HandType.THREE_OF_A_KIND]
    rage_hand = Hand(
        hand_type=HandType.THREE_OF_A_KIND,
        scoring_indices=(0, 1, 2),
        scoring_values=(4, 4, 4),
        base_chips=base,
        mult=mult,
    )

    result = resolver.resolve(
        ActionType.QUICK_STRIKE,
        rage_hand,
        actor,
        [enemy],
        encounter,
        rage_strike=True,
    )

    # Rage Strike: (15 + 4+4+4) * 2 = 54
    assert result.score == (15 + 4 + 4 + 4) * 2


# ---------------------------------------------------------------------------
# Wizard Overcharge
# ---------------------------------------------------------------------------


def test_wizard_overcharge_doubles_mult_on_five_of_a_kind() -> None:
    """Five of a Kind → mult doubled for Wizard."""
    resolver = ActionResolver()
    actor = _make_combatant(class_type=ClassType.WIZARD)
    enemy = _make_enemy(hp=500)
    encounter = _make_encounter(actor, enemy)
    hand = _five_of_a_kind_hand(value=5)

    result = resolver.resolve(ActionType.CATACLYSM, hand, actor, [enemy], encounter)

    # FIVE_OF_A_KIND: base=100, mult=10, Overcharge doubles → mult=20
    # Score = (100 + 5*5) * 20 = (100+25)*20 = 2500
    expected = (100 + 5 * 5) * 20
    assert result.score == expected


# ---------------------------------------------------------------------------
# Cleric Blessed Hands — dice recovery flagged
# ---------------------------------------------------------------------------


def test_cleric_blessed_hands_sets_dice_recovered() -> None:
    """Any Pair-or-better hand for a Cleric should flag dice_recovered += 1."""
    resolver = ActionResolver()
    actor = _make_combatant(class_type=ClassType.CLERIC)
    encounter = _make_encounter(actor, _make_enemy())
    hand = _pair_hand()

    result = resolver.resolve(ActionType.AID, hand, actor, [actor], encounter)

    assert result.dice_recovered >= 1


# ---------------------------------------------------------------------------
# BLOCK provides temp HP
# ---------------------------------------------------------------------------


def test_block_grants_temp_hp() -> None:
    resolver = ActionResolver()
    actor = _make_combatant()
    encounter = _make_encounter(actor, _make_enemy())
    base, mult = HAND_SCORING[HandType.PAIR]
    block_hand = Hand(
        hand_type=HandType.PAIR,
        scoring_indices=(0, 1),
        scoring_values=(4, 4),
        base_chips=base,
        mult=mult,
    )

    result = resolver.resolve(ActionType.BLOCK, block_hand, actor, [], encounter)

    assert result.temp_hp_gained == result.score
    assert actor.temp_hp == result.score


# ---------------------------------------------------------------------------
# HEAL restores actor HP
# ---------------------------------------------------------------------------


def test_heal_restores_hp() -> None:
    resolver = ActionResolver()
    # hp < max_hp so there is headroom to restore.
    actor = _make_combatant(hp=20, equipment=Equipment())
    actor.max_hp = 50
    encounter = _make_encounter(actor, _make_enemy())
    base, mult = HAND_SCORING[HandType.TWO_PAIR]
    heal_hand = Hand(
        hand_type=HandType.TWO_PAIR,
        scoring_indices=(0, 1, 2, 3),
        scoring_values=(3, 3, 5, 5),
        base_chips=base,
        mult=mult,
    )

    resolver.resolve(ActionType.HEAL, heal_hand, actor, [], encounter)

    assert actor.hp > 20

"""
Tests for Combatant aggregate methods.

Covers: spend_dice, recover_dice, take_damage (with/without temp HP),
heal (clamped at max), status ticking, is_downed, is_exhausted.
"""

import uuid

import pytest

from app.combat.domain.models import (
    ClassType,
    Combatant,
    CombatantType,
    DieType,
    Equipment,
    StatusEffect,
    StatusEffectType,
)


def _make_combatant(
    pool: list[int] | None = None,
    hp: int = 30,
    max_hp: int = 30,
    temp_hp: int = 0,
    discard: list[int] | None = None,
) -> Combatant:
    return Combatant(
        id=uuid.uuid4(),
        name="Test",
        combatant_type=CombatantType.PLAYER,
        class_type=ClassType.FIGHTER,
        die_type=DieType.D10,
        max_pool_size=5,
        hp=hp,
        max_hp=max_hp,
        temp_hp=temp_hp,
        pool=pool if pool is not None else [3, 5, 7, 2, 8],
        discard=discard if discard is not None else [],
        status_effects=[],
        initiative=10,
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


# ---------------------------------------------------------------------------
# spend_dice
# ---------------------------------------------------------------------------


def test_spend_dice_removes_from_pool() -> None:
    c = _make_combatant(pool=[3, 5, 7])

    c.spend_dice([1])

    assert 5 not in c.pool
    assert len(c.pool) == 2


def test_spend_dice_adds_to_discard() -> None:
    c = _make_combatant(pool=[3, 5, 7])

    c.spend_dice([0, 2])

    assert sorted(c.discard) == [3, 7]


def test_spend_dice_invalid_index_raises() -> None:
    c = _make_combatant(pool=[1, 2, 3])

    with pytest.raises(ValueError):
        c.spend_dice([5])


def test_spend_dice_empty_list_returns_empty() -> None:
    c = _make_combatant(pool=[4, 6])

    result = c.spend_dice([])

    assert result == []
    assert c.pool == [4, 6]


# ---------------------------------------------------------------------------
# recover_dice
# ---------------------------------------------------------------------------


def test_recover_dice_adds_to_pool() -> None:
    c = _make_combatant(pool=[], discard=[5, 7])

    c.recover_dice([5, 7])

    assert c.pool == [5, 7]


# ---------------------------------------------------------------------------
# take_damage
# ---------------------------------------------------------------------------


def test_take_damage_reduces_hp() -> None:
    c = _make_combatant(hp=30)

    c.take_damage(10)

    assert c.hp == 20


def test_take_damage_absorbs_temp_hp_first() -> None:
    c = _make_combatant(hp=30, temp_hp=5)

    c.take_damage(8)

    assert c.temp_hp == 0
    assert c.hp == 27  # 5 absorbed, 3 passed through


def test_take_damage_hp_does_not_go_below_zero() -> None:
    c = _make_combatant(hp=5)

    c.take_damage(100)

    assert c.hp == 0


def test_take_damage_temp_hp_fully_absorbs() -> None:
    c = _make_combatant(hp=30, temp_hp=20)

    c.take_damage(15)

    assert c.temp_hp == 5
    assert c.hp == 30


# ---------------------------------------------------------------------------
# heal
# ---------------------------------------------------------------------------


def test_heal_restores_hp() -> None:
    c = _make_combatant(hp=10, max_hp=30)

    c.heal(15)

    assert c.hp == 25


def test_heal_clamped_at_max_hp() -> None:
    c = _make_combatant(hp=28, max_hp=30)

    c.heal(10)

    assert c.hp == 30


# ---------------------------------------------------------------------------
# is_downed / is_exhausted
# ---------------------------------------------------------------------------


def test_is_downed_when_hp_zero() -> None:
    c = _make_combatant(hp=0)

    assert c.is_downed() is True


def test_is_not_downed_when_hp_positive() -> None:
    c = _make_combatant(hp=1)

    assert c.is_downed() is False


def test_is_exhausted_when_pool_empty() -> None:
    c = _make_combatant(pool=[])

    assert c.is_exhausted() is True


def test_is_not_exhausted_when_pool_has_dice() -> None:
    c = _make_combatant(pool=[3])

    assert c.is_exhausted() is False


# ---------------------------------------------------------------------------
# Status effects
# ---------------------------------------------------------------------------


def test_apply_status_adds_effect() -> None:
    c = _make_combatant()
    effect = StatusEffect(effect_type=StatusEffectType.BURNING, duration=2)

    c.apply_status(effect)

    assert any(e.effect_type == StatusEffectType.BURNING for e in c.status_effects)


def test_apply_status_replaces_same_type() -> None:
    c = _make_combatant()
    c.apply_status(StatusEffect(effect_type=StatusEffectType.CURSED, duration=1))
    c.apply_status(StatusEffect(effect_type=StatusEffectType.CURSED, duration=3))

    cursed_effects = [
        e for e in c.status_effects if e.effect_type == StatusEffectType.CURSED
    ]
    assert len(cursed_effects) == 1
    assert cursed_effects[0].duration == 3


def test_tick_status_decrements_duration() -> None:
    c = _make_combatant()
    c.apply_status(StatusEffect(effect_type=StatusEffectType.FROZEN, duration=2))

    c.tick_status_effects()

    frozen = next(
        e for e in c.status_effects if e.effect_type == StatusEffectType.FROZEN
    )
    assert frozen.duration == 1


def test_tick_status_removes_expired_effect() -> None:
    c = _make_combatant()
    c.apply_status(StatusEffect(effect_type=StatusEffectType.FROZEN, duration=1))

    c.tick_status_effects()

    assert not any(e.effect_type == StatusEffectType.FROZEN for e in c.status_effects)


def test_tick_burning_deals_damage() -> None:
    c = _make_combatant(hp=30)
    c.apply_status(StatusEffect(effect_type=StatusEffectType.BURNING, duration=2))

    c.tick_status_effects()

    assert c.hp == 28  # 2 burning damage


def test_tick_permanent_status_stays() -> None:
    c = _make_combatant()
    c.apply_status(StatusEffect(effect_type=StatusEffectType.BLESSED, duration=-1))

    c.tick_status_effects()

    assert any(
        e.effect_type == StatusEffectType.BLESSED and e.duration == -1
        for e in c.status_effects
    )

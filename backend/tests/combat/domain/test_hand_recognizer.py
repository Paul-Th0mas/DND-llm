"""
Tests for HandRecognizer — all 10 hand types, edge cases, and invalid pools.
"""

import pytest

from app.combat.domain.models import HandType
from app.combat.domain.services import HandRecognizer


@pytest.fixture()
def recognizer() -> HandRecognizer:
    return HandRecognizer()


# ---------------------------------------------------------------------------
# identify_best_hand — all 10 hand types
# ---------------------------------------------------------------------------


def test_five_of_a_kind(recognizer: HandRecognizer) -> None:
    hand = recognizer.identify_best_hand([7, 7, 7, 7, 7])

    assert hand is not None
    assert hand.hand_type == HandType.FIVE_OF_A_KIND


def test_four_of_a_kind(recognizer: HandRecognizer) -> None:
    hand = recognizer.identify_best_hand([5, 5, 5, 5, 2])

    assert hand is not None
    assert hand.hand_type == HandType.FOUR_OF_A_KIND


def test_run_5(recognizer: HandRecognizer) -> None:
    hand = recognizer.identify_best_hand([3, 4, 5, 6, 7])

    assert hand is not None
    assert hand.hand_type == HandType.RUN_5


def test_full_house(recognizer: HandRecognizer) -> None:
    hand = recognizer.identify_best_hand([8, 8, 8, 3, 3])

    assert hand is not None
    assert hand.hand_type == HandType.FULL_HOUSE


def test_run_4(recognizer: HandRecognizer) -> None:
    hand = recognizer.identify_best_hand([2, 3, 4, 5, 9])

    assert hand is not None
    assert hand.hand_type == HandType.RUN_4


def test_three_of_a_kind(recognizer: HandRecognizer) -> None:
    hand = recognizer.identify_best_hand([6, 6, 6, 1, 9])

    assert hand is not None
    assert hand.hand_type == HandType.THREE_OF_A_KIND


def test_two_pair(recognizer: HandRecognizer) -> None:
    hand = recognizer.identify_best_hand([4, 4, 7, 7, 1])

    assert hand is not None
    assert hand.hand_type == HandType.TWO_PAIR


def test_run_3(recognizer: HandRecognizer) -> None:
    hand = recognizer.identify_best_hand([5, 6, 7, 1, 1])

    # Note: [1,1] is a Pair which ranks below RUN_3 — best hand is RUN_3.
    assert hand is not None
    assert hand.hand_type == HandType.RUN_3


def test_pair(recognizer: HandRecognizer) -> None:
    hand = recognizer.identify_best_hand([3, 3, 1, 5, 9])

    assert hand is not None
    assert hand.hand_type == HandType.PAIR


def test_high_die(recognizer: HandRecognizer) -> None:
    hand = recognizer.identify_best_hand([1, 3, 5, 7, 9])

    assert hand is not None
    assert hand.hand_type == HandType.HIGH_DIE


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_empty_pool_returns_none(recognizer: HandRecognizer) -> None:
    hand = recognizer.identify_best_hand([])

    assert hand is None


def test_single_die_returns_high_die(recognizer: HandRecognizer) -> None:
    hand = recognizer.identify_best_hand([8])

    assert hand is not None
    assert hand.hand_type == HandType.HIGH_DIE


def test_run_with_gap_is_not_a_run(recognizer: HandRecognizer) -> None:
    """[1, 2, 4, 5, 6] has a gap at 3 — best 3-run is [4,5,6]."""
    hand = recognizer.identify_best_hand([1, 2, 4, 5, 6])

    assert hand is not None
    # 4-5-6 is a valid run of 3; 1-2 is a pair; best overall is RUN_3.
    assert hand.hand_type == HandType.RUN_3


def test_full_house_detected_over_three_of_a_kind(recognizer: HandRecognizer) -> None:
    """[9,9,9,2,2] must be FULL_HOUSE, not THREE_OF_A_KIND."""
    hand = recognizer.identify_best_hand([9, 9, 9, 2, 2])

    assert hand is not None
    assert hand.hand_type == HandType.FULL_HOUSE


def test_five_of_a_kind_beats_run_5(recognizer: HandRecognizer) -> None:
    """If pool somehow had 5-of-a-kind that could also be read as a run, 5oK wins."""
    # Pure 5oK pool — no run possible with duplicate values.
    hand = recognizer.identify_best_hand([4, 4, 4, 4, 4])

    assert hand is not None
    assert hand.hand_type == HandType.FIVE_OF_A_KIND


def test_score_formula(recognizer: HandRecognizer) -> None:
    """Hand.score() == (base_chips + sum(scoring_values)) * mult."""
    # PAIR: base_chips=10, mult=2, values=[7, 7] → (10 + 14) * 2 = 48
    hand = recognizer.identify_best_hand([7, 7, 1, 3])

    assert hand is not None
    assert hand.hand_type == HandType.PAIR
    assert hand.score() == (10 + 7 + 7) * 2


def test_scoring_indices_point_to_correct_pool_positions(
    recognizer: HandRecognizer,
) -> None:
    pool = [1, 5, 5, 3]
    hand = recognizer.identify_best_hand(pool)

    assert hand is not None
    for idx, val in zip(hand.scoring_indices, hand.scoring_values):
        assert pool[idx] == val


# ---------------------------------------------------------------------------
# identify_from_indices
# ---------------------------------------------------------------------------


def test_identify_from_indices_finds_pair() -> None:
    pool = [1, 8, 8, 3, 5]
    recognizer = HandRecognizer()

    hand = recognizer.identify_from_indices(pool, [1, 2])

    assert hand is not None
    assert hand.hand_type == HandType.PAIR
    # Scoring indices must map back to the full pool.
    assert set(hand.scoring_indices).issubset({1, 2})


def test_identify_from_indices_empty_returns_none() -> None:
    recognizer = HandRecognizer()

    hand = recognizer.identify_from_indices([1, 2, 3], [])

    assert hand is None


# ---------------------------------------------------------------------------
# can_form_hand_for_action
# ---------------------------------------------------------------------------


def test_can_form_hand_for_quick_strike_with_pair(recognizer: HandRecognizer) -> None:
    from app.combat.domain.models import ActionType

    result = recognizer.can_form_hand_for_action([4, 4, 1, 2], ActionType.QUICK_STRIKE)

    assert result is True


def test_cannot_form_hand_for_heavy_strike_with_only_pair(
    recognizer: HandRecognizer,
) -> None:
    from app.combat.domain.models import ActionType

    result = recognizer.can_form_hand_for_action([4, 4, 1, 2], ActionType.HEAVY_STRIKE)

    assert result is False


def test_free_action_always_possible(recognizer: HandRecognizer) -> None:
    from app.combat.domain.models import ActionType

    assert recognizer.can_form_hand_for_action([], ActionType.FLEE) is True
    assert recognizer.can_form_hand_for_action([], ActionType.REST) is True
    assert recognizer.can_form_hand_for_action([], ActionType.REROLL) is True

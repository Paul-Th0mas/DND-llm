"""
Combat domain models.

Contains all enums, value objects, and the two aggregates:
  - Combatant  — a single participant (player or enemy)
  - CombatEncounter — aggregate root; owns the list of combatants and tracks
    turn order, round number, and overall combat status.

No SQLAlchemy or FastAPI imports belong here. This is pure Python domain logic.
"""

import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class DieType(int, Enum):
    """The faces on a die. Value doubles as the max roll (e.g. D8 → 1-8)."""

    D8 = 8
    D10 = 10
    D12 = 12
    D20 = 20


class HandType(Enum):
    """
    Poker-style hand ranks, ordered from weakest to strongest.
    The integer values are used for rank comparisons in HandRecognizer.
    """

    HIGH_DIE = 1
    PAIR = 2
    TWO_PAIR = 3
    RUN_3 = 4
    THREE_OF_A_KIND = 5
    RUN_4 = 6
    FULL_HOUSE = 7
    RUN_5 = 8
    FOUR_OF_A_KIND = 9
    FIVE_OF_A_KIND = 10


class ActionType(Enum):
    """Every action a combatant may declare on their turn."""

    # Attack actions
    QUICK_STRIKE = auto()
    HEAVY_STRIKE = auto()
    PRECISION_STRIKE = auto()
    DEVASTATING_BLOW = auto()
    CATACLYSM = auto()
    # Defense / utility actions
    BLOCK = auto()
    DODGE = auto()
    BRACE = auto()
    HEAL = auto()
    AID = auto()
    RALLY = auto()
    CAST_SPELL = auto()
    # Meta actions (no hand requirement)
    REROLL = auto()
    FLEE = auto()
    REST = auto()
    DISRUPT = auto()


class ClassType(Enum):
    """Player character classes, each with unique ability hooks."""

    FIGHTER = auto()
    BARBARIAN = auto()
    ROGUE = auto()
    WIZARD = auto()
    CLERIC = auto()
    RANGER = auto()
    BARD = auto()


class CombatantType(Enum):
    PLAYER = auto()
    ENEMY = auto()


class CombatStatus(Enum):
    """Overall state of the encounter."""

    ACTIVE = auto()
    VICTORY = auto()  # all enemies downed
    DEFEAT = auto()  # all players downed
    FLED = auto()  # a player used FLEE


class StatusEffectType(Enum):
    BURNING = auto()
    FROZEN = auto()
    CURSED = auto()
    POISONED = auto()
    BLESSED = auto()
    INSPIRED = auto()


# ---------------------------------------------------------------------------
# Hand scoring table
#
# Keyed by HandType; value is (base_chips, mult).
# ActionResolver and HandRecognizer both read from this table so the numbers
# live in exactly one place.
# ---------------------------------------------------------------------------

HAND_SCORING: dict[HandType, tuple[int, int]] = {
    HandType.HIGH_DIE: (5, 1),
    HandType.PAIR: (10, 2),
    HandType.TWO_PAIR: (20, 2),
    HandType.RUN_3: (20, 3),
    HandType.THREE_OF_A_KIND: (30, 3),
    HandType.RUN_4: (30, 4),
    HandType.FULL_HOUSE: (40, 4),
    HandType.RUN_5: (40, 5),
    HandType.FOUR_OF_A_KIND: (60, 7),
    HandType.FIVE_OF_A_KIND: (100, 10),
}

# Minimum hand required to declare each action.
# REROLL, FLEE, REST have no requirement (not in this table).
ACTION_HAND_REQUIREMENTS: dict[ActionType, HandType | None] = {
    ActionType.QUICK_STRIKE: HandType.PAIR,
    ActionType.HEAVY_STRIKE: HandType.THREE_OF_A_KIND,
    ActionType.PRECISION_STRIKE: HandType.RUN_3,
    ActionType.DEVASTATING_BLOW: HandType.FOUR_OF_A_KIND,
    ActionType.CATACLYSM: HandType.FIVE_OF_A_KIND,
    ActionType.BLOCK: None,  # any 2 dice
    ActionType.DODGE: HandType.RUN_3,
    ActionType.BRACE: HandType.FULL_HOUSE,
    ActionType.HEAL: HandType.TWO_PAIR,
    ActionType.AID: HandType.PAIR,
    ActionType.RALLY: HandType.THREE_OF_A_KIND,
    ActionType.CAST_SPELL: HandType.FULL_HOUSE,
    ActionType.DISRUPT: HandType.PAIR,
    ActionType.REROLL: None,
    ActionType.FLEE: None,
    ActionType.REST: None,
}


# ---------------------------------------------------------------------------
# Value Objects  (frozen — identity comes from content, not reference)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Hand:
    """
    The result of hand recognition: which hand was found and where.

    scoring_indices — positions in the pool list that form the hand.
    scoring_values  — the actual die values at those positions.
    base_chips / mult come from HAND_SCORING and are pre-populated by
    HandRecognizer so callers never have to look them up separately.
    """

    hand_type: HandType
    scoring_indices: tuple[int, ...]
    scoring_values: tuple[int, ...]
    base_chips: int
    mult: int

    def score(self) -> int:
        """(base_chips + sum of scoring die values) × mult."""
        return (self.base_chips + sum(self.scoring_values)) * self.mult


@dataclass(frozen=True)
class StatusEffect:
    """An active status on a combatant. duration=-1 means until cured."""

    effect_type: StatusEffectType
    duration: int  # turns remaining; -1 = permanent until cured


@dataclass(frozen=True)
class Equipment:
    """
    A combatant's equipped items. Each slot is optional.
    Concrete item names are treated as opaque strings; ActionResolver
    applies their numeric effects based on a lookup.
    """

    weapon: str | None = None
    armor: str | None = None
    accessory: str | None = None


@dataclass(frozen=True)
class ActionResult:
    """
    The resolved outcome of a single action.
    Produced by ActionResolver and returned through the application layer
    to the API response.
    """

    action_type: ActionType
    hand_type: HandType | None
    score: int
    # combatant id (as string) → damage or healing amount
    damage_dealt: dict[str, int]
    healing_done: dict[str, int]
    temp_hp_gained: int
    messages: list[str]  # human-readable combat log entries
    dice_recovered: int  # extra dice moved from discard → pool (e.g. Cleric)


# ---------------------------------------------------------------------------
# Combatant aggregate
# ---------------------------------------------------------------------------


@dataclass
class Combatant:
    """
    A single participant in combat. Tracks dice pool, HP, status effects,
    and all class-specific one-time-use flags.

    This is an aggregate: it enforces its own invariants (e.g. HP never
    goes below 0, spend_dice validates indices).
    """

    id: uuid.UUID
    name: str
    combatant_type: CombatantType
    class_type: ClassType | None
    die_type: DieType
    max_pool_size: int
    hp: int
    max_hp: int
    temp_hp: int
    pool: list[int]  # dice currently available to play
    discard: list[int]  # spent dice
    status_effects: list[StatusEffect]
    initiative: int
    equipment: Equipment
    wild_tokens: int  # Wizard: 3 per encounter, used to force a die value
    relics: list[str]
    # --- per-turn / per-encounter flags ---
    free_reroll_used: bool  # Fighter: one free single-die reroll per turn
    second_wind_used: bool  # Fighter: once per encounter self-heal
    case_joint_used: bool  # Rogue: once per encounter twin strike variant
    sanctuary_used: bool  # Cleric: once per encounter invulnerability
    discordant_used: bool  # Bard: once per encounter Discordant Note
    fury_bonus_active: bool  # Barbarian: set after a Spell that triggers Rage
    fury_chips_bonus: int
    fury_mult_bonus: int
    escalation_count: int  # Escalation Die relic: tracks consecutive hand improvements
    last_hand_type: HandType | None  # for Escalation Die comparison
    trap_dice: list[int]  # Ranger: face-down dice set as traps
    trap_trigger: str  # Ranger: what activates the trap
    inspire_given: bool  # Bard: whether Inspire has been used this turn

    def take_damage(self, amount: int) -> int:
        """
        Apply damage, absorbing through temp HP first.
        Returns the actual damage taken after temp HP absorption.
        HP is clamped to 0 (never goes negative).
        """
        logger.debug("Combatant %s take_damage amount=%d", self.name, amount)
        absorbed = min(self.temp_hp, amount)
        self.temp_hp -= absorbed
        remainder = amount - absorbed
        actual = min(remainder, self.hp)
        self.hp -= actual
        logger.debug(
            "Combatant %s: absorbed=%d remainder=%d hp_lost=%d new_hp=%d",
            self.name,
            absorbed,
            remainder,
            actual,
            self.hp,
        )
        return actual

    def heal(self, amount: int) -> None:
        """Restore HP up to max_hp."""
        logger.debug("Combatant %s heal amount=%d", self.name, amount)
        self.hp = min(self.hp + amount, self.max_hp)
        logger.debug("Combatant %s new_hp=%d", self.name, self.hp)

    def gain_temp_hp(self, amount: int) -> None:
        """Add temporary hit points (they do not stack — take the higher value)."""
        logger.debug("Combatant %s gain_temp_hp amount=%d", self.name, amount)
        self.temp_hp = max(self.temp_hp, amount)

    def spend_dice(self, indices: list[int]) -> list[int]:
        """
        Remove dice at the given pool indices, move them to discard, and
        return their values. Indices are consumed in descending order so
        earlier indices remain valid after each removal.

        Raises ValueError when any index is out of range.
        """
        logger.debug("Combatant %s spend_dice indices=%s", self.name, indices)
        if not indices:
            return []
        if max(indices) >= len(self.pool) or min(indices) < 0:
            raise ValueError(
                f"Invalid dice indices {indices} for pool of size {len(self.pool)}"
            )
        # Descending order prevents index shift during pop.
        spent: list[int] = []
        for idx in sorted(set(indices), reverse=True):
            spent.append(self.pool.pop(idx))
        self.discard.extend(spent)
        logger.debug(
            "Combatant %s spent=%s discard_size=%d", self.name, spent, len(self.discard)
        )
        return spent

    def reroll_dice(self, indices: list[int], new_values: list[int]) -> None:
        """
        Replace the values at the given pool indices with new_values.
        Indices and new_values must be the same length.
        """
        logger.debug(
            "Combatant %s reroll_dice indices=%s new_values=%s",
            self.name,
            indices,
            new_values,
        )
        if len(indices) != len(new_values):
            raise ValueError("indices and new_values must be the same length")
        for idx, val in zip(indices, new_values):
            self.pool[idx] = val

    def recover_dice(self, values: list[int]) -> None:
        """
        Add dice back into the pool (e.g. Cleric Blessed Hands recovery).
        Does not pull from discard — caller supplies the specific values.
        """
        logger.debug("Combatant %s recover_dice values=%s", self.name, values)
        self.pool.extend(values)

    def apply_status(self, effect: StatusEffect) -> None:
        """
        Apply a status effect. If the same effect type is already present,
        the new one replaces it (refresh / overwrite, not stack).
        """
        logger.debug(
            "Combatant %s apply_status type=%s duration=%d",
            self.name,
            effect.effect_type,
            effect.duration,
        )
        self.status_effects = [
            e for e in self.status_effects if e.effect_type != effect.effect_type
        ]
        self.status_effects.append(effect)

    def tick_status_effects(self) -> list[str]:
        """
        Called at the start of a combatant's turn.
        Decrements duration on each effect; removes effects that hit 0.
        Returns human-readable messages for each effect that fired.
        Duration -1 means permanent (never decremented here — cured by ability).
        """
        messages: list[str] = []
        remaining: list[StatusEffect] = []
        for effect in self.status_effects:
            msg = self._apply_status_effect_tick(effect)
            if msg:
                messages.append(msg)
            if effect.duration == -1 or effect.duration > 1:
                # Permanent effects stay; multi-turn effects count down.
                new_duration = (
                    effect.duration if effect.duration == -1 else effect.duration - 1
                )
                remaining.append(
                    StatusEffect(effect_type=effect.effect_type, duration=new_duration)
                )
            # duration == 1 means this was the last tick; drop it.
        self.status_effects = remaining
        return messages

    def _apply_status_effect_tick(self, effect: StatusEffect) -> str | None:
        """
        Apply the per-tick consequence of a status effect.
        Returns a log message, or None if the effect has no tick damage.
        Damage-over-time effects (BURNING, POISONED) deal 2 HP damage on tick.
        """
        if effect.effect_type == StatusEffectType.BURNING:
            self.take_damage(2)
            return f"{self.name} takes 2 burning damage"
        if effect.effect_type == StatusEffectType.POISONED:
            self.take_damage(2)
            return f"{self.name} takes 2 poison damage"
        return None

    def is_downed(self) -> bool:
        """A combatant is downed when their HP reaches 0."""
        return self.hp <= 0

    def is_exhausted(self) -> bool:
        """A combatant is exhausted when they have no dice left in their pool."""
        return len(self.pool) == 0


# ---------------------------------------------------------------------------
# CombatEncounter aggregate root
# ---------------------------------------------------------------------------


@dataclass
class CombatEncounter:
    """
    Aggregate root for a single combat encounter.

    Owns the list of combatants and is the single source of truth for
    turn order, round count, and encounter status. All mutations go through
    methods on this class — callers should not mutate combatants directly
    without going through the encounter.
    """

    id: uuid.UUID
    room_id: uuid.UUID | None
    combatants: list[Combatant]
    round: int
    # Combatant UUIDs sorted by initiative descending, set once at encounter start.
    turn_order: list[uuid.UUID]
    current_turn_index: int
    status: CombatStatus

    def get_current_actor(self) -> Combatant:
        """Return the combatant whose turn it currently is."""
        actor_id = self.turn_order[self.current_turn_index]
        return self.get_combatant(actor_id)

    def get_combatant(self, combatant_id: uuid.UUID) -> Combatant:
        """
        Look up a combatant by ID.
        Raises ValueError if the ID is not in this encounter.
        """
        for c in self.combatants:
            if c.id == combatant_id:
                return c
        raise ValueError(f"Combatant {combatant_id} not found in encounter {self.id}")

    def advance_turn(self) -> None:
        """
        Move to the next combatant in turn order.
        Wraps around to index 0 and increments the round counter when the
        full rotation is complete.
        """
        logger.debug(
            "CombatEncounter %s advance_turn current_index=%d",
            self.id,
            self.current_turn_index,
        )
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
        if self.current_turn_index == 0:
            self.round += 1
            logger.info("CombatEncounter %s new round=%d", self.id, self.round)

    def check_end_conditions(self) -> None:
        """
        Inspect combatant HP and update status to VICTORY or DEFEAT if the
        fight is over.  Called after every action that might deal damage.
        """
        players = [
            c for c in self.combatants if c.combatant_type == CombatantType.PLAYER
        ]
        enemies = [
            c for c in self.combatants if c.combatant_type == CombatantType.ENEMY
        ]

        all_players_down = all(c.is_downed() for c in players)
        all_enemies_down = all(c.is_downed() for c in enemies)

        if all_enemies_down and enemies:
            logger.info("CombatEncounter %s — VICTORY", self.id)
            self.status = CombatStatus.VICTORY
        elif all_players_down and players:
            logger.info("CombatEncounter %s — DEFEAT", self.id)
            self.status = CombatStatus.DEFEAT

    def apply_start_of_turn_effects(self) -> list[str]:
        """
        Tick status effects for the current actor and return any messages.
        Called by TakeActionUseCase before resolving the actor's action.
        """
        actor = self.get_current_actor()
        messages = actor.tick_status_effects()
        logger.debug(
            "CombatEncounter %s start-of-turn effects for %s: %s",
            self.id,
            actor.name,
            messages,
        )
        return messages

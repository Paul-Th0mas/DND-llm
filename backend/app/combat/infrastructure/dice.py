"""
Concrete DiceRoller implementation using Python's random module.

This is the real implementation used in production. Tests inject a seeded
or deterministic roller by implementing the DiceRoller protocol directly
without subclassing anything.
"""

import logging
import random

from app.combat.domain.models import DieType

logger = logging.getLogger(__name__)


class RandomDiceRoller:
    """Rolls dice using Python's random.randint."""

    def roll(self, die_type: DieType) -> int:
        result = random.randint(1, die_type.value)
        logger.debug("roll %s → %d", die_type.name, result)
        return result

    def roll_many(self, die_type: DieType, count: int) -> list[int]:
        results = [random.randint(1, die_type.value) for _ in range(count)]
        logger.debug("roll_many %s ×%d → %s", die_type.name, count, results)
        return results

"""
Abstract repository interface for the combat bounded context.

The domain defines what it needs from persistence; the infrastructure layer
provides the SQLAlchemy implementation. This keeps the domain free of any
DB knowledge.
"""

import uuid
from abc import ABC, abstractmethod

from app.combat.domain.models import CombatEncounter


class CombatRepository(ABC):
    @abstractmethod
    def get_by_id(self, encounter_id: uuid.UUID) -> CombatEncounter | None: ...

    @abstractmethod
    def save(self, encounter: CombatEncounter) -> None: ...

    @abstractmethod
    def delete(self, encounter_id: uuid.UUID) -> None: ...

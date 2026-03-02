"""
Abstract repository interfaces for the worlds bounded context.

Domain exceptions are co-located here so the domain layer owns its error vocabulary.
No SQLAlchemy or FastAPI imports belong in this file.
"""

import uuid
from abc import ABC, abstractmethod

from app.core.exceptions import DomainError, NotFoundError
from app.worlds.domain.models import (
    EnemyPreset,
    ItemPreset,
    NPCPreset,
    QuestTemplate,
    Theme,
    ThemeName,
    WorldSkeleton,
)


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------


class WorldNotFoundError(NotFoundError):
    """Raised when a WorldSkeleton cannot be found by id or room_id."""


class WorldRoomNotFoundError(NotFoundError):
    """Raised when a room_number does not exist in a WorldSkeleton."""


class ThemeNotFoundError(NotFoundError):
    """Raised when a ThemeName has no Theme record in the database."""


class WorldCompilationError(DomainError):
    """Raised when WorldCompiler cannot build a valid WorldSkeleton."""


# ---------------------------------------------------------------------------
# Repository interfaces
# ---------------------------------------------------------------------------


class ThemeRepository(ABC):
    """Abstracts persistence for Theme value objects."""

    @abstractmethod
    def get_by_name(self, name: ThemeName) -> Theme | None: ...


class PresetRepository(ABC):
    """Abstracts persistence for the four preset entity types."""

    @abstractmethod
    def get_enemies_by_theme(self, theme: ThemeName) -> list[EnemyPreset]: ...

    @abstractmethod
    def get_items_by_theme(self, theme: ThemeName) -> list[ItemPreset]: ...

    @abstractmethod
    def get_npcs_by_theme(self, theme: ThemeName) -> list[NPCPreset]: ...

    @abstractmethod
    def get_quests_by_theme(self, theme: ThemeName) -> list[QuestTemplate]: ...


class WorldSkeletonRepository(ABC):
    """Abstracts persistence for the WorldSkeleton aggregate root."""

    @abstractmethod
    def get_by_id(self, world_id: uuid.UUID) -> WorldSkeleton | None: ...

    @abstractmethod
    def get_by_room_id(self, room_id: uuid.UUID) -> WorldSkeleton | None: ...

    @abstractmethod
    def save(self, skeleton: WorldSkeleton) -> None: ...

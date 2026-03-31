"""
Abstract repository interfaces for the Rooms bounded context.

The domain defines what persistence operations it needs; the infrastructure
layer provides the concrete SQLAlchemy implementations.
"""

import uuid
from abc import ABC, abstractmethod

from app.core.exceptions import (
    ConflictError,
    DomainError,
    ForbiddenError,
    GoneError,
    NotFoundError,
)
from app.rooms.domain.models import Room, RoomPlayer, RoomStatus


# ---------------------------------------------------------------------------
# Domain exceptions — subclass the core hierarchy so the global handler
# maps them to the correct HTTP status codes automatically.
# ---------------------------------------------------------------------------


class RoomNotFoundError(NotFoundError):
    """Raised when a requested room does not exist."""


class RoomFullError(ConflictError):
    """Raised when a room has reached its max_players limit. Maps to HTTP 409."""


class NotDMError(DomainError):
    """Raised when a non-DM user attempts a DM-only action."""


class AlreadyInRoomError(DomainError):
    """Raised when a user tries to join a room they are already in."""


class WrongPasswordError(ForbiddenError):
    """Raised when a player supplies an incorrect room password. Maps to HTTP 403."""


class RoomClosedError(GoneError):
    """Raised when a player tries to join a room that is no longer open. Maps to HTTP 410."""


# ---------------------------------------------------------------------------
# Repository interfaces
# ---------------------------------------------------------------------------


class RoomRepository(ABC):
    @abstractmethod
    def get_by_id(self, room_id: uuid.UUID) -> Room | None: ...

    @abstractmethod
    def get_by_invite_code(self, invite_code: str) -> Room | None: ...

    @abstractmethod
    def get_by_dungeon_id(self, dungeon_id: uuid.UUID) -> Room | None:
        """
        Return the most recently created Room whose dungeon_id matches,
        or None if no room is linked to that dungeon.

        Used by ListDungeonsUseCase to embed room status on each dungeon
        summary without leaking ORM details into the dungeon context.

        @param dungeon_id - The UUID of the dungeon to look up.
        """
        ...

    @abstractmethod
    def save(self, room: Room) -> None: ...

    @abstractmethod
    def update(self, room: Room) -> Room:
        """Persist changes to an existing room aggregate and return it."""
        ...

    @abstractmethod
    def delete(self, room_id: uuid.UUID) -> None: ...

    @abstractmethod
    def list_by_status(self, status: RoomStatus) -> list[Room]:
        """
        Returns all rooms with the given status, ordered by created_at descending.
        Used by the lobby browser to display open rooms to players.
        """
        ...


class RoomPlayerRepository(ABC):
    @abstractmethod
    def add(self, room_player: RoomPlayer) -> None: ...

    @abstractmethod
    def get_by_room(self, room_id: uuid.UUID) -> list[RoomPlayer]: ...

    @abstractmethod
    def is_member(self, room_id: uuid.UUID, user_id: uuid.UUID) -> bool: ...

    @abstractmethod
    def count(self, room_id: uuid.UUID) -> int: ...

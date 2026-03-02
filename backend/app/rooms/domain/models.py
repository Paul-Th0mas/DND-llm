"""
Rooms domain models.

Room is the aggregate root. RoomPlayer is a simple entity that records
membership. InviteCode is a value object wrapping the short, URL-safe
code players use to join a room.
"""

import logging
import secrets
import string
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.core.exceptions import DomainError
from app.rooms.domain.events import PlayerJoined, RoomClosed, RoomCreated

logger = logging.getLogger(__name__)

_INVITE_ALPHABET = string.ascii_uppercase + string.digits
_INVITE_LENGTH = 8


# ---------------------------------------------------------------------------
# Value Objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InviteCode:
    """
    Short alphanumeric code (e.g. "A3K9BZ2T") shared with players so they
    can join a room without knowing its internal UUID.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or len(self.value) != _INVITE_LENGTH:
            raise ValueError(
                f"InviteCode must be exactly {_INVITE_LENGTH} characters, "
                f"got '{self.value}'"
            )

    @classmethod
    def generate(cls) -> "InviteCode":
        """Generates a cryptographically random invite code."""
        code = "".join(secrets.choice(_INVITE_ALPHABET) for _ in range(_INVITE_LENGTH))
        return cls(value=code)


# ---------------------------------------------------------------------------
# Entities
# ---------------------------------------------------------------------------


@dataclass
class RoomPlayer:
    """
    Records that a user is a member of a room.
    The DM is also stored here so they appear in the player list.
    """

    room_id: uuid.UUID
    user_id: uuid.UUID
    joined_at: datetime


# ---------------------------------------------------------------------------
# Aggregate Root
# ---------------------------------------------------------------------------


@dataclass
class Room:
    """
    Aggregate root for the Rooms bounded context.

    Invariants enforced here:
      - A room can only be closed once (is_active=False is terminal).
      - max_players must be at least 1.
    """

    id: uuid.UUID
    name: str
    dm_id: uuid.UUID
    invite_code: InviteCode
    max_players: int
    is_active: bool
    created_at: datetime

    @classmethod
    def create(
        cls,
        name: str,
        dm_id: uuid.UUID,
        max_players: int,
    ) -> tuple["Room", RoomCreated]:
        """
        Factory method — creates a new Room and returns it with its domain event.
        The invite code is generated here inside the aggregate so callers never
        need to construct one manually.
        """
        if max_players < 1:
            raise DomainError("max_players must be at least 1")

        room_id = uuid.uuid4()
        now = datetime.now(tz=timezone.utc)
        room = cls(
            id=room_id,
            name=name,
            dm_id=dm_id,
            invite_code=InviteCode.generate(),
            max_players=max_players,
            is_active=True,
            created_at=now,
        )
        logger.info("Room.create: room id=%s name='%s' dm_id=%s", room_id, name, dm_id)
        event = RoomCreated(room_id=room_id, dm_id=dm_id, occurred_at=now)
        return room, event

    def close(self) -> RoomClosed:
        """
        Marks the room as inactive. Once closed, no new players can join
        and the WebSocket endpoint rejects new connections.
        """
        if not self.is_active:
            raise DomainError("Room is already closed")
        self.is_active = False
        logger.info("Room.close: room id=%s closed", self.id)
        return RoomClosed(room_id=self.id, occurred_at=datetime.now(tz=timezone.utc))

    def can_accept_player(self, current_player_count: int) -> bool:
        """Returns True when the room is open and has capacity."""
        return self.is_active and current_player_count < self.max_players

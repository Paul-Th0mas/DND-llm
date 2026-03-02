import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RoomCreated:
    room_id: uuid.UUID
    dm_id: uuid.UUID
    occurred_at: datetime


@dataclass(frozen=True)
class PlayerJoined:
    room_id: uuid.UUID
    user_id: uuid.UUID
    occurred_at: datetime


@dataclass(frozen=True)
class RoomClosed:
    room_id: uuid.UUID
    occurred_at: datetime

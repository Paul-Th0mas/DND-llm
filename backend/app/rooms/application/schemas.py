"""
Input/output DTOs for the Rooms bounded context.

These Pydantic models are the API contract — they are NOT the same as the
domain models (Room, RoomPlayer) or the ORM models (RoomORM, RoomPlayerORM).
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class LinkRoomDungeonRequest(BaseModel):
    """Request body for PATCH /rooms/{room_id}/link."""

    dungeon_id: uuid.UUID
    campaign_id: uuid.UUID


class CreateRoomRequest(BaseModel):
    name: str
    max_players: int = Field(default=8, ge=1, le=50)
    # Optional: link this room to a generated dungeon session.
    dungeon_id: uuid.UUID | None = None
    # Optional: link this room to its parent campaign for narrative context.
    campaign_id: uuid.UUID | None = None


class RoomResponse(BaseModel):
    """Full room representation returned to clients."""

    id: uuid.UUID
    name: str
    dm_id: uuid.UUID
    invite_code: str
    max_players: int
    is_active: bool
    created_at: datetime
    player_ids: list[uuid.UUID]
    dungeon_id: uuid.UUID | None = None
    campaign_id: uuid.UUID | None = None


class CreateRoomResponse(BaseModel):
    """Returned when a DM creates a room. Includes the room-scoped JWT."""

    room: RoomResponse
    # room_token is the JWT the DM must use to connect via WebSocket.
    room_token: str


class JoinRoomResponse(BaseModel):
    """Returned when a player joins a room. Includes the room-scoped JWT."""

    room: RoomResponse
    # room_token is the JWT the player must use to connect via WebSocket.
    room_token: str

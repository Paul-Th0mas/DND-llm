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
    # Optional plaintext password. If provided, the router hashes it before
    # passing password_hash to the use case.
    password: str | None = None


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


class LobbyRoomItem(BaseModel):
    """Summary of a single room shown in the lobby browser."""

    id: uuid.UUID
    name: str
    status: str
    player_count: int
    max_players: int
    # True if the room requires a password to join.
    has_password: bool
    created_at: datetime


class LobbyListResponse(BaseModel):
    """Response for GET /rooms — the lobby browser listing."""

    rooms: list[LobbyRoomItem]


class JoinRoomByIdRequest(BaseModel):
    """Request body for POST /rooms/{roomId}/join."""

    # Plaintext password. Empty string is valid for rooms with no password.
    password: str = ""


class JoinRoomByIdResponse(BaseModel):
    """Returned when a player joins a room via the lobby browser."""

    room: RoomResponse
    room_token: str
    message: str

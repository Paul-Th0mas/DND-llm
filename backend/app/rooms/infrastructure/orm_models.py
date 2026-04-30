import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RoomORM(Base):
    __tablename__ = "rooms"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    dm_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    invite_code: Mapped[str] = mapped_column(
        String(8), unique=True, index=True, nullable=False
    )
    max_players: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # Optional FK to a generated Dungeon. NULL for quick-play rooms created
    # without going through the dungeon generation pipeline.
    dungeon_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("dungeons.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
    # Optional FK to a Campaign. No FK constraint — the campaigns table may
    # not be present in all deployment environments. Matches the dungeon_id
    # pattern: NULL until the DM links the room to a campaign.
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        nullable=True,
        default=None,
    )


class RoomPlayerORM(Base):
    __tablename__ = "room_players"

    # Composite primary key: one row per (room, user) pair.
    room_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RoomPlayerStateORM(Base):
    """
    Persists per-player combat state (HP, status effects, downed flag) for a
    given room session. Allows HP to survive server restarts (US-080).

    Composite PK: one row per (room, user) pair. Upserted on every HP change.
    CASCADE DELETE on room_id ensures rows are cleaned up when the room is deleted.
    """

    __tablename__ = "room_player_state"

    room_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    current_hp: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    max_hp: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    downed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # JSON array of status effect strings stored as TEXT. Null treated as "[]" on read.
    status_effects: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

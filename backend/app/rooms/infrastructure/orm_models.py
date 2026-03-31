import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Uuid
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
    # Lobby status: "open" | "in_progress" | "closed". Stored as a plain
    # string for portability — the domain RoomStatus enum handles validation.
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    # bcrypt hash of the room password. NULL means the room is public (no password).
    password_hash: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
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

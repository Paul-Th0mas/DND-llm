"""
SQLAlchemy ORM model for the dungeons bounded context.

This is an infrastructure detail — it must not be imported by the domain or
application layers. The repository maps between ORM rows and domain objects.

dungeon_data is a JSON column storing the full rooms and quest payload:
  {
    "rooms": [ { index, room_type, name, description, enemy_names,
                 npc_names, special_notes }, ... ],
    "quest":  { name, description, stages }
  }
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DungeonORM(Base):
    __tablename__ = "dungeons"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False
    )
    world_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("worlds.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    premise: Mapped[str] = mapped_column(Text, nullable=False)
    # Full dungeon payload: rooms[] and quest stored as JSON
    dungeon_data: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

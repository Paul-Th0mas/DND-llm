"""
SQLAlchemy ORM models for the campaigns bounded context.

These are infrastructure details — they must not be imported by the domain
or application layers. The repository maps between ORM rows and domain objects.

JSON columns (themes, content_boundaries, homebrew_rules, world_data) store
Python dicts/lists that SQLAlchemy serialises to the DB's JSON type.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CampaignORM(Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    edition: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="5e-2024"
    )
    tone: Mapped[str] = mapped_column(String(50), nullable=False)
    player_count: Mapped[int] = mapped_column(Integer, nullable=False)
    level_start: Mapped[int] = mapped_column(Integer, nullable=False)
    level_end: Mapped[int] = mapped_column(Integer, nullable=False)
    session_count_estimate: Mapped[int] = mapped_column(Integer, nullable=False)
    setting_preference: Mapped[str] = mapped_column(String(50), nullable=False)

    # JSON columns: store list[str] as {"values": [...]} to keep a consistent shape
    themes: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    content_boundaries: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    homebrew_rules: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)

    inspirations: Mapped[str | None] = mapped_column(Text, nullable=True)
    dm_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # Nullable until a world is generated via POST /campaigns/{id}/world
    world_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class CampaignWorldORM(Base):
    __tablename__ = "campaign_worlds"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False
    )
    world_name: Mapped[str] = mapped_column(String(200), nullable=False)
    premise: Mapped[str] = mapped_column(Text, nullable=False)
    # Full world data: settlement, factions, npcs, hooks, central_conflict
    world_data: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

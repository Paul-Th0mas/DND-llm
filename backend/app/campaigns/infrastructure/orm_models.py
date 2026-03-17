"""
SQLAlchemy ORM models for the campaigns bounded context.

These are infrastructure details — they must not be imported by the domain
or application layers. The repository maps between ORM rows and domain objects.

JSON columns (themes, content_boundaries) store Python dicts/lists that
SQLAlchemy serialises to the DB's JSON type.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid
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

    # JSON columns: store list[str] as {"values": [...]} for a consistent shape
    themes: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    # content_boundaries stores {"lines": [...]}; old rows may contain "veils"
    # which are silently ignored on read.
    content_boundaries: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)

    dm_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # world_id references the admin-seeded World selected at campaign creation.
    # Nullable in the DB to allow migration of existing rows; the domain always
    # requires it to be set via Campaign.create().
    world_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("worlds.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

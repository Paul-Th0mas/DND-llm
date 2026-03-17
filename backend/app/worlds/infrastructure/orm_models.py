"""
SQLAlchemy ORM model for the worlds bounded context.

This is an infrastructure detail — it must not be imported by the domain or
application layers. The repository maps between ORM rows and domain objects.

factions and bosses are stored as JSON arrays of dicts. The repository
deserializes them using type-narrowing helpers to satisfy mypy strict mode.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WorldORM(Base):
    __tablename__ = "worlds"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    theme: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    lore_summary: Mapped[str] = mapped_column(Text, nullable=False)
    # JSON arrays: list of faction dicts and list of boss dicts
    factions: Mapped[list[object]] = mapped_column(JSON, nullable=False)
    bosses: Mapped[list[object]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

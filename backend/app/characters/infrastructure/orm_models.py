"""
SQLAlchemy ORM model for the characters bounded context.

This is an infrastructure detail — it must not be imported by the domain or
application layers. The repository maps between ORM rows and domain objects.

ability_scores is stored as a JSON object:
  {"strength": int, "dexterity": int, "constitution": int,
   "intelligence": int, "wisdom": int, "charisma": int}
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CharacterORM(Base):
    __tablename__ = "characters"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # owner_id is the user who created this character (player or DM).
    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # world_id references the admin-seeded World this character was created for.
    world_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("worlds.id"), nullable=False
    )
    # class_id references the character_classes table.
    class_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("character_classes.id"), nullable=False
    )
    # species_id references the character_species table.
    species_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("character_species.id"), nullable=False
    )
    background: Mapped[str] = mapped_column(Text, nullable=False)
    # JSON column: {"strength": int, "dexterity": int, ...}
    ability_scores: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    # campaign_id is nullable: None until the character is linked (US-029).
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # JSON array of skill name strings chosen during character creation.
    skill_proficiencies: Mapped[list[object]] = mapped_column(
        JSON, nullable=False, server_default="[]"
    )
    # JSON array of equipment item strings granted at character creation.
    starting_equipment: Mapped[list[object]] = mapped_column(
        JSON, nullable=False, server_default="[]"
    )
    # JSON array of spell name strings chosen during character creation.
    spells: Mapped[list[object]] = mapped_column(
        JSON, nullable=False, server_default="[]"
    )

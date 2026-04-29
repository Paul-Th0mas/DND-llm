"""
SQLAlchemy ORM models for the character_options bounded context.

These are infrastructure details — they must not be imported by the domain
or application layers. The repository maps between ORM rows and domain objects.

traits is stored as a JSON array of strings.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CharacterClassORM(Base):
    __tablename__ = "character_classes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    chassis_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hit_die: Mapped[int] = mapped_column(Integer, nullable=False)
    primary_ability: Mapped[str] = mapped_column(String(100), nullable=False)
    # Null for non-caster classes.
    spellcasting_ability: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # World theme this class belongs to (e.g. "MEDIEVAL_FANTASY").
    theme: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # JSON array of {"name": str, "ability": str} dicts — skills the player may choose from.
    skill_options: Mapped[list[object] | None] = mapped_column(JSON, nullable=True)
    # How many skills the player must pick from skill_options (0 = none to choose).
    skill_choose_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    # JSON array of strings — starting gear items granted to the class.
    starting_equipment_items: Mapped[list[object] | None] = mapped_column(
        JSON, nullable=True
    )
    # JSON array of spell-section objects; None for non-caster classes.
    # Structure: [{"level": int, "label": str, "choose_count": int,
    #               "spells": [{"name": str, "description": str}]}]
    spell_options: Mapped[list[object] | None] = mapped_column(JSON, nullable=True)


class CharacterSpeciesORM(Base):
    __tablename__ = "character_species"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    archetype_key: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[str] = mapped_column(String(50), nullable=False)
    speed: Mapped[int] = mapped_column(Integer, nullable=False)
    # JSON array of trait description strings: ["Darkvision", "Fey Ancestry", ...]
    traits: Mapped[list[object]] = mapped_column(JSON, nullable=False)
    theme: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # description is optional lore text for the species.
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

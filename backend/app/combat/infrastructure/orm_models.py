"""
SQLAlchemy 2.0 ORM models for the combat bounded context.

These are infrastructure details. They must never be imported in the domain
or application layers. The repository maps between these ORM rows and the
domain Combatant / CombatEncounter objects.

Lookup tables (class_types, die_types, etc.) are seeded once in the Alembic
migration and are never mutated at runtime.
"""

import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


# ---------------------------------------------------------------------------
# Lookup / reference tables
#
# Each table has the same shape: VARCHAR primary key + VARCHAR label.
# The PK value is the enum name (e.g. "FIGHTER"); label is display text.
# ---------------------------------------------------------------------------


class ClassTypeORM(Base):
    __tablename__ = "class_types"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    label: Mapped[str] = mapped_column(String, nullable=False)


class DieTypeORM(Base):
    __tablename__ = "die_types"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    label: Mapped[str] = mapped_column(String, nullable=False)


class CombatantTypeORM(Base):
    __tablename__ = "combatant_types"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    label: Mapped[str] = mapped_column(String, nullable=False)


class CombatStatusORM(Base):
    __tablename__ = "combat_statuses"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    label: Mapped[str] = mapped_column(String, nullable=False)


class StatusEffectTypeORM(Base):
    __tablename__ = "status_effect_types"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    label: Mapped[str] = mapped_column(String, nullable=False)


# ---------------------------------------------------------------------------
# Main tables
# ---------------------------------------------------------------------------


class CombatEncounterORM(Base):
    __tablename__ = "combat_encounters"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    room_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    # FK into the combat_statuses lookup table.
    status_id: Mapped[str] = mapped_column(
        String, ForeignKey("combat_statuses.id"), nullable=False
    )
    round: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    current_turn_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # JSON list of UUID strings, preserving the initiative-sorted turn order.
    turn_order: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


class CombatantORM(Base):
    __tablename__ = "combatants"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    encounter_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("combat_encounters.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    combatant_type_id: Mapped[str] = mapped_column(
        String, ForeignKey("combatant_types.id"), nullable=False
    )
    class_type_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("class_types.id"), nullable=True
    )
    die_type_id: Mapped[str] = mapped_column(
        String, ForeignKey("die_types.id"), nullable=False
    )
    max_pool_size: Mapped[int] = mapped_column(Integer, nullable=False)
    hp: Mapped[int] = mapped_column(Integer, nullable=False)
    max_hp: Mapped[int] = mapped_column(Integer, nullable=False)
    temp_hp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # JSON list of ints — current dice available.
    pool: Mapped[list[int]] = mapped_column(JSON, nullable=False)
    # JSON list of ints — spent dice.
    discard: Mapped[list[int]] = mapped_column(JSON, nullable=False)
    # JSON list of {type_id: str, duration: int} dicts.
    status_effects: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, nullable=False
    )
    initiative: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wild_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # JSON: {weapon: str|null, armor: str|null, accessory: str|null}
    equipment: Mapped[dict[str, str | None]] = mapped_column(JSON, nullable=False)
    # JSON list of str relic names.
    relics: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    # JSON dict for per-turn / per-encounter boolean flags and counters.
    # Keys mirror Combatant dataclass fields: free_reroll_used, second_wind_used, etc.
    turn_state: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)

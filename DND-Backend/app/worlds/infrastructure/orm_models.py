"""
SQLAlchemy 2.0 ORM models for the worlds bounded context.

These are infrastructure details.  They must never be imported in the domain
or application layers.  The repository maps between ORM rows and domain objects.

Six tables:
  themes          — theme value objects
  enemy_presets   — enemy stat blocks per theme
  item_presets    — shop items per theme
  npc_presets     — NPC personalities per theme
  quest_templates — quest arcs per theme
  world_skeletons — compiled dungeon runs (stores room_sequence etc. as JSON blobs)
"""

import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ThemeORM(Base):
    __tablename__ = "themes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # name is unique because it doubles as the FK target from preset tables.
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    tone_descriptor: Mapped[str] = mapped_column(String, nullable=False)
    language_style: Mapped[str] = mapped_column(String, nullable=False)
    currency_name: Mapped[str] = mapped_column(String, nullable=False)
    health_term: Mapped[str] = mapped_column(String, nullable=False)
    death_term: Mapped[str] = mapped_column(String, nullable=False)
    # JSON list of strings — words banned from LLM narration.
    banned_words: Mapped[list[str]] = mapped_column(JSON, nullable=False)


class EnemyPresetORM(Base):
    __tablename__ = "enemy_presets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # theme_name references themes.name (the string enum value, not themes.id).
    theme_name: Mapped[str] = mapped_column(
        String, ForeignKey("themes.name"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    hp: Mapped[int] = mapped_column(Integer, nullable=False)
    # die_type stored as the DieType enum name ("D8", "D10", etc.).
    die_type: Mapped[str] = mapped_column(String, nullable=False)
    pool_size: Mapped[int] = mapped_column(Integer, nullable=False)
    # ai_behavior stored as the AIBehavior enum name.
    ai_behavior: Mapped[str] = mapped_column(String, nullable=False)
    # JSON list of strings — thematic tags used by the LLM narrator.
    lore_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False)


class ItemPresetORM(Base):
    __tablename__ = "item_presets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    theme_name: Mapped[str] = mapped_column(
        String, ForeignKey("themes.name"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    # item_type stored as the ItemType enum name.
    item_type: Mapped[str] = mapped_column(String, nullable=False)
    # rarity is a free-text tier: "common", "uncommon", "rare", "legendary".
    rarity: Mapped[str] = mapped_column(String, nullable=False)
    gold_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    chips_bonus: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mult_bonus: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(String, nullable=False)


class NPCPresetORM(Base):
    __tablename__ = "npc_presets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    theme_name: Mapped[str] = mapped_column(
        String, ForeignKey("themes.name"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    # role stored as the NPCRole enum name.
    role: Mapped[str] = mapped_column(String, nullable=False)
    # JSON list of strings — personality trait phrases.
    personality_traits: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    # LLM instruction for how this NPC speaks (e.g. "speaks in riddles").
    speech_style: Mapped[str] = mapped_column(String, nullable=False)
    faction: Mapped[str | None] = mapped_column(String, nullable=True)


class QuestTemplateORM(Base):
    __tablename__ = "quest_templates"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    theme_name: Mapped[str] = mapped_column(
        String, ForeignKey("themes.name"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    # quest_type stored as the QuestType enum name ("MAIN" or "SIDE").
    quest_type: Mapped[str] = mapped_column(String, nullable=False)
    # JSON list of stage dicts: {stage_number, title, description, trigger_room, completion_condition}
    stages: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    reward_gold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # JSON list of item preset id strings.
    reward_item_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False)


class WorldSkeletonORM(Base):
    __tablename__ = "world_skeletons"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # room_id references the multiplayer Room aggregate by UUID.
    # No SQLAlchemy FK to rooms.id here because the worlds context must not couple
    # its ORM to the rooms ORM (bounded context rule).  Referential integrity is
    # enforced at the application layer instead.
    room_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    theme_name: Mapped[str] = mapped_column(
        String, ForeignKey("themes.name"), nullable=False
    )
    # JSON blob: {theme, difficulty, room_count, seed}
    settings: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    # JSON blob: list of DungeonRoom dicts in room order (avoids extra join tables).
    room_sequence: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    # JSON list of quest template id strings (resolved to full objects by the repository).
    active_quest_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    # JSON list of item preset id strings (shop inventory for this run).
    available_item_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    # JSON dict of narrative flag name → bool.
    world_flags: Mapped[dict[str, bool]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)

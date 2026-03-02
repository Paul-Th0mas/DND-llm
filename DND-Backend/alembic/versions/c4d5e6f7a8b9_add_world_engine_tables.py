"""add world engine tables

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-02-27 12:00:00.000000

Changes:
  - Create themes table.
  - Create enemy_presets, item_presets, npc_presets, quest_templates tables
    (all FK → themes.name).
  - Create world_skeletons table (FK → themes.name; room_id is a plain UUID
    with no ORM-level FK to rooms.id to preserve bounded context isolation).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "b3c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create world engine tables in FK-safe order."""

    # -- themes (must be created first; preset tables FK to themes.name) --
    op.create_table(
        "themes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("tone_descriptor", sa.String(), nullable=False),
        sa.Column("language_style", sa.String(), nullable=False),
        sa.Column("currency_name", sa.String(), nullable=False),
        sa.Column("health_term", sa.String(), nullable=False),
        sa.Column("death_term", sa.String(), nullable=False),
        sa.Column("banned_words", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_themes_name", "themes", ["name"])

    # -- enemy_presets --
    op.create_table(
        "enemy_presets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("theme_name", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("hp", sa.Integer(), nullable=False),
        sa.Column("die_type", sa.String(), nullable=False),
        sa.Column("pool_size", sa.Integer(), nullable=False),
        sa.Column("ai_behavior", sa.String(), nullable=False),
        sa.Column("lore_tags", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["theme_name"], ["themes.name"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_enemy_presets_theme_name", "enemy_presets", ["theme_name"])

    # -- item_presets --
    op.create_table(
        "item_presets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("theme_name", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("item_type", sa.String(), nullable=False),
        sa.Column("rarity", sa.String(), nullable=False),
        sa.Column("gold_cost", sa.Integer(), nullable=False),
        sa.Column("chips_bonus", sa.Integer(), nullable=False),
        sa.Column("mult_bonus", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["theme_name"], ["themes.name"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_item_presets_theme_name", "item_presets", ["theme_name"])

    # -- npc_presets --
    op.create_table(
        "npc_presets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("theme_name", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("personality_traits", sa.JSON(), nullable=False),
        sa.Column("speech_style", sa.String(), nullable=False),
        sa.Column("faction", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["theme_name"], ["themes.name"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_npc_presets_theme_name", "npc_presets", ["theme_name"])

    # -- quest_templates --
    op.create_table(
        "quest_templates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("theme_name", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("quest_type", sa.String(), nullable=False),
        sa.Column("stages", sa.JSON(), nullable=False),
        sa.Column("reward_gold", sa.Integer(), nullable=False),
        sa.Column("reward_item_ids", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["theme_name"], ["themes.name"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_quest_templates_theme_name", "quest_templates", ["theme_name"]
    )

    # -- world_skeletons (created last; references themes.name) --
    op.create_table(
        "world_skeletons",
        sa.Column("id", sa.Uuid(), nullable=False),
        # room_id is a plain UUID column — no FK to rooms.id.
        # Bounded context rule: worlds ORM must not import rooms ORM.
        sa.Column("room_id", sa.Uuid(), nullable=False),
        sa.Column("theme_name", sa.String(), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=False),
        sa.Column("room_sequence", sa.JSON(), nullable=False),
        sa.Column("active_quest_ids", sa.JSON(), nullable=False),
        sa.Column("available_item_ids", sa.JSON(), nullable=False),
        sa.Column("world_flags", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["theme_name"], ["themes.name"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_world_skeletons_room_id", "world_skeletons", ["room_id"])


def downgrade() -> None:
    """Drop tables in reverse FK order."""
    op.drop_table("world_skeletons")
    op.drop_index("ix_quest_templates_theme_name", table_name="quest_templates")
    op.drop_table("quest_templates")
    op.drop_index("ix_npc_presets_theme_name", table_name="npc_presets")
    op.drop_table("npc_presets")
    op.drop_index("ix_item_presets_theme_name", table_name="item_presets")
    op.drop_table("item_presets")
    op.drop_index("ix_enemy_presets_theme_name", table_name="enemy_presets")
    op.drop_table("enemy_presets")
    op.drop_index("ix_themes_name", table_name="themes")
    op.drop_table("themes")

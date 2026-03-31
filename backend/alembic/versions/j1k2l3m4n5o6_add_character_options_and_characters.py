"""add character_options and characters tables

Revision ID: j1k2l3m4n5o6
Revises: i0j1k2l3m4n5
Create Date: 2026-03-30 00:00:00.000000

Changes:
  - Create character_classes table (seeded reference data per theme)
  - Create character_species table (seeded reference data per theme)
  - Create characters table (player-owned characters with ability scores JSON)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "j1k2l3m4n5o6"
down_revision: Union[str, Sequence[str], None] = "i0j1k2l3m4n5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create character_classes, character_species, and characters tables."""

    op.create_table(
        "character_classes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("chassis_name", sa.String(100), nullable=False),
        sa.Column("hit_die", sa.Integer(), nullable=False),
        sa.Column("primary_ability", sa.String(100), nullable=False),
        # Null for non-caster classes.
        sa.Column("spellcasting_ability", sa.String(100), nullable=True),
        # World theme this class belongs to (e.g. "MEDIEVAL_FANTASY").
        sa.Column("theme", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "character_species",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("archetype_key", sa.String(100), nullable=False),
        sa.Column("size", sa.String(50), nullable=False),
        sa.Column("speed", sa.Integer(), nullable=False),
        # JSON array of trait description strings: ["Darkvision 60 ft", ...]
        sa.Column("traits", sa.JSON(), nullable=False),
        sa.Column("theme", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        # Optional lore text for the species.
        sa.Column("description", sa.Text(), nullable=True),
    )

    op.create_table(
        "characters",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "owner_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "world_id",
            sa.Uuid(),
            sa.ForeignKey("worlds.id"),
            nullable=False,
        ),
        sa.Column(
            "class_id",
            sa.Uuid(),
            sa.ForeignKey("character_classes.id"),
            nullable=False,
        ),
        sa.Column(
            "species_id",
            sa.Uuid(),
            sa.ForeignKey("character_species.id"),
            nullable=False,
        ),
        sa.Column("background", sa.Text(), nullable=False),
        # JSON object: {"strength": int, "dexterity": int, ...}
        sa.Column("ability_scores", sa.JSON(), nullable=False),
        # Nullable until the character is linked to a campaign (US-029).
        sa.Column(
            "campaign_id",
            sa.Uuid(),
            sa.ForeignKey("campaigns.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    """Drop characters first (FK dependencies), then character_options tables."""
    op.drop_table("characters")
    op.drop_table("character_species")
    op.drop_table("character_classes")

"""add campaigns tables

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-03-04 00:00:00.000000

Changes:
  - Create campaigns table (DM requirements intake — Step 1 of pipeline)
  - Create campaign_worlds table (generated world — Step 2 of pipeline)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "b3c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create campaigns and campaign_worlds tables."""

    op.create_table(
        "campaigns",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column(
            "edition", sa.String(20), nullable=False, server_default="5e-2024"
        ),
        sa.Column("tone", sa.String(50), nullable=False),
        sa.Column("player_count", sa.Integer(), nullable=False),
        sa.Column("level_start", sa.Integer(), nullable=False),
        sa.Column("level_end", sa.Integer(), nullable=False),
        sa.Column("session_count_estimate", sa.Integer(), nullable=False),
        sa.Column("setting_preference", sa.String(50), nullable=False),
        # JSON columns: themes and homebrew_rules stored as {"values": [...]}
        # content_boundaries stored as {"lines": [...], "veils": [...]}
        sa.Column("themes", sa.JSON(), nullable=False),
        sa.Column("content_boundaries", sa.JSON(), nullable=False),
        sa.Column("homebrew_rules", sa.JSON(), nullable=False),
        sa.Column("inspirations", sa.Text(), nullable=True),
        sa.Column(
            "dm_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Nullable until POST /campaigns/{id}/world is called
        sa.Column("world_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "campaign_worlds",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "campaign_id",
            sa.Uuid(),
            sa.ForeignKey("campaigns.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("world_name", sa.String(200), nullable=False),
        sa.Column("premise", sa.Text(), nullable=False),
        # Full world payload: settlement, factions, key_npcs, adventure_hooks,
        # central_conflict. Stored as JSON to keep Phase 1 schema minimal.
        sa.Column("world_data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    """Drop campaign_worlds first (FK dependency), then campaigns."""
    op.drop_table("campaign_worlds")
    op.drop_table("campaigns")

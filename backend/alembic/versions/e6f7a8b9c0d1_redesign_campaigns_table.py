"""redesign campaigns table

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
Create Date: 2026-03-11 00:00:00.000000

Changes:
  - Drop campaign_worlds table (replaced by dungeons context in Phase 3)
  - Drop setting_preference column from campaigns (replaced by world_id FK)
  - Add FK constraint from campaigns.world_id to worlds(id)

Note: world_id remains nullable in the DB to allow migration of existing rows.
      The domain layer enforces that all new campaigns have a world_id set.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e6f7a8b9c0d1"
down_revision: Union[str, Sequence[str], None] = "d5e6f7a8b9c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Drop campaign_worlds, remove setting_preference, add FK on world_id.
    Existing campaigns with world_id = NULL are left as-is; the application
    layer prevents new NULL world_ids.
    """
    # 1. Drop campaign_worlds (no longer used — replaced by dungeons context)
    op.drop_table("campaign_worlds")

    # 2. Remove setting_preference column — world selection replaces this
    op.drop_column("campaigns", "setting_preference")

    # 3. Add FK constraint linking campaigns.world_id → worlds.id
    op.create_foreign_key(
        "fk_campaigns_world_id_worlds",
        "campaigns",
        "worlds",
        ["world_id"],
        ["id"],
    )


def downgrade() -> None:
    """Restore campaign_worlds, setting_preference, and remove FK."""
    # 1. Remove FK constraint
    op.drop_constraint("fk_campaigns_world_id_worlds", "campaigns", type_="foreignkey")

    # 2. Re-add setting_preference with a safe default
    op.add_column(
        "campaigns",
        sa.Column(
            "setting_preference",
            sa.String(50),
            nullable=False,
            server_default="homebrew",
        ),
    )

    # 3. Recreate campaign_worlds table
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
        sa.Column("world_data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

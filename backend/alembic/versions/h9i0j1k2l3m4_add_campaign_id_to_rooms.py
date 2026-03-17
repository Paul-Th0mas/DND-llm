"""add campaign_id to rooms

Revision ID: h9i0j1k2l3m4
Revises: g8h9i0j1k2l3
Create Date: 2026-03-16 00:00:00.000000

Changes (US-024):
  - Add nullable campaign_id UUID column to rooms.
  - No FK constraint — mirrors the pattern used for dungeon_id.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "h9i0j1k2l3m4"
down_revision: Union[str, Sequence[str], None] = "g8h9i0j1k2l3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add campaign_id column to rooms table."""
    op.add_column(
        "rooms",
        sa.Column(
            "campaign_id",
            sa.Uuid(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove campaign_id column from rooms table."""
    op.drop_column("rooms", "campaign_id")

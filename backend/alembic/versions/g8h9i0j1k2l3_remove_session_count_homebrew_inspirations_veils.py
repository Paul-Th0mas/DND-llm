"""remove session_count_estimate homebrew_rules inspirations from campaigns

Revision ID: g8h9i0j1k2l3
Revises: f7a8b9c0d1e2
Create Date: 2026-03-16 00:00:00.000000

Changes (US-020, US-021, US-022):
  - Drop session_count_estimate column from campaigns
  - Drop homebrew_rules column from campaigns
  - Drop inspirations column from campaigns

Note (US-023): The content_boundaries JSON column is kept as-is. Old rows
that contain a "veils" key in the JSON are harmless — the application layer
silently ignores that key on read. No schema change is required for US-023.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "g8h9i0j1k2l3"
down_revision: Union[str, Sequence[str], None] = "f7a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop the three columns removed in US-020, US-021, and US-022."""
    op.drop_column("campaigns", "session_count_estimate")
    op.drop_column("campaigns", "homebrew_rules")
    op.drop_column("campaigns", "inspirations")


def downgrade() -> None:
    """Restore the three columns with safe defaults for existing rows."""
    op.add_column(
        "campaigns",
        sa.Column(
            "inspirations",
            sa.Text(),
            nullable=True,
        ),
    )
    op.add_column(
        "campaigns",
        sa.Column(
            "homebrew_rules",
            sa.JSON(),
            nullable=False,
            server_default='{"values": []}',
        ),
    )
    op.add_column(
        "campaigns",
        sa.Column(
            "session_count_estimate",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )

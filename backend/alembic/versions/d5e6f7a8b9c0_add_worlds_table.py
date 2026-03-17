"""add worlds table

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-03-11 00:00:00.000000

Changes:
  - Create worlds table (admin-seeded settings: lore, factions, bosses)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, Sequence[str], None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the worlds table."""
    op.create_table(
        "worlds",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False, unique=True),
        sa.Column("theme", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("lore_summary", sa.Text(), nullable=False),
        # JSON arrays: list of faction dicts and list of boss dicts
        sa.Column("factions", sa.JSON(), nullable=False),
        sa.Column("bosses", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    """Drop the worlds table."""
    op.drop_table("worlds")

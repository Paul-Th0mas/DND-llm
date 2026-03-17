"""add dungeon_id to rooms

Revision ID: a8b9c0d1e2f3
Revises: f7a8b9c0d1e2
Create Date: 2026-03-11 00:00:00.000000

Changes:
  - Add nullable dungeon_id FK column to rooms table
    (NULL for quick-play rooms created without dungeon generation)
"""

from alembic import op
import sqlalchemy as sa

revision = "a8b9c0d1e2f3"
down_revision = "f7a8b9c0d1e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "rooms",
        sa.Column(
            "dungeon_id",
            sa.Uuid(),
            sa.ForeignKey("dungeons.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("rooms", "dungeon_id")

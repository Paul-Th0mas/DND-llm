"""add room_player_state table

Revision ID: b3f1a9c2d7e4
Revises: None
Create Date: 2026-04-29

NOTE: Before running this migration, set down_revision to the revision ID of
your current Alembic head. You can find it by running:
    alembic heads
Then replace the None below with the head revision string.

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3f1a9c2d7e4"
down_revision: Union[str, Sequence[str], None] = "n5o6p7q8r9s0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create room_player_state table for persistent combat HP/status (US-080)."""
    op.create_table(
        "room_player_state",
        sa.Column("room_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "current_hp", sa.Integer(), nullable=False, server_default="10"
        ),
        sa.Column("max_hp", sa.Integer(), nullable=False, server_default="10"),
        sa.Column(
            "downed", sa.Boolean(), nullable=False, server_default="false"
        ),
        # JSON array of status effect strings stored as TEXT.
        # Null treated as empty list on read by the repository.
        sa.Column(
            "status_effects",
            sa.Text(),
            nullable=False,
            server_default="'[]'",
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["room_id"], ["rooms.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("room_id", "user_id"),
    )


def downgrade() -> None:
    """Drop room_player_state table."""
    op.drop_table("room_player_state")

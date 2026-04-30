"""add_dungeon_progression_columns

Revision ID: 2bab62c46410
Revises: m4n5o6p7q8r9
Create Date: 2026-04-15 10:44:08.226930

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2bab62c46410'
down_revision: Union[str, Sequence[str], None] = 'm4n5o6p7q8r9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "dungeons",
        sa.Column("current_room_index", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "dungeons",
        sa.Column(
            "completed_stage_indices",
            postgresql.JSON(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("dungeons", "completed_stage_indices")
    op.drop_column("dungeons", "current_room_index")

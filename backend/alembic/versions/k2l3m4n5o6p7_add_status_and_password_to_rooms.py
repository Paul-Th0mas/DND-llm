"""add status and password_hash to rooms

Revision ID: k2l3m4n5o6p7
Revises: j1k2l3m4n5o6
Create Date: 2026-03-30 00:00:00.000000

Changes:
  - Add status column to rooms table (open/in_progress/closed).
    Existing rows are back-filled: is_active=true → 'open', false → 'closed'.
  - Add password_hash column to rooms table (nullable, bcrypt hash).
    NULL means the room is public (no password required).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "k2l3m4n5o6p7"
down_revision: Union[str, Sequence[str], None] = "j1k2l3m4n5o6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add status as nullable first so we can back-fill existing rows without
    # a NOT NULL violation, then tighten to NOT NULL with a server default.
    op.add_column(
        "rooms",
        sa.Column("status", sa.String(20), nullable=True),
    )
    op.add_column(
        "rooms",
        sa.Column("password_hash", sa.String(), nullable=True),
    )

    # Back-fill status from the existing is_active boolean.
    op.execute("UPDATE rooms SET status = 'closed' WHERE is_active = false")
    op.execute("UPDATE rooms SET status = 'open'   WHERE is_active = true")

    # Now tighten the column to NOT NULL with a default for future inserts.
    op.alter_column("rooms", "status", nullable=False, server_default="open")


def downgrade() -> None:
    op.drop_column("rooms", "password_hash")
    op.drop_column("rooms", "status")

"""add roles, passwords, rooms

Revision ID: a1b2c3d4e5f6
Revises: 85a6cc7469e5
Create Date: 2026-02-19 12:00:00.000000

Changes:
  - users: add role (varchar, default 'player'), hashed_password (nullable varchar)
  - users: make google_id nullable (email/password users have no google_id)
  - Create rooms table
  - Create room_players table
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "85a6cc7469e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # -- Alter users table --
    # Add role column with default so existing rows get 'player'.
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(),
            nullable=False,
            server_default="player",
        ),
    )
    # Add nullable hashed_password (None for Google OAuth users).
    op.add_column(
        "users",
        sa.Column("hashed_password", sa.String(), nullable=True),
    )
    # Make google_id nullable so email/password users can register without one.
    op.alter_column("users", "google_id", existing_type=sa.String(), nullable=True)

    # -- Create rooms table --
    op.create_table(
        "rooms",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("dm_id", sa.Uuid(), nullable=False),
        sa.Column("invite_code", sa.String(8), nullable=False),
        sa.Column("max_players", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dm_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rooms_invite_code"), "rooms", ["invite_code"], unique=True)

    # -- Create room_players join table --
    op.create_table(
        "room_players",
        sa.Column("room_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("room_id", "user_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("room_players")
    op.drop_index(op.f("ix_rooms_invite_code"), table_name="rooms")
    op.drop_table("rooms")
    op.drop_column("users", "hashed_password")
    op.drop_column("users", "role")
    op.alter_column("users", "google_id", existing_type=sa.String(), nullable=False)

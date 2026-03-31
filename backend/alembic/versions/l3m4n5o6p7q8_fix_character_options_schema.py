"""fix character_options schema: add missing columns and character_species table

Revision ID: l3m4n5o6p7q8
Revises: k2l3m4n5o6p7
Create Date: 2026-03-31 00:00:00.000000

Changes:
  - Add is_active (Boolean) to character_classes
  - Add created_at (DateTime) to character_classes
  - Widen primary_ability and spellcasting_ability from VARCHAR(10) to VARCHAR(100)
  - Create character_species table (was missing from DB despite prior migration)
"""

from typing import Sequence, Union
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

revision: str = "l3m4n5o6p7q8"
down_revision: Union[str, Sequence[str], None] = "k2l3m4n5o6p7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to character_classes.
    op.add_column(
        "character_classes",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
    )
    op.add_column(
        "character_classes",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Widen columns that were created as VARCHAR(10) instead of VARCHAR(100).
    op.alter_column(
        "character_classes",
        "primary_ability",
        type_=sa.String(100),
        existing_nullable=False,
    )
    op.alter_column(
        "character_classes",
        "spellcasting_ability",
        type_=sa.String(100),
        existing_nullable=True,
    )

    # Existing characters reference the old 'species' table via species_id.
    # This is dev seed data only — truncate to allow the FK to be repointed.
    op.execute("TRUNCATE TABLE characters RESTART IDENTITY CASCADE")

    # Drop the old FK that points characters.species_id -> species.
    op.drop_constraint("characters_species_id_fkey", "characters", type_="foreignkey")

    # Create character_species table which was absent from the database.
    op.create_table(
        "character_species",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("archetype_key", sa.String(100), nullable=False),
        sa.Column("size", sa.String(50), nullable=False),
        sa.Column("speed", sa.Integer(), nullable=False),
        sa.Column("traits", sa.JSON(), nullable=False),
        sa.Column("theme", sa.String(50), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("description", sa.Text(), nullable=True),
    )

    # Repoint characters.species_id to the new character_species table.
    op.create_foreign_key(
        "characters_species_id_fkey",
        "characters",
        "character_species",
        ["species_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("characters_species_id_fkey", "characters", type_="foreignkey")
    op.create_foreign_key(
        "characters_species_id_fkey",
        "characters",
        "species",
        ["species_id"],
        ["id"],
    )
    op.drop_table("character_species")
    op.drop_column("character_classes", "created_at")
    op.drop_column("character_classes", "is_active")
    op.alter_column(
        "character_classes",
        "primary_ability",
        type_=sa.String(10),
        existing_nullable=False,
    )
    op.alter_column(
        "character_classes",
        "spellcasting_ability",
        type_=sa.String(10),
        existing_nullable=True,
    )

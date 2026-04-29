"""add_skill_equipment_spells

Adds skill/equipment/spell columns to character_classes and characters tables
to support US-048, US-049, US-050 (skill proficiency selection, starting
equipment, and spell selection during character creation).

Revision ID: n5o6p7q8r9s0
Revises: 2bab62c46410
Create Date: 2026-04-28 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSON

revision: str = "n5o6p7q8r9s0"
down_revision: Union[str, Sequence[str], None] = "2bab62c46410"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- character_classes: new reference-data columns ---
    op.add_column(
        "character_classes",
        sa.Column("skill_options", JSON, nullable=True),
    )
    op.add_column(
        "character_classes",
        sa.Column(
            "skill_choose_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "character_classes",
        sa.Column("starting_equipment_items", JSON, nullable=True),
    )
    op.add_column(
        "character_classes",
        sa.Column("spell_options", JSON, nullable=True),
    )

    # --- characters: player-chosen data columns ---
    # server_default='[]' means existing rows default to an empty array.
    op.add_column(
        "characters",
        sa.Column(
            "skill_proficiencies",
            JSON,
            nullable=False,
            server_default="'[]'::json",
        ),
    )
    op.add_column(
        "characters",
        sa.Column(
            "starting_equipment",
            JSON,
            nullable=False,
            server_default="'[]'::json",
        ),
    )
    op.add_column(
        "characters",
        sa.Column(
            "spells",
            JSON,
            nullable=False,
            server_default="'[]'::json",
        ),
    )


def downgrade() -> None:
    op.drop_column("characters", "spells")
    op.drop_column("characters", "starting_equipment")
    op.drop_column("characters", "skill_proficiencies")
    op.drop_column("character_classes", "spell_options")
    op.drop_column("character_classes", "starting_equipment_items")
    op.drop_column("character_classes", "skill_choose_count")
    op.drop_column("character_classes", "skill_options")

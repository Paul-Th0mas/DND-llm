"""add combat tables

Revision ID: b3c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-02-20 12:00:00.000000

Changes:
  - Create 5 lookup/reference tables (class_types, die_types, combatant_types,
    combat_statuses, status_effect_types) and seed their rows.
  - Create combat_encounters table with FK to combat_statuses.
  - Create combatants table with FK to combat_encounters (CASCADE DELETE)
    and FKs to all lookup tables.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create lookup tables, seed rows, then create main combat tables."""

    # -- Lookup table: class_types --
    op.create_table(
        "class_types",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("label", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        sa.table(
            "class_types",
            sa.column("id", sa.String()),
            sa.column("label", sa.String()),
        ),
        [
            {"id": "FIGHTER", "label": "Fighter"},
            {"id": "BARBARIAN", "label": "Barbarian"},
            {"id": "ROGUE", "label": "Rogue"},
            {"id": "WIZARD", "label": "Wizard"},
            {"id": "CLERIC", "label": "Cleric"},
            {"id": "RANGER", "label": "Ranger"},
            {"id": "BARD", "label": "Bard"},
        ],
    )

    # -- Lookup table: die_types --
    op.create_table(
        "die_types",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("label", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        sa.table(
            "die_types",
            sa.column("id", sa.String()),
            sa.column("label", sa.String()),
        ),
        [
            {"id": "D8", "label": "d8"},
            {"id": "D10", "label": "d10"},
            {"id": "D12", "label": "d12"},
            {"id": "D20", "label": "d20"},
        ],
    )

    # -- Lookup table: combatant_types --
    op.create_table(
        "combatant_types",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("label", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        sa.table(
            "combatant_types",
            sa.column("id", sa.String()),
            sa.column("label", sa.String()),
        ),
        [
            {"id": "PLAYER", "label": "Player"},
            {"id": "ENEMY", "label": "Enemy"},
        ],
    )

    # -- Lookup table: combat_statuses --
    op.create_table(
        "combat_statuses",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("label", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        sa.table(
            "combat_statuses",
            sa.column("id", sa.String()),
            sa.column("label", sa.String()),
        ),
        [
            {"id": "ACTIVE", "label": "Active"},
            {"id": "VICTORY", "label": "Victory"},
            {"id": "DEFEAT", "label": "Defeat"},
            {"id": "FLED", "label": "Fled"},
        ],
    )

    # -- Lookup table: status_effect_types --
    op.create_table(
        "status_effect_types",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("label", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        sa.table(
            "status_effect_types",
            sa.column("id", sa.String()),
            sa.column("label", sa.String()),
        ),
        [
            {"id": "BURNING", "label": "Burning"},
            {"id": "FROZEN", "label": "Frozen"},
            {"id": "CURSED", "label": "Cursed"},
            {"id": "POISONED", "label": "Poisoned"},
            {"id": "BLESSED", "label": "Blessed"},
            {"id": "INSPIRED", "label": "Inspired"},
        ],
    )

    # -- Main table: combat_encounters --
    op.create_table(
        "combat_encounters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("room_id", sa.Uuid(), nullable=True),
        sa.Column("status_id", sa.String(), nullable=False),
        sa.Column("round", sa.Integer(), nullable=False),
        sa.Column("current_turn_index", sa.Integer(), nullable=False),
        sa.Column("turn_order", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["status_id"], ["combat_statuses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # -- Main table: combatants --
    op.create_table(
        "combatants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("encounter_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("combatant_type_id", sa.String(), nullable=False),
        sa.Column("class_type_id", sa.String(), nullable=True),
        sa.Column("die_type_id", sa.String(), nullable=False),
        sa.Column("max_pool_size", sa.Integer(), nullable=False),
        sa.Column("hp", sa.Integer(), nullable=False),
        sa.Column("max_hp", sa.Integer(), nullable=False),
        sa.Column("temp_hp", sa.Integer(), nullable=False),
        sa.Column("pool", sa.JSON(), nullable=False),
        sa.Column("discard", sa.JSON(), nullable=False),
        sa.Column("status_effects", sa.JSON(), nullable=False),
        sa.Column("initiative", sa.Integer(), nullable=False),
        sa.Column("wild_tokens", sa.Integer(), nullable=False),
        sa.Column("equipment", sa.JSON(), nullable=False),
        sa.Column("relics", sa.JSON(), nullable=False),
        sa.Column("turn_state", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["encounter_id"], ["combat_encounters.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["combatant_type_id"], ["combatant_types.id"]),
        sa.ForeignKeyConstraint(["class_type_id"], ["class_types.id"]),
        sa.ForeignKeyConstraint(["die_type_id"], ["die_types.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop main tables first (FK dependents), then lookup tables."""
    op.drop_table("combatants")
    op.drop_table("combat_encounters")
    op.drop_table("status_effect_types")
    op.drop_table("combat_statuses")
    op.drop_table("combatant_types")
    op.drop_table("die_types")
    op.drop_table("class_types")

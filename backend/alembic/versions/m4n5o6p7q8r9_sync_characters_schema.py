"""sync characters table schema with ORM model

Revision ID: m4n5o6p7q8r9
Revises: l3m4n5o6p7q8
Create Date: 2026-03-31 00:00:00.000000

Changes:
  - Add campaign_id (nullable UUID FK -> campaigns) — present in ORM, missing from DB
  - Drop score_method and level — present in DB, absent from ORM and unused
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "m4n5o6p7q8r9"
down_revision: Union[str, Sequence[str], None] = "l3m4n5o6p7q8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "characters",
        sa.Column(
            "campaign_id",
            sa.Uuid(),
            sa.ForeignKey("campaigns.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.drop_column("characters", "score_method")
    op.drop_column("characters", "level")


def downgrade() -> None:
    op.add_column(
        "characters",
        sa.Column("score_method", sa.String(20), nullable=False, server_default="standard"),
    )
    op.add_column(
        "characters",
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
    )
    op.drop_constraint("characters_campaign_id_fkey", "characters", type_="foreignkey")
    op.drop_column("characters", "campaign_id")

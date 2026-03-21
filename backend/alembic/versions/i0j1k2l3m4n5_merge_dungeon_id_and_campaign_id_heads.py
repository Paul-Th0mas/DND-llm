"""merge dungeon_id and campaign_id heads

Revision ID: i0j1k2l3m4n5
Revises: a8b9c0d1e2f3, h9i0j1k2l3m4
Create Date: 2026-03-21 00:00:00.000000

Merges two independent branches that both originate from f7a8b9c0d1e2:
  - a8b9c0d1e2f3: added dungeon_id to rooms
  - h9i0j1k2l3m4: added campaign_id to rooms (via g8h9i0j1k2l3)
"""

from typing import Sequence, Union

from alembic import op

revision: str = "i0j1k2l3m4n5"
down_revision: Union[str, Sequence[str], None] = ("a8b9c0d1e2f3", "h9i0j1k2l3m4")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

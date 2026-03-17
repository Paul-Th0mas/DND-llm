"""
Concrete SQLAlchemy repository implementation for the campaigns bounded context.

Maps between CampaignORM rows and Campaign domain aggregates.
JSON columns (themes, content_boundaries) are deserialized with
type-narrowing helpers to satisfy mypy strict mode.
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.campaigns.domain.models import (
    Campaign,
    CampaignTone,
    ContentBoundaries,
    LevelRange,
)
from app.campaigns.domain.repositories import CampaignRepository
from app.campaigns.infrastructure.orm_models import CampaignORM

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# JSON field type-narrowing helpers
# ---------------------------------------------------------------------------


def _str_list(d: dict[str, object], key: str) -> list[str]:
    v = d.get(key, [])
    if isinstance(v, list):
        return [x for x in v if isinstance(x, str)]
    return []


# ---------------------------------------------------------------------------
# Repository implementation
# ---------------------------------------------------------------------------


class SqlAlchemyCampaignRepository(CampaignRepository):
    """SQLAlchemy-backed implementation of CampaignRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, campaign: Campaign) -> None:
        """Insert or update a Campaign aggregate."""
        logger.debug("save: campaign id=%s", campaign.id)
        orm = CampaignORM(
            id=campaign.id,
            name=campaign.name,
            edition=campaign.edition,
            tone=campaign.tone.value,
            player_count=campaign.player_count,
            level_start=campaign.level_range.start,
            level_end=campaign.level_range.end,
            # Wrap list[str] in a dict for a consistent JSON object shape
            themes={"values": list(campaign.themes)},
            content_boundaries={
                "lines": list(campaign.content_boundaries.lines),
            },
            dm_id=campaign.dm_id,
            world_id=campaign.world_id,
            created_at=campaign.created_at,
        )
        self._session.merge(orm)
        self._session.flush()

    def list_by_dm_id(self, dm_id: uuid.UUID) -> list[Campaign]:
        """Return all campaigns for the given DM, newest first."""
        logger.debug("list_by_dm_id: dm_id=%s", dm_id)
        stmt = (
            select(CampaignORM)
            .where(CampaignORM.dm_id == dm_id)
            .order_by(CampaignORM.created_at.desc())
        )
        rows = self._session.execute(stmt).scalars().all()
        return [self._to_domain(row) for row in rows]

    def get_by_id(self, campaign_id: uuid.UUID) -> Campaign | None:
        """Return a Campaign by UUID, or None if not found."""
        logger.debug("get_by_id: campaign_id=%s", campaign_id)
        stmt = select(CampaignORM).where(CampaignORM.id == campaign_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        return self._to_domain(row) if row is not None else None

    @staticmethod
    def _to_domain(orm: CampaignORM) -> Campaign:
        """Map a CampaignORM row to a Campaign domain aggregate."""
        themes_raw = orm.themes if isinstance(orm.themes, dict) else {}
        cb_raw = (
            orm.content_boundaries if isinstance(orm.content_boundaries, dict) else {}
        )

        # world_id is nullable in the DB for migration compatibility, but
        # the domain always provides it. Use a zero UUID as a safe fallback.
        world_id = orm.world_id if orm.world_id is not None else uuid.UUID(int=0)

        return Campaign(
            id=orm.id,
            name=orm.name,
            edition=orm.edition,
            tone=CampaignTone(orm.tone),
            player_count=orm.player_count,
            level_range=LevelRange(start=orm.level_start, end=orm.level_end),
            themes=tuple(_str_list(themes_raw, "values")),
            content_boundaries=ContentBoundaries(
                lines=tuple(_str_list(cb_raw, "lines")),
                # "veils" key in old JSON rows is silently ignored here.
            ),
            dm_id=orm.dm_id,
            world_id=world_id,
            created_at=orm.created_at,
        )

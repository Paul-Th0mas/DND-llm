"""
Concrete SQLAlchemy repository implementations for the campaigns bounded context.

These classes implement the abstract interfaces defined in domain/repositories.py.
They are the only place where ORM models are constructed and queried.
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
    SettingPreference,
)
from app.campaigns.domain.repositories import (
    CampaignRepository,
    CampaignWorldRepository,
)
from app.campaigns.domain.world_models import (
    AdventureHook,
    CampaignNPC,
    CampaignWorld,
    Faction,
    Settlement,
)
from app.campaigns.infrastructure.orm_models import CampaignORM, CampaignWorldORM

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# JSON field type-narrowing helpers
# (JSON columns return dict[str, object]; we must narrow before use)
# ---------------------------------------------------------------------------


def _str_field(d: dict[str, object], key: str, default: str = "") -> str:
    v = d.get(key, default)
    return v if isinstance(v, str) else default


def _int_field(d: dict[str, object], key: str, default: int = 0) -> int:
    v = d.get(key, default)
    return v if isinstance(v, int) else default


def _str_list(d: dict[str, object], key: str) -> list[str]:
    v = d.get(key, [])
    if isinstance(v, list):
        return [x for x in v if isinstance(x, str)]
    return []


# ---------------------------------------------------------------------------
# Campaign repository
# ---------------------------------------------------------------------------


class SqlAlchemyCampaignRepository(CampaignRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, campaign: Campaign) -> None:
        logger.debug("save: campaign id=%s", campaign.id)
        orm = CampaignORM(
            id=campaign.id,
            name=campaign.name,
            edition=campaign.edition,
            tone=campaign.tone.value,
            player_count=campaign.player_count,
            level_start=campaign.level_range.start,
            level_end=campaign.level_range.end,
            session_count_estimate=campaign.session_count_estimate,
            setting_preference=campaign.setting_preference.value,
            # Wrap list[str] in a dict so we get a consistent JSON object shape
            themes={"values": list(campaign.themes)},
            content_boundaries={
                "lines": list(campaign.content_boundaries.lines),
                "veils": list(campaign.content_boundaries.veils),
            },
            homebrew_rules={"values": list(campaign.homebrew_rules)},
            inspirations=campaign.inspirations,
            dm_id=campaign.dm_id,
            world_id=campaign.world_id,
            created_at=campaign.created_at,
        )
        self._session.merge(orm)
        self._session.flush()

    def get_by_id(self, campaign_id: uuid.UUID) -> Campaign | None:
        logger.debug("get_by_id: campaign_id=%s", campaign_id)
        stmt = select(CampaignORM).where(CampaignORM.id == campaign_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        return self._to_domain(row) if row is not None else None

    @staticmethod
    def _to_domain(orm: CampaignORM) -> Campaign:
        themes_raw = orm.themes if isinstance(orm.themes, dict) else {}
        cb_raw = (
            orm.content_boundaries if isinstance(orm.content_boundaries, dict) else {}
        )
        hr_raw = orm.homebrew_rules if isinstance(orm.homebrew_rules, dict) else {}

        return Campaign(
            id=orm.id,
            name=orm.name,
            edition=orm.edition,
            tone=CampaignTone(orm.tone),
            player_count=orm.player_count,
            level_range=LevelRange(start=orm.level_start, end=orm.level_end),
            session_count_estimate=orm.session_count_estimate,
            setting_preference=SettingPreference(orm.setting_preference),
            themes=tuple(_str_list(themes_raw, "values")),
            content_boundaries=ContentBoundaries(
                lines=tuple(_str_list(cb_raw, "lines")),
                veils=tuple(_str_list(cb_raw, "veils")),
            ),
            homebrew_rules=tuple(_str_list(hr_raw, "values")),
            inspirations=orm.inspirations,
            dm_id=orm.dm_id,
            created_at=orm.created_at,
            world_id=orm.world_id,
        )


# ---------------------------------------------------------------------------
# CampaignWorld repository
# ---------------------------------------------------------------------------


class SqlAlchemyCampaignWorldRepository(CampaignWorldRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, world: CampaignWorld) -> None:
        logger.debug(
            "save: world_id=%s campaign_id=%s", world.world_id, world.campaign_id
        )
        world_data: dict[str, object] = {
            "central_conflict": world.central_conflict,
            "settlement": {
                "name": world.starting_settlement.name,
                "population": world.starting_settlement.population,
                "governance": world.starting_settlement.governance,
                "description": world.starting_settlement.description,
            },
            "factions": [
                {
                    "name": f.name,
                    "goals": f.goals,
                    "public_reputation": f.public_reputation,
                    "hidden_agenda": f.hidden_agenda,
                }
                for f in world.factions
            ],
            "key_npcs": [
                {
                    "name": n.name,
                    "species": n.species,
                    "role": n.role,
                    "personality": n.personality,
                    "secret": n.secret,
                    "stat_block_ref": n.stat_block_ref,
                }
                for n in world.key_npcs
            ],
            "adventure_hooks": [
                {
                    "pillar": h.pillar,
                    "hook": h.hook,
                    "connected_npc": h.connected_npc,
                }
                for h in world.adventure_hooks
            ],
        }
        orm = CampaignWorldORM(
            id=world.world_id,
            campaign_id=world.campaign_id,
            world_name=world.world_name,
            premise=world.premise,
            world_data=world_data,
            created_at=world.created_at,
        )
        self._session.merge(orm)
        self._session.flush()

    def get_by_campaign_id(self, campaign_id: uuid.UUID) -> CampaignWorld | None:
        logger.debug("get_by_campaign_id: campaign_id=%s", campaign_id)
        stmt = select(CampaignWorldORM).where(
            CampaignWorldORM.campaign_id == campaign_id
        )
        row = self._session.execute(stmt).scalar_one_or_none()
        return self._to_domain(row) if row is not None else None

    @staticmethod
    def _to_domain(orm: CampaignWorldORM) -> CampaignWorld:
        data = orm.world_data if isinstance(orm.world_data, dict) else {}

        # --- Settlement ---
        settlement_raw = data.get("settlement")
        sd: dict[str, object] = (
            settlement_raw if isinstance(settlement_raw, dict) else {}
        )
        settlement = Settlement(
            name=_str_field(sd, "name"),
            population=_int_field(sd, "population"),
            governance=_str_field(sd, "governance"),
            description=_str_field(sd, "description"),
        )

        # --- Factions ---
        factions: list[Faction] = []
        factions_raw = data.get("factions", [])
        if isinstance(factions_raw, list):
            for item in factions_raw:
                if isinstance(item, dict):
                    fd: dict[str, object] = dict(item)
                    factions.append(
                        Faction(
                            name=_str_field(fd, "name"),
                            goals=_str_field(fd, "goals"),
                            public_reputation=_str_field(fd, "public_reputation"),
                            hidden_agenda=_str_field(fd, "hidden_agenda"),
                        )
                    )

        # --- Key NPCs ---
        npcs: list[CampaignNPC] = []
        npcs_raw = data.get("key_npcs", [])
        if isinstance(npcs_raw, list):
            for item in npcs_raw:
                if isinstance(item, dict):
                    nd: dict[str, object] = dict(item)
                    secret_val = nd.get("secret")
                    stat_ref_val = nd.get("stat_block_ref")
                    npcs.append(
                        CampaignNPC(
                            name=_str_field(nd, "name"),
                            species=_str_field(nd, "species"),
                            role=_str_field(nd, "role"),
                            personality=_str_field(nd, "personality"),
                            secret=(
                                secret_val if isinstance(secret_val, str) else None
                            ),
                            stat_block_ref=(
                                stat_ref_val if isinstance(stat_ref_val, str) else None
                            ),
                        )
                    )

        # --- Adventure hooks ---
        hooks: list[AdventureHook] = []
        hooks_raw = data.get("adventure_hooks", [])
        if isinstance(hooks_raw, list):
            for item in hooks_raw:
                if isinstance(item, dict):
                    hd: dict[str, object] = dict(item)
                    npc_val = hd.get("connected_npc")
                    hooks.append(
                        AdventureHook(
                            pillar=_str_field(hd, "pillar"),
                            hook=_str_field(hd, "hook"),
                            connected_npc=(
                                npc_val if isinstance(npc_val, str) else None
                            ),
                        )
                    )

        return CampaignWorld(
            world_id=orm.id,
            campaign_id=orm.campaign_id,
            world_name=orm.world_name,
            premise=orm.premise,
            starting_settlement=settlement,
            factions=tuple(factions),
            key_npcs=tuple(npcs),
            central_conflict=_str_field(data, "central_conflict"),
            adventure_hooks=tuple(hooks),
            created_at=orm.created_at,
        )

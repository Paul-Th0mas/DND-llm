"""
SQLAlchemy implementations of the worlds domain repository interfaces.

Maps between ORM rows and domain objects in both directions.
All domain logic stays in the domain layer — this file only handles
persistence translation.
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.combat.domain.models import DieType
from app.worlds.domain.models import (
    AIBehavior,
    DungeonRoom,
    EnemyPreset,
    ItemPreset,
    ItemType,
    NPCPreset,
    NPCRole,
    QuestStage,
    QuestTemplate,
    QuestType,
    RoomType,
    Theme,
    ThemeName,
    WorldSettings,
    WorldSkeleton,
)
from app.worlds.domain.repositories import (
    PresetRepository,
    ThemeRepository,
    WorldSkeletonRepository,
)
from app.worlds.infrastructure.orm_models import (
    EnemyPresetORM,
    ItemPresetORM,
    NPCPresetORM,
    QuestTemplateORM,
    ThemeORM,
    WorldSkeletonORM,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Typed helpers for reading JSON dict values stored as `dict[str, object]`.
# isinstance narrowing is used so mypy can verify the return types.
# ---------------------------------------------------------------------------


def _jint(d: dict[str, object], key: str, default: int = 0) -> int:
    """Read an int from a JSON dict, falling back to `default`."""
    v = d.get(key, default)
    return v if isinstance(v, int) else default


def _jstr(d: dict[str, object], key: str, default: str = "") -> str:
    """Read a str from a JSON dict, falling back to `default`."""
    v = d.get(key, default)
    return v if isinstance(v, str) else default


def _jlist_str(d: dict[str, object], key: str) -> list[str]:
    """Read a list[str] from a JSON dict, falling back to []."""
    v = d.get(key, [])
    if isinstance(v, list):
        return [str(x) for x in v]
    return []


# ---------------------------------------------------------------------------
# ThemeRepository implementation
# ---------------------------------------------------------------------------


class SqlAlchemyThemeRepository(ThemeRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_name(self, name: ThemeName) -> Theme | None:
        logger.debug("ThemeRepository.get_by_name: name=%s", name.value)
        stmt = select(ThemeORM).where(ThemeORM.name == name.value)
        row = self._session.execute(stmt).scalar_one_or_none()
        if row is None:
            return None
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: ThemeORM) -> Theme:
        return Theme(
            name=ThemeName(row.name),
            tone_descriptor=row.tone_descriptor,
            language_style=row.language_style,
            currency_name=row.currency_name,
            health_term=row.health_term,
            death_term=row.death_term,
            banned_words=tuple(row.banned_words),
        )


# ---------------------------------------------------------------------------
# PresetRepository implementation
# ---------------------------------------------------------------------------


class SqlAlchemyPresetRepository(PresetRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_enemies_by_theme(self, theme: ThemeName) -> list[EnemyPreset]:
        logger.debug("PresetRepository.get_enemies_by_theme: theme=%s", theme.value)
        stmt = select(EnemyPresetORM).where(EnemyPresetORM.theme_name == theme.value)
        rows = self._session.execute(stmt).scalars().all()
        return [self._enemy_to_domain(r) for r in rows]

    def get_items_by_theme(self, theme: ThemeName) -> list[ItemPreset]:
        logger.debug("PresetRepository.get_items_by_theme: theme=%s", theme.value)
        stmt = select(ItemPresetORM).where(ItemPresetORM.theme_name == theme.value)
        rows = self._session.execute(stmt).scalars().all()
        return [self._item_to_domain(r) for r in rows]

    def get_npcs_by_theme(self, theme: ThemeName) -> list[NPCPreset]:
        logger.debug("PresetRepository.get_npcs_by_theme: theme=%s", theme.value)
        stmt = select(NPCPresetORM).where(NPCPresetORM.theme_name == theme.value)
        rows = self._session.execute(stmt).scalars().all()
        return [self._npc_to_domain(r) for r in rows]

    def get_quests_by_theme(self, theme: ThemeName) -> list[QuestTemplate]:
        logger.debug("PresetRepository.get_quests_by_theme: theme=%s", theme.value)
        stmt = select(QuestTemplateORM).where(
            QuestTemplateORM.theme_name == theme.value
        )
        rows = self._session.execute(stmt).scalars().all()
        return [self._quest_to_domain(r) for r in rows]

    @staticmethod
    def _enemy_to_domain(row: EnemyPresetORM) -> EnemyPreset:
        return EnemyPreset(
            id=str(row.id),
            theme=ThemeName(row.theme_name),
            name=row.name,
            hp=row.hp,
            die_type=DieType[row.die_type],
            pool_size=row.pool_size,
            ai_behavior=AIBehavior[row.ai_behavior],
            lore_tags=list(row.lore_tags),
        )

    @staticmethod
    def _item_to_domain(row: ItemPresetORM) -> ItemPreset:
        return ItemPreset(
            id=str(row.id),
            theme=ThemeName(row.theme_name),
            name=row.name,
            item_type=ItemType[row.item_type],
            rarity=row.rarity,
            gold_cost=row.gold_cost,
            chips_bonus=row.chips_bonus,
            mult_bonus=row.mult_bonus,
            description=row.description,
        )

    @staticmethod
    def _npc_to_domain(row: NPCPresetORM) -> NPCPreset:
        return NPCPreset(
            id=str(row.id),
            theme=ThemeName(row.theme_name),
            name=row.name,
            role=NPCRole[row.role],
            personality_traits=list(row.personality_traits),
            speech_style=row.speech_style,
            faction=row.faction,
        )

    @staticmethod
    def _quest_to_domain(row: QuestTemplateORM) -> QuestTemplate:
        stages = [
            QuestStage(
                stage_number=_jint(s, "stage_number"),
                title=_jstr(s, "title"),
                description=_jstr(s, "description"),
                trigger_room=_jint(s, "trigger_room"),
                completion_condition=_jstr(s, "completion_condition"),
            )
            for s in row.stages
        ]
        return QuestTemplate(
            id=str(row.id),
            theme=ThemeName(row.theme_name),
            name=row.name,
            quest_type=QuestType[row.quest_type],
            stages=stages,
            reward_gold=row.reward_gold,
            reward_item_ids=list(row.reward_item_ids),
        )


# ---------------------------------------------------------------------------
# WorldSkeletonRepository implementation
# ---------------------------------------------------------------------------


class SqlAlchemyWorldSkeletonRepository(WorldSkeletonRepository):
    """
    Persists WorldSkeleton as a single row with JSON blobs for room_sequence,
    active_quest_ids, and available_item_ids.  Full entity data (enemy stats,
    NPC details) is looked up from preset tables at query time via the
    PresetRepository — not stored redundantly here.
    """

    def __init__(
        self,
        session: Session,
        preset_repo: PresetRepository,
        theme_repo: ThemeRepository,
    ) -> None:
        self._session = session
        self._preset_repo = preset_repo
        self._theme_repo = theme_repo

    def get_by_id(self, world_id: uuid.UUID) -> WorldSkeleton | None:
        logger.debug("WorldSkeletonRepository.get_by_id: world_id=%s", world_id)
        stmt = select(WorldSkeletonORM).where(WorldSkeletonORM.id == world_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        if row is None:
            return None
        return self._to_domain(row)

    def get_by_room_id(self, room_id: uuid.UUID) -> WorldSkeleton | None:
        logger.debug("WorldSkeletonRepository.get_by_room_id: room_id=%s", room_id)
        stmt = select(WorldSkeletonORM).where(WorldSkeletonORM.room_id == room_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        if row is None:
            return None
        return self._to_domain(row)

    def save(self, skeleton: WorldSkeleton) -> None:
        logger.debug("WorldSkeletonRepository.save: world_id=%s", skeleton.id)

        room_sequence_json = [
            {
                "room_number": r.room_number,
                "room_type": r.room_type.name,
                "enemy_preset_ids": list(r.enemy_preset_ids),
                "npc_preset_id": r.npc_preset_id,
                "lore_seed": r.lore_seed,
                "is_boss_room": r.is_boss_room,
            }
            for r in skeleton.room_sequence
        ]

        settings_json: dict[str, object] = {
            "theme": skeleton.settings.theme.value,
            "difficulty": skeleton.settings.difficulty,
            "room_count": skeleton.settings.room_count,
            "seed": skeleton.settings.seed,
        }

        orm_row = WorldSkeletonORM(
            id=skeleton.id,
            room_id=skeleton.room_id,
            theme_name=skeleton.theme.name.value,
            settings=settings_json,
            room_sequence=room_sequence_json,
            active_quest_ids=[q.id for q in skeleton.active_quests],
            available_item_ids=[i.id for i in skeleton.available_items],
            world_flags=skeleton.world_flags,
            created_at=skeleton.created_at,
        )
        self._session.merge(orm_row)
        self._session.flush()
        logger.debug("WorldSkeletonRepository.save: flushed world_id=%s", skeleton.id)

    def _to_domain(self, row: WorldSkeletonORM) -> WorldSkeleton:
        """Reconstruct a full WorldSkeleton from the ORM row + preset lookups."""
        theme_name = ThemeName(row.theme_name)

        # Re-hydrate the Theme value object.
        theme = self._theme_repo.get_by_name(theme_name)
        if theme is None:
            # Should never happen if FK is intact; log and construct a minimal fallback.
            logger.error(
                "WorldSkeletonRepository._to_domain: theme %s not found", row.theme_name
            )
            raise ValueError(f"Theme {row.theme_name} missing from database")

        # Re-hydrate room sequence from JSON blob.
        room_sequence = [
            DungeonRoom(
                room_number=_jint(r, "room_number"),
                room_type=RoomType[_jstr(r, "room_type")],
                enemy_preset_ids=tuple(_jlist_str(r, "enemy_preset_ids")),
                npc_preset_id=_jstr(r, "npc_preset_id") or None,
                lore_seed=_jstr(r, "lore_seed"),
                is_boss_room=bool(r.get("is_boss_room", False)),
            )
            for r in row.room_sequence
        ]

        # Re-hydrate quests from preset repo.
        all_quests = self._preset_repo.get_quests_by_theme(theme_name)
        quest_map = {q.id: q for q in all_quests}
        active_quests = [
            quest_map[qid] for qid in row.active_quest_ids if qid in quest_map
        ]

        # Re-hydrate available items from preset repo.
        all_items = self._preset_repo.get_items_by_theme(theme_name)
        item_map = {i.id: i for i in all_items}
        available_items = [
            item_map[iid] for iid in row.available_item_ids if iid in item_map
        ]

        settings_dict = row.settings
        seed_raw = settings_dict.get("seed")
        settings = WorldSettings(
            theme=theme_name,
            difficulty=_jstr(settings_dict, "difficulty", "normal"),
            room_count=_jint(settings_dict, "room_count", 10),
            seed=_jint(settings_dict, "seed") if isinstance(seed_raw, int) else None,
        )

        # created_at is stored as a DateTime column; SQLAlchemy returns a datetime object.
        created_at_raw = row.created_at
        if isinstance(created_at_raw, datetime):
            created_at = created_at_raw
        else:
            # Fallback: parse from string if stored as ISO string (shouldn't happen).
            created_at = datetime.fromisoformat(str(created_at_raw))

        return WorldSkeleton(
            id=row.id,
            room_id=row.room_id,
            theme=theme,
            settings=settings,
            room_sequence=room_sequence,
            active_quests=active_quests,
            available_items=available_items,
            world_flags=dict(row.world_flags),
            created_at=created_at,
        )

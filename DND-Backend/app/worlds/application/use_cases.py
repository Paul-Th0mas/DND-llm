"""
Application use cases for the worlds bounded context.

Each class handles exactly one use case.  They orchestrate domain objects,
repositories, and services but contain no business logic themselves — all
invariants live in the domain layer.
"""

import json
import logging
import uuid
from abc import ABC, abstractmethod

from app.worlds.application.schemas import (
    DungeonRoomResponse,
    EnemyPresetResponse,
    NPCPresetResponse,
    NarrateRoomResponse,
    WorldSkeletonResponse,
)
from app.worlds.domain.models import (
    DungeonRoom,
    EnemyPreset,
    NPCPreset,
    WorldSettings,
    WorldSkeleton,
)
from app.worlds.domain.repositories import (
    PresetRepository,
    ThemeNotFoundError,
    ThemeRepository,
    WorldNotFoundError,
    WorldSkeletonRepository,
)
from app.worlds.domain.services import WorldCompiler

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Narrator port — abstract interface defined in the application layer
# so use cases depend on an abstraction, not a concrete LLM client.
# ---------------------------------------------------------------------------


class NarratorPort(ABC):
    """
    Port for the LLM narrator.

    Returns None on failure; use cases fall back to lore_seed template text.
    The concrete implementation lives in infrastructure/narrator.py and is
    injected via FastAPI dependency injection.
    """

    @abstractmethod
    def narrate_room(self, prompt: str) -> str | None: ...


# ---------------------------------------------------------------------------
# CompileWorldUseCase
# ---------------------------------------------------------------------------


class CompileWorldUseCase:
    """
    Orchestrates world compilation:
      1. Load theme + presets from DB via repositories.
      2. Delegate compilation to WorldCompiler domain service.
      3. Patch the skeleton's room_id with the caller-supplied value.
      4. Persist the WorldSkeleton.
      5. Return WorldSkeletonResponse DTO.
    """

    def __init__(
        self,
        theme_repo: ThemeRepository,
        preset_repo: PresetRepository,
        world_repo: WorldSkeletonRepository,
        compiler: WorldCompiler,
    ) -> None:
        self._theme_repo = theme_repo
        self._preset_repo = preset_repo
        self._world_repo = world_repo
        self._compiler = compiler

    def execute(
        self, settings: WorldSettings, room_id: uuid.UUID
    ) -> WorldSkeletonResponse:
        logger.debug(
            "CompileWorldUseCase: theme=%s difficulty=%s room_id=%s",
            settings.theme.value,
            settings.difficulty,
            room_id,
        )

        theme = self._theme_repo.get_by_name(settings.theme)
        if theme is None:
            raise ThemeNotFoundError(
                f"Theme '{settings.theme.value}' not found in database"
            )

        enemies = self._preset_repo.get_enemies_by_theme(settings.theme)
        items = self._preset_repo.get_items_by_theme(settings.theme)
        npcs = self._preset_repo.get_npcs_by_theme(settings.theme)
        quests = self._preset_repo.get_quests_by_theme(settings.theme)

        logger.debug(
            "Loaded presets: enemies=%d items=%d npcs=%d quests=%d",
            len(enemies),
            len(items),
            len(npcs),
            len(quests),
        )

        skeleton = self._compiler.compile(
            settings=settings,
            theme=theme,
            enemies=enemies,
            items=items,
            npcs=npcs,
            quests=quests,
        )

        # WorldCompiler uses a placeholder room_id (UUID int=0) to stay pure.
        # Patch it with the real room_id before persisting.
        skeleton.room_id = room_id

        self._world_repo.save(skeleton)
        logger.info(
            "CompileWorld: saved world id=%s room_id=%s", skeleton.id, skeleton.room_id
        )

        return WorldSkeletonResponse(
            id=skeleton.id,
            theme=skeleton.theme.name.value,
            difficulty=skeleton.settings.difficulty,
            room_count=len(skeleton.room_sequence),
            active_quests=[q.name for q in skeleton.active_quests],
        )


# ---------------------------------------------------------------------------
# GetRoomUseCase
# ---------------------------------------------------------------------------


class GetRoomUseCase:
    """Return full DungeonRoomResponse for a specific room number."""

    def __init__(
        self,
        world_repo: WorldSkeletonRepository,
        preset_repo: PresetRepository,
    ) -> None:
        self._world_repo = world_repo
        self._preset_repo = preset_repo

    def execute(self, world_id: uuid.UUID, room_number: int) -> DungeonRoomResponse:
        logger.debug(
            "GetRoomUseCase: world_id=%s room_number=%d", world_id, room_number
        )

        skeleton = self._world_repo.get_by_id(world_id)
        if skeleton is None:
            raise WorldNotFoundError(f"World {world_id} not found")

        # get_room raises WorldRoomNotFoundError (→ HTTP 404) if out of range.
        dungeon_room: DungeonRoom = skeleton.get_room(room_number)

        # Resolve enemy preset ids → full EnemyPreset objects.
        all_enemies = self._preset_repo.get_enemies_by_theme(skeleton.theme.name)
        enemy_map: dict[str, EnemyPreset] = {e.id: e for e in all_enemies}
        enemies: list[EnemyPreset] = [
            enemy_map[eid] for eid in dungeon_room.enemy_preset_ids if eid in enemy_map
        ]

        # Resolve optional NPC preset id → NPCPreset.
        npc_response: NPCPresetResponse | None = None
        if dungeon_room.npc_preset_id is not None:
            all_npcs = self._preset_repo.get_npcs_by_theme(skeleton.theme.name)
            npc_map: dict[str, NPCPreset] = {n.id: n for n in all_npcs}
            npc: NPCPreset | None = npc_map.get(dungeon_room.npc_preset_id)
            if npc is not None:
                npc_response = NPCPresetResponse(
                    id=npc.id,
                    name=npc.name,
                    role=npc.role.name,
                    speech_style=npc.speech_style,
                )

        return DungeonRoomResponse(
            room_number=dungeon_room.room_number,
            room_type=dungeon_room.room_type.name,
            enemies=[
                EnemyPresetResponse(
                    id=e.id,
                    name=e.name,
                    hp=e.hp,
                    die_type=e.die_type.name,
                    pool_size=e.pool_size,
                    ai_behavior=e.ai_behavior.name,
                    lore_tags=e.lore_tags,
                )
                for e in enemies
            ],
            npc=npc_response,
            lore_seed=dungeon_room.lore_seed,
            is_boss_room=dungeon_room.is_boss_room,
        )


# ---------------------------------------------------------------------------
# NarrateRoomUseCase
# ---------------------------------------------------------------------------


class NarrateRoomUseCase:
    """
    Assembles an LLM prompt from the WorldSkeleton + caller-supplied game_state,
    delegates to NarratorPort, and returns themed narrative text.

    Falls back to lore_seed text if the narrator returns None (e.g. NullNarrator
    or network failure from a real LLM client).
    """

    def __init__(
        self,
        world_repo: WorldSkeletonRepository,
        narrator: NarratorPort,
    ) -> None:
        self._world_repo = world_repo
        self._narrator = narrator

    def execute(
        self,
        world_id: uuid.UUID,
        room_number: int,
        game_state: dict[str, object],
    ) -> NarrateRoomResponse:
        logger.debug(
            "NarrateRoomUseCase: world_id=%s room_number=%d", world_id, room_number
        )

        skeleton = self._world_repo.get_by_id(world_id)
        if skeleton is None:
            raise WorldNotFoundError(f"World {world_id} not found")

        dungeon_room: DungeonRoom = skeleton.get_room(room_number)

        prompt = self._build_prompt(skeleton, dungeon_room, game_state)
        narrative = self._narrator.narrate_room(prompt)

        if narrative is None:
            # Graceful fallback: use the room's lore seed as the description.
            logger.warning(
                "NarrateRoom: narrator returned None for world=%s room=%d; using fallback",
                world_id,
                room_number,
            )
            threat = "high" if dungeon_room.is_boss_room else "medium"
            return NarrateRoomResponse(
                description=dungeon_room.lore_seed,
                ambient_detail="The air is still.",
                threat_level=threat,
                cached=False,
            )

        # Attempt to parse the structured JSON the LLM returns.
        try:
            parsed: dict[str, object] = json.loads(narrative)
            return NarrateRoomResponse(
                description=str(parsed.get("description", dungeon_room.lore_seed)),
                ambient_detail=str(parsed.get("ambient_detail", "")),
                threat_level=str(parsed.get("threat_level", "medium")),
                cached=False,
            )
        except (json.JSONDecodeError, KeyError):
            logger.warning(
                "NarrateRoom: failed to parse LLM JSON; using raw text as description"
            )
            return NarrateRoomResponse(
                description=narrative,
                ambient_detail="",
                threat_level="medium",
                cached=False,
            )

    def _build_prompt(
        self,
        skeleton: WorldSkeleton,
        dungeon_room: DungeonRoom,
        game_state: dict[str, object],
    ) -> str:
        """
        Interpolate theme metadata and game state into the narrator prompt template.
        The template is defined in infrastructure/narrator.py (ROOM_NARRATIVE_PROMPT).
        """
        from app.worlds.infrastructure.narrator import ROOM_NARRATIVE_PROMPT

        # Determine current quest stage title from the active main quest.
        quest_stage_title = "Unknown"
        if skeleton.active_quests:
            main_quest = skeleton.active_quests[0]
            for stage in main_quest.stages:
                if stage.trigger_room <= dungeon_room.room_number:
                    quest_stage_title = stage.title

        flags_str = (
            ", ".join(f"{k}={v}" for k, v in skeleton.world_flags.items()) or "none"
        )

        # Enemy names from the room's preset ids (ids serve as names in the prompt
        # until the real narrator resolves them via the DB at runtime).
        enemy_names = ", ".join(dungeon_room.enemy_preset_ids) or "none"
        npc_name = dungeon_room.npc_preset_id or "none"

        hp = game_state.get("hp", "?")
        max_hp = game_state.get("max_hp", "?")
        gold = game_state.get("gold", 0)

        return ROOM_NARRATIVE_PROMPT.format(
            tone_descriptor=skeleton.theme.tone_descriptor,
            language_style=skeleton.theme.language_style,
            currency_name=skeleton.theme.currency_name,
            health_term=skeleton.theme.health_term,
            banned_words_csv=", ".join(skeleton.theme.banned_words),
            room_number=dungeon_room.room_number,
            room_count=len(skeleton.room_sequence),
            quest_stage_title=quest_stage_title,
            flags=flags_str,
            lore_seed=dungeon_room.lore_seed,
            enemy_names=enemy_names,
            npc_name=npc_name,
            npc_speech_style="direct",
            hp=hp,
            max_hp=max_hp,
            gold=gold,
        )

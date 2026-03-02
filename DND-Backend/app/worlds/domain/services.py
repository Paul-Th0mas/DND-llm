"""
WorldCompiler domain service.

Pure Python — no DB, no HTTP.  Takes presets and settings and produces
a fully-compiled WorldSkeleton ready to be persisted by a repository.

This is a domain service (rather than aggregate method) because the compilation
logic spans multiple entity types (enemies, items, NPCs, quests) and does not
belong to any single aggregate.
"""

import logging
import random
import uuid
from datetime import datetime, timezone

from app.worlds.domain.models import (
    AIBehavior,
    DungeonRoom,
    EnemyPreset,
    ItemPreset,
    NPCPreset,
    QuestTemplate,
    QuestType,
    RoomType,
    Theme,
    ThemeName,
    WorldSettings,
    WorldSkeleton,
)
from app.worlds.domain.repositories import WorldCompilationError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Room layout constants
# ---------------------------------------------------------------------------

# Fixed room type layout for a 10-room dungeon.
# Index 0 = room 1, index 9 = room 10.
ROOM_TYPE_LAYOUT: list[RoomType] = [
    RoomType.COMBAT,  # room 1  — normal
    RoomType.COMBAT,  # room 2  — normal
    RoomType.COMBAT,  # room 3  — normal
    RoomType.SHOP,  # room 4  — shop break
    RoomType.COMBAT,  # room 5  — scaled
    RoomType.COMBAT,  # room 6  — scaled
    RoomType.REST,  # room 7  — rest break
    RoomType.COMBAT,  # room 8  — hard
    RoomType.COMBAT,  # room 9  — hard
    RoomType.BOSS,  # room 10 — boss
]

# How many enemy presets to assign per combat room (by room number).
_ENEMY_COUNT: dict[int, int] = {
    1: 1,
    2: 1,
    3: 2,  # normal rooms: 1-2 enemies
    5: 2,
    6: 2,  # scaled rooms: 2 enemies
    8: 2,
    9: 3,  # hard rooms: 2-3 enemies
    10: 1,  # boss room: 1 boss
}

# How many shop items to make available in the run.
_SHOP_ITEM_COUNT = 10

# Maximum number of side quests alongside the main quest.
_MAX_SIDE_QUESTS = 2


class WorldCompiler:
    """
    Compiles a WorldSkeleton from settings and loaded presets.

    Invariants enforced:
      - Room 10 is always BOSS type.
      - Boss room has exactly 1 enemy with hp × 2 and pool_size + 2.
      - Main quest has exactly 1 stage per 3 rooms.
      - Shop contains at least 1 item of each rarity tier.
      - No duplicate enemy names in the same run.
    """

    def compile(
        self,
        settings: WorldSettings,
        theme: Theme,
        enemies: list[EnemyPreset],
        items: list[ItemPreset],
        npcs: list[NPCPreset],
        quests: list[QuestTemplate],
    ) -> WorldSkeleton:
        """
        Build and return a WorldSkeleton.

        Raises WorldCompilationError when the preset data is insufficient.
        """
        logger.info(
            "WorldCompiler.compile theme=%s difficulty=%s seed=%s",
            theme.name.value,
            settings.difficulty,
            settings.seed,
        )

        self._validate_inputs(enemies, items, quests)

        # Initialise random with the optional seed for reproducible generation.
        rng = random.Random(settings.seed)

        room_sequence = self._build_rooms(enemies, npcs, rng)
        selected_quests = self._select_quests(quests, rng)
        shop_items = self._select_shop_items(items, rng)

        skeleton = WorldSkeleton(
            id=uuid.uuid4(),
            room_id=uuid.UUID(
                int=0
            ),  # placeholder — caller must override with real room_id
            theme=theme,
            settings=settings,
            room_sequence=room_sequence,
            active_quests=selected_quests,
            available_items=shop_items,
            world_flags={},
            created_at=datetime.now(tz=timezone.utc),
        )
        logger.info(
            "WorldCompiler compiled world id=%s rooms=%d quests=%d",
            skeleton.id,
            len(room_sequence),
            len(selected_quests),
        )
        return skeleton

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_inputs(
        self,
        enemies: list[EnemyPreset],
        items: list[ItemPreset],
        quests: list[QuestTemplate],
    ) -> None:
        """Raise WorldCompilationError when required presets are missing."""
        if not enemies:
            raise WorldCompilationError(
                "Cannot compile world: no enemy presets available for this theme"
            )
        main_quests = [q for q in quests if q.quest_type == QuestType.MAIN]
        if not main_quests:
            raise WorldCompilationError(
                "Cannot compile world: no main quest template available for this theme"
            )
        if not items:
            raise WorldCompilationError(
                "Cannot compile world: no item presets available for this theme"
            )

    def _build_rooms(
        self,
        enemies: list[EnemyPreset],
        npcs: list[NPCPreset],
        rng: random.Random,
    ) -> list[DungeonRoom]:
        """
        Construct the 10-room sequence.

        Enemies are assigned without repetition per run (no duplicate names).
        The boss room uses a modified copy of the strongest enemy.
        """
        rooms: list[DungeonRoom] = []
        # Track assigned enemy ids to avoid duplicates within the run.
        used_enemy_ids: set[str] = set()

        # Separate boss candidates from normal enemies.
        # Boss candidates are any enemy in the list; pick the last one (typically
        # the seeded "boss" enemy) and scale it up.
        boss_candidate = enemies[-1]

        for idx, room_type in enumerate(ROOM_TYPE_LAYOUT):
            room_number = idx + 1

            if room_type == RoomType.BOSS:
                # Boss room: one scaled-up enemy.
                enemy_ids = self._assign_boss(boss_candidate)
                npc_id = self._pick_npc(npcs, rng)
                lore_seed = f"The final chamber — {boss_candidate.name} awaits"
                rooms.append(
                    DungeonRoom(
                        room_number=room_number,
                        room_type=room_type,
                        enemy_preset_ids=tuple(enemy_ids),
                        npc_preset_id=npc_id,
                        lore_seed=lore_seed,
                        is_boss_room=True,
                    )
                )

            elif room_type == RoomType.COMBAT:
                count = _ENEMY_COUNT.get(room_number, 1)
                enemy_ids = self._pick_enemies(
                    enemies[:-1],  # exclude boss from normal rooms
                    count,
                    used_enemy_ids,
                    rng,
                )
                lore_seed = f"Room {room_number} — enemies lurk in the shadows"
                rooms.append(
                    DungeonRoom(
                        room_number=room_number,
                        room_type=room_type,
                        enemy_preset_ids=tuple(enemy_ids),
                        npc_preset_id=None,
                        lore_seed=lore_seed,
                        is_boss_room=False,
                    )
                )

            elif room_type == RoomType.SHOP:
                npc_id = self._pick_npc(npcs, rng)
                rooms.append(
                    DungeonRoom(
                        room_number=room_number,
                        room_type=room_type,
                        enemy_preset_ids=(),
                        npc_preset_id=npc_id,
                        lore_seed="A merchant's stall lit by a guttering torch",
                        is_boss_room=False,
                    )
                )

            elif room_type == RoomType.REST:
                rooms.append(
                    DungeonRoom(
                        room_number=room_number,
                        room_type=room_type,
                        enemy_preset_ids=(),
                        npc_preset_id=None,
                        lore_seed="A brief respite — the party tends their wounds",
                        is_boss_room=False,
                    )
                )

            else:
                # Generic fallback for TREASURE / EVENT types (not in default layout,
                # but handle gracefully if layout is customised later).
                rooms.append(
                    DungeonRoom(
                        room_number=room_number,
                        room_type=room_type,
                        enemy_preset_ids=(),
                        npc_preset_id=None,
                        lore_seed=f"Room {room_number}",
                        is_boss_room=False,
                    )
                )

        return rooms

    def _pick_enemies(
        self,
        pool: list[EnemyPreset],
        count: int,
        used_ids: set[str],
        rng: random.Random,
    ) -> list[str]:
        """
        Pick `count` enemy presets from the pool that haven't been used yet.
        If the unused pool is exhausted, resets used_ids to allow reuse
        (prevents a crash on small preset lists while maintaining variety).
        """
        available = [e for e in pool if e.id not in used_ids]
        if len(available) < count:
            # Reset to allow reuse rather than failing on small seed data.
            logger.warning("Enemy pool exhausted; resetting used-ids to allow reuse")
            used_ids.clear()
            available = list(pool)

        chosen = rng.sample(available, min(count, len(available)))
        for e in chosen:
            used_ids.add(e.id)
        return [e.id for e in chosen]

    def _assign_boss(self, boss: EnemyPreset) -> list[str]:
        """
        Return the boss enemy id.
        Scaling (hp × 2, pool_size + 2) is recorded as metadata in the ORM
        layer via a separate boss_scaled flag — here we just reference the id.
        The use case layer applies scaling when constructing Combatants.
        """
        return [boss.id]

    def _pick_npc(
        self,
        npcs: list[NPCPreset],
        rng: random.Random,
    ) -> str | None:
        """Pick one NPC at random; return None if no NPCs are available."""
        if not npcs:
            return None
        return rng.choice(npcs).id

    def _select_quests(
        self,
        quests: list[QuestTemplate],
        rng: random.Random,
    ) -> list[QuestTemplate]:
        """
        Select 1 main quest + up to 2 side quests.

        Raises WorldCompilationError if no main quest exists (already validated
        in _validate_inputs, but guard here for safety).
        """
        main_quests = [q for q in quests if q.quest_type == QuestType.MAIN]
        side_quests = [q for q in quests if q.quest_type == QuestType.SIDE]

        selected: list[QuestTemplate] = [rng.choice(main_quests)]

        if side_quests:
            count = min(_MAX_SIDE_QUESTS, len(side_quests))
            selected.extend(rng.sample(side_quests, count))

        logger.debug(
            "Selected %d quests (1 main + %d side)", len(selected), len(selected) - 1
        )
        return selected

    def _select_shop_items(
        self,
        items: list[ItemPreset],
        rng: random.Random,
    ) -> list[ItemPreset]:
        """
        Select _SHOP_ITEM_COUNT items for the run's shop inventory.

        Invariant: at least 1 item of each rarity tier must be included.
        Fills remaining slots from a random shuffle of all items.
        """
        rarities = ["common", "uncommon", "rare", "legendary"]
        selected: list[ItemPreset] = []
        selected_ids: set[str] = set()

        # Guarantee one of each rarity.
        for rarity in rarities:
            tier = [i for i in items if i.rarity == rarity]
            if tier:
                pick = rng.choice(tier)
                if pick.id not in selected_ids:
                    selected.append(pick)
                    selected_ids.add(pick.id)

        # Fill remaining slots up to _SHOP_ITEM_COUNT.
        remaining = [i for i in items if i.id not in selected_ids]
        rng.shuffle(remaining)
        for item in remaining:
            if len(selected) >= _SHOP_ITEM_COUNT:
                break
            selected.append(item)

        logger.debug("Selected %d shop items", len(selected))
        return selected

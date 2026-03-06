"""
World narration infrastructure.

Contains two narrator classes:

  StubNarrator   — implements NarratorPort with deterministic template output.
                   No LLM calls. Swap in for offline development and testing.

  GeminiNarrator — implements NarratorPort using the Google Gemini API.
                   Requires GEMINI_API_KEY in the environment.
                   Uses PromptAssembler (from prompts/) to build the prompt and
                   parses the JSON response back into domain objects.

Prompt assembly has moved to app/worlds/infrastructure/prompts/:
  dnd_rules_context.py  — static D&D 5e rules block (cacheable)
  world_generation.py   — per-run dynamic block (changes every request)
  assembler.py          — PromptAssembler composes both into a final string
"""

import json
import logging
from typing import cast

from google import genai
from google.genai import types as genai_types

from app.worlds.application.narrator_port import NarratorPort
from app.worlds.infrastructure.prompts import PromptAssembler
from app.worlds.domain.exceptions import WorldGenerationError
from app.worlds.domain.models import (
    Difficulty,
    GeneratedWorld,
    MainQuest,
    NarratedRoom,
    QuestFocus,
    RoomType,
    Theme,
    WorldSettings,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Static per-theme data used by StubNarrator
# ---------------------------------------------------------------------------

# World names pool per theme — StubNarrator picks based on room_count parity
# to stay deterministic for the same settings.
_WORLD_NAMES: dict[Theme, list[str]] = {
    Theme.MEDIEVAL_FANTASY: [
        "The Sunken Citadel of Malachar",
        "Dungeon of the Ashen Crown",
        "The Hollow Keep of Greyspire",
        "Catacombs of the Forgotten King",
        "The Shattered Vault of Eldenmoor",
    ],
    Theme.CYBERPUNK: [
        "Neon District Zero-Seven",
        "The Hexadome of Nexus Corp",
        "Sublevel Omega, DataHaven",
        "The Glitch Corridor",
        "Undercity Node 44",
    ],
    Theme.MANHWA: [
        "The Abyssal Gate — Floor 43",
        "Red Lotus Sect Hidden Realm",
        "Sky Sovereign's Trial Ground",
        "The Cursed Dungeon of Iron Blood",
        "Heaven's Peak Secret Domain",
    ],
    Theme.POST_APOCALYPTIC: [
        "The Rust Bunker, Sector 9",
        "Wasteland Crucible of the Warlords",
        "Crumbled Vault of the Old World",
        "The Rad-Storm Maze",
        "Deadzone Facility Epsilon",
    ],
}

_WORLD_DESCRIPTIONS: dict[Theme, str] = {
    Theme.MEDIEVAL_FANTASY: (
        "Ancient stone corridors carved by long-dead dwarven hands, now overrun by "
        "dark creatures serving a shadowy master. Every torch-lit hall hides traps "
        "and secrets from a forgotten age."
    ),
    Theme.CYBERPUNK: (
        "A maze of flickering neon signs, corroded server racks, and razor-wire "
        "fences deep beneath the megacity. Corporate kill-squads patrol the upper "
        "levels while rogue AIs own the dark."
    ),
    Theme.MANHWA: (
        "A dimensional gate dungeon pulsing with spiritual energy. Ranked hunters "
        "have failed to clear this floor for months. Mana crystals float through "
        "corridors where ancient beasts have evolved beyond their base forms."
    ),
    Theme.POST_APOCALYPTIC: (
        "A pre-war bunker complex reclaimed by scavenger gangs and mutated wildlife. "
        "Radiation seeps through cracked concrete. Salvageable tech hides behind "
        "rusted blast doors and the bones of those who came before."
    ),
}

_ATMOSPHERES: dict[Theme, str] = {
    Theme.MEDIEVAL_FANTASY: "Oppressive dread broken by flickering torchlight and distant chanting.",
    Theme.CYBERPUNK: "Damp ozone and the hum of illegal servers. Surveillance drones circle overhead.",
    Theme.MANHWA: "Dense mana pressure that makes breathing difficult. The air tastes of blood and qi.",
    Theme.POST_APOCALYPTIC: "Acrid smoke, Geiger-counter clicks, and the distant howl of wasteland wind.",
}

_FACTIONS: dict[Theme, list[str]] = {
    Theme.MEDIEVAL_FANTASY: [
        "The Ashen Brotherhood",
        "Order of the Gilded Seal",
        "Shadowthorn Cultists",
        "The Iron Merchants Guild",
    ],
    Theme.CYBERPUNK: [
        "Nexus Corp Security Division",
        "Ghost Protocol Hackers",
        "The Chrome Syndicate",
        "NeuroFlesh Augmenters",
    ],
    Theme.MANHWA: [
        "Red Lotus Sect",
        "Heaven's Peak Association",
        "The Iron Blood Warriors",
        "Void Sovereign's Remnants",
    ],
    Theme.POST_APOCALYPTIC: [
        "The Rustblood Raiders",
        "Vault-Keeper Remnants",
        "Scavenger Kings of Sector 9",
        "The Rad-Cult",
    ],
}

# Enemy name pools per theme — stub generates names by cycling through these lists
_ENEMIES: dict[Theme, list[str]] = {
    Theme.MEDIEVAL_FANTASY: [
        "Skeletal Warrior",
        "Cursed Knight",
        "Dungeon Troll",
        "Wraith of the Fallen",
        "Stone Golem",
        "Venomfang Bat",
        "Dark Acolyte",
        "Bone Archer",
    ],
    Theme.CYBERPUNK: [
        "Corp Enforcer",
        "Rogue Combat Drone",
        "Neural-Hacked Guard",
        "Killbot MK-3",
        "Black-Ice Construct",
        "Wired Mercenary",
        "Turret Mk-VII",
    ],
    Theme.MANHWA: [
        "B-Rank Stone Ogre",
        "Mana Poisoned Wolf",
        "Iron-Body Beetle",
        "Shadow Leopard",
        "A-Rank Bone Drake",
        "Cursed Spirit Remnant",
        "Elite Gate Guardian",
    ],
    Theme.POST_APOCALYPTIC: [
        "Raider Scout",
        "Irradiated Ghoul",
        "Mutant Hound",
        "Scrap-Armored Brute",
        "Toxic Crawler",
        "Salvage Drone",
        "Warlord's Lieutenant",
    ],
}

# Boss enemies (one per theme)
_BOSS_ENEMIES: dict[Theme, str] = {
    Theme.MEDIEVAL_FANTASY: "The Lich Lord Malachar",
    Theme.CYBERPUNK: "Apex Combat Unit — CERBERUS",
    Theme.MANHWA: "S-Rank Gate Boss: Void Sovereign Fragment",
    Theme.POST_APOCALYPTIC: "Warlord Rex, the Chrome Butcher",
}

# Room names per room type and theme
_ROOM_NAMES: dict[Theme, dict[RoomType, list[str]]] = {
    Theme.MEDIEVAL_FANTASY: {
        RoomType.COMBAT: [
            "Guard Chamber",
            "Crypts Antechamber",
            "Torch Hall",
            "Bone Pit",
        ],
        RoomType.SHOP: ["Wandering Merchant's Alcove", "Trapped Trader's Den"],
        RoomType.REST: ["Hidden Shrine of Respite", "Collapsed Safe Room"],
        RoomType.BOSS: ["The Throne of Ash"],
        RoomType.TREASURE: ["Forgotten Vault", "Hoard Chamber"],
        RoomType.EVENT: ["The Whispering Statue", "The Cursed Mirror Room"],
    },
    Theme.CYBERPUNK: {
        RoomType.COMBAT: [
            "Server Corridor",
            "Maintenance Shaft",
            "Guard Post Alpha",
            "Loading Bay",
        ],
        RoomType.SHOP: ["Black Market Stall", "Ripperdoc Nook"],
        RoomType.REST: ["Abandoned Break Room", "Shielded Safe Node"],
        RoomType.BOSS: ["Core Processing Chamber"],
        RoomType.TREASURE: ["Data Vault", "Contraband Cache"],
        RoomType.EVENT: ["Neural Firewall Puzzle", "Rogue AI Terminal"],
    },
    Theme.MANHWA: {
        RoomType.COMBAT: [
            "Trial Chamber",
            "Mana Crystal Corridor",
            "Beast Den",
            "Bone Graveyard",
        ],
        RoomType.SHOP: ["Wandering Merchant Gate", "Hunter's Supply Cache"],
        RoomType.REST: ["Spiritual Recovery Node", "Safe Zone Pocket"],
        RoomType.BOSS: ["Final Boss Chamber"],
        RoomType.TREASURE: ["Mana Crystal Vault", "Ancient Artifact Room"],
        RoomType.EVENT: ["The Illusion Trial", "Rank Assessment Chamber"],
    },
    Theme.POST_APOCALYPTIC: {
        RoomType.COMBAT: [
            "Raider Checkpoint",
            "Collapsed Corridor",
            "Motor Pool",
            "Guard Shack",
        ],
        RoomType.SHOP: ["Wasteland Trader's Wagon", "Black Market Stash"],
        RoomType.REST: ["Sealed Bunk Room", "Filtered Air Chamber"],
        RoomType.BOSS: ["Warlord's Command Bunker"],
        RoomType.TREASURE: ["Armory Cache", "Pre-War Supply Depot"],
        RoomType.EVENT: ["The Propaganda Terminal", "Mutant Negotiation Standoff"],
    },
}

# Quest templates per quest_focus
_QUEST_NAMES: dict[QuestFocus, str] = {
    QuestFocus.EXPLORATION: "Map the Unknown",
    QuestFocus.RESCUE: "Rescue the Captive",
    QuestFocus.ASSASSINATION: "Eliminate the Target",
    QuestFocus.HEIST: "Steal the Relic",
    QuestFocus.MYSTERY: "Uncover the Truth",
}

_QUEST_DESCRIPTIONS: dict[QuestFocus, str] = {
    QuestFocus.EXPLORATION: (
        "Push through every room of the dungeon, chart its layout, and return "
        "with knowledge of what lies within."
    ),
    QuestFocus.RESCUE: (
        "A prisoner is held somewhere in the depths. Find them alive, neutralize "
        "their guards, and bring them back to the surface."
    ),
    QuestFocus.ASSASSINATION: (
        "A high-value target commands this dungeon. Fight through their defenses "
        "and end their reign permanently."
    ),
    QuestFocus.HEIST: (
        "A priceless relic is locked in the deepest vault. Extract it without "
        "triggering the full alarm — stealth matters as much as strength."
    ),
    QuestFocus.MYSTERY: (
        "Strange disappearances link back to this dungeon. Gather evidence, "
        "decode the hidden messages, and expose the true threat."
    ),
}

_QUEST_STAGES: dict[QuestFocus, tuple[str, ...]] = {
    QuestFocus.EXPLORATION: (
        "Enter the dungeon and breach the first locked gate.",
        "Chart the mid-tier rooms and mark points of interest.",
        "Reach the deepest chamber and confirm the dungeon layout.",
    ),
    QuestFocus.RESCUE: (
        "Locate the prisoner's last known holding area.",
        "Neutralize the guard captain and acquire the cell key.",
        "Escort the prisoner safely back to the entrance.",
    ),
    QuestFocus.ASSASSINATION: (
        "Fight past the outer guard posts to reach the inner sanctum.",
        "Eliminate the target's lieutenants to isolate them.",
        "Confront and eliminate the primary target.",
    ),
    QuestFocus.HEIST: (
        "Bypass security in the outer corridors undetected.",
        "Crack the vault's secondary lock system.",
        "Extract the relic and escape before the alarm reaches full alert.",
    ),
    QuestFocus.MYSTERY: (
        "Gather evidence from the first three rooms.",
        "Decode the hidden message found in the event room.",
        "Confront the true mastermind revealed by the evidence.",
    ),
}


# ---------------------------------------------------------------------------
# Room distribution algorithm
# ---------------------------------------------------------------------------


def _build_room_sequence(room_count: int) -> list[RoomType]:
    """
    Build the ordered list of room types for a dungeon of the given size.

    Rules (from design spec):
      - Room 0 (first): always COMBAT
      - Room room_count-1 (last): always BOSS
      - ~30% mark: SHOP
      - ~60% mark: REST
      - >= 8 rooms: one EVENT room placed mid-run
      - All other rooms: COMBAT

    The result is deterministic for a given room_count — no randomness.
    This makes test assertions reliable.
    """
    sequence: list[RoomType] = [RoomType.COMBAT] * room_count

    # Last room is always BOSS
    sequence[room_count - 1] = RoomType.BOSS

    # Mark the SHOP at ~30% of the run (but not index 0 or last)
    shop_index = max(1, round(room_count * 0.3))
    if shop_index >= room_count - 1:
        shop_index = room_count - 2
    sequence[shop_index] = RoomType.SHOP

    # Mark REST at ~60% (not overlapping SHOP or last)
    rest_index = max(1, round(room_count * 0.6))
    if rest_index >= room_count - 1:
        rest_index = room_count - 2
    if rest_index == shop_index:
        rest_index = min(rest_index + 1, room_count - 2)
    sequence[rest_index] = RoomType.REST

    # One EVENT room if room count allows, placed mid-run
    if room_count >= 8:
        event_index = room_count // 2
        if sequence[event_index] == RoomType.COMBAT:
            sequence[event_index] = RoomType.EVENT

    logger.debug("Room sequence built: %s", [r.value for r in sequence])
    return sequence


def _pick(pool: list[str], index: int) -> str:
    """Select an item from a pool by cycling through it using the given index."""
    return pool[index % len(pool)]


# ---------------------------------------------------------------------------
# StubNarrator
# ---------------------------------------------------------------------------


class StubNarrator(NarratorPort):
    """
    Template-based narrator that returns realistic worlds without any LLM call.

    All output is deterministic: the same WorldSettings always produces the
    same GeneratedWorld. This makes tests reliable and development fast.

    Room content is built from per-theme static lookup tables. When a real
    LLM narrator is ready, swap StubNarrator in get_narrator() (dependencies.py).
    """

    def generate_world(self, settings: WorldSettings) -> GeneratedWorld:
        """
        Generate a complete world from theme-based static templates.

        @param settings - Validated WorldSettings domain value object.
        @returns A fully populated GeneratedWorld with rooms, quest, and factions.
        """
        logger.info(
            "StubNarrator generating world: theme=%s difficulty=%s rooms=%d",
            settings.theme,
            settings.difficulty,
            settings.room_count,
        )

        theme = settings.theme

        # Pick world name deterministically (parity of room_count as offset)
        name_pool = _WORLD_NAMES[theme]
        world_name = name_pool[settings.room_count % len(name_pool)]

        # Build ordered room type sequence
        sequence = _build_room_sequence(settings.room_count)

        # Build room objects from sequence
        rooms = self._build_rooms(settings, sequence)

        # Build main quest from quest_focus
        quest = self._build_quest(settings)

        # Pick two factions deterministically
        faction_pool = _FACTIONS[theme]
        active_factions = (
            faction_pool[0],
            faction_pool[settings.room_count % len(faction_pool)],
        )

        world = GeneratedWorld(
            world_name=world_name,
            world_description=_WORLD_DESCRIPTIONS[theme],
            atmosphere=_ATMOSPHERES[theme],
            theme=theme,
            rooms=tuple(rooms),
            main_quest=quest,
            active_factions=active_factions,
        )

        logger.debug("StubNarrator complete: world_name=%s", world_name)
        return world

    def _build_rooms(
        self, settings: WorldSettings, sequence: list[RoomType]
    ) -> list[NarratedRoom]:
        """Build NarratedRoom objects from the room type sequence."""
        theme = settings.theme
        enemy_pool = _ENEMIES[theme]
        rooms: list[NarratedRoom] = []

        for idx, room_type in enumerate(sequence):
            name_pool = _ROOM_NAMES[theme].get(room_type, ["Unknown Chamber"])
            room_name = _pick(name_pool, idx)

            # Boss room gets a dedicated description and enemy
            if room_type == RoomType.BOSS:
                description = (
                    f"The final chamber radiates power and dread. "
                    f"{_BOSS_ENEMIES[theme]} awaits, surrounded by their most "
                    f"devoted servants. There is no retreat from this room."
                )
                enemy_names: tuple[str, ...] = (_BOSS_ENEMIES[theme],)
            elif room_type in (RoomType.SHOP, RoomType.REST):
                # Non-combat rooms have no enemies
                description = self._describe_room(theme, room_type, idx)
                enemy_names = ()
            elif room_type == RoomType.EVENT:
                description = self._describe_room(theme, room_type, idx)
                enemy_names = ()
            else:
                # COMBAT rooms get 1-2 enemies from the pool
                description = self._describe_room(theme, room_type, idx)
                e1 = _pick(enemy_pool, idx)
                e2 = _pick(enemy_pool, idx + 3)
                # Avoid duplicate enemy names in the same room
                enemy_names = (e1,) if e1 == e2 else (e1, e2)

            rooms.append(
                NarratedRoom(
                    index=idx,
                    room_type=room_type,
                    name=room_name,
                    description=description,
                    enemy_names=enemy_names,
                    npc_names=(),
                    special_notes=None,
                )
            )

        return rooms

    def _describe_room(self, theme: Theme, room_type: RoomType, idx: int) -> str:
        """Produce a brief template description for a non-boss room."""
        # Simple description templates keyed by room type
        templates: dict[RoomType, str] = {
            RoomType.COMBAT: (
                f"Room {idx + 1}: A guarded corridor patrolled by hostile units loyal to the dungeon's master. "
                f"The floor is stained from past battles. Combat is unavoidable here."
            ),
            RoomType.SHOP: (
                f"Room {idx + 1}: A neutral trading post maintained by a merchant who serves neither side. "
                f"Supplies, consumables, and rare equipment are available for the right price."
            ),
            RoomType.REST: (
                f"Room {idx + 1}: A fortified safe zone shielded from the dungeon's corruption. "
                f"The party can recover here without fear of interruption."
            ),
            RoomType.EVENT: (
                f"Room {idx + 1}: A chamber where the dungeon itself seems to test the party. "
                f"A non-combat challenge — negotiation, puzzle, or a pivotal choice — awaits."
            ),
            RoomType.TREASURE: (
                f"Room {idx + 1}: A sealed cache of valuables left by a previous occupant. "
                f"Looting is possible but traps may have been set."
            ),
        }
        return templates.get(room_type, f"Room {idx + 1}: An unremarkable chamber.")

    def _build_quest(self, settings: WorldSettings) -> MainQuest:
        """Build a MainQuest from the quest_focus setting."""
        focus = settings.quest_focus
        return MainQuest(
            name=_QUEST_NAMES[focus],
            description=_QUEST_DESCRIPTIONS[focus],
            stages=_QUEST_STAGES[focus],
        )


# ---------------------------------------------------------------------------
# GeminiNarrator
# ---------------------------------------------------------------------------

# Default Gemini model. gemini-2.0-flash balances quality and speed well for
# structured generation tasks.
_DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"


class GeminiNarrator(NarratorPort):
    """
    LLM-backed narrator using the Google Gemini API.

    Sends a structured prompt (built by PromptAssembler) to Gemini and parses
    the JSON response into a GeneratedWorld domain object.

    Raises WorldGenerationError on API failure or if the response cannot be
    parsed into the expected structure. This keeps the use case clean — it only
    sees domain exceptions, never SDK exceptions.
    """

    def __init__(
        self,
        api_key: str,
        model: str = _DEFAULT_GEMINI_MODEL,
    ) -> None:
        # genai.Client is the entry point for the google-genai SDK.
        # Each narrator instance owns its client — stateless and safe to share.
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._assembler = PromptAssembler()

    def generate_world(self, settings: WorldSettings) -> GeneratedWorld:
        """
        Call Gemini with the assembled prompt and parse the JSON response.

        @param settings - Validated WorldSettings domain value object.
        @returns A fully populated GeneratedWorld from the LLM output.
        @raises WorldGenerationError if the API call fails or response is malformed.
        """
        logger.info(
            "GeminiNarrator generating world: theme=%s difficulty=%s rooms=%d model=%s",
            settings.theme,
            settings.difficulty,
            settings.room_count,
            self._model,
        )

        prompt = self._assembler.assemble_world_prompt(settings)
        logger.debug("Assembled prompt length: %d chars", len(prompt))

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                # Requesting JSON MIME type tells Gemini to return pure JSON
                # without markdown code fences. We still strip them defensively
                # in _parse_response in case the model ignores the setting.
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:
            exc_str = str(exc)
            if "429" in exc_str or "RESOURCE_EXHAUSTED" in exc_str:
                logger.error(
                    "Gemini quota exhausted — check your API key quota. "
                    "Request rejected rather than falling back to stub output."
                )
                raise WorldGenerationError(
                    "Gemini API quota exhausted. Check your key at https://ai.dev/rate-limit"
                ) from exc
            logger.error("Gemini API call failed: %s", exc)
            raise WorldGenerationError(f"Gemini API call failed: {exc}") from exc

        raw = response.text
        if not raw:
            raise WorldGenerationError("Gemini returned an empty response")

        logger.debug("Gemini raw response length: %d chars", len(raw))
        return self._parse_response(raw, settings.theme)

    def _parse_response(self, raw: str, theme: Theme) -> GeneratedWorld:
        """
        Parse the Gemini JSON string into a GeneratedWorld domain object.

        Strips markdown code fences defensively, then validates and converts
        each field. Raises WorldGenerationError for any structural mismatch.

        We trust the domain enum (theme) rather than any theme field the LLM
        might return — the LLM cannot change which theme was requested.
        """
        text = raw.strip()
        # Strip ```json ... ``` fences if the model added them despite the MIME hint
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            text = text.rsplit("```", 1)[0].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            logger.error("Gemini returned invalid JSON: %s", exc)
            raise WorldGenerationError(f"LLM returned invalid JSON: {exc}") from exc

        if not isinstance(data, dict):
            raise WorldGenerationError("LLM response was not a JSON object")

        # cast is safe here: isinstance(data, dict) guarantees dict type;
        # cast[str, object] lets us use _require_* helpers without mypy errors.
        data_dict = cast(dict[str, object], data)

        try:
            rooms_raw = self._require_list(data_dict, "rooms")
            rooms = tuple(
                self._parse_room(cast(dict[str, object], item))
                for item in rooms_raw
                if isinstance(item, dict)
            )

            quest_raw = data_dict.get("main_quest")
            if not isinstance(quest_raw, dict):
                raise WorldGenerationError("main_quest field missing or not an object")
            quest_dict = cast(dict[str, object], quest_raw)
            quest = MainQuest(
                name=self._require_str(quest_dict, "name"),
                description=self._require_str(quest_dict, "description"),
                stages=tuple(self._require_str_list(quest_dict, "stages")),
            )

            world = GeneratedWorld(
                world_name=self._require_str(data_dict, "world_name"),
                world_description=self._require_str(data_dict, "world_description"),
                atmosphere=self._require_str(data_dict, "atmosphere"),
                theme=theme,
                rooms=rooms,
                main_quest=quest,
                active_factions=tuple(
                    self._require_str_list(data_dict, "active_factions")
                ),
            )
        except WorldGenerationError:
            raise
        except Exception as exc:
            logger.error("Failed to parse Gemini response structure: %s", exc)
            raise WorldGenerationError(
                f"LLM response did not match expected structure: {exc}"
            ) from exc

        logger.info(
            "GeminiNarrator parsed world: name=%s rooms=%d",
            world.world_name,
            len(world.rooms),
        )
        return world

    def _parse_room(self, raw: dict[str, object]) -> NarratedRoom:
        """Convert a single room dict from the LLM response into a NarratedRoom."""
        # Parse room_type safely — default to COMBAT if the LLM returns a bad value
        rt_raw = raw.get("room_type", "COMBAT")
        rt_str = rt_raw if isinstance(rt_raw, str) else "COMBAT"
        try:
            room_type = RoomType(rt_str)
        except ValueError:
            logger.warning(
                "LLM returned unknown room_type %r, defaulting to COMBAT", rt_str
            )
            room_type = RoomType.COMBAT

        idx_raw = raw.get("index", 0)
        idx = idx_raw if isinstance(idx_raw, int) else 0

        notes_raw = raw.get("special_notes")
        special_notes = notes_raw if isinstance(notes_raw, str) else None

        return NarratedRoom(
            index=idx,
            room_type=room_type,
            name=self._require_str(raw, "name"),
            description=self._require_str(raw, "description"),
            enemy_names=tuple(self._require_str_list(raw, "enemy_names")),
            npc_names=tuple(self._require_str_list(raw, "npc_names")),
            special_notes=special_notes,
        )

    # --- Type-safe field extraction helpers ---
    # These mirror the _jint / _jstr helpers used in combat/infrastructure/repositories.py.

    def _require_str(self, d: dict[str, object], key: str) -> str:
        """Extract a required string field; raise WorldGenerationError if missing."""
        v = d.get(key)
        if not isinstance(v, str):
            raise WorldGenerationError(
                f"LLM response field '{key}' missing or not a string (got {type(v).__name__})"
            )
        return v

    def _require_list(self, d: dict[str, object], key: str) -> list[object]:
        """Extract a required list field; raise WorldGenerationError if missing."""
        v = d.get(key)
        if not isinstance(v, list):
            raise WorldGenerationError(
                f"LLM response field '{key}' missing or not a list (got {type(v).__name__})"
            )
        return list(v)

    def _require_str_list(self, d: dict[str, object], key: str) -> list[str]:
        """Extract a required list-of-strings field; non-string items are dropped."""
        items = self._require_list(d, key)
        result: list[str] = []
        for item in items:
            if isinstance(item, str):
                result.append(item)
            else:
                logger.warning(
                    "Non-string item in field '%s': %r — skipping", key, item
                )
        return result

"""
Narrator implementations for the dungeons bounded context.

StubDungeonNarrator  — deterministic templates keyed by CampaignTone.
                       No LLM calls. Used in dev/offline/testing.
GeminiDungeonNarrator — calls the Google Gemini API (gemini-2.0-flash)
                        with the full World + Campaign + Settings prompt.
                        Parses JSON response. Raises DungeonGenerationError
                        on API or parse failure.
"""

import json
import logging
import uuid
from datetime import datetime, timezone

from app.campaigns.domain.models import Campaign, CampaignTone
from app.dungeons.application.narrator_port import DungeonNarratorPort
from app.dungeons.domain.exceptions import DungeonGenerationError
from app.dungeons.domain.models import (
    Dungeon,
    DungeonQuest,
    DungeonRoom,
    DungeonSettings,
    RoomType,
)
from app.dungeons.infrastructure.prompts.assembler import PromptAssembler
from app.worlds.domain.models import World

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Room sequence algorithm (shared by both narrators)
# ---------------------------------------------------------------------------


def _build_room_sequence(room_count: int) -> list[RoomType]:
    """
    Produce a deterministic room type ordering.

    Rules:
      - Room 0:    always COMBAT
      - Room last: always BOSS
      - ~30% mark: SHOP
      - ~60% mark: REST
      - If room_count >= 8: one EVENT room at midpoint
      - All remaining slots: COMBAT
    """
    sequence = [RoomType.COMBAT] * room_count
    sequence[-1] = RoomType.BOSS
    sequence[max(1, int(room_count * 0.3))] = RoomType.SHOP
    sequence[max(2, int(room_count * 0.6))] = RoomType.REST
    if room_count >= 8:
        sequence[room_count // 2] = RoomType.EVENT
    return sequence


# ---------------------------------------------------------------------------
# Stub narrator
# ---------------------------------------------------------------------------

# Static templates keyed by CampaignTone for StubDungeonNarrator
_TONE_TEMPLATES: dict[CampaignTone, dict[str, object]] = {
    CampaignTone.DARK_FANTASY: {
        "dungeon_name": "The Crypt of Shattered Oaths",
        "premise": (
            "An ancient crypt beneath a fallen citadel stirs with undead energy. "
            "The party must descend to destroy the cursed relic at its heart."
        ),
        "quest_name": "Break the Undying Pact",
        "quest_description": "Destroy the Shard of Broken Oaths to collapse the lich's hold on this crypt.",
        "quest_stages": [
            "Breach the outer seal guarded by oath-sworn wights",
            "Recover the key from the crypt librarian in the EVENT chamber",
            "Destroy the Shard of Broken Oaths in the boss chamber",
        ],
        "enemies_by_type": {
            RoomType.COMBAT: ["Oath-sworn Wight", "Skeleton Archer", "Shadow"],
            RoomType.BOSS: ["The Pale Keeper (Revenant Lord)"],
            RoomType.EVENT: ["Crypt Librarian (NPC)"],
            RoomType.SHOP: ["Wandering Tomb Trader"],
            RoomType.REST: [],
            RoomType.TREASURE: ["Treasure Golem Guardian"],
        },
        "room_names_by_type": {
            RoomType.COMBAT: "Bone-Strewn Hall",
            RoomType.BOSS: "The Oath Chamber",
            RoomType.EVENT: "The Librarian's Alcove",
            RoomType.SHOP: "Tomb Trader's Alcove",
            RoomType.REST: "Collapsed Shrine",
            RoomType.TREASURE: "The Sealed Vault",
        },
    },
    CampaignTone.HIGH_FANTASY: {
        "dungeon_name": "The Sunken Elven Archive",
        "premise": (
            "A flooded library of the ancients holds a lost spell that can seal "
            "the rift. The party must navigate magical hazards and guardians."
        ),
        "quest_name": "Retrieve the Sealing Glyph",
        "quest_description": "Find the Glyph of Sealing lost in the archive's deepest vaults.",
        "quest_stages": [
            "Navigate the flooded entry halls past the water elemental guardians",
            "Decode the archive's magical lock with help from the archivist spirit",
            "Claim the Sealing Glyph from the vault's arcane custodian",
        ],
        "enemies_by_type": {
            RoomType.COMBAT: ["Water Elemental", "Animated Tome", "Crystal Golem"],
            RoomType.BOSS: ["The Arcane Custodian (Archmage)"],
            RoomType.EVENT: ["Archivist Spirit (Ghost NPC)"],
            RoomType.SHOP: ["Wandering Artificer"],
            RoomType.REST: [],
            RoomType.TREASURE: ["Arcane Chest Guardian"],
        },
        "room_names_by_type": {
            RoomType.COMBAT: "Flooded Reading Hall",
            RoomType.BOSS: "The Grand Vault",
            RoomType.EVENT: "The Spirit's Study",
            RoomType.SHOP: "Artificer's Waypoint",
            RoomType.REST: "Dry Alcove",
            RoomType.TREASURE: "The Sealed Reliquary",
        },
    },
    CampaignTone.HORROR: {
        "dungeon_name": "The Hollow Below",
        "premise": (
            "Something ancient and hungry has awakened beneath the asylum. "
            "The party must find what feeds it before it feeds on them."
        ),
        "quest_name": "Silence the Hunger",
        "quest_description": "Destroy the aberrant heart that pulses at the deepest level.",
        "quest_stages": [
            "Survive the maddened patients in the upper wards",
            "Find the doctor's journal that reveals the creature's weakness",
            "Destroy the Aberrant Heart before it fully awakens",
        ],
        "enemies_by_type": {
            RoomType.COMBAT: ["Maddened Patient", "Crawling Horror", "Flesh Tendril"],
            RoomType.BOSS: ["The Aberrant Heart (Elder Aberration)"],
            RoomType.EVENT: ["Surviving Doctor (NPC)"],
            RoomType.SHOP: ["Scavenger hiding in a locked ward"],
            RoomType.REST: [],
            RoomType.TREASURE: ["Locked Surgery Cabinet"],
        },
        "room_names_by_type": {
            RoomType.COMBAT: "Ruined Ward",
            RoomType.BOSS: "The Feeding Chamber",
            RoomType.EVENT: "The Doctor's Office",
            RoomType.SHOP: "The Locked Ward",
            RoomType.REST: "Barricaded Storeroom",
            RoomType.TREASURE: "The Surgery Cabinet",
        },
    },
    CampaignTone.POLITICAL_INTRIGUE: {
        "dungeon_name": "The Underhand Exchange",
        "premise": (
            "A blackmail ledger that could topple the ruling council is held "
            "in a thieves' guild vault. Getting it out means going in."
        ),
        "quest_name": "Recover the Ledger of Secrets",
        "quest_description": "Steal the Ledger of Secrets from the guild vault without triggering a war.",
        "quest_stages": [
            "Bypass guild sentinels in the outer exchange halls",
            "Convince or bribe the guild archivist to reveal the vault combination",
            "Defeat the guild enforcer and escape with the ledger",
        ],
        "enemies_by_type": {
            RoomType.COMBAT: ["Guild Sentinel", "Hired Assassin", "Crossbow Sniper"],
            RoomType.BOSS: ["The Guild Enforcer (Master Assassin)"],
            RoomType.EVENT: ["Guild Archivist (NPC, bribeable)"],
            RoomType.SHOP: ["Black Market Fence"],
            RoomType.REST: [],
            RoomType.TREASURE: ["The Sealed Vault"],
        },
        "room_names_by_type": {
            RoomType.COMBAT: "Exchange Hall",
            RoomType.BOSS: "The Enforcer's Den",
            RoomType.EVENT: "The Archive Room",
            RoomType.SHOP: "The Black Market Stall",
            RoomType.REST: "A Safe House Alcove",
            RoomType.TREASURE: "The Sealed Vault",
        },
    },
    CampaignTone.SWASHBUCKLING: {
        "dungeon_name": "The Corsair's Hidden Cove",
        "premise": (
            "A legendary pirate's hoard sits behind three locks in a sea cave. "
            "The corsair's ghost still guards what she died for."
        ),
        "quest_name": "Claim the Corsair's Hoard",
        "quest_description": "Retrieve the Corsair's Compass from the deepest vault before the tide rises.",
        "quest_stages": [
            "Fight through the corsair's undead crew in the outer caves",
            "Negotiate or outsmart the first mate's ghost for a key",
            "Defeat the Corsair's Ghost and claim the Compass",
        ],
        "enemies_by_type": {
            RoomType.COMBAT: [
                "Undead Corsair",
                "Sea Spawn",
                "Cursed Gunpowder Keg (trap)",
            ],
            RoomType.BOSS: ["The Corsair's Ghost (Banshee Captain)"],
            RoomType.EVENT: ["First Mate's Ghost (NPC, negotiable)"],
            RoomType.SHOP: ["Stranded Merchant Sailor"],
            RoomType.REST: [],
            RoomType.TREASURE: ["The Corsair's Chest"],
        },
        "room_names_by_type": {
            RoomType.COMBAT: "The Dripping Tunnel",
            RoomType.BOSS: "The Captain's Vault",
            RoomType.EVENT: "The First Mate's Watch Post",
            RoomType.SHOP: "The Survivor's Alcove",
            RoomType.REST: "Dry Ledge Above the Tide",
            RoomType.TREASURE: "The Hidden Chest Room",
        },
    },
}

_ROOM_DESCRIPTIONS: dict[RoomType, str] = {
    RoomType.COMBAT: "A chamber bearing the scars of past violence. Enemies lurk here.",
    RoomType.SHOP: "A surprisingly well-stocked alcove. Someone makes a living here.",
    RoomType.REST: "A defensible alcove, quiet enough for a short rest.",
    RoomType.BOSS: "The heart of the dungeon. Something powerful waits here.",
    RoomType.TREASURE: "Signs of wealth — locked chests, hidden caches, forgotten riches.",
    RoomType.EVENT: "Something unusual has happened here. Closer inspection is warranted.",
}


class StubDungeonNarrator(DungeonNarratorPort):
    """
    Deterministic dungeon narrator for dev and testing.

    Uses static templates keyed by CampaignTone. The same inputs always
    produce the same output — no LLM calls, no randomness.
    """

    def generate_dungeon(
        self,
        settings: DungeonSettings,
        world: World,
        campaign: Campaign,
    ) -> Dungeon:
        """Generate a template-based dungeon. No LLM call."""
        logger.info(
            "StubDungeonNarrator.generate_dungeon: tone=%s rooms=%d",
            campaign.tone.value,
            settings.room_count,
        )
        template = _TONE_TEMPLATES.get(
            campaign.tone, _TONE_TEMPLATES[CampaignTone.HIGH_FANTASY]
        )
        sequence = _build_room_sequence(settings.room_count)
        rooms = tuple(
            self._make_room(index, room_type, template)
            for index, room_type in enumerate(sequence)
        )
        quest = DungeonQuest(
            name=str(template["quest_name"]),
            description=str(template["quest_description"]),
            stages=tuple(
                str(s)
                for s in (
                    template["quest_stages"]
                    if isinstance(template["quest_stages"], list)
                    else []
                )
            ),
        )
        dungeon = Dungeon(
            id=uuid.uuid4(),
            campaign_id=settings.campaign_id,
            world_id=world.id,
            name=str(template["dungeon_name"]),
            premise=str(template["premise"]),
            rooms=rooms,
            quest=quest,
            created_at=datetime.now(tz=timezone.utc),
        )
        logger.info("StubDungeonNarrator: generated dungeon '%s'", dungeon.name)
        return dungeon

    @staticmethod
    def _make_room(
        index: int,
        room_type: RoomType,
        template: dict[str, object],
    ) -> DungeonRoom:
        """Build a single DungeonRoom from the template."""
        enemies_map = template.get("enemies_by_type", {})
        names_map = template.get("room_names_by_type", {})

        enemy_list: list[str] = []
        if isinstance(enemies_map, dict):
            raw = enemies_map.get(room_type, [])
            if isinstance(raw, list):
                enemy_list = [str(e) for e in raw]

        npc_list: list[str] = []
        room_name = ""
        if isinstance(names_map, dict):
            raw_name = names_map.get(room_type, "Room")
            room_name = str(raw_name)

        # NPCs appear only in EVENT and SHOP rooms
        if room_type in (RoomType.EVENT, RoomType.SHOP) and enemy_list:
            npc_list = enemy_list
            enemy_list = []

        return DungeonRoom(
            index=index,
            room_type=room_type,
            name=(
                f"{room_name} {index + 1}" if room_type != RoomType.BOSS else room_name
            ),
            description=_ROOM_DESCRIPTIONS.get(room_type, "A dungeon room."),
            enemy_names=tuple(enemy_list),
            npc_names=tuple(npc_list),
        )


# ---------------------------------------------------------------------------
# Gemini narrator
# ---------------------------------------------------------------------------


class GeminiDungeonNarrator(DungeonNarratorPort):
    """
    LLM-powered dungeon narrator using Google Gemini (gemini-2.0-flash).

    Builds a structured prompt via PromptAssembler, calls the Gemini API
    via the google-genai package, and parses the JSON response into a
    Dungeon aggregate. Raises DungeonGenerationError on API failure or
    malformed JSON.

    The google.genai package uses a Client-based API:
      client = genai.Client(api_key=...)
      response = client.models.generate_content(model=..., contents=...)
    """

    # Model identifier — pinned so behaviour is deterministic.
    _MODEL = "gemini-2.0-flash"

    def __init__(self, api_key: str) -> None:
        # google.genai is imported at call-time so the module loads without
        # the package installed — StubDungeonNarrator stays usable offline.
        import google.genai as genai  # noqa: PLC0415

        self._api_key: str = api_key
        self._assembler = PromptAssembler()
        # Eagerly construct the client to fail fast on missing or invalid keys.
        # The type is not resolvable at class scope without a top-level import,
        # so we store it untyped and re-create a typed client inside each call.
        self._client = genai.Client(api_key=api_key)

    def generate_dungeon(
        self,
        settings: DungeonSettings,
        world: World,
        campaign: Campaign,
    ) -> Dungeon:
        """Generate a dungeon via the Gemini API."""
        logger.info(
            "GeminiDungeonNarrator.generate_dungeon: world=%s tone=%s rooms=%d",
            world.name,
            campaign.tone.value,
            settings.room_count,
        )
        prompt = self._assembler.build(settings, world, campaign)

        try:
            # Re-import locally so the type is known to mypy in this scope.
            import google.genai as genai  # noqa: PLC0415

            client = genai.Client(api_key=self._api_key)
            response = client.models.generate_content(
                model=self._MODEL,
                contents=prompt,
            )
            # GenerateContentResponse.text is a convenience property that
            # returns the first candidate's text part, or None if absent.
            text_or_none: str | None = response.text
            if text_or_none is None:
                raise DungeonGenerationError(
                    "Gemini API returned an empty response (no text content)"
                )
            raw_text: str = text_or_none
        except DungeonGenerationError:
            raise
        except Exception as exc:
            logger.error("GeminiDungeonNarrator: API call failed: %s", exc)
            raise DungeonGenerationError(f"Gemini API call failed: {exc}") from exc

        logger.debug(
            "GeminiDungeonNarrator: received %d chars of raw response",
            len(raw_text),
        )

        # Gemini often wraps JSON in markdown code fences (```json ... ```).
        # Strip them before attempting to parse.
        clean_text = raw_text.strip()
        if clean_text.startswith("```"):
            # Remove the opening fence line (e.g. "```json\n") and closing "```"
            clean_text = clean_text.split("\n", 1)[-1]
            if clean_text.endswith("```"):
                clean_text = clean_text[: clean_text.rfind("```")]
            clean_text = clean_text.strip()

        try:
            data = json.loads(clean_text)
        except json.JSONDecodeError as exc:
            logger.error(
                "GeminiDungeonNarrator: failed to parse JSON response: %s\nRaw: %s",
                exc,
                raw_text[:500],
            )
            raise DungeonGenerationError(
                f"Failed to parse Gemini response as JSON: {exc}"
            ) from exc

        return self._parse_dungeon(data, settings, world.id)

    @staticmethod
    def _parse_dungeon(
        data: object,
        settings: DungeonSettings,
        world_id: uuid.UUID,
    ) -> Dungeon:
        """
        Parse the LLM JSON response into a Dungeon aggregate.

        Raises DungeonGenerationError if required fields are missing.
        """
        if not isinstance(data, dict):
            raise DungeonGenerationError("Gemini response is not a JSON object")

        d: dict[str, object] = data

        name = d.get("dungeon_name")
        premise = d.get("premise")
        if not isinstance(name, str) or not isinstance(premise, str):
            raise DungeonGenerationError(
                "Gemini response missing dungeon_name or premise"
            )

        quest_raw = d.get("quest")
        if not isinstance(quest_raw, dict):
            raise DungeonGenerationError("Gemini response missing quest object")
        qd: dict[str, object] = quest_raw

        quest_name = qd.get("name", "")
        quest_desc = qd.get("description", "")
        stages_raw = qd.get("stages", [])
        if not isinstance(quest_name, str) or not isinstance(quest_desc, str):
            raise DungeonGenerationError("Gemini quest missing name or description")
        stages_list = stages_raw if isinstance(stages_raw, list) else []
        stages = tuple(str(s) for s in stages_list if isinstance(s, str))

        quest = DungeonQuest(
            name=quest_name,
            description=quest_desc,
            stages=stages,
        )

        rooms_raw = d.get("rooms", [])
        if not isinstance(rooms_raw, list):
            raise DungeonGenerationError("Gemini response rooms field is not a list")

        rooms: list[DungeonRoom] = []
        for item in rooms_raw:
            if not isinstance(item, dict):
                continue
            rd: dict[str, object] = item

            index_val = rd.get("index", len(rooms))
            room_type_val = rd.get("room_type", "COMBAT")
            special_val = rd.get("special_notes")

            try:
                room_type = RoomType(str(room_type_val))
            except ValueError:
                room_type = RoomType.COMBAT

            enemy_names_raw = rd.get("enemy_names", [])
            npc_names_raw = rd.get("npc_names", [])
            enemy_list_raw = (
                enemy_names_raw if isinstance(enemy_names_raw, list) else []
            )
            npc_list_raw = npc_names_raw if isinstance(npc_names_raw, list) else []

            rooms.append(
                DungeonRoom(
                    index=int(index_val) if isinstance(index_val, int) else len(rooms),
                    room_type=room_type,
                    name=str(rd.get("name", "Unknown Room")),
                    description=str(rd.get("description", "")),
                    enemy_names=tuple(
                        str(e) for e in enemy_list_raw if isinstance(e, str)
                    ),
                    npc_names=tuple(str(n) for n in npc_list_raw if isinstance(n, str)),
                    special_notes=special_val if isinstance(special_val, str) else None,
                )
            )

        if not rooms:
            raise DungeonGenerationError("Gemini response contains no rooms")

        return Dungeon(
            id=uuid.uuid4(),
            campaign_id=settings.campaign_id,
            world_id=world_id,
            name=name,
            premise=premise,
            rooms=tuple(rooms),
            quest=quest,
            created_at=datetime.now(tz=timezone.utc),
        )

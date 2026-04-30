"""
PromptAssembler — builds the LLM prompt for dungeon generation.

Combines World lore, Campaign requirements, and DungeonSettings into a
single structured prompt string. Keeps the prompt logic separate from the
narrator so it can be tested independently.
"""

import logging

from app.campaigns.domain.models import Campaign
from app.dungeons.domain.models import DungeonSettings, ROOM_COUNT_MIN, ROOM_COUNT_MAX
from app.worlds.domain.models import World

logger = logging.getLogger(__name__)

# The expected JSON schema embedded in the prompt so the LLM knows exactly
# what structure to return. Strict schema reduces parse errors.
_JSON_SCHEMA = """
{
  "dungeon_name": "<string>",
  "premise": "<string — 2-3 sentence spoiler-free pitch of this session>",
  "quest": {
    "name": "<string>",
    "description": "<string>",
    "stages": ["<stage 1>", "<stage 2>", "<stage 3>"]
  },
  "rooms": [
    {
      "index": 0,
      "room_type": "<COMBAT|SHOP|REST|BOSS|TREASURE|EVENT>",
      "name": "<string>",
      "description": "<string — 2-3 sentences describing the room>",
      "enemy_names": ["<name>"],
      "npc_names": [],
      "mechanics": [
        {
          "trigger": {
            "trigger_action": "<string — player action that activates this mechanic, e.g. investigate, attack, enter>",
            "check_stat": "<string or null — e.g. Investigation, Perception, Athletics>",
            "dc": "<integer 1-30 or null>"
          },
          "effects": [
            {
              "effect_type": "<DAMAGE|HEAL|APPLY_STATUS|GRANT_LOOT|SPAWN_ENEMY|UNLOCK_PATH|NONE>",
              "value": "<integer or null — damage/heal amount>",
              "status": "<string or null — status name for APPLY_STATUS>",
              "item_id": "<string or null — item identifier for GRANT_LOOT>"
            }
          ],
          "description": "<string — human-readable description of this mechanic>"
        }
      ],
      "loot": [
        {
          "item_id": "<string — snake_case identifier>",
          "name": "<string — display name>",
          "quantity": "<integer >= 1>"
        }
      ]
    }
  ]
}
"""

# One-shot example showing how to translate a room narrative into the
# required structured format. Placed before the schema to prime the LLM.
_ONE_SHOT_EXAMPLE = """The following example shows how to translate a room narrative into the required structured format.

NARRATIVE: "A pressure plate trap hides near the entrance. A successful DC 15 Investigation
check reveals it. On failure, poison needles fire from the walls dealing 1d6 damage."

STRUCTURED OUTPUT for that room:
{
  "index": 0,
  "room_type": "COMBAT",
  "name": "The Needle Hall",
  "description": "A long corridor scarred by old battles. The floor is suspiciously clean near the entrance.",
  "enemy_names": ["Skeleton Archer"],
  "npc_names": [],
  "mechanics": [
    {
      "trigger": {
        "trigger_action": "investigate",
        "check_stat": "Investigation",
        "dc": 15
      },
      "effects": [
        {
          "effect_type": "DAMAGE",
          "value": 6,
          "status": null,
          "item_id": null
        }
      ],
      "description": "Pressure plate trap near the entrance. DC 15 Investigation to spot. Failure triggers poison needles for 1d6 damage."
    }
  ],
  "loot": []
}
"""


class PromptAssembler:
    """
    Composes a structured dungeon generation prompt from World + Campaign + Settings.

    The prompt is split into sections:
      1. World context (lore, factions, bosses) — gives the LLM narrative anchor
      2. Campaign context (tone, themes, level range, content restrictions)
      3. Session parameters (room count, party size, difficulty, DM notes)
      4. Room sequence instructions (first=COMBAT, last=BOSS, etc.)
      5. One-shot example — shows the expected structured mechanics format
      6. JSON output schema
    """

    def build(
        self,
        settings: DungeonSettings,
        world: World,
        campaign: Campaign,
    ) -> str:
        """
        Build and return the full prompt string.

        @param settings  - Per-session parameters from the DM.
        @param world     - Admin-seeded world with lore and factions.
        @param campaign  - DM campaign with tone and content requirements.
        @returns A single prompt string ready to send to an LLM.
        """
        lines_block = self._format_lines(campaign)
        factions_block = self._format_factions(world)
        bosses_block = self._format_bosses(world)
        dm_notes_block = (
            f"\nDM's additional notes for this session:\n{settings.dm_notes}\n"
            if settings.dm_notes
            else ""
        )
        difficulty = settings.difficulty_override or "match campaign level range"

        prompt = f"""You are a Dungeon Master assistant generating a D&D 5e dungeon session.
Return ONLY valid JSON — no markdown, no explanation, no code fences.

=== WORLD CONTEXT ===
World: {world.name}
Theme: {world.theme.value}
Lore: {world.lore_summary}

Factions present in this world:
{factions_block}

Notable bosses in this world:
{bosses_block}

=== CAMPAIGN CONTEXT ===
Tone: {campaign.tone.value}
Themes: {", ".join(campaign.themes) if campaign.themes else "none specified"}
Party level range: {campaign.level_range.start}–{campaign.level_range.end}
Content restrictions (NEVER generate these):
{lines_block}

=== SESSION PARAMETERS ===
Number of rooms: {settings.room_count}
Party size: {settings.party_size} players
Difficulty: {difficulty}
{dm_notes_block}
=== ROOM SEQUENCE RULES ===
- Room at index 0 MUST be room_type COMBAT
- Last room (index {settings.room_count - 1}) MUST be room_type BOSS
- Include exactly one SHOP room and one REST room in the middle sections
- All other rooms should be COMBAT, TREASURE, or EVENT
- The BOSS room should feature one of the world's notable bosses or a lieutenant

=== ROOM MECHANICS RULES ===
- COMBAT, EVENT, BOSS rooms: mechanics must have at least one entry
- TREASURE rooms: mechanics may be empty, loot must have at least one entry
- REST rooms: mechanics may have one entry with effect_type HEAL or NONE; loot must be empty
- SHOP rooms: mechanics and loot must both be empty arrays

=== ONE-SHOT EXAMPLE ===
{_ONE_SHOT_EXAMPLE}

=== OUTPUT FORMAT ===
Return exactly {settings.room_count} rooms.
Use only these room_type values: COMBAT, SHOP, REST, BOSS, TREASURE, EVENT
The JSON must match this schema exactly:
{_JSON_SCHEMA}
"""
        logger.debug(
            "PromptAssembler.build: world=%s tone=%s rooms=%d",
            world.name,
            campaign.tone.value,
            settings.room_count,
        )
        return prompt

    @staticmethod
    def _format_lines(campaign: Campaign) -> str:
        """Format the campaign's content restrictions (Lines) for the prompt."""
        if not campaign.content_boundaries.lines:
            return "  (none)"
        return "\n".join(f"  - {line}" for line in campaign.content_boundaries.lines)

    @staticmethod
    def _format_factions(world: World) -> str:
        """Format world factions for the prompt (public info only)."""
        if not world.factions:
            return "  (none)"
        parts = []
        for f in world.factions:
            parts.append(f"  - {f.name} ({f.alignment}): {f.description}")
        return "\n".join(parts)

    @staticmethod
    def _format_bosses(world: World) -> str:
        """Format world bosses for the prompt."""
        if not world.bosses:
            return "  (none)"
        parts = []
        for b in world.bosses:
            parts.append(f"  - {b.name} ({b.challenge_rating}): {b.lore[:200]}")
        return "\n".join(parts)

"""
PromptAssembler — composes the static rules context and the per-run block
into a single prompt string ready to send to an LLM.

Separation of concerns:
  - dnd_rules_context.get_dnd_rules_block()  → static, cacheable at LLM layer
  - world_generation.get_world_run_block()   → dynamic, changes per request
  - PromptAssembler.assemble_world_prompt()  → joins them with the output contract

To add a new static rule category, edit dnd_rules_context.py.
To change the per-run fields sent to the LLM, edit world_generation.py.
To change the output JSON contract, edit assemble_world_prompt() below.
"""

import logging

from app.worlds.domain.models import WorldSettings
from app.worlds.infrastructure.prompts.dnd_rules_context import get_dnd_rules_block
from app.worlds.infrastructure.prompts.world_generation import get_world_run_block

logger = logging.getLogger(__name__)

# JSON output contract sent to the LLM. Kept as a module-level constant so it
# is easy to locate and update without scrolling through method bodies.
_OUTPUT_CONTRACT = """\
OUTPUT FORMAT (JSON — return only this, no markdown fences):
{
  "world_name": "string",
  "world_description": "string (2-3 sentences)",
  "atmosphere": "string (1 sentence)",
  "active_factions": ["string", ...],
  "main_quest": {
    "name": "string",
    "description": "string",
    "stages": ["string", "string", "string"]
  },
  "rooms": [
    {
      "index": 0,
      "room_type": "COMBAT|SHOP|REST|BOSS|TREASURE|EVENT",
      "name": "string",
      "description": "string (2-3 sentences)",
      "enemy_names": ["string (include implied CR in parentheses)", ...],
      "npc_names": ["string", ...],
      "special_notes": "string or null"
    }
  ]
}"""

# Narrative style directives that apply to all themes. These stay here rather
# than in dnd_rules_context.py because they govern output style, not D&D rules.
_NARRATIVE_DIRECTIVES = """\
NARRATIVE DIRECTIVES:
- Match the vocabulary, tone, and aesthetic of the theme strictly.
- Each room description must be 2-3 sentences. No filler phrases.
- Banned words: epic, legendary, mysterious, adventure (overused — avoid).
- Enemy names must fit the theme. No anachronistic names.
- The last room MUST be a BOSS room.
- If DM NOTES are present, every named faction, item, location, and character
  mentioned there MUST appear somewhere in the output."""


class PromptAssembler:
    """
    Composes the D&D rules context, narrative directives, per-run request
    block, and JSON output contract into a single prompt string.

    The assembled prompt has a clear structure:
      1. Role and task declaration
      2. D&D 5e rules (static — suitable for LLM context caching)
      3. Narrative style directives (static)
      4. Per-run generation request (dynamic — changes every call)
      5. Output format contract (static)

    To swap in context caching: send sections 2–3 as a cached system message
    and sections 4–5 as the user turn. No code changes required beyond the
    narrator's API call setup.
    """

    def assemble_world_prompt(self, settings: WorldSettings) -> str:
        """
        Assemble a full world generation prompt from the given settings.

        @param settings - Validated WorldSettings value object.
        @returns A complete prompt string ready to send to an LLM.
        """
        dnd_rules = get_dnd_rules_block(settings.difficulty)
        run_block = get_world_run_block(settings)

        prompt = "\n\n".join(
            [
                "You are a world generation engine for a tabletop RPG video game.\n"
                "Generate a complete dungeon world following the D&D 5e design rules\n"
                "and the generation request below.",
                dnd_rules,
                _NARRATIVE_DIRECTIVES,
                run_block,
                _OUTPUT_CONTRACT,
            ]
        )

        logger.debug(
            "PromptAssembler assembled prompt: difficulty=%s length=%d chars",
            settings.difficulty,
            len(prompt),
        )
        return prompt

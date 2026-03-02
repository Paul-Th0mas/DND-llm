"""
Narrator infrastructure implementations.

NullNarrator — placeholder that always returns None so use cases fall back
to the lore_seed text.  Replace with a real LLM client later by implementing
NarratorPort and wiring it via dependency injection.  No use case code needs
to change when the real narrator is added.
"""

import logging

from app.worlds.application.use_cases import NarratorPort

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt template
#
# Defined here so the real narrator can import it directly.  Use cases import
# this constant when building the prompt string.
# ---------------------------------------------------------------------------

ROOM_NARRATIVE_PROMPT = """\
System: You are a {tone_descriptor} narrator for a tabletop RPG.
  Speak in {language_style} style.
  Currency = "{currency_name}". Health = "{health_term}".
  NEVER use these words: {banned_words_csv}

Context:
  Room {room_number} of {room_count}. Quest stage: "{quest_stage_title}".
  Active world flags: {flags}

Scene: {lore_seed}
  Enemies present: {enemy_names}
  NPC present: {npc_name} — "{npc_speech_style}"
  Game state: Player HP={hp}/{max_hp}, Gold={gold}

Output valid JSON only:
{{"description": "2-3 sentences", "ambient_detail": "1 sentence", "threat_level": "low|medium|high"}}
"""


# ---------------------------------------------------------------------------
# NullNarrator (Phase 1 placeholder)
# ---------------------------------------------------------------------------


class NullNarrator(NarratorPort):
    """
    Placeholder narrator that always returns None.

    NarrateRoomUseCase treats a None return as a signal to fall back to the
    room's lore_seed text.  This keeps the system functional without an LLM.

    To add real narration: implement NarratorPort in a new class, call the LLM
    API inside narrate_room(), and swap the dependency in api/dependencies.py.
    """

    def narrate_room(self, prompt: str) -> str | None:
        logger.debug("NullNarrator.narrate_room called (returning None)")
        return None

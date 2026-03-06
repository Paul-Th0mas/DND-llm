"""
Per-run dynamic prompt block for world generation.

This module contains one public function: get_world_run_block(settings).

The returned string contains only the fields that change between requests:
theme, difficulty, room count, quest focus, party size, and optional DM notes.
It is intentionally free of static rules — those live in dnd_rules_context.py.

Keeping variable data here means the static rules block can be cached at the
LLM layer without mixing cacheable and non-cacheable content.
"""

from app.worlds.domain.models import WorldSettings


def get_world_run_block(settings: WorldSettings) -> str:
    """
    Return the per-run configuration block for a world generation request.

    Contains only the fields that vary between requests. Narrative directives
    and D&D rules are not included here — they belong in dnd_rules_context.py.

    @param settings - Validated WorldSettings value object from the domain.
    @returns A multi-line string describing this specific generation request.
    """
    notes_section = (
        f"\nDM NOTES (mandatory — highest priority):\n"
        f"These instructions override all defaults. Incorporate every named\n"
        f"faction, item, location, and character into the world output:\n"
        f"{settings.dm_notes}"
        if settings.dm_notes
        else ""
    )

    return f"""GENERATION REQUEST:
THEME: {settings.theme.value}
DIFFICULTY: {settings.difficulty.value}
ROOM COUNT: {settings.room_count}
QUEST FOCUS: {settings.quest_focus.value}
PARTY SIZE: {settings.party_size}{notes_section}"""

"""
Prompt building for the worlds bounded context.

Three modules, each with a single responsibility:

  dnd_rules_context  — Static D&D 5e rules block. Content never changes between
                       requests and is a candidate for LLM context caching.

  world_generation   — Per-run dynamic block. Contains only the fields that vary
                       per request: theme, difficulty, room count, quest focus,
                       party size, and optional DM notes.

  assembler          — PromptAssembler composes the two blocks into a single
                       prompt string ready to send to an LLM.
"""

from app.worlds.infrastructure.prompts.assembler import PromptAssembler

__all__ = ["PromptAssembler"]

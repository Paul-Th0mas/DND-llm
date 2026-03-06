"""
FastAPI dependency providers for the worlds bounded context.

get_narrator               — returns the active NarratorPort implementation.
get_generate_world_use_case — wires the narrator into the use case.

Narrator selection:
  - GEMINI_API_KEY must be set in the environment — GeminiNarrator is always used.
  - StubNarrator is disabled. If the key is missing the app will raise on startup.

To re-enable StubNarrator for offline testing, restore the fallback branch here.
To add another LLM provider: implement NarratorPort, then swap the return below.
"""

import logging

from fastapi import Depends

from app.core.config import settings
from app.worlds.application.narrator_port import NarratorPort
from app.worlds.application.use_cases import GenerateWorldUseCase
from app.worlds.infrastructure.narrator import GeminiNarrator

logger = logging.getLogger(__name__)


def get_narrator() -> NarratorPort:
    """
    Provide the active world narrator implementation.

    Always returns GeminiNarrator. GEMINI_API_KEY must be present in the
    environment — pydantic-settings will raise a validation error on startup
    if the key is missing, so this function can assume it is set.
    """
    logger.info("Using GeminiNarrator for world generation")
    return GeminiNarrator(api_key=settings.GEMINI_API_KEY)


def get_generate_world_use_case(
    narrator: NarratorPort = Depends(get_narrator),
) -> GenerateWorldUseCase:
    """Provide a GenerateWorldUseCase wired with the current narrator."""
    return GenerateWorldUseCase(narrator=narrator)

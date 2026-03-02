"""
FastAPI dependency providers for the worlds bounded context.

All repositories, use cases, and services are wired here and injected
via Depends() into the router endpoints.
"""

import logging

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.worlds.application.use_cases import NarratorPort
from app.worlds.domain.repositories import (
    PresetRepository,
    ThemeRepository,
    WorldSkeletonRepository,
)
from app.worlds.domain.services import WorldCompiler
from app.worlds.infrastructure.narrator import NullNarrator
from app.worlds.infrastructure.repositories import (
    SqlAlchemyPresetRepository,
    SqlAlchemyThemeRepository,
    SqlAlchemyWorldSkeletonRepository,
)

logger = logging.getLogger(__name__)


def get_theme_repository(db: Session = Depends(get_db)) -> ThemeRepository:
    """Provide a session-scoped theme repository."""
    return SqlAlchemyThemeRepository(session=db)


def get_preset_repository(db: Session = Depends(get_db)) -> PresetRepository:
    """Provide a session-scoped preset repository."""
    return SqlAlchemyPresetRepository(session=db)


def get_world_skeleton_repository(
    db: Session = Depends(get_db),
    preset_repo: PresetRepository = Depends(get_preset_repository),
    theme_repo: ThemeRepository = Depends(get_theme_repository),
) -> WorldSkeletonRepository:
    """Provide a session-scoped world skeleton repository."""
    return SqlAlchemyWorldSkeletonRepository(
        session=db, preset_repo=preset_repo, theme_repo=theme_repo
    )


def get_world_compiler() -> WorldCompiler:
    """Provide the WorldCompiler domain service (stateless — same instance is fine)."""
    return WorldCompiler()


def get_narrator() -> NarratorPort:
    """
    Provide the narrator implementation.
    Currently NullNarrator (no LLM).  Swap to a real LLM client here later.
    """
    return NullNarrator()

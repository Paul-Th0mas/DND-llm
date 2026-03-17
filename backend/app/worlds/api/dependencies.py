"""
FastAPI dependency providers for the worlds bounded context.

Wires the SQLAlchemy repository into the use cases via Depends().
The router never instantiates repositories or use cases directly.
"""

import logging

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.worlds.application.use_cases import GetWorldByIdUseCase, GetWorldsUseCase
from app.worlds.infrastructure.repositories import SQLAlchemyWorldRepository

logger = logging.getLogger(__name__)


def get_world_repository(
    session: Session = Depends(get_db),
) -> SQLAlchemyWorldRepository:
    """Provide a SQLAlchemyWorldRepository bound to the current request session."""
    return SQLAlchemyWorldRepository(session)


def get_worlds_use_case(
    repo: SQLAlchemyWorldRepository = Depends(get_world_repository),
) -> GetWorldsUseCase:
    """Provide a GetWorldsUseCase wired with the current repository."""
    return GetWorldsUseCase(repo=repo)


def get_world_by_id_use_case(
    repo: SQLAlchemyWorldRepository = Depends(get_world_repository),
) -> GetWorldByIdUseCase:
    """Provide a GetWorldByIdUseCase wired with the current repository."""
    return GetWorldByIdUseCase(repo=repo)

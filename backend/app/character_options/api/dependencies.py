"""
FastAPI dependency injection for the character_options bounded context.

All repository and use-case bindings are wired here so routers stay thin.
"""

import logging

from fastapi import Depends
from sqlalchemy.orm import Session

from app.character_options.application.use_cases import (
    GetClassUseCase,
    GetSpeciesUseCase,
    ListClassesUseCase,
    ListSpeciesUseCase,
)
from app.character_options.infrastructure.repositories import (
    SqlAlchemyCharacterClassRepository,
    SqlAlchemyCharacterSpeciesRepository,
)
from app.db.session import get_db

logger = logging.getLogger(__name__)


def get_class_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyCharacterClassRepository:
    return SqlAlchemyCharacterClassRepository(session=db)


def get_species_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyCharacterSpeciesRepository:
    return SqlAlchemyCharacterSpeciesRepository(session=db)


def get_list_classes_use_case(
    repo: SqlAlchemyCharacterClassRepository = Depends(get_class_repository),
) -> ListClassesUseCase:
    return ListClassesUseCase(repo=repo)


def get_class_use_case(
    repo: SqlAlchemyCharacterClassRepository = Depends(get_class_repository),
) -> GetClassUseCase:
    return GetClassUseCase(repo=repo)


def get_list_species_use_case(
    repo: SqlAlchemyCharacterSpeciesRepository = Depends(get_species_repository),
) -> ListSpeciesUseCase:
    return ListSpeciesUseCase(repo=repo)


def get_species_use_case(
    repo: SqlAlchemyCharacterSpeciesRepository = Depends(get_species_repository),
) -> GetSpeciesUseCase:
    return GetSpeciesUseCase(repo=repo)

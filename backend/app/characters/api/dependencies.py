"""
FastAPI dependency injection for the characters bounded context.

All repository and use-case bindings are wired here so routers stay thin.
"""

import logging

from fastapi import Depends
from sqlalchemy.orm import Session

from app.character_options.infrastructure.repositories import (
    SqlAlchemyCharacterClassRepository,
    SqlAlchemyCharacterSpeciesRepository,
)
from app.characters.application.use_cases import (
    CreateCharacterUseCase,
    GetCampaignRosterUseCase,
    GetCharacterUseCase,
    LinkCharacterUseCase,
    ListMyCharactersUseCase,
    UnlinkCharacterUseCase,
)
from app.characters.infrastructure.repositories import SqlAlchemyCharacterRepository
from app.campaigns.infrastructure.repositories import SqlAlchemyCampaignRepository
from app.db.session import get_db
from app.users.infrastructure.repositories import SqlAlchemyUserRepository
from app.worlds.infrastructure.repositories import SQLAlchemyWorldRepository

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Repository dependencies
# ---------------------------------------------------------------------------


def get_character_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyCharacterRepository:
    return SqlAlchemyCharacterRepository(session=db)


def get_class_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyCharacterClassRepository:
    return SqlAlchemyCharacterClassRepository(session=db)


def get_species_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyCharacterSpeciesRepository:
    return SqlAlchemyCharacterSpeciesRepository(session=db)


def get_campaign_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyCampaignRepository:
    return SqlAlchemyCampaignRepository(session=db)


def get_user_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session=db)


def get_world_repository(
    db: Session = Depends(get_db),
) -> SQLAlchemyWorldRepository:
    return SQLAlchemyWorldRepository(session=db)


# ---------------------------------------------------------------------------
# Use-case dependencies
# ---------------------------------------------------------------------------


def get_create_character_use_case(
    character_repo: SqlAlchemyCharacterRepository = Depends(get_character_repository),
    class_repo: SqlAlchemyCharacterClassRepository = Depends(get_class_repository),
    species_repo: SqlAlchemyCharacterSpeciesRepository = Depends(
        get_species_repository
    ),
) -> CreateCharacterUseCase:
    return CreateCharacterUseCase(
        character_repo=character_repo,
        class_repo=class_repo,
        species_repo=species_repo,
    )


def get_character_use_case(
    character_repo: SqlAlchemyCharacterRepository = Depends(get_character_repository),
    class_repo: SqlAlchemyCharacterClassRepository = Depends(get_class_repository),
    species_repo: SqlAlchemyCharacterSpeciesRepository = Depends(
        get_species_repository
    ),
) -> GetCharacterUseCase:
    return GetCharacterUseCase(
        character_repo=character_repo,
        class_repo=class_repo,
        species_repo=species_repo,
    )


def get_list_my_characters_use_case(
    character_repo: SqlAlchemyCharacterRepository = Depends(get_character_repository),
    class_repo: SqlAlchemyCharacterClassRepository = Depends(get_class_repository),
    species_repo: SqlAlchemyCharacterSpeciesRepository = Depends(
        get_species_repository
    ),
    world_repo: SQLAlchemyWorldRepository = Depends(get_world_repository),
) -> ListMyCharactersUseCase:
    return ListMyCharactersUseCase(
        character_repo=character_repo,
        class_repo=class_repo,
        species_repo=species_repo,
        world_repo=world_repo,
    )


def get_link_character_use_case(
    character_repo: SqlAlchemyCharacterRepository = Depends(get_character_repository),
    campaign_repo: SqlAlchemyCampaignRepository = Depends(get_campaign_repository),
    class_repo: SqlAlchemyCharacterClassRepository = Depends(get_class_repository),
    species_repo: SqlAlchemyCharacterSpeciesRepository = Depends(
        get_species_repository
    ),
) -> LinkCharacterUseCase:
    return LinkCharacterUseCase(
        character_repo=character_repo,
        campaign_repo=campaign_repo,
        class_repo=class_repo,
        species_repo=species_repo,
    )


def get_unlink_character_use_case(
    character_repo: SqlAlchemyCharacterRepository = Depends(get_character_repository),
) -> UnlinkCharacterUseCase:
    return UnlinkCharacterUseCase(character_repo=character_repo)


def get_campaign_roster_use_case(
    character_repo: SqlAlchemyCharacterRepository = Depends(get_character_repository),
    campaign_repo: SqlAlchemyCampaignRepository = Depends(get_campaign_repository),
    class_repo: SqlAlchemyCharacterClassRepository = Depends(get_class_repository),
    species_repo: SqlAlchemyCharacterSpeciesRepository = Depends(
        get_species_repository
    ),
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repository),
) -> GetCampaignRosterUseCase:
    return GetCampaignRosterUseCase(
        character_repo=character_repo,
        campaign_repo=campaign_repo,
        class_repo=class_repo,
        species_repo=species_repo,
        user_repo=user_repo,
    )

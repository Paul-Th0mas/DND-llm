import logging

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.rooms.infrastructure.repositories import (
    SqlAlchemyRoomPlayerRepository,
    SqlAlchemyRoomRepository,
)
from app.users.api.dependencies import get_current_user
from app.users.domain.models import User
from app.rooms.domain.repositories import NotDMError

logger = logging.getLogger(__name__)


def get_room_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyRoomRepository:
    return SqlAlchemyRoomRepository(session=db)


def get_room_player_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyRoomPlayerRepository:
    return SqlAlchemyRoomPlayerRepository(session=db)


def get_dm_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that enforces the requesting user has the 'dm' role.
    Raises NotDMError (→ HTTP 400) if they are not a DM.
    """
    if current_user.role.value != "dm":
        logger.warning(
            "get_dm_user: user id=%s tried a DM-only action with role=%s",
            current_user.id,
            current_user.role.value,
        )
        raise NotDMError("This action is restricted to Dungeon Masters")
    return current_user

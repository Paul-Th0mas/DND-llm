"""
Rooms API router — thin layer that delegates to application use cases.
No business logic lives here.
"""

import logging
import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.rooms.api.dependencies import (
    get_dm_user,
    get_room_player_repository,
    get_room_repository,
)
from app.rooms.application.schemas import (
    CreateRoomRequest,
    CreateRoomResponse,
    JoinRoomResponse,
    RoomResponse,
)
from app.rooms.application.use_cases import CreateRoom, DeleteRoom, GetRoom, JoinRoom
from app.rooms.infrastructure.repositories import (
    SqlAlchemyRoomPlayerRepository,
    SqlAlchemyRoomRepository,
)
from app.users.api.dependencies import get_current_user
from app.users.domain.models import User
from app.users.infrastructure.auth import create_room_token

logger = logging.getLogger(__name__)

rooms_router = APIRouter(prefix="/rooms", tags=["rooms"])


def _room_response(room_domain: object, player_ids: list[uuid.UUID]) -> RoomResponse:
    """
    Helper that builds a RoomResponse DTO from a Room aggregate.
    Keeping this here (not in the use case) follows the rule that mapping to
    API schemas is the API layer's responsibility.
    """
    from app.rooms.domain.models import Room as RoomDomain  # local import avoids cycle

    assert isinstance(room_domain, RoomDomain)
    return RoomResponse(
        id=room_domain.id,
        name=room_domain.name,
        dm_id=room_domain.dm_id,
        invite_code=room_domain.invite_code.value,
        max_players=room_domain.max_players,
        is_active=room_domain.is_active,
        created_at=room_domain.created_at,
        player_ids=player_ids,
    )


@rooms_router.post(
    "/create",
    response_model=CreateRoomResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_room(
    body: CreateRoomRequest,
    db: Session = Depends(get_db),
    dm: User = Depends(get_dm_user),
    room_repo: SqlAlchemyRoomRepository = Depends(get_room_repository),
    player_repo: SqlAlchemyRoomPlayerRepository = Depends(get_room_player_repository),
) -> CreateRoomResponse:
    """
    DM creates a new campaign room.
    Returns the room details plus a room-scoped JWT for the DM to use with WebSocket.
    Requires the caller's JWT to have role='dm'.
    """
    logger.info("create_room: dm_id=%s name='%s'", dm.id, body.name)
    use_case = CreateRoom(room_repo=room_repo, player_repo=player_repo)
    room = use_case.execute(name=body.name, dm_id=dm.id, max_players=body.max_players)
    db.commit()

    room_token = create_room_token(
        user_id=dm.id,
        room_id=room.id,
        role="dm",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    response = _room_response(room, [dm.id])
    return CreateRoomResponse(room=response, room_token=room_token)


@rooms_router.post(
    "/join/{invite_code}",
    response_model=JoinRoomResponse,
)
def join_room(
    invite_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    room_repo: SqlAlchemyRoomRepository = Depends(get_room_repository),
    player_repo: SqlAlchemyRoomPlayerRepository = Depends(get_room_player_repository),
) -> JoinRoomResponse:
    """
    Any authenticated user joins a room using its invite code.
    Returns the room details plus a room-scoped JWT for WebSocket use.
    """
    logger.info("join_room: user_id=%s invite_code=%s", current_user.id, invite_code)
    use_case = JoinRoom(room_repo=room_repo, player_repo=player_repo)
    room = use_case.execute(invite_code=invite_code.upper(), user_id=current_user.id)
    db.commit()

    room_token = create_room_token(
        user_id=current_user.id,
        room_id=room.id,
        role=current_user.role.value,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    # Fetch current player list for the response.
    players = player_repo.get_by_room(room.id)
    player_ids = [p.user_id for p in players]
    response = _room_response(room, player_ids)
    return JoinRoomResponse(room=response, room_token=room_token)


@rooms_router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    room_repo: SqlAlchemyRoomRepository = Depends(get_room_repository),
    player_repo: SqlAlchemyRoomPlayerRepository = Depends(get_room_player_repository),
) -> RoomResponse:
    """Returns room details and the current player list. Any authenticated user may call this."""
    logger.debug("get_room: room_id=%s user_id=%s", room_id, current_user.id)
    use_case = GetRoom(room_repo=room_repo, player_repo=player_repo)
    room, player_ids = use_case.execute(room_id)
    return _room_response(room, player_ids)


@rooms_router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: uuid.UUID,
    db: Session = Depends(get_db),
    dm: User = Depends(get_dm_user),
    room_repo: SqlAlchemyRoomRepository = Depends(get_room_repository),
) -> None:
    """
    DM closes and deletes a room.
    Only the DM who created the room may call this.
    Returns 204 No Content on success.
    """
    logger.info("delete_room: room_id=%s dm_id=%s", room_id, dm.id)
    use_case = DeleteRoom(room_repo=room_repo)
    use_case.execute(room_id=room_id, requesting_user_id=dm.id)
    db.commit()

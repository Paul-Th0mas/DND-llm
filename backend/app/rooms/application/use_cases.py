"""
Application services for the Rooms bounded context.

Each class is a single use case. They orchestrate domain objects and
repositories but contain no business logic themselves — invariants live
on the Room aggregate.
"""

import logging
import uuid
from collections.abc import Callable
from datetime import datetime, timezone

from app.campaigns.domain.repositories import CampaignRepository
from app.core.exceptions import AuthenticationError, ForbiddenError, NotFoundError
from app.dungeons.domain.repositories import DungeonRepository
from app.rooms.domain.models import Room, RoomPlayer, RoomStatus
from app.rooms.domain.repositories import (
    AlreadyInRoomError,
    NotDMError,
    RoomClosedError,
    RoomFullError,
    RoomNotFoundError,
    RoomPlayerRepository,
    RoomRepository,
    WrongPasswordError,
)

logger = logging.getLogger(__name__)


class CreateRoom:
    """
    DM creates a new room. The DM is automatically added as the first member
    so they appear in the connected-players list when they open the WebSocket.
    """

    def __init__(
        self,
        room_repo: RoomRepository,
        player_repo: RoomPlayerRepository,
    ) -> None:
        self._room_repo = room_repo
        self._player_repo = player_repo

    def execute(
        self,
        name: str,
        dm_id: uuid.UUID,
        max_players: int,
        dungeon_id: uuid.UUID | None = None,
        campaign_id: uuid.UUID | None = None,
        password_hash: str | None = None,
    ) -> Room:
        logger.debug(
            "CreateRoom: name='%s' dm_id=%s max_players=%d dungeon_id=%s campaign_id=%s",
            name,
            dm_id,
            max_players,
            dungeon_id,
            campaign_id,
        )
        room, _ = Room.create(
            name=name,
            dm_id=dm_id,
            max_players=max_players,
            dungeon_id=dungeon_id,
            campaign_id=campaign_id,
            password_hash=password_hash,
        )
        self._room_repo.save(room)
        # DM is the first room member.
        dm_entry = RoomPlayer(
            room_id=room.id,
            user_id=dm_id,
            joined_at=datetime.now(tz=timezone.utc),
        )
        self._player_repo.add(dm_entry)
        logger.info(
            "CreateRoom: room id=%s created invite_code=%s",
            room.id,
            room.invite_code.value,
        )
        return room


class JoinRoom:
    """
    Player joins a room via its invite code.
    Idempotent: if the user is already a member, their existing membership
    is returned rather than raising an error.
    """

    def __init__(
        self,
        room_repo: RoomRepository,
        player_repo: RoomPlayerRepository,
    ) -> None:
        self._room_repo = room_repo
        self._player_repo = player_repo

    def execute(self, invite_code: str, user_id: uuid.UUID) -> Room:
        logger.debug("JoinRoom: invite_code=%s user_id=%s", invite_code, user_id)
        room = self._room_repo.get_by_invite_code(invite_code)
        if room is None:
            raise RoomNotFoundError(f"No active room with invite code '{invite_code}'")

        if self._player_repo.is_member(room.id, user_id):
            logger.info(
                "JoinRoom: user_id=%s already a member of room id=%s", user_id, room.id
            )
            return room

        count = self._player_repo.count(room.id)
        if not room.can_accept_player(count):
            raise RoomFullError(
                f"Room '{room.name}' is full ({count}/{room.max_players}) or inactive"
            )

        entry = RoomPlayer(
            room_id=room.id,
            user_id=user_id,
            joined_at=datetime.now(tz=timezone.utc),
        )
        self._player_repo.add(entry)
        logger.info("JoinRoom: user_id=%s joined room id=%s", user_id, room.id)
        return room


class GetRoom:
    """Returns the Room aggregate along with the list of member UUIDs."""

    def __init__(
        self,
        room_repo: RoomRepository,
        player_repo: RoomPlayerRepository,
    ) -> None:
        self._room_repo = room_repo
        self._player_repo = player_repo

    def execute(self, room_id: uuid.UUID) -> tuple[Room, list[uuid.UUID]]:
        logger.debug("GetRoom: room_id=%s", room_id)
        room = self._room_repo.get_by_id(room_id)
        if room is None:
            raise RoomNotFoundError(f"Room {room_id} not found")
        players = self._player_repo.get_by_room(room_id)
        player_ids = [p.user_id for p in players]
        return room, player_ids


class DeleteRoom:
    """
    DM closes and removes a room. Only the room's DM may call this.
    Raises NotDMError (→ HTTP 400) if a non-DM user attempts deletion.
    """

    def __init__(self, room_repo: RoomRepository) -> None:
        self._room_repo = room_repo

    def execute(self, room_id: uuid.UUID, requesting_user_id: uuid.UUID) -> None:
        logger.debug(
            "DeleteRoom: room_id=%s requesting_user_id=%s", room_id, requesting_user_id
        )
        room = self._room_repo.get_by_id(room_id)
        if room is None:
            raise RoomNotFoundError(f"Room {room_id} not found")
        if room.dm_id != requesting_user_id:
            raise NotDMError("Only the DM who created this room can delete it")
        room.close()
        self._room_repo.delete(room_id)
        logger.info(
            "DeleteRoom: room id=%s deleted by dm_id=%s", room_id, requesting_user_id
        )


class LinkRoomDungeon:
    """
    DM links a dungeon (and its campaign) to an existing room.

    This lets the room carry narrative context (world lore, tone, quest) from
    the campaign/dungeon without re-creating the room. Only the room's own DM
    may call this; any other authenticated DM gets an AuthenticationError.
    """

    def __init__(
        self,
        room_repo: RoomRepository,
        dungeon_repo: DungeonRepository,
        campaign_repo: CampaignRepository,
    ) -> None:
        self._room_repo = room_repo
        self._dungeon_repo = dungeon_repo
        self._campaign_repo = campaign_repo

    def execute(
        self,
        room_id: uuid.UUID,
        dungeon_id: uuid.UUID,
        campaign_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> Room:
        logger.debug(
            "LinkRoomDungeon: room_id=%s dungeon_id=%s campaign_id=%s user_id=%s",
            room_id,
            dungeon_id,
            campaign_id,
            requesting_user_id,
        )

        room = self._room_repo.get_by_id(room_id)
        if room is None:
            raise RoomNotFoundError(f"Room {room_id} not found")

        # Only the DM who owns this room may modify it.
        if room.dm_id != requesting_user_id:
            raise AuthenticationError(
                "Only the DM who created this room can link a dungeon to it"
            )

        # Validate the dungeon exists.
        if self._dungeon_repo.get_by_id(dungeon_id) is None:
            raise NotFoundError(f"Dungeon {dungeon_id} not found")

        # Validate the campaign exists.
        if self._campaign_repo.get_by_id(campaign_id) is None:
            raise NotFoundError(f"Campaign {campaign_id} not found")

        # Room is a plain (non-frozen) dataclass — fields are mutable.
        room.dungeon_id = dungeon_id
        room.campaign_id = campaign_id

        updated_room = self._room_repo.update(room)
        logger.info(
            "LinkRoomDungeon: room id=%s linked dungeon_id=%s campaign_id=%s",
            room_id,
            dungeon_id,
            campaign_id,
        )
        return updated_room


class ListRooms:
    """
    Returns a list of rooms filtered by status, ordered newest first.
    Used by the lobby browser so players can see available games.
    Each result is a tuple of (Room, player_count) to avoid N+1 queries
    in the caller — the repository fetches counts alongside rooms.
    """

    def __init__(
        self,
        room_repo: RoomRepository,
        player_repo: RoomPlayerRepository,
    ) -> None:
        self._room_repo = room_repo
        self._player_repo = player_repo

    def execute(self, status: RoomStatus) -> list[tuple[Room, int]]:
        logger.debug("ListRooms: status=%s", status.value)
        rooms = self._room_repo.list_by_status(status)
        # Fetch player counts individually. Acceptable for the expected number
        # of open rooms (typically < 50). Replace with a JOIN if this becomes slow.
        results = [(room, self._player_repo.count(room.id)) for room in rooms]
        logger.info(
            "ListRooms: returned %d rooms with status=%s", len(results), status.value
        )
        return results


class JoinRoomById:
    """
    Player joins a room via the lobby browser using the room's UUID and a password.

    Unlike JoinRoom (which uses an invite code), this use case enforces:
      - Only players (not DMs) may join via the lobby.
      - The room must be in 'open' status.
      - The room must not be full.
      - If the room has a password, the supplied password must match.

    verify_password_fn is injected so the use case stays free of bcrypt imports
    (bcrypt is an infrastructure detail).
    """

    def __init__(
        self,
        room_repo: RoomRepository,
        player_repo: RoomPlayerRepository,
        verify_password_fn: Callable[[str, str], bool],
    ) -> None:
        self._room_repo = room_repo
        self._player_repo = player_repo
        self._verify_password = verify_password_fn

    def execute(
        self,
        room_id: uuid.UUID,
        user_id: uuid.UUID,
        user_role: str,
        password: str,
    ) -> Room:
        logger.debug(
            "JoinRoomById: room_id=%s user_id=%s user_role=%s",
            room_id,
            user_id,
            user_role,
        )
        room = self._room_repo.get_by_id(room_id)
        if room is None:
            raise RoomNotFoundError(f"Room {room_id} not found")

        # Only the player role may join via the lobby (DMs own rooms, not join them).
        if user_role != "player":
            raise ForbiddenError("Only players can join rooms via the lobby")

        if room.status == RoomStatus.closed:
            raise RoomClosedError("This room is no longer accepting players")

        if room.status == RoomStatus.in_progress:
            raise RoomClosedError("This room is no longer accepting players")

        # Verify password before checking capacity so the error message leaks
        # no information about whether the room has space.
        if room.password_hash is not None:
            if not self._verify_password(password, room.password_hash):
                raise WrongPasswordError("Incorrect password")

        count = self._player_repo.count(room.id)
        if not room.can_accept_player(count):
            raise RoomFullError(
                f"Room '{room.name}' is full ({count}/{room.max_players})"
            )

        # Idempotent: return existing membership without error.
        if self._player_repo.is_member(room.id, user_id):
            logger.info(
                "JoinRoomById: user_id=%s already a member of room id=%s",
                user_id,
                room.id,
            )
            return room

        entry = RoomPlayer(
            room_id=room.id,
            user_id=user_id,
            joined_at=datetime.now(tz=timezone.utc),
        )
        self._player_repo.add(entry)
        logger.info("JoinRoomById: user_id=%s joined room id=%s", user_id, room.id)
        return room

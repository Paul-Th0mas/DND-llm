import logging
import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.rooms.domain.models import InviteCode, Room, RoomPlayer
from app.rooms.domain.repositories import RoomPlayerRepository, RoomRepository
from app.rooms.infrastructure.orm_models import RoomORM, RoomPlayerORM

logger = logging.getLogger(__name__)


class SqlAlchemyRoomRepository(RoomRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, room_id: uuid.UUID) -> Room | None:
        logger.debug("get_by_id: room_id=%s", room_id)
        stmt = select(RoomORM).where(RoomORM.id == room_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        return self._to_domain(row) if row is not None else None

    def get_by_invite_code(self, invite_code: str) -> Room | None:
        logger.debug("get_by_invite_code: invite_code=%s", invite_code)
        stmt = select(RoomORM).where(RoomORM.invite_code == invite_code.upper())
        row = self._session.execute(stmt).scalar_one_or_none()
        return self._to_domain(row) if row is not None else None

    def save(self, room: Room) -> None:
        logger.debug("save: room id=%s", room.id)
        orm = RoomORM(
            id=room.id,
            name=room.name,
            dm_id=room.dm_id,
            invite_code=room.invite_code.value,
            max_players=room.max_players,
            is_active=room.is_active,
            created_at=room.created_at,
        )
        self._session.merge(orm)
        self._session.flush()

    def delete(self, room_id: uuid.UUID) -> None:
        logger.debug("delete: room_id=%s", room_id)
        stmt = delete(RoomORM).where(RoomORM.id == room_id)
        self._session.execute(stmt)
        self._session.flush()

    @staticmethod
    def _to_domain(orm: RoomORM) -> Room:
        return Room(
            id=orm.id,
            name=orm.name,
            dm_id=orm.dm_id,
            invite_code=InviteCode(value=orm.invite_code),
            max_players=orm.max_players,
            is_active=orm.is_active,
            created_at=orm.created_at,
        )


class SqlAlchemyRoomPlayerRepository(RoomPlayerRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, room_player: RoomPlayer) -> None:
        logger.debug(
            "add: room_id=%s user_id=%s", room_player.room_id, room_player.user_id
        )
        orm = RoomPlayerORM(
            room_id=room_player.room_id,
            user_id=room_player.user_id,
            joined_at=room_player.joined_at,
        )
        self._session.merge(orm)
        self._session.flush()

    def get_by_room(self, room_id: uuid.UUID) -> list[RoomPlayer]:
        logger.debug("get_by_room: room_id=%s", room_id)
        stmt = select(RoomPlayerORM).where(RoomPlayerORM.room_id == room_id)
        rows = self._session.execute(stmt).scalars().all()
        return [
            RoomPlayer(room_id=r.room_id, user_id=r.user_id, joined_at=r.joined_at)
            for r in rows
        ]

    def is_member(self, room_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = select(RoomPlayerORM).where(
            RoomPlayerORM.room_id == room_id,
            RoomPlayerORM.user_id == user_id,
        )
        return self._session.execute(stmt).scalar_one_or_none() is not None

    def count(self, room_id: uuid.UUID) -> int:
        rows = self.get_by_room(room_id)
        return len(rows)

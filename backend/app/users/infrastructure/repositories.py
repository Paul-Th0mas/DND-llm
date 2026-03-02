import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.domain.models import Email, GoogleID, User, UserRole
from app.users.domain.repositories import UserRepository
from app.users.infrastructure.orm_models import UserORM


logger = logging.getLogger(__name__)


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_google_id(self, google_id: str) -> User | None:
        logger.debug("get_by_google_id: querying google_id=%s", google_id)
        stmt = select(UserORM).where(UserORM.google_id == google_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        if row is None:
            return None
        logger.debug("get_by_google_id: found user id=%s", row.id)
        return self._to_domain(row)

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        logger.debug("get_by_id: querying user_id=%s", user_id)
        stmt = select(UserORM).where(UserORM.id == user_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        if row is None:
            return None
        logger.debug("get_by_id: found user email=%s", row.email)
        return self._to_domain(row)

    def get_by_email(self, email: str) -> User | None:
        logger.debug("get_by_email: querying email=%s", email)
        stmt = select(UserORM).where(UserORM.email == email.lower())
        row = self._session.execute(stmt).scalar_one_or_none()
        if row is None:
            return None
        logger.debug("get_by_email: found user id=%s", row.id)
        return self._to_domain(row)

    def save(self, user: User) -> None:
        logger.debug("save: persisting user id=%s", user.id)
        # merge() handles INSERT for new PKs and UPDATE for existing ones.
        orm = UserORM(
            id=user.id,
            google_id=user.google_id.value if user.google_id is not None else None,
            email=user.email.value,
            name=user.name,
            picture_url=user.picture_url,
            role=user.role.value,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
        )
        self._session.merge(orm)
        self._session.flush()

    @staticmethod
    def _to_domain(orm: UserORM) -> User:
        """Maps a UserORM row to the User aggregate."""
        return User(
            id=orm.id,
            google_id=(
                GoogleID(value=orm.google_id) if orm.google_id is not None else None
            ),
            email=Email(value=orm.email),
            name=orm.name,
            picture_url=orm.picture_url,
            role=UserRole(value=orm.role),
            hashed_password=orm.hashed_password,
            created_at=orm.created_at,
        )

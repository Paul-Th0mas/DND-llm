import logging

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.users.application.use_cases import GetCurrentUser
from app.users.domain.models import User
from app.users.infrastructure.auth import decode_access_token
from app.users.infrastructure.repositories import SqlAlchemyUserRepository

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer()


def get_user_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session=db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repository),
) -> User:
    logger.debug("get_current_user: decoding bearer token")
    # decode_access_token now raises AuthenticationError (not HTTPException),
    # which the global handler converts to HTTP 401.
    payload = decode_access_token(credentials.credentials)
    logger.debug("get_current_user: token valid, fetching user id=%s", payload.user_id)
    return GetCurrentUser(repo=user_repo).execute(user_id=payload.user_id)

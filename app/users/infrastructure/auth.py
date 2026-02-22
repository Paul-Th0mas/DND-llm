"""
JWT creation and decoding.

Infrastructure layer: depends on python-jose and app.core.config.
Must not raise HTTPException — raises AuthenticationError instead so the
global handler in app/core/error_handlers.py converts it to HTTP 401.
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TokenPayload:
    """
    Decoded contents of a JWT issued by this application.

    user_id  — the authenticated user's UUID (from the 'sub' claim).
    role     — "dm" or "player".
    room_id  — present only in room-scoped tokens issued at join/create time;
               None in plain user tokens issued at login.
    """

    user_id: uuid.UUID
    role: str
    room_id: uuid.UUID | None


def create_access_token(
    data: dict[str, object],
    expires_delta: timedelta | None = None,
) -> str:
    """Signs a JWT with the given payload. 'sub' must be the user UUID string."""
    to_encode: dict[str, object] = data.copy()
    expire = datetime.now(tz=timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    logger.debug("create_access_token: encoding JWT for sub=%s", data.get("sub"))
    token: str = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return token


def create_room_token(
    user_id: uuid.UUID,
    room_id: uuid.UUID,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Issues a room-scoped JWT that the client sends when opening a WebSocket
    connection to /ws/{room_id}. The room_id claim ties this token to a
    specific room, preventing cross-room token reuse.
    """
    logger.debug(
        "create_room_token: issuing room token user_id=%s room_id=%s role=%s",
        user_id,
        room_id,
        role,
    )
    return create_access_token(
        data={"sub": str(user_id), "room_id": str(room_id), "role": role},
        expires_delta=expires_delta,
    )


def decode_access_token(token: str) -> TokenPayload:
    """
    Decodes and validates a JWT. Raises AuthenticationError on any failure
    (expired, tampered, missing claims) — never HTTPException.
    """
    try:
        payload: dict[str, object] = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        sub = payload.get("sub")
        if not isinstance(sub, str):
            raise AuthenticationError("Invalid token: missing 'sub' claim")

        # role defaults to "player" for tokens issued before roles were added.
        role_raw = payload.get("role", "player")
        role = role_raw if isinstance(role_raw, str) else "player"

        room_id_raw = payload.get("room_id")
        room_id = uuid.UUID(str(room_id_raw)) if room_id_raw is not None else None

        result = TokenPayload(
            user_id=uuid.UUID(sub),
            role=role,
            room_id=room_id,
        )
        logger.debug("decode_access_token: valid token for user_id=%s", result.user_id)
        return result
    except (JWTError, ValueError) as exc:
        logger.warning("decode_access_token: invalid or expired token: %s", exc)
        raise AuthenticationError("Could not validate credentials") from exc

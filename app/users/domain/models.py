import logging
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from app.users.domain.events import UserRegisteredViaGoogle, UserRegisteredWithPassword

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Value Objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        lowered = self.value.lower()
        # object.__setattr__ is required to mutate a field on a frozen dataclass
        # during __post_init__ — it bypasses the immutability guard legally.
        object.__setattr__(self, "value", lowered)
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", lowered):
            raise ValueError(f"Invalid email address: {lowered}")


@dataclass(frozen=True)
class GoogleID:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("GoogleID cannot be empty")


@dataclass(frozen=True)
class UserRole:
    """
    Encodes the user's role within the platform.
    Only "dm" (Dungeon Master) and "player" are valid roles.
    Keeping this as a value object lets the domain enforce the invariant
    rather than relying on callers to pass valid strings.
    """

    value: str

    def __post_init__(self) -> None:
        if self.value not in ("dm", "player"):
            raise ValueError(f"Invalid role '{self.value}'. Must be 'dm' or 'player'.")


# ---------------------------------------------------------------------------
# Aggregate Root
# ---------------------------------------------------------------------------


@dataclass
class User:
    """
    Aggregate root for the Users bounded context.

    Supports two registration paths:
      - Google OAuth  (google_id is set, hashed_password is None)
      - Email/password (google_id is None, hashed_password is set)
    """

    id: uuid.UUID
    email: Email
    name: str
    role: UserRole
    created_at: datetime
    # One of these is always None depending on the auth method used.
    google_id: GoogleID | None
    hashed_password: str | None
    picture_url: str

    @classmethod
    def register_via_google(
        cls,
        google_id: str,
        email: str,
        name: str,
        picture_url: str,
    ) -> tuple["User", UserRegisteredViaGoogle]:
        """Factory: creates a new User from a Google OAuth profile."""
        user_id = uuid.uuid4()
        now = datetime.now(tz=timezone.utc)
        user = cls(
            id=user_id,
            google_id=GoogleID(value=google_id),
            email=Email(value=email),
            name=name,
            picture_url=picture_url,
            # Google users default to "player"; a DM must be promoted explicitly.
            role=UserRole(value="player"),
            hashed_password=None,
            created_at=now,
        )
        logger.info(
            "User.register_via_google: created user id=%s email=%s", user_id, email
        )
        event = UserRegisteredViaGoogle(
            user_id=user_id,
            email=email,
            google_id=google_id,
            occurred_at=now,
        )
        return user, event

    @classmethod
    def register_with_password(
        cls,
        email: str,
        name: str,
        hashed_password: str,
        role: str,
    ) -> tuple["User", UserRegisteredWithPassword]:
        """Factory: creates a new User from an email + pre-hashed password."""
        user_id = uuid.uuid4()
        now = datetime.now(tz=timezone.utc)
        user = cls(
            id=user_id,
            google_id=None,
            email=Email(value=email),
            name=name,
            picture_url="",
            role=UserRole(value=role),
            hashed_password=hashed_password,
            created_at=now,
        )
        logger.info(
            "User.register_with_password: created user id=%s email=%s role=%s",
            user_id,
            email,
            role,
        )
        event = UserRegisteredWithPassword(
            user_id=user_id,
            email=email,
            occurred_at=now,
        )
        return user, event

    def update_profile(self, name: str, picture_url: str) -> None:
        """Syncs name and picture from Google on every OAuth login."""
        self.name = name
        self.picture_url = picture_url

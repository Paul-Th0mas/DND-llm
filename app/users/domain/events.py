import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserRegisteredViaGoogle:
    user_id: uuid.UUID
    email: str
    google_id: str
    occurred_at: datetime


@dataclass(frozen=True)
class UserRegisteredWithPassword:
    """Raised when a new user registers via email + password."""

    user_id: uuid.UUID
    email: str
    occurred_at: datetime

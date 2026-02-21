import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # Nullable: Google OAuth users have a google_id; email/password users do not.
    google_id: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    email: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    picture_url: Mapped[str] = mapped_column(String, default="")
    # "dm" or "player" — enforced by the UserRole value object in the domain.
    role: Mapped[str] = mapped_column(String, nullable=False, default="player")
    # Nullable: only set for email/password users.
    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

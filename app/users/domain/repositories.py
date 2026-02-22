import uuid
from abc import ABC, abstractmethod

from app.core.exceptions import NotFoundError
from app.users.domain.models import User


# Subclass of NotFoundError so the global handler returns HTTP 404 automatically.
class UserNotFoundError(NotFoundError):
    pass


class UserRepository(ABC):
    @abstractmethod
    def get_by_google_id(self, google_id: str) -> User | None: ...

    @abstractmethod
    def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def save(self, user: User) -> None: ...

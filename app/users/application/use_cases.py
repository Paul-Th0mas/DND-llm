import logging
import uuid
from collections.abc import Callable

from app.core.exceptions import AuthenticationError, DomainError
from app.users.domain.models import User
from app.users.domain.repositories import UserNotFoundError, UserRepository


logger = logging.getLogger(__name__)


class RegisterOrRetrieveUser:
    """Handles the 'sign in with Google' use case — creates or updates a user."""

    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def execute(
        self,
        google_id: str,
        email: str,
        name: str,
        picture_url: str,
    ) -> User:
        logger.debug("RegisterOrRetrieveUser: looking up google_id=%s", google_id)
        existing = self._repo.get_by_google_id(google_id)
        if existing is None:
            logger.info("RegisterOrRetrieveUser: new user, registering email=%s", email)
            user, _ = User.register_via_google(
                google_id=google_id,
                email=email,
                name=name,
                picture_url=picture_url,
            )
            self._repo.save(user)
            logger.info("RegisterOrRetrieveUser: saved new user id=%s", user.id)
            return user
        logger.info(
            "RegisterOrRetrieveUser: existing user id=%s, updating profile",
            existing.id,
        )
        existing.update_profile(name=name, picture_url=picture_url)
        self._repo.save(existing)
        return existing


class RegisterUserWithPassword:
    """
    Registers a new user with email + password.

    hash_password is injected so the application layer stays independent of
    the bcrypt infrastructure — the API layer wires in the concrete function.
    """

    def __init__(
        self,
        repo: UserRepository,
        hash_password: Callable[[str], str],
    ) -> None:
        self._repo = repo
        self._hash_password = hash_password

    def execute(self, email: str, name: str, password: str, role: str) -> User:
        logger.debug("RegisterUserWithPassword: checking for existing email=%s", email)
        if self._repo.get_by_email(email) is not None:
            raise DomainError(f"Email '{email}' is already registered")
        hashed = self._hash_password(password)
        user, _ = User.register_with_password(
            email=email,
            name=name,
            hashed_password=hashed,
            role=role,
        )
        self._repo.save(user)
        logger.info(
            "RegisterUserWithPassword: registered user id=%s email=%s role=%s",
            user.id,
            email,
            role,
        )
        return user


class LoginUser:
    """
    Authenticates a user by email + password and returns the User aggregate.

    verify_password is injected for the same reason as hash_password above —
    bcrypt is an infrastructure detail.
    """

    def __init__(
        self,
        repo: UserRepository,
        verify_password: Callable[[str, str], bool],
    ) -> None:
        self._repo = repo
        self._verify_password = verify_password

    def execute(self, email: str, password: str) -> User:
        logger.debug("LoginUser: attempting login for email=%s", email)
        user = self._repo.get_by_email(email)
        # Use a generic error message to avoid leaking whether the email exists.
        if user is None or user.hashed_password is None:
            logger.warning(
                "LoginUser: user not found or no password set email=%s", email
            )
            raise AuthenticationError("Invalid email or password")
        if not self._verify_password(password, user.hashed_password):
            logger.warning("LoginUser: incorrect password for email=%s", email)
            raise AuthenticationError("Invalid email or password")
        logger.info("LoginUser: successful login for user id=%s", user.id)
        return user


class GetCurrentUser:
    """Fetches a user by their internal UUID — used to resolve the JWT subject."""

    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def execute(self, user_id: uuid.UUID) -> User:
        logger.debug("GetCurrentUser: fetching user id=%s", user_id)
        user = self._repo.get_by_id(user_id)
        if user is None:
            logger.warning("GetCurrentUser: user id=%s not found", user_id)
            raise UserNotFoundError(f"User {user_id} not found")
        logger.debug("GetCurrentUser: found user email=%s", user.email.value)
        return user

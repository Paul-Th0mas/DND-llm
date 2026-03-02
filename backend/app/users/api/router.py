import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.users.api.dependencies import get_current_user, get_user_repository
from app.users.application.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)
from app.users.application.use_cases import (
    LoginUser,
    RegisterOrRetrieveUser,
    RegisterUserWithPassword,
)
from app.users.domain.models import User
from app.users.infrastructure.auth import create_access_token
from app.users.infrastructure.google_oauth import (
    exchange_code_for_user_info,
    get_google_redirect_url,
)
from app.users.infrastructure.password import hash_password, verify_password
from app.users.infrastructure.repositories import SqlAlchemyUserRepository

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(prefix="/users", tags=["users"])


# ---------------------------------------------------------------------------
# Google OAuth endpoints (existing flow — unchanged)
# ---------------------------------------------------------------------------


@auth_router.get("/google")
async def google_login(request: Request) -> RedirectResponse:
    """Redirects the user to Google's OAuth consent screen."""
    logger.debug("google_login: redirecting to Google consent screen")
    return await get_google_redirect_url(request)


@auth_router.get("/google/callback", name="google_callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repository),
) -> RedirectResponse:
    """Handles the OAuth callback: creates/updates the user and issues a JWT."""
    logger.info("google_callback: OAuth callback received")
    user_info = await exchange_code_for_user_info(request)
    use_case = RegisterOrRetrieveUser(repo=user_repo)
    user = use_case.execute(
        google_id=user_info["google_id"],
        email=user_info["email"],
        name=user_info["name"],
        picture_url=user_info["picture_url"],
    )
    db.commit()
    logger.info("google_callback: user id=%s committed, issuing JWT", user.id)
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return RedirectResponse(url=f"{settings.FRONTEND_URL}?token={token}")


# ---------------------------------------------------------------------------
# Email + password endpoints (new)
# ---------------------------------------------------------------------------


@auth_router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    body: RegisterRequest,
    db: Session = Depends(get_db),
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repository),
) -> TokenResponse:
    """
    Registers a new user with email + password.
    The caller chooses their role: 'dm' or 'player' (defaults to 'player').
    Returns a JWT immediately so the user is logged in right after registering.
    """
    logger.info("register: registering email=%s role=%s", body.email, body.role)
    use_case = RegisterUserWithPassword(repo=user_repo, hash_password=hash_password)
    user = use_case.execute(
        email=str(body.email),
        name=body.name,
        password=body.password,
        role=body.role,
    )
    db.commit()
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info("register: user id=%s registered and token issued", user.id)
    return TokenResponse(access_token=token)


@auth_router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repository),
) -> TokenResponse:
    """
    Authenticates an email/password user and returns a JWT.
    Returns HTTP 401 on invalid credentials (via AuthenticationError → global handler).
    """
    logger.info("login: attempt for email=%s", body.email)
    use_case = LoginUser(repo=user_repo, verify_password=verify_password)
    user = use_case.execute(email=str(body.email), password=body.password)
    # No db.commit() needed — login is read-only.
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info("login: JWT issued for user id=%s", user.id)
    return TokenResponse(access_token=token)


# ---------------------------------------------------------------------------
# Authenticated user profile
# ---------------------------------------------------------------------------


@users_router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    """Returns the profile of the currently authenticated user."""
    logger.debug("get_me: returning profile for user id=%s", current_user.id)
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email.value,
        name=current_user.name,
        picture_url=current_user.picture_url,
        role=current_user.role.value,
        created_at=current_user.created_at,
    )

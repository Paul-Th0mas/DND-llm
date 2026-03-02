import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.error_handlers import EXCEPTION_HANDLERS
from app.api.v1.router import api_router

# Root logger at WARNING keeps third-party libraries (httpcore, httpx, authlib,
# sqlalchemy, uvicorn internals) quiet. Only our own "app" namespace is set to
# DEBUG so we see full detail without the noise.
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("app").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

# Tag metadata controls the grouping and descriptions shown in Swagger UI.
# Each tag here matches the tags=["..."] declared on the routers.
_openapi_tags = [
    {
        "name": "auth",
        "description": (
            "Google OAuth sign-in flow. "
            "**To test protected endpoints in Swagger UI:** "
            "open `/api/v1/auth/google` in your browser, complete the Google sign-in, "
            "then copy the `token` query param from the redirect URL. "
            "Click the **Authorize** button at the top of this page and paste the token."
        ),
    },
    {
        "name": "users",
        "description": "Authenticated user profile endpoints. Requires a Bearer token.",
    },
]

logger.info("Creating FastAPI application")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description=(
        "DnD API — backend for the DnD project.\n\n"
        "**Authentication:** This API uses Google OAuth2. "
        "Sign in via `GET /api/v1/auth/google`. "
        "You will receive a JWT that must be sent as `Authorization: Bearer <token>` "
        "on all protected routes."
    ),
    openapi_tags=_openapi_tags,
    # Swagger UI is served at /docs, ReDoc at /redoc.
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORSMiddleware must be added before SessionMiddleware so it runs on the way
# out (after the response is built) and can attach the correct headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,  # needed so the browser sends cookies (OAuth state)
    allow_methods=["*"],
    allow_headers=["*"],
)

# SessionMiddleware is required by authlib to store the OAuth state cookie.
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Register domain exception handlers most-specific → least-specific.
# FastAPI checks handlers in registration order and calls the first type match,
# so NotFoundError and AuthenticationError must be registered before their parent
# DomainError, and DomainError before the Exception catch-all.
for exc_type, handler in EXCEPTION_HANDLERS:
    app.add_exception_handler(exc_type, handler)  # type: ignore[arg-type]

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}

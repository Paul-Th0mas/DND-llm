"""
Global exception handlers registered on the FastAPI app via add_exception_handler().

FastAPI's exception handler mechanism works like middleware for errors: when an
exception propagates out of any endpoint or dependency, FastAPI checks the registered
handlers in registration order (most-specific first) and calls the first match.

All handlers return a JSONResponse with {"detail": "..."} — the same shape as
FastAPI's built-in HTTPException handler — so clients always see a consistent body.
"""

import logging
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AuthenticationError, DomainError, NotFoundError

logger = logging.getLogger(__name__)


def handle_not_found(request: Request, exc: Exception) -> JSONResponse:
    """Converts NotFoundError → HTTP 404."""
    logger.warning("Not found: %s %s — %s", request.method, request.url.path, exc)
    return JSONResponse(status_code=404, content={"detail": str(exc) or "Not found"})


def handle_authentication_error(request: Request, exc: Exception) -> JSONResponse:
    """Converts AuthenticationError → HTTP 401."""
    logger.warning(
        "Authentication error: %s %s — %s", request.method, request.url.path, exc
    )
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc) or "Authentication failed"},
        headers={"WWW-Authenticate": "Bearer"},
    )


def handle_domain_error(request: Request, exc: Exception) -> JSONResponse:
    """Fallback for any DomainError not caught by a more specific handler → HTTP 400."""
    logger.warning("Domain error: %s %s — %s", request.method, request.url.path, exc)
    return JSONResponse(status_code=400, content={"detail": str(exc) or "Bad request"})


def handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for any exception that slips past all other handlers → HTTP 500.

    Logs the full traceback at ERROR level so nothing is silently swallowed.
    """
    logger.error(
        "Unhandled exception: %s %s\n%s",
        request.method,
        request.url.path,
        traceback.format_exc(),
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Exported as a list so main.py can iterate and register each pair cleanly.
# Order here is most-specific → least-specific, which mirrors registration order.
EXCEPTION_HANDLERS: list[tuple[type[Exception], object]] = [
    (NotFoundError, handle_not_found),
    (AuthenticationError, handle_authentication_error),
    (DomainError, handle_domain_error),
    (Exception, handle_unhandled_exception),
]

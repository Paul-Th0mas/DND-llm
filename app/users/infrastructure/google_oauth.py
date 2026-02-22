import logging
from typing import cast

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from fastapi import Request
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

oauth = OAuth()

# Register Google as an OIDC provider. server_metadata_url triggers OIDC Discovery,
# which automatically fetches the JWKS endpoint for ID token verification.
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


async def get_google_redirect_url(request: Request) -> RedirectResponse:
    """Generates the Google OAuth consent URL and redirects the user there."""
    redirect_uri = request.url_for("google_callback")
    logger.debug("get_google_redirect_url: redirect_uri=%s", redirect_uri)
    return cast(
        RedirectResponse, await oauth.google.authorize_redirect(request, redirect_uri)
    )


async def exchange_code_for_user_info(request: Request) -> dict[str, str]:
    """Exchanges the authorization code for tokens and extracts user profile data."""
    logger.debug("exchange_code_for_user_info: exchanging authorization code for token")
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as exc:
        # OAuthError covers: state mismatch, code reuse, provider-side errors, etc.
        # Translate to a domain AuthenticationError so the global handler returns 401.
        logger.error(
            "exchange_code_for_user_info: OAuth token exchange failed: %s", exc
        )
        raise AuthenticationError(f"Google OAuth failed: {exc}") from exc
    # userinfo comes from the OIDC ID token claims (no extra network call needed).
    user_info = token.get("userinfo") or await oauth.google.userinfo(token=token)
    result = {
        "google_id": str(user_info["sub"]),
        "email": str(user_info["email"]),
        "name": str(user_info.get("name", "")),
        "picture_url": str(user_info.get("picture", "")),
    }
    logger.info(
        "exchange_code_for_user_info: resolved email=%s google_id=%s",
        result["email"],
        result["google_id"],
    )
    return result

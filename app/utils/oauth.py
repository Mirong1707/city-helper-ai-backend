"""OAuth2 utilities and helpers"""

import httpx
import structlog
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException

from app.core.config import settings

logger = structlog.get_logger()

# OAuth2 client configuration
oauth = OAuth()


def configure_google_oauth():
    """
    Configure Google OAuth2 client

    Must be called after settings are loaded
    """
    if not settings.secrets.has_google_oauth():
        logger.warning(
            "google_oauth_not_configured",
            message="Google OAuth2 credentials not found in environment",
        )
        return

    oauth.register(
        name="google",
        client_id=settings.secrets.get_google_client_id(),
        client_secret=settings.secrets.get_google_client_secret(),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile",
        },
    )
    logger.info(
        "google_oauth_configured", client_id_prefix=settings.secrets.get_google_client_id()[:20]
    )


async def exchange_google_code_for_user_info(code: str, redirect_uri: str) -> dict:
    """
    Exchange Google authorization code for user information

    Args:
        code: Authorization code from Google
        redirect_uri: Redirect URI used in authorization request

    Returns:
        Dict with user info: {email, name, picture, sub (Google user ID)}

    Raises:
        HTTPException: If token exchange fails
    """
    client_id = settings.secrets.get_google_client_id()
    client_secret = settings.secrets.get_google_client_secret()

    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth2 not configured")

    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    logger.debug("exchanging_google_code", redirect_uri=redirect_uri)

    async with httpx.AsyncClient() as client:
        # Get access token
        token_response = await client.post(token_url, data=token_data)

        if token_response.status_code != 200:
            logger.error(
                "google_token_exchange_failed",
                status_code=token_response.status_code,
                response=token_response.text,
            )
            raise HTTPException(status_code=400, detail="Failed to exchange authorization code")

        tokens = token_response.json()
        access_token = tokens.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="No access token in response")

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        userinfo_response = await client.get(
            userinfo_url, headers={"Authorization": f"Bearer {access_token}"}
        )

        if userinfo_response.status_code != 200:
            logger.error("google_userinfo_failed", status_code=userinfo_response.status_code)
            raise HTTPException(status_code=400, detail="Failed to get user information")

        user_info = userinfo_response.json()
        logger.info("google_oauth_success", email=user_info.get("email"))

        return user_info


def get_google_oauth_url(redirect_uri: str, state: str | None = None) -> str:
    """
    Generate Google OAuth2 authorization URL

    Args:
        redirect_uri: Where Google should redirect after auth
        state: Optional state parameter for CSRF protection

    Returns:
        Authorization URL to redirect user to
    """
    client_id = settings.secrets.get_google_client_id()

    if not client_id:
        raise HTTPException(status_code=500, detail="Google OAuth2 not configured")

    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": redirect_uri,
        "access_type": "offline",
        "prompt": "consent",
    }

    if state:
        params["state"] = state

    # Build URL with query parameters
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"

    logger.debug("generated_google_oauth_url", redirect_uri=redirect_uri)
    return auth_url

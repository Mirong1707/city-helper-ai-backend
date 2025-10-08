"""Authentication endpoints"""

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from app.core.config import settings

# Access config directly
config = settings.config
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, User
from app.services import auth_service
from app.utils.oauth import exchange_google_code_for_user_info, get_google_oauth_url

router = APIRouter(prefix="/api/auth", tags=["auth"])


class GoogleAuthUrlResponse(BaseModel):
    """Google OAuth2 URL response"""

    auth_url: str


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    User login endpoint

    Args:
        request: Login credentials

    Returns:
        User info and authentication token
    """
    user, token = auth_service.login(
        email=request.email, password=request.password, delay=config.auth_delay
    )

    return AuthResponse(user=user, token=token)


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    User registration endpoint

    Args:
        request: Registration data

    Returns:
        User info and authentication token

    Raises:
        HTTPException 400: If user already exists
    """
    user, token = auth_service.register(
        email=request.email, password=request.password, delay=config.auth_delay
    )

    return AuthResponse(user=user, token=token)


@router.post("/logout")
async def logout(authorization: str | None = Header(None)):
    """
    User logout endpoint

    Args:
        authorization: Bearer token from header

    Returns:
        Success message
    """
    token = authorization.replace("Bearer ", "") if authorization else None
    auth_service.logout(token=token, delay=0.2)

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=User)
async def get_current_user(authorization: str | None = Header(None)):
    """
    Get current authenticated user

    Args:
        authorization: Bearer token from header

    Returns:
        User information

    Raises:
        HTTPException 401: If not authenticated or invalid token
    """
    if not authorization:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.replace("Bearer ", "")
    return auth_service.get_current_user(token=token)


# Google OAuth2 endpoints


@router.get("/google", response_model=GoogleAuthUrlResponse)
async def google_login(
    redirect_uri: str = Query(default="http://localhost:3001/api/auth/google/callback"),
):
    """
    Initiate Google OAuth2 login

    Args:
        redirect_uri: Where to redirect after Google auth

    Returns:
        Authorization URL to redirect user to
    """
    if not settings.secrets.has_google_oauth():
        raise HTTPException(status_code=503, detail="Google OAuth2 is not configured")

    auth_url = get_google_oauth_url(redirect_uri=redirect_uri)
    return GoogleAuthUrlResponse(auth_url=auth_url)


@router.get("/google/callback", response_model=AuthResponse)
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    redirect_uri: str = Query(default="http://localhost:3001/api/auth/google/callback"),
):
    """
    Handle Google OAuth2 callback

    Args:
        code: Authorization code from Google
        redirect_uri: Redirect URI used in authorization

    Returns:
        User info and authentication token
    """
    if not settings.secrets.has_google_oauth():
        raise HTTPException(status_code=503, detail="Google OAuth2 is not configured")

    # Exchange code for user info
    user_info = await exchange_google_code_for_user_info(code, redirect_uri)

    # Create or get user
    user, token = auth_service.authenticate_or_create_oauth_user(
        email=user_info.get("email"),
        provider="google",
        provider_user_id=user_info.get("sub"),  # Google user ID
        name=user_info.get("name"),
        avatar_url=user_info.get("picture"),
    )

    return AuthResponse(user=user, token=token)

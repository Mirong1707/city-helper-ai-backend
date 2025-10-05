"""Authentication endpoints"""

from fastapi import APIRouter, Header

from app.core.config import settings

# Access config directly
config = settings.config
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, User
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


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

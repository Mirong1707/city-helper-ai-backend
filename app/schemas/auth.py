"""Authentication schemas"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request schema"""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request schema"""

    email: EmailStr
    password: str


class User(BaseModel):
    """User model"""

    id: str
    email: str
    name: str | None = None
    avatar_url: str | None = None
    auth_provider: str = "email"  # "email", "google", "apple"
    provider_user_id: str | None = None  # Google user ID, Apple user ID, etc.


class AuthResponse(BaseModel):
    """Authentication response with user and token"""

    user: User
    token: str

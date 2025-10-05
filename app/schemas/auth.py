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


class AuthResponse(BaseModel):
    """Authentication response with user and token"""

    user: User
    token: str

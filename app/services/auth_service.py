"""Authentication service"""

import random
import time

import structlog
from fastapi import HTTPException

from app.schemas.auth import User

logger = structlog.get_logger()


class AuthService:
    """Service for handling authentication logic"""

    def __init__(self):
        # In-memory storage (replace with DB in future)
        self.users_db: dict = {}
        self.sessions_db: dict = {}

    def login(self, email: str, password: str, delay: float = 0.5) -> tuple[User, str]:
        """
        Authenticate user and create session

        Args:
            email: User email
            password: User password
            delay: Network delay simulation

        Returns:
            Tuple of (User, token)
        """
        logger.debug("login_attempt", email=email)
        time.sleep(delay)

        user = User(id=f"user-{int(time.time() * 1000)}", email=email)

        token = self._generate_token()
        self.sessions_db[token] = user.model_dump()
        self.users_db[user.id] = {"user": user.model_dump(), "password": password}

        logger.info("login_success", user_id=user.id, email=email)
        return user, token

    def register(self, email: str, password: str, delay: float = 0.5) -> tuple[User, str]:
        """
        Register new user

        Args:
            email: User email
            password: User password
            delay: Network delay simulation

        Returns:
            Tuple of (User, token)

        Raises:
            HTTPException: If user already exists
        """
        time.sleep(delay)

        # Check if user exists
        existing_user = next(
            (u for u in self.users_db.values() if u["user"]["email"] == email), None
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        user = User(id=f"user-{int(time.time() * 1000)}", email=email)

        token = self._generate_token()
        self.sessions_db[token] = user.model_dump()
        self.users_db[user.id] = {"user": user.model_dump(), "password": password}

        return user, token

    def logout(self, token: str | None, delay: float = 0.2) -> None:
        """
        Logout user by removing session

        Args:
            token: Session token
            delay: Network delay simulation
        """
        time.sleep(delay)

        if token:
            self.sessions_db.pop(token, None)

    def get_current_user(self, token: str) -> User:
        """
        Get user by session token

        Args:
            token: Session token

        Returns:
            User object

        Raises:
            HTTPException: If session is invalid
        """
        user_data = self.sessions_db.get(token)

        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid session")

        return User(**user_data)

    @staticmethod
    def _generate_token() -> str:
        """Generate random session token"""
        return f"session-{int(time.time() * 1000)}-{random.randint(100000, 999999)}"

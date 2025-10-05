"""Environment-specific configurations"""

from enum import Enum

from pydantic import Field

from .base import BaseConfig


class Environment(str, Enum):
    """Supported application environments"""

    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LocalConfig(BaseConfig):
    """
    Local development configuration.

    - Auto-reload enabled
    - Debug logging
    - Permissive CORS
    - Fast response times
    """

    environment: Environment = Environment.LOCAL
    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"

    # Fast delays for development
    auth_delay: float = 0.1
    chat_delay: float = 0.5
    session_delay: float = 0.1


class DevelopmentConfig(BaseConfig):
    """
    Development environment configuration.

    - Similar to local but for shared dev server
    - More realistic delays
    - Still verbose logging
    """

    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"

    # Slightly more realistic delays
    auth_delay: float = 0.3
    chat_delay: float = 1.0
    session_delay: float = 0.2


class StagingConfig(BaseConfig):
    """
    Staging environment configuration.

    - Production-like settings
    - Less verbose logging
    - Real delays for testing
    """

    environment: Environment = Environment.STAGING
    debug: bool = False
    reload: bool = False
    log_level: str = "INFO"

    # Restricted CORS for staging
    cors_origins: list[str] = Field(
        default=[
            "https://staging.example.com",
            "http://localhost:5173",  # For local testing against staging
        ]
    )

    # Production-like delays
    auth_delay: float = 0.5
    chat_delay: float = 1.5
    session_delay: float = 0.3


class ProductionConfig(BaseConfig):
    """
    Production environment configuration.

    - Security hardened
    - Minimal logging
    - Strict CORS
    - No debug features
    """

    environment: Environment = Environment.PRODUCTION
    debug: bool = False
    reload: bool = False
    log_level: str = "WARNING"

    # Strict CORS for production
    cors_origins: list[str] = Field(default=["https://cityhelper.ai", "https://www.cityhelper.ai"])

    # Production delays
    auth_delay: float = 0.5
    chat_delay: float = 1.5
    session_delay: float = 0.3

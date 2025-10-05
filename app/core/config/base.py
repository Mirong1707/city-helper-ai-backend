"""Base configuration shared across all environments"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """
    Base configuration class with common settings.

    All environment-specific configs inherit from this.
    """

    # Application metadata
    app_name: str = Field(default="City Helper AI Backend", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    app_description: str = Field(
        default="Mock backend server for City Helper AI", description="Application description"
    )

    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=3001, ge=1, le=65535, description="Server port")
    reload: bool = Field(default=False, description="Enable auto-reload (development only)")

    # CORS settings
    cors_origins: list[str] = Field(default=["*"], description="Allowed CORS origins")
    cors_allow_credentials: bool = Field(
        default=True, description="Allow credentials in CORS requests"
    )
    cors_allow_methods: list[str] = Field(default=["*"], description="Allowed HTTP methods")
    cors_allow_headers: list[str] = Field(default=["*"], description="Allowed HTTP headers")

    # Network delays (for realistic testing)
    auth_delay: float = Field(default=0.5, ge=0.0, description="Authentication delay in seconds")
    chat_delay: float = Field(default=1.5, ge=0.0, description="Chat processing delay in seconds")
    session_delay: float = Field(
        default=0.3, ge=0.0, description="Session operation delay in seconds"
    )

    # Logging settings
    log_level: str = Field(
        default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_json: bool = Field(default=True, description="Output logs in JSON format")

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore unknown fields from .env
    )

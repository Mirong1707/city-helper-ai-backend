"""Secrets management with secure handling"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecretsConfig(BaseSettings):
    """
    Secure secrets configuration.

    Uses Pydantic's SecretStr to prevent accidental logging of sensitive data.
    Secrets are loaded from environment variables or .env file.
    """

    # Observability secrets
    logfire_token: SecretStr | None = Field(
        default=None, description="Logfire write token for cloud logging"
    )

    # Database secrets (for future use)
    database_url: SecretStr | None = Field(default=None, description="Database connection URL")
    database_password: SecretStr | None = Field(default=None, description="Database password")

    # API keys (for future use)
    openai_api_key: SecretStr | None = Field(
        default=None, description="OpenAI API key for AI features"
    )
    anthropic_api_key: SecretStr | None = Field(
        default=None, description="Anthropic API key for Claude"
    )

    # Authentication secrets
    jwt_secret_key: SecretStr | None = Field(default=None, description="JWT signing secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")

    # External service secrets (for future use)
    redis_url: SecretStr | None = Field(default=None, description="Redis connection URL")
    sentry_dsn: SecretStr | None = Field(default=None, description="Sentry DSN for error tracking")

    model_config = SettingsConfigDict(
        env_prefix="SECRET_",
        env_file=".env/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def get_logfire_token(self) -> str | None:
        """Get Logfire token as plain string (use carefully)"""
        return self.logfire_token.get_secret_value() if self.logfire_token else None

    def get_database_url(self) -> str | None:
        """Get database URL as plain string (use carefully)"""
        return self.database_url.get_secret_value() if self.database_url else None

    def get_jwt_secret(self) -> str | None:
        """Get JWT secret as plain string (use carefully)"""
        return self.jwt_secret_key.get_secret_value() if self.jwt_secret_key else None

    def has_logfire_token(self) -> bool:
        """Check if Logfire token is configured"""
        return self.logfire_token is not None

    def has_database_url(self) -> bool:
        """Check if database URL is configured"""
        return self.database_url is not None

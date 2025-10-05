"""Configuration loader with environment detection"""

import os
from functools import lru_cache

from .environments import (
    DevelopmentConfig,
    Environment,
    LocalConfig,
    ProductionConfig,
    StagingConfig,
)
from .secrets import SecretsConfig

ConfigType = LocalConfig | DevelopmentConfig | StagingConfig | ProductionConfig


@lru_cache
def get_settings() -> ConfigType:
    """
    Get application settings based on APP_ENV environment variable.

    Cached using lru_cache for performance - settings loaded once per app lifecycle.

    Environment precedence:
    1. Environment variables (APP_*)
    2. .env file
    3. Default values from config classes

    Returns:
        Environment-specific configuration instance
    """
    env = os.getenv("APP_ENV", Environment.LOCAL.value).lower()

    config_map = {
        Environment.LOCAL.value: LocalConfig,
        Environment.DEVELOPMENT.value: DevelopmentConfig,
        Environment.STAGING.value: StagingConfig,
        Environment.PRODUCTION.value: ProductionConfig,
    }

    config_class = config_map.get(env, LocalConfig)
    return config_class()


@lru_cache
def get_secrets() -> SecretsConfig:
    """
    Get secrets configuration.

    Cached using lru_cache for security - secrets loaded once.
    Uses SecretStr to prevent accidental logging.

    Returns:
        Secrets configuration instance
    """
    return SecretsConfig()


class Settings:
    """
    Unified settings accessor combining config and secrets.

    Usage:
        from app.core.config import settings

        # Access config
        print(settings.app_name)

        # Access secrets (use get_* methods)
        token = settings.secrets.get_logfire_token()
    """

    def __init__(self):
        self._config = get_settings()
        self._secrets = get_secrets()

    @property
    def config(self) -> ConfigType:
        """Get configuration"""
        return self._config

    @property
    def secrets(self) -> SecretsConfig:
        """Get secrets"""
        return self._secrets

    # Proxy commonly used config attributes
    @property
    def app_name(self) -> str:
        return self._config.app_name

    @property
    def app_version(self) -> str:
        return self._config.app_version

    @property
    def host(self) -> str:
        return self._config.host

    @property
    def port(self) -> int:
        return self._config.port

    @property
    def environment(self) -> Environment:
        return self._config.environment

    @property
    def debug(self) -> bool:
        return self._config.debug

    @property
    def log_level(self) -> str:
        return self._config.log_level

    # Convenience methods for secrets
    def get_logfire_token(self) -> str:
        """Get Logfire token (None-safe)"""
        return self._secrets.get_logfire_token() or ""

    def has_logfire(self) -> bool:
        """Check if Logfire is configured"""
        return self._secrets.has_logfire_token()

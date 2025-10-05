"""Configuration management module"""

from .loader import Settings

# Export main settings instance
settings = Settings()

__all__ = ["settings", "Settings"]

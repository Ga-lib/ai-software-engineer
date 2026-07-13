"""
Centralized application configuration.
Reads values from environment variables / .env file using Pydantic Settings.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings, loaded from environment variables."""

    app_name: str = "Multi-Agent AI Software Engineer"
    app_version: str = "0.1.0"
    debug: bool = False

    # LLM provider (wired up in a later step)
    groq_api_key: str = ""

    # Database (wired up in a later step)
    database_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    lru_cache ensures the .env file is only read once, not on every request.
    """
    return Settings()
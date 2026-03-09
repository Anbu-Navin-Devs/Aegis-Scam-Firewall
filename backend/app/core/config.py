"""
Application configuration management using Pydantic Settings.
Loads environment variables from .env file for secure credential management.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Core application settings loaded from environment variables.

    All sensitive credentials (API keys, database URLs) should be stored
    in a .env file that is excluded from version control.
    """

    # Google Gemini API Configuration
    GEMINI_API_KEY: str

    # Application metadata
    APP_NAME: str = "Aegis Scam Firewall API"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    DEBUG: bool = True

    # Future database/cache configuration
    # DATABASE_URL: str | None = None
    # REDIS_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance - imported throughout the application
settings = Settings()


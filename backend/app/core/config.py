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

    # PostgreSQL — must use the postgresql+asyncpg:// scheme for async engine.
    # ⚠️ Override in .env; the default targets a local dev database.
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aegis"

    # Application metadata
    APP_NAME: str = "Aegis Scam Firewall API"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance - imported throughout the application
settings = Settings()


"""
Application configuration, loaded from environment variables.
All secrets and environment-specific values live here — never hardcode
DB URLs, keys, or secrets anywhere else in the codebase.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    PROJECT_NAME: str = "MediTwin AI"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development | staging | production

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://meditwin:meditwin@localhost:5432/meditwin"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-.env-never-commit-this"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # External services (populated when those modules are built)
    GROQ_API_KEY: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — avoids re-reading .env on every call."""
    return Settings()


settings = get_settings()

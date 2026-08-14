"""Typed environment configuration."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "AutoResearchAI"
    APP_VERSION: str = "0.2.0"
    ENVIRONMENT: str = "development"
    OPENROUTER_API_KEY: str = Field(..., min_length=1)
    MODEL_NAME: str = "deepseek/deepseek-chat-v3-0324:free"
    TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0)
    MAX_TOKENS: int = Field(default=4096, gt=0, le=16384)
    LOG_LEVEL: str = "INFO"
    DATABASE_PATH: str = str(PROJECT_ROOT / "database" / "autoresearch.sqlite3")
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    LLM_TIMEOUT_SECONDS: float = Field(default=60, gt=0, le=300)
    LLM_MAX_RETRIES: int = Field(default=2, ge=0, le=5)

    @property
    def cors_origins(self):
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()

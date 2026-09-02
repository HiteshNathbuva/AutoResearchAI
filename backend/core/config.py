"""Typed environment configuration.

Settings are resolved lazily through :func:`get_settings` so that importing any
backend module never validates the environment or touches the filesystem.
"""

from functools import lru_cache
from pathlib import Path
from typing import List

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
    CORS_ORIGINS: str = "*"
    LLM_TIMEOUT_SECONDS: float = Field(default=60, gt=0, le=300)
    LLM_MAX_RETRIES: int = Field(default=2, ge=0, le=5)

    @property
    def cors_origins(self) -> List[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        # Allow wildcard to mean all origins. When "*" is present, FastAPI's
        # CORSMiddleware with allow_credentials=False will allow any origin.
        if "*" in origins:
            return ["*"]
        return origins

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings instance (cached).

    Importing this module has no side effects; the environment is validated on
    the first call, which happens during application startup or explicitly in
    tests.
    """

    return Settings()

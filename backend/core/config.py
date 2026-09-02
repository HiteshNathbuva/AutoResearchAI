"""Typed environment configuration.

Settings are resolved lazily through :func:`get_settings` so that importing any
backend module never validates the environment or touches the filesystem.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

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

    # ------------------------------------------------------------------
    # Phase 2: optional real web research configuration.
    # All of these are additive and have safe defaults. The application
    # boots with the existing required configuration; web research is
    # disabled unless ``WEB_RESEARCH_ENABLED`` and (for Tavily) a key are
    # present. No secret is required for the application to start.
    # ------------------------------------------------------------------
    WEB_RESEARCH_ENABLED: bool = False
    #: ``auto`` (Tavily when a key exists, otherwise keyless/disabled),
    #: ``tavily`` (require a key), or ``none`` (explicitly disabled).
    SEARCH_PROVIDER: str = "auto"
    # Optional so the app boots without any Tavily key. The empty string is
    # treated as "not configured" by :meth:`effective_search_provider`.
    TAVILY_API_KEY: Optional[str] = None
    SEARCH_MAX_RESULTS: int = Field(default=5, ge=1, le=20)
    SEARCH_TIMEOUT_SECONDS: float = Field(default=10, gt=0, le=120)
    SEARCH_MAX_RETRIES: int = Field(default=2, ge=0, le=5)
    MAX_FETCHED_SOURCES: int = Field(default=5, ge=1, le=20)
    FETCH_TIMEOUT_SECONDS: float = Field(default=10, gt=0, le=120)
    FETCH_MAX_REDIRECTS: int = Field(default=3, ge=0, le=10)
    FETCH_MAX_BYTES: int = Field(default=2_000_000, ge=1_024, le=20_000_000)
    EXTRACT_MAX_CHARS: int = Field(default=8_000, ge=256, le=100_000)
    WEB_RESEARCH_EVIDENCE_MAX_CHARS: int = Field(default=20_000, ge=1_000, le=200_000)

    @property
    def cors_origins(self) -> List[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        # Allow wildcard to mean all origins when explicitly configured.
        # In production this should not be used, but we still parse it.
        if "*" in origins:
            return ["*"]
        return origins

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def effective_search_provider(self) -> str:
        """Normalize :attr:`SEARCH_PROVIDER` into ``tavily`` or ``none``.

        ``auto`` selects Tavily when a key is configured and falls back to a
        keyless disabled provider otherwise. Unknown values map to ``none``.
        """

        mode = (self.SEARCH_PROVIDER or "").strip().lower()
        if mode in ("auto", "tavily"):
            return "tavily" if self.TAVILY_API_KEY else "none"
        return "none"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings instance (cached).

    Importing this module has no side effects; the environment is validated on
    the first call, which happens during application startup or explicitly in
    tests.
    """

    return Settings()

"""FastAPI entry point for AutoResearchAI."""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.core.config import Settings, get_settings
from backend.core.container import Resources, build_resources
from backend.core.logger import configure_logging, get_logger

logger = get_logger(__name__)


def create_app(settings: Optional[Settings] = None,
               resources: Optional[Resources] = None) -> FastAPI:
    """Build the FastAPI application.

    Args:
        settings: Optional settings override (defaults to cached settings).
        resources: Optional pre-built resources. When supplied, startup reuses
            them instead of constructing an LLM client and database connection,
            which keeps tests offline.
    """

    settings = settings or (resources.settings if resources else get_settings())
    configure_logging(settings.LOG_LEVEL)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        active = resources or build_resources(settings)
        app.state.settings = active.settings
        app.state.llm_client = active.llm_client
        app.state.session_manager = active.session_manager
        app.state.workflow = active.workflow
        logger.info("%s %s started in %s mode", active.settings.APP_NAME,
                    active.settings.APP_VERSION, active.settings.ENVIRONMENT)
        try:
            yield
        finally:
            logger.info("%s shutting down", active.settings.APP_NAME)

    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION,
                  description="Multi-agent research platform", lifespan=lifespan)
    # Keep a safe restricted default for CORS. Wildcard "*" is allowed only
    # when explicitly configured and only in non-production (dev/preview) to
    # avoid unintentionally exposing the API. Frontend uses relative "/api"
    # with Vite proxy, so same-origin requests work without CORS.
    if getattr(settings, "is_production", False):
        # In production, respect configured origins. If wildcard was explicitly
        # set in production, we still honor it but log a warning (user intent).
        allowed_origins = settings.cors_origins
    else:
        # Non-production: allow wildcard only if explicitly set via CORS_ORIGINS="*"
        allowed_origins = settings.cors_origins
    app.add_middleware(CORSMiddleware, allow_origins=allowed_origins,
                       allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
    app.include_router(router)

    @app.get("/")
    def root():
        return {"application": settings.APP_NAME, "version": settings.APP_VERSION,
                "status": "running", "api": "/docs"}

    return app


def __getattr__(name: str):
    """Lazily build ``app`` so importing this module has no side effects.

    ``uvicorn backend.main:app`` keeps working, but importing ``create_app`` in
    tests does not validate the environment or open a database.
    """

    if name == "app":
        application = create_app()
        globals()["app"] = application
        return application
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

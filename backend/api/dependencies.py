"""FastAPI dependency providers.

Application resources are created once during startup (see
``backend.main.lifespan``) and stored on ``app.state``. These providers expose
them to route handlers via ``Depends`` so tests can override them.
"""

from fastapi import Depends, Request

from backend.core.config import Settings, get_settings
from backend.core.llm import LLMClient
from backend.core.session import SessionManager
from backend.core.workflow import WorkflowOrchestrator


def get_settings_dependency() -> Settings:
    """Expose cached settings as a dependency."""

    return get_settings()


def get_llm_client(request: Request) -> LLMClient:
    """Return the shared LLM client created at startup."""

    return request.app.state.llm_client


def get_session_manager(request: Request) -> SessionManager:
    """Return the shared session manager created at startup."""

    return request.app.state.session_manager


def get_workflow(request: Request) -> WorkflowOrchestrator:
    """Return the shared workflow orchestrator created at startup."""

    return request.app.state.workflow


SettingsDep = Depends(get_settings_dependency)
LLMClientDep = Depends(get_llm_client)
SessionManagerDep = Depends(get_session_manager)
WorkflowDep = Depends(get_workflow)

"""Shared pytest fixtures.

Every fixture here is offline: no OpenRouter call is ever made, and no
environment variable from a developer's real ``.env`` is required.
"""

import os
from pathlib import Path

import pytest

# Settings are read on first access; make sure that happens against a
# deterministic, offline environment before any backend module is imported.
os.environ.setdefault("OPENROUTER_API_KEY", "test-key-not-a-real-secret")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "WARNING")

from backend.core.config import Settings  # noqa: E402
from backend.core.container import build_resources, build_workflow  # noqa: E402
from backend.core.session import SessionManager  # noqa: E402
from backend.core.state import WorkflowState  # noqa: E402

PLANNER_OUTPUT = "# Research Plan\n\n## Objective\nUnderstand the topic.\n"
RESEARCH_OUTPUT = "# Quick Summary\n\n- " + "fact " * 200
VERIFICATION_OUTPUT = (
    "# AI Fact Check Complete\n\nOverall Score: 8/10\n\nConfidence: High\n\n"
    "## Summary\nThe research is solid.\n"
)
REPORT_OUTPUT = "# Title\n\n## Executive Summary\n" + "word " * 400


class FakeLLMClient:
    """Offline stand-in for :class:`~backend.core.llm.LLMClient`.

    Responses are chosen from the system prompt so a single instance can serve
    all four agents, exactly like the real shared client.
    """

    def __init__(self, responses=None, error=None):
        self.responses = responses or {}
        self.error = error
        self.calls = []
        self.model = "fake-model"

    def chat(self, messages, model=None):
        self.calls.append({"messages": messages, "model": model})
        if self.error is not None:
            raise self.error

        system_prompt = messages[0]["content"] if messages else ""
        for key, value in self.responses.items():
            if key in system_prompt:
                return value

        if "Research Planning Agent" in system_prompt:
            return PLANNER_OUTPUT
        if "Research Agent" in system_prompt:
            return RESEARCH_OUTPUT
        if "Fact Check Agent" in system_prompt:
            return VERIFICATION_OUTPUT
        if "Report Generation Agent" in system_prompt:
            return REPORT_OUTPUT
        return "fake response"

    @property
    def call_count(self) -> int:
        return len(self.calls)


@pytest.fixture
def fake_llm() -> FakeLLMClient:
    return FakeLLMClient()


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    """Settings pointed at a temporary database."""

    return Settings(OPENROUTER_API_KEY="test-key-not-a-real-secret",
                    ENVIRONMENT="test", LOG_LEVEL="WARNING",
                    DATABASE_PATH=str(tmp_path / "test.sqlite3"))


@pytest.fixture
def session_manager(test_settings: Settings) -> SessionManager:
    return SessionManager(test_settings.DATABASE_PATH)


@pytest.fixture
def workflow(fake_llm: FakeLLMClient):
    return build_workflow(fake_llm)


@pytest.fixture
def resources(test_settings: Settings, fake_llm: FakeLLMClient, session_manager: SessionManager):
    return build_resources(settings=test_settings, llm_client=fake_llm,
                           session_manager=session_manager)


@pytest.fixture
def client(resources):
    """TestClient wired to offline resources, with lifespan executed."""

    from fastapi.testclient import TestClient

    from backend.main import create_app

    app = create_app(settings=resources.settings, resources=resources)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def researched_state() -> WorkflowState:
    """A state that has already completed planning and research."""

    state = WorkflowState()
    state.update_query("What is retrieval augmented generation?")
    state.update_plan(PLANNER_OUTPUT)
    state.add_research_note(RESEARCH_OUTPUT)
    state.mark_task_complete("Planner")
    state.mark_task_complete("Research")
    state.update_status("Research completed")
    return state

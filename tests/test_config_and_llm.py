"""Configuration caching, application wiring, and the LLM client contract.

The LLM client is exercised against an in-memory stub transport, so no
OpenRouter request is ever made.
"""

import pytest
from pydantic import ValidationError

from backend.core.config import Settings, get_settings
from backend.core.container import build_resources
from backend.core.exceptions import LLMError
from backend.core.llm import LLMClient


class _Message:
    def __init__(self, content):
        self.content = content


class _Choice:
    def __init__(self, content):
        self.message = _Message(content)


class _Completion:
    def __init__(self, content):
        self.choices = [_Choice(content)]


class StubCompletions:
    """Records calls and replays scripted responses/errors."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        result = self.responses.pop(0) if self.responses else _Completion("default")
        if isinstance(result, Exception):
            raise result
        return result


class StubOpenAI:
    def __init__(self, responses):
        self.chat = type("Chat", (), {"completions": StubCompletions(responses)})()

    @property
    def calls(self):
        return self.chat.completions.calls


def _settings(**overrides) -> Settings:
    base = {"OPENROUTER_API_KEY": "test-key-not-a-real-secret", "LLM_MAX_RETRIES": 0}
    base.update(overrides)
    return Settings(**base)


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

def test_get_settings_is_cached():
    assert get_settings() is get_settings()


def test_cors_origins_are_parsed():
    settings = _settings(CORS_ORIGINS="http://a.test, http://b.test ,")
    assert settings.cors_origins == ["http://a.test", "http://b.test"]


def test_api_key_is_required():
    with pytest.raises(ValidationError):
        Settings(OPENROUTER_API_KEY="", _env_file=None)


@pytest.mark.parametrize("field,value", [("TEMPERATURE", 2.5), ("TEMPERATURE", -0.1),
                                        ("MAX_TOKENS", 0), ("MAX_TOKENS", 99999),
                                        ("LLM_MAX_RETRIES", -1), ("LLM_TIMEOUT_SECONDS", 0)])
def test_numeric_fields_are_range_validated(field, value):
    with pytest.raises(ValidationError):
        _settings(**{field: value})


def test_importing_modules_has_no_side_effects():
    """Regression test: importing must not build settings or open a database."""

    import importlib

    for module in ["backend.core.llm", "backend.core.session", "backend.core.workflow",
                   "backend.api.routes", "backend.main"]:
        importlib.import_module(module)


# ----------------------------------------------------------------------
# LLM client
# ----------------------------------------------------------------------

def test_chat_returns_content():
    stub = StubOpenAI([_Completion("hello")])
    client = LLMClient(settings=_settings(), client=stub)

    assert client.chat([{"role": "user", "content": "hi"}]) == "hello"


def test_chat_sends_configured_parameters():
    stub = StubOpenAI([_Completion("hello")])
    settings = _settings(MODEL_NAME="model-x", TEMPERATURE=0.3, MAX_TOKENS=128)
    LLMClient(settings=settings, client=stub).chat([{"role": "user", "content": "hi"}])

    call = stub.calls[0]
    assert call["model"] == "model-x"
    assert call["temperature"] == 0.3
    assert call["max_tokens"] == 128


def test_per_call_model_override():
    stub = StubOpenAI([_Completion("hello")])
    LLMClient(settings=_settings(), client=stub).chat([{"role": "user", "content": "hi"}],
                                                      model="override")
    assert stub.calls[0]["model"] == "override"


def test_empty_response_raises_llm_error():
    stub = StubOpenAI([_Completion("")])
    with pytest.raises(LLMError):
        LLMClient(settings=_settings(), client=stub).chat([{"role": "user", "content": "hi"}])


def test_provider_errors_are_wrapped_in_llm_error():
    stub = StubOpenAI([RuntimeError("boom")])
    with pytest.raises(LLMError):
        LLMClient(settings=_settings(), client=stub).chat([{"role": "user", "content": "hi"}])


def test_retries_are_bounded_and_then_succeed(monkeypatch):
    monkeypatch.setattr("backend.core.llm.time.sleep", lambda _: None)
    stub = StubOpenAI([RuntimeError("boom"), _Completion("recovered")])
    client = LLMClient(settings=_settings(LLM_MAX_RETRIES=2), client=stub)

    assert client.chat([{"role": "user", "content": "hi"}]) == "recovered"
    assert len(stub.calls) == 2


def test_retries_stop_at_the_configured_limit(monkeypatch):
    monkeypatch.setattr("backend.core.llm.time.sleep", lambda _: None)
    stub = StubOpenAI([RuntimeError("a"), RuntimeError("b"), RuntimeError("c")])
    client = LLMClient(settings=_settings(LLM_MAX_RETRIES=2), client=stub)

    with pytest.raises(LLMError):
        client.chat([{"role": "user", "content": "hi"}])
    assert len(stub.calls) == 3


def test_switch_model():
    client = LLMClient(settings=_settings(), client=StubOpenAI([]))
    client.switch_model("  new-model  ")
    assert client.model == "new-model"

    with pytest.raises(ValueError):
        client.switch_model("")


# ----------------------------------------------------------------------
# Composition root
# ----------------------------------------------------------------------

def test_build_resources_shares_one_llm_client(test_settings, fake_llm, session_manager):
    resources = build_resources(settings=test_settings, llm_client=fake_llm,
                                session_manager=session_manager)
    workflow = resources.workflow
    agents = [workflow.planner_agent, workflow.research_agent,
              workflow.verifier_agent, workflow.writer_agent]

    assert all(agent.llm is fake_llm for agent in agents)
    assert len({id(agent.llm) for agent in agents}) == 1


def test_create_app_uses_injected_resources(resources):
    from fastapi.testclient import TestClient

    from backend.main import create_app

    app = create_app(settings=resources.settings, resources=resources)
    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200
        assert app.state.llm_client is resources.llm_client
        assert app.state.session_manager is resources.session_manager
        assert app.state.workflow is resources.workflow

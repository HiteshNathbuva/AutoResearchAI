"""API-level tests for Phase 2 source/diagnostic exposure and compatibility.

Everything is offline: fake LLM + fake search + fake fetcher.
"""

import tempfile

from fastapi.testclient import TestClient

from backend.core.config import Settings
from backend.core.container import build_resources
from backend.core.session import SessionManager
from backend.main import create_app
from backend.tools.web.models import FetchedContent, SearchResult
from backend.tools.web.search import SearchProvider
from backend.tools.web.service import WebResearchService


class FakeSearch(SearchProvider):
    name = "fake"

    def __init__(self, results=None):
        self.results = results or []

    def search(self, query, max_results=5):
        return self.results[:max_results]


class FakeFetcher:
    def fetch(self, url):
        return FetchedContent(
            url=url,
            content=b"<html><title>Title</title><p>Body</p></html>",
            content_type="text/html", status_code=200, final_url=url,
        )


def _make_app(*, web_enabled=True, search_results=None, tmp_path=None):
    tmp_path = tmp_path or tempfile.mkdtemp()
    settings = Settings(
        OPENROUTER_API_KEY="test-key", ENVIRONMENT="test", LOG_LEVEL="WARNING",
        DATABASE_PATH=str(tmp_path) + "/webtest.sqlite3",
        WEB_RESEARCH_ENABLED=web_enabled, _env_file=None,
    )
    session_manager = SessionManager(settings.DATABASE_PATH)
    from tests.conftest import FakeLLMClient

    fake_llm = FakeLLMClient()
    service = WebResearchService(
        settings=settings,
        search_provider=FakeSearch(search_results or []),
        fetcher=FakeFetcher(),
    )
    resources = build_resources(
        settings=settings, llm_client=fake_llm,
        session_manager=session_manager, web_research=service,
    )
    app = create_app(settings=settings, resources=resources)
    # Populate app.state the same way the lifespan would, so a bare TestClient
    # (used without the ``with`` context manager) still has the resources.
    app.state.settings = resources.settings
    app.state.llm_client = resources.llm_client
    app.state.session_manager = resources.session_manager
    app.state.workflow = resources.workflow
    return TestClient(app), fake_llm


def _client(tmp_path):
    return _make_app(tmp_path=tmp_path)[0]


def test_research_populates_sources(tmp_path):
    client, _ = _make_app(
        tmp_path=tmp_path,
        search_results=[SearchResult(title="Wiki", url="http://example.com/wiki", snippet="rag")],
    )
    response = client.post("/api/research", json={"query": "what is rag?"})
    assert response.status_code == 200
    body = response.json()
    assert body["sources"]
    assert body["sources"][0]["url"] == "http://example.com/wiki"
    assert body["sources"][0]["source_id"] == 1
    assert body["diagnostics"]["used_web"] is True
    assert "# Sources" in body["research"]


def test_research_empty_sources_on_fallback(tmp_path):
    # Web research enabled but no search results -> fallback -> empty sources.
    client, _ = _make_app(tmp_path=tmp_path, search_results=[])
    response = client.post("/api/research", json={"query": "what is rag?"})
    assert response.status_code == 200
    body = response.json()
    assert body["sources"] == []
    assert body["diagnostics"]["used_web"] is False


def test_research_web_disabled_empty_sources(tmp_path):
    client, _ = _make_app(tmp_path=tmp_path, web_enabled=False, search_results=[SearchResult("x", "http://a.example/")])
    response = client.post("/api/research", json={"query": "what is rag?"})
    assert response.status_code == 200
    body = response.json()
    assert body["sources"] == []
    assert body["diagnostics"]["tool_mode"] == "disabled"


def test_existing_status_codes_preserved(tmp_path):
    client, _ = _make_app(tmp_path=tmp_path)
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/sessions").status_code == 200
    assert client.get("/api/sessions/missing").status_code == 404
    assert client.post("/api/research", json={"query": "ab"}).status_code == 422


def test_verify_and_report_still_work_with_sources(tmp_path):
    client, _ = _make_app(
        tmp_path=tmp_path,
        search_results=[SearchResult("Wiki", "http://example.com/wiki", "rag")],
    )
    session_id = client.post("/api/research", json={"query": "rag"}).json()["session_id"]
    assert client.post(f"/api/verify/{session_id}").status_code == 200
    assert client.post(f"/api/report/{session_id}").status_code == 200
    session = client.get(f"/api/sessions/{session_id}").json()
    assert session["report"]
    # Sources survive through the whole session round-trip.
    assert session["sources"]


def test_openapi_schema_remains_valid_and_includes_sources(tmp_path):
    client = _client(tmp_path)
    schema = client.get("/openapi.json").json()
    assert schema["openapi"]
    session_model = schema["components"]["schemas"]["SessionResponse"]["properties"]
    assert "sources" in session_model
    assert "diagnostics" in session_model


def test_get_session_response_includes_sources(tmp_path):
    client, _ = _make_app(
        tmp_path=tmp_path,
        search_results=[SearchResult("Wiki", "http://example.com/wiki", "rag")],
    )
    session_id = client.post("/api/research", json={"query": "rag"}).json()["session_id"]
    persisted = client.get(f"/api/sessions/{session_id}").json()
    assert persisted["sources"]
    assert persisted["diagnostics"]

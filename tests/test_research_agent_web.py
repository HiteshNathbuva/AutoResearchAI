"""ResearchAgent web-research integration tests.

All web traffic is faked: search providers and fetchers are injected, and the
LLM is a fake. No real network access.
"""

import pytest

from backend.agents.research_agent import WEB_EVIDENCE_CLOSE, WEB_EVIDENCE_OPEN, ResearchAgent
from backend.core.exceptions import LLMError
from backend.core.state import WorkflowState
from backend.tools.web.models import FetchedContent, ResearchOutcome, SearchResult, WebSource
from backend.tools.web.search import SearchError, SearchProvider
from backend.tools.web.service import WebResearchService


class FakeLLM:
    def __init__(self, response="RESEARCH OUTPUT", error=None):
        self.response = response
        self.error = error
        self.calls = []

    def chat(self, messages, model=None):
        self.calls.append({"messages": messages, "model": model})
        if self.error is not None:
            raise self.error
        return self.response


class FakeSearch(SearchProvider):
    name = "fake"

    def __init__(self, results=None, error=None):
        self.results = results or []
        self.error = error

    def search(self, query, max_results=5):
        if self.error is not None:
            raise self.error
        return self.results[:max_results]


class FakeFetcher:
    def __init__(self, error=None, content=None, content_type="text/html"):
        self.error = error
        # No <title> so the search result's title is preferred as the source title.
        self.content = content if content is not None else b"<html><body><p>Evidence body</p></body></html>"
        self.content_type = content_type

    def fetch(self, url):
        if self.error is not None:
            raise self.error
        return FetchedContent(
            url=url, content=self.content, content_type=self.content_type,
            status_code=200, final_url=url,
        )


def _web_search_result(url="http://example.com/page", title="Page Title"):
    return SearchResult(title=title, url=url, snippet="About the topic")


def _state(query="what is RAG?"):
    state = WorkflowState()
    state.update_query(query)
    state.update_plan("# Research Plan\n\n## Objective\nUnderstand RAG.")
    return state


def _make_agent(llm, service):
    return ResearchAgent(llm=llm, web_research=service)


def _service(*, search_results=None, search_error=None, fetch_error=None,
             enabled=True, settings_overrides=None):
    from backend.core.config import Settings
    settings = Settings(OPENROUTER_API_KEY="k", _env_file=None, WEB_RESEARCH_ENABLED=enabled,
                        **(settings_overrides or {}))
    search = FakeSearch(results=search_results or [], error=search_error)
    fetcher = FakeFetcher(error=fetch_error)
    return WebResearchService(settings=settings, search_provider=search, fetcher=fetcher)


def test_real_evidence_path_uses_web_context():
    llm = FakeLLM()
    service = _service(search_results=[_web_search_result()])
    agent = _make_agent(llm, service)

    agent.execute(_state())

    user_content = llm.calls[0]["messages"][1]["content"]
    assert WEB_EVIDENCE_OPEN in user_content
    assert WEB_EVIDENCE_CLOSE in user_content
    assert "Page Title" in user_content
    assert "http://example.com/page" in user_content
    # The security notice is present.
    assert "UNTRUSTED" in user_content


def test_sources_are_persisted_in_state():
    llm = FakeLLM()
    service = _service(search_results=[_web_search_result()])
    agent = _make_agent(llm, service)

    state = agent.execute(_state())

    assert len(state.sources) == 1
    source = state.sources[0]
    assert source["url"] == "http://example.com/page"
    assert source["source_id"] == 1


def test_research_output_contains_deterministic_citations():
    llm = FakeLLM()
    service = _service(search_results=[
        _web_search_result("http://a.example/", "A"),
        _web_search_result("http://b.example/", "B"),
    ])
    agent = _make_agent(llm, service)

    state = agent.execute(_state())

    assert "# Sources" in state.research
    assert "[1] A — http://a.example/" in state.research
    assert "[2] B — http://b.example/" in state.research
    assert state.sources[0]["source_id"] == 1
    assert state.sources[1]["source_id"] == 2


def test_search_failure_falls_back_to_llm_only():
    llm = FakeLLM()
    service = _service(search_error=SearchError("search down"))
    agent = _make_agent(llm, service)

    state = agent.execute(_state())

    user_content = llm.calls[0]["messages"][1]["content"]
    assert WEB_EVIDENCE_OPEN not in user_content
    assert state.sources == []
    assert state.diagnostics["search_status"] == "failed"
    # research still produced by the LLM
    assert state.research == "RESEARCH OUTPUT"


def test_fetch_failure_falls_back_to_llm_only():
    llm = FakeLLM()
    service = _service(search_results=[_web_search_result()], fetch_error=Exception("boom"))
    agent = _make_agent(llm, service)

    state = agent.execute(_state())

    user_content = llm.calls[0]["messages"][1]["content"]
    assert WEB_EVIDENCE_OPEN not in user_content
    assert state.sources == []


def test_zero_results_falls_back_to_llm_only():
    llm = FakeLLM()
    service = _service(search_results=[])
    agent = _make_agent(llm, service)

    state = agent.execute(_state())

    user_content = llm.calls[0]["messages"][1]["content"]
    assert WEB_EVIDENCE_OPEN not in user_content
    assert state.sources == []
    assert state.research == "RESEARCH OUTPUT"


def test_all_fetches_fail_falls_back_to_llm_only():
    llm = FakeLLM()
    service = _service(
        search_results=[_web_search_result("http://a.example/"), _web_search_result("http://b.example/")],
        fetch_error=Exception("connection refused"),
    )
    agent = _make_agent(llm, service)

    state = agent.execute(_state())

    user_content = llm.calls[0]["messages"][1]["content"]
    assert WEB_EVIDENCE_OPEN not in user_content
    assert state.sources == []
    # diagnostics record fetch failures and no usable source
    assert state.diagnostics["used_web"] is False


def test_web_research_disabled_falls_back_to_llm_only():
    llm = FakeLLM()
    service = _service(enabled=False, search_results=[_web_search_result()])
    agent = _make_agent(llm, service)

    state = agent.execute(_state())

    user_content = llm.calls[0]["messages"][1]["content"]
    assert "User Query" in user_content
    assert WEB_EVIDENCE_OPEN not in user_content
    assert state.sources == []
    assert state.diagnostics["tool_mode"] == "disabled"


def test_no_web_research_injected_is_llm_only():
    llm = FakeLLM()
    agent = ResearchAgent(llm=llm)  # no web_research
    state = agent.execute(_state())

    user_content = llm.calls[0]["messages"][1]["content"]
    assert WEB_EVIDENCE_OPEN not in user_content
    assert state.sources == []
    assert state.diagnostics == {}


def test_llm_failure_still_propagates():
    llm = FakeLLM(error=LLMError("provider down"))
    agent = ResearchAgent(llm=llm)
    with pytest.raises(LLMError):
        agent.execute(_state())


def test_web_tool_failure_still_calls_llm_on_fallback():
    """A web-tool crash must not become an LLM/no-op failure."""

    class ExplodingService:
        def research(self, query, plan):
            raise RuntimeError("web service exploded")

    llm = FakeLLM()
    agent = ResearchAgent(llm=llm, web_research=ExplodingService())

    state = agent.execute(_state())
    assert state.research == "RESEARCH OUTPUT"
    assert state.sources == []
    assert state.diagnostics["tool_mode"] == "error"


def test_sources_section_only_added_when_web_used():
    llm = FakeLLM()
    service = _service(enabled=False)
    agent = _make_agent(llm, service)
    state = agent.execute(_state())
    assert "# Sources" not in state.research


def test_research_outcome_directly_used():
    outcome = ResearchOutcome(
        used_web=True,
        sources=[WebSource(source_id=1, url="http://x.example/", title="X")],
        evidence="[1] X\nURL: http://x.example/",
        diagnostics={"used_web": True},
    )
    assert outcome.used_web is True
    assert outcome.diagnostics["used_web"] is True

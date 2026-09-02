"""Offline search provider tests. No real Tavily / search engine requests."""

import httpx
import pytest

from backend.core.config import Settings
from backend.tools.web.search import (
    NullSearchProvider,
    SearchError,
    TavilySearchProvider,
    create_search_provider,
)

ENDPOINT = "https://api.tavily.com/search"


def _client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler), trust_env=False)


def _search_response(items):
    return httpx.Response(200, json={"results": items})


def test_provider_success():
    def handler(request):
        assert request.url == ENDPOINT
        assert request.headers["Authorization"].startswith("Bearer ")
        body = request.read()
        assert b"query" in body
        return _search_response([
            {"title": "Result One", "url": "https://a.example", "content": "snippet a"},
            {"title": "Result Two", "url": "https://b.example", "content": "snippet b"},
        ])

    provider = TavilySearchProvider("tvly-test-key", client=_client(handler), max_retries=0)
    results = provider.search("hello", max_results=5)
    assert len(results) == 2
    assert results[0].title == "Result One"
    assert results[0].url == "https://a.example"
    assert results[0].snippet == "snippet a"
    assert provider.name == "tavily"


def test_provider_failure_raises_search_error():
    def handler(request):
        return httpx.Response(500, text="server error")

    provider = TavilySearchProvider("tvly-key", client=_client(handler), max_retries=0)
    with pytest.raises(SearchError):
        provider.search("hello")


def test_provider_timeout_raises_search_error():
    def handler(request):
        raise httpx.ReadTimeout("timed out")

    provider = TavilySearchProvider("tvly-key", client=_client(handler), max_retries=0)
    with pytest.raises(SearchError):
        provider.search("hello")


def test_provider_malformed_response_raises_search_error():
    def handler(request):
        return httpx.Response(200, text="not-json")

    provider = TavilySearchProvider("tvly-key", client=_client(handler), max_retries=0)
    with pytest.raises(SearchError):
        provider.search("hello")


def test_provider_empty_results_returns_empty_list():
    def handler(request):
        return _search_response([])

    provider = TavilySearchProvider("tvly-key", client=_client(handler), max_retries=0)
    assert provider.search("nothing") == []


def test_bounded_retry_then_succeed():
    attempts = {"count": 0}

    def handler(request):
        attempts["count"] += 1
        if attempts["count"] < 3:
            return httpx.Response(500, text="boom")
        return _search_response([{"title": "ok", "url": "https://ok.example", "content": "s"}])

    provider = TavilySearchProvider("tvly-key", client=_client(handler), max_retries=2)
    results = provider.search("hello")
    assert attempts["count"] == 3
    assert len(results) == 1


def test_bounded_retry_stops_at_limit():
    attempts = {"count": 0}

    def handler(request):
        attempts["count"] += 1
        return httpx.Response(500, text="always down")

    provider = TavilySearchProvider("tvly-key", client=_client(handler), max_retries=2)
    with pytest.raises(SearchError):
        provider.search("hello")
    assert attempts["count"] == 3  # 1 initial + 2 retries


def test_api_key_never_appears_in_error_or_results():
    def handler(request):
        return httpx.Response(500, text="boom")

    provider = TavilySearchProvider("tvly-supersecret", client=_client(handler), max_retries=0)
    with pytest.raises(SearchError) as exc:
        provider.search("hello")
    assert "tvly-supersecret" not in str(exc.value)


def test_null_provider_returns_nothing():
    provider = NullSearchProvider()
    assert provider.search("anything") == []
    assert provider.name == "none"


def _settings(**overrides):
    base = {"OPENROUTER_API_KEY": "test-key", "_env_file": None}
    base.update(overrides)
    return Settings(**base)


def test_provider_selection_auto_with_key_is_tavily():
    settings = _settings(SEARCH_PROVIDER="auto", TAVILY_API_KEY="tvly-key")
    provider = create_search_provider(settings)
    assert isinstance(provider, TavilySearchProvider)


def test_provider_selection_auto_without_key_is_null():
    settings = _settings(SEARCH_PROVIDER="auto")
    provider = create_search_provider(settings)
    assert isinstance(provider, NullSearchProvider)


def test_provider_selection_explicit_tavily_without_key_falls_back_to_null():
    settings = _settings(SEARCH_PROVIDER="tavily")
    provider = create_search_provider(settings)
    assert isinstance(provider, NullSearchProvider)


def test_provider_selection_none_is_null():
    settings = _settings(SEARCH_PROVIDER="none", TAVILY_API_KEY="tvly-key")
    provider = create_search_provider(settings)
    assert isinstance(provider, NullSearchProvider)


def test_provider_selection_unknown_is_null():
    settings = _settings(SEARCH_PROVIDER="weird")
    provider = create_search_provider(settings)
    assert isinstance(provider, NullSearchProvider)

"""Search provider abstraction.

Providers are intentionally conservative:

* bounded result count
* timeout handling
* bounded retries
* API keys never appear in logs, prompts, diagnostics, or returned data
* provider failures are surfaced as :class:`SearchError` so the caller can fall
  back to LLM-only research instead of failing the whole request
"""

from typing import List, Optional

import httpx

from backend.core.config import Settings
from backend.tools.web.models import SearchResult

__all__ = [
    "SearchError",
    "SearchProvider",
    "TavilySearchProvider",
    "NullSearchProvider",
    "create_search_provider",
]

_TAVILY_ENDPOINT = "https://api.tavily.com/search"


class SearchError(Exception):
    """Raised when a search provider cannot complete a search."""


class SearchProvider:
    """Base class for search providers. Subclasses implement :meth:`search`."""

    name = "unknown"

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:  # noqa: ARG002
        """Return up to ``max_results`` results, or raise :class:`SearchError`."""

        raise NotImplementedError


class NullSearchProvider(SearchProvider):
    """Keyless, no-op provider used when search is disabled/unavailable.

    It never produces results, which keeps the "web research disabled" path
    deterministic and offline.
    """

    name = "none"

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        return []


class TavilySearchProvider(SearchProvider):
    """Search provider backed by the Tavily Search API."""

    name = "tavily"

    def __init__(
        self,
        api_key: str,
        *,
        client: Optional[httpx.Client] = None,
        timeout: float = 10.0,
        max_retries: int = 2,
    ) -> None:
        if not api_key:
            raise ValueError("TavilySearchProvider requires an API key")
        self.api_key = api_key
        self._client = client or httpx.Client(
            trust_env=False, timeout=httpx.Timeout(timeout)
        )
        self.timeout = timeout
        self.max_retries = max_retries
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        payload = {
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_answer": False,
            "include_raw_content": False,
        }
        last_error: Optional[BaseException] = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.post(
                    _TAVILY_ENDPOINT, json=payload, headers=self._headers
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("results") or []
                return [
                    SearchResult(
                        title=str(item.get("title", "") or ""),
                        url=str(item.get("url", "") or ""),
                        snippet=str(item.get("content", "") or ""),
                        domain=str(item.get("domain", "") or ""),
                    )
                    for item in results
                ]
            except (httpx.HTTPError, ValueError) as error:
                last_error = error
                if attempt >= self.max_retries:
                    raise SearchError(
                        f"{self.name} search failed: {error}"
                    ) from error
        raise SearchError(f"{self.name} search failed") from last_error


def create_search_provider(settings: Settings, client: Optional[httpx.Client] = None) -> SearchProvider:
    """Build a provider from configuration.

    ``auto`` uses Tavily when a key is configured and otherwise the keyless
    null provider. ``tavily`` requires a key (falling back to null when the key
    is missing so a misconfigured deployment stays offline rather than crashing).
    ``none`` always yields a null provider.
    """

    mode = settings.effective_search_provider
    if mode == "tavily":
        return TavilySearchProvider(
            settings.TAVILY_API_KEY,  # type: ignore[arg-type]  # guaranteed by effective_search_provider
            client=client,
            timeout=settings.SEARCH_TIMEOUT_SECONDS,
            max_retries=settings.SEARCH_MAX_RETRIES,
        )
    return NullSearchProvider()

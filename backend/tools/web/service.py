"""Web research orchestration service.

This service runs a single, bounded research pass:

1. search (bounded, provider-agnostic)
2. safe fetch a bounded number of results
3. extract text
4. collect sources + evidence

It never fails the whole request: every failure is recorded in ``diagnostics``
and, when no usable source is found, the caller is told via ``used_web=False``
to fall back to the existing LLM-only research.
"""

from typing import Any, Dict, List, Optional

from backend.core.config import Settings
from backend.tools.web.fetch import SafeFetcher
from backend.tools.web.models import ResearchOutcome, SearchResult, WebSource
from backend.tools.web.search import SearchError, SearchProvider, create_search_provider
from backend.tools.web.sources import SourceRegistry

__all__ = ["WebResearchService", "build_web_research"]

#: Maximum length of a synthesized search query derived from the user query.
_SEARCH_QUERY_MAX_CHARS = 220


def _derive_search_query(query: str, plan: str = "") -> str:
    """Derive a single, conservative search query from the user query.

    We deliberately run ONE search per research request (not one per plan
    section) to keep the request bounded. If the query is short we use it as-is;
    otherwise we use the first sentence so we never send a huge blob to search.
    """

    text = (query or "").strip()
    if not text:
        # Fall back to the plan objective if present.
        for line in (plan or "").splitlines():
            if line.strip().lower().startswith("objective"):
                return line.split(":", 1)[-1].strip().strip(".")[:_SEARCH_QUERY_MAX_CHARS]
        return ""
    # Short queries go through unchanged (bounded length).
    if len(text) <= _SEARCH_QUERY_MAX_CHARS:
        return text
    # Otherwise use the first sentence.
    for separator in (".", "!", "?", "\n"):
        cut = text.find(separator)
        if 0 < cut <= _SEARCH_QUERY_MAX_CHARS:
            return text[:cut].strip()
    return text[:_SEARCH_QUERY_MAX_CHARS]


class WebResearchService:
    """Bound the whole web-research pass for one research request."""

    def __init__(
        self,
        settings: Settings,
        search_provider: Optional[SearchProvider] = None,
        fetcher: Optional[SafeFetcher] = None,
    ) -> None:
        self.settings = settings
        self.search_provider = search_provider or create_search_provider(settings)
        self.fetcher = fetcher or SafeFetcher(
            timeout=settings.FETCH_TIMEOUT_SECONDS,
            max_redirects=settings.FETCH_MAX_REDIRECTS,
            max_bytes=settings.FETCH_MAX_BYTES,
        )

    @property
    def enabled(self) -> bool:
        return bool(self.settings.WEB_RESEARCH_ENABLED)

    def _diagnostics(self, **overrides: Any) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "web_research_enabled": self.enabled,
            "tool_mode": "enabled" if self.enabled else "disabled",
            "search_provider": self.search_provider.name,
            "search_status": "not_performed",
            "search_results_count": 0,
            "fetch_attempts": 0,
            "fetch_successes": 0,
            "fetch_errors": [],
            "source_count": 0,
            "used_web": False,
        }
        payload.update(overrides)
        return payload

    def research(self, query: str, plan: str = "") -> ResearchOutcome:
        """Run a single bounded web-research pass.

        Returns :class:`ResearchOutcome`. ``used_web`` is ``True`` only when at
        least one source was successfully fetched and extracted.
        """

        if not self.enabled:
            return ResearchOutcome(
                used_web=False,
                sources=[],
                evidence="",
                diagnostics=self._diagnostics(search_status="not_performed"),
            )

        diagnostics = self._diagnostics()

        search_query = _derive_search_query(query, plan)
        if not search_query:
            diagnostics["search_status"] = "failed"
            diagnostics["search_errors"] = ["no usable search query derived"]
            return ResearchOutcome(
                used_web=False, sources=[], evidence="", diagnostics=diagnostics
            )

        # 1. Search (bounded). Provider failures never crash the request.
        try:
            results = self.search_provider.search(
                search_query, max_results=self.settings.SEARCH_MAX_RESULTS
            )
            diagnostics["search_status"] = "success"
            diagnostics["search_results_count"] = len(results)
        except SearchError as error:
            diagnostics["search_status"] = "failed"
            diagnostics["search_errors"] = [str(error)]
            return ResearchOutcome(
                used_web=False, sources=[], evidence="", diagnostics=diagnostics
            )
        except Exception as error:  # noqa: BLE001 - defensive: never crash request
            diagnostics["search_status"] = "failed"
            diagnostics["search_errors"] = [str(error)]
            return ResearchOutcome(
                used_web=False, sources=[], evidence="", diagnostics=diagnostics
            )

        # 2. Fetch a bounded number of sources.
        registry = SourceRegistry()
        fetch_attempts = 0
        fetch_successes = 0
        fetch_errors: List[str] = []
        for result in results[: self.settings.MAX_FETCHED_SOURCES]:
            if not self._result_url_ok(result):
                continue
            fetch_attempts += 1
            try:
                fetched = self.fetcher.fetch(result.url)
                extracted = _extract_page_content(
                    fetched.content,
                    fetched.content_type,
                    max_chars=self.settings.EXTRACT_MAX_CHARS,
                )
                snippet = result.snippet or (extracted.text[:240] if extracted.text else "")
                registry.add(
                    url=fetched.final_url,
                    title=extracted.title or result.title,
                    snippet=snippet,
                    status="fetched",
                    content_type=fetched.content_type,
                    text_excerpt=extracted.text,
                )
                fetch_successes += 1
            except Exception as error:  # noqa: BLE001 - per-source isolation
                fetch_errors.append(str(error))

        diagnostics["fetch_attempts"] = fetch_attempts
        diagnostics["fetch_successes"] = fetch_successes
        diagnostics["fetch_errors"] = fetch_errors[:20]
        diagnostics["source_count"] = len(registry)

        sources = registry.all()
        if not sources:
            diagnostics["used_web"] = False
            diagnostics["search_status"] = diagnostics.get("search_status", "failed")
            return ResearchOutcome(
                used_web=False, sources=[], evidence="", diagnostics=diagnostics
            )

        evidence = self._build_evidence(sources)
        diagnostics["used_web"] = True
        return ResearchOutcome(
            used_web=True, sources=sources, evidence=evidence, diagnostics=diagnostics
        )

    @staticmethod
    def _result_url_ok(result: SearchResult) -> bool:
        """Cheap pre-filter before the fetcher (which is the SSRF gate).

        We deliberately do NOT resolve the hostname here (that would require
        DNS and make tests network-dependent). The authoritative
        :class:`SafeFetcher` validates every URL — and every redirect — against
        the SSRF blocklist before any connection.
        """

        from urllib.parse import urlsplit

        url = (result.url or "").strip()
        if not url:
            return False
        parts = urlsplit(url)
        if (parts.scheme or "").lower() not in ("http", "https"):
            return False
        return bool(parts.hostname)

    @staticmethod
    def _build_evidence(sources: List[WebSource]) -> str:
        """Render delimited, untrusted evidence text for the LLM context."""

        blocks: List[str] = []
        for source in sources:
            lines = [f"[{source.source_id}] {source.title or source.url}"]
            lines.append(f"URL: {source.url}")
            lines.append(f"Domain: {source.domain}")
            if source.snippet:
                lines.append(f"Snippet: {source.snippet}")
            blocks.append("\n".join(lines))
        return "\n\n".join(blocks)


def _extract_page_content(content: bytes, content_type: str, max_chars: int):
    """Lazy import to keep module import side-effect free and avoid cycles."""

    from backend.tools.web.extract import extract_page

    return extract_page(content, content_type, max_chars=max_chars)


def build_web_research(settings: Settings) -> WebResearchService:
    """Build a :class:`WebResearchService` from configuration."""

    return WebResearchService(settings=settings)

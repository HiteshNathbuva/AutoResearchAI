"""Real web research tool layer.

This package provides deterministic, offline-testable building blocks for
searching the web, fetching pages safely, extracting content, and tracking
sources, as well as a small orchestration service used by the ResearchAgent.

Public surface (kept intentionally small):

* :class:`~backend.tools.web.security.validate_url` / ``is_safe_url`` — SSRF checks
* :class:`~backend.tools.web.fetch.SafeFetcher` — the only fetch entry point
* :class:`~backend.tools.web.search.create_search_provider` — provider factory
* :class:`~backend.tools.web.service.WebResearchService` — bounded research pass
"""

from backend.tools.web.fetch import SafeFetcher
from backend.tools.web.models import (
    ExtractedContent,
    FetchedContent,
    ResearchOutcome,
    SearchResult,
    WebSource,
)
from backend.tools.web.search import (
    NullSearchProvider,
    SearchError,
    SearchProvider,
    TavilySearchProvider,
    create_search_provider,
)
from backend.tools.web.security import (
    UnsafeURLError,
    is_public_ip,
    is_safe_url,
    validate_url,
)
from backend.tools.web.service import WebResearchService, build_web_research
from backend.tools.web.sources import SourceRegistry, render_sources_section

__all__ = [
    "SafeFetcher",
    "ExtractedContent",
    "FetchedContent",
    "ResearchOutcome",
    "SearchResult",
    "WebSource",
    "NullSearchProvider",
    "SearchError",
    "SearchProvider",
    "TavilySearchProvider",
    "create_search_provider",
    "UnsafeURLError",
    "is_safe_url",
    "is_public_ip",
    "validate_url",
    "WebResearchService",
    "build_web_research",
    "SourceRegistry",
    "render_sources_section",
]

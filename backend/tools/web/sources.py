"""Deterministic source tracking and citation rendering.

The source registry is responsible for assigning stable, deterministic citation
IDs (``[1]``, ``[2]``, ...), de-duplicating URLs, and rendering the ``Sources``
section. The LLM never chooses the source list — application code always does,
so the cited sources are the sources that were actually consulted.
"""

from typing import Dict, List, Optional

from backend.tools.web.models import WebSource, domain_of, normalize_url, utc_now_iso

__all__ = ["SourceRegistry", "render_sources_section", "SOURCES_HEADER"]

SOURCES_HEADER = "# Sources"


class SourceRegistry:
    """Collect de-duplicated sources with deterministic, 1-based IDs."""

    def __init__(self) -> None:
        self._sources: List[WebSource] = []
        self._by_url: Dict[str, WebSource] = {}

    def add(
        self,
        *,
        url: str,
        title: str = "",
        snippet: str = "",
        domain: str = "",
        status: str = "fetched",
        content_type: str = "",
        text_excerpt: str = "",
    ) -> Optional[WebSource]:
        """Register a source, de-duplicating by normalized URL.

        Returns the (new or existing) source when the URL is usable and is in
        a fetchable scheme; otherwise returns ``None``.
        """

        normalized = normalize_url(url)
        if not normalized:
            return None
        existing = self._by_url.get(normalized)
        if existing is not None:
            # Keep richer metadata if a later fetch found more than the first.
            if not existing.snippet and snippet:
                existing.snippet = snippet
                self._sources[self._sources.index(existing)] = existing
            return existing

        source = WebSource(
            source_id=len(self._sources) + 1,
            url=normalized,
            title=title or "",
            domain=domain or domain_of(normalized),
            snippet=snippet or "",
            status=status,
            retrieved_at=utc_now_iso(),
            content_type=content_type or "",
            text_excerpt=(text_excerpt or "")[:1200],
        )
        self._sources.append(source)
        self._by_url[normalized] = source
        return source

    def all(self) -> List[WebSource]:
        """Return sources in insertion (citation) order."""

        return list(self._sources)

    def __len__(self) -> int:
        return len(self._sources)

    def render(self) -> str:
        """Render the ``Sources`` section body (without the header)."""

        lines: List[str] = []
        for source in self._sources:
            title = source.title or source.url
            lines.append(f"[{source.source_id}] {title} — {source.url}")
        return "\n".join(lines)


def render_sources_section(sources: List[WebSource]) -> str:
    """Render a full ``# Sources`` markdown section for a list of sources."""

    if not sources:
        return ""
    body = "\n".join(
        f"[{source.source_id}] {source.title or source.url} — {source.url}"
        for source in sources
    )
    return f"{SOURCES_HEADER}\n\n{body}"

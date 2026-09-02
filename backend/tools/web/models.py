"""Typed data models for the web research tool layer.

These are plain dataclasses with explicit :meth:`to_dict` / :meth:`from_dict`
conversions so they can live inside the JSON-backed :class:`WorkflowState`
without pulling a framework into the tool layer.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urlsplit


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""

    return datetime.now(timezone.utc).isoformat()


def domain_of(url: str) -> str:
    """Return the lowercase hostname of a URL, or an empty string."""

    try:
        host = urlsplit(url or "").hostname or ""
    except ValueError:
        return ""
    return host.strip().lower()


def normalize_url(url: str) -> str:
    """Normalize a URL for stable de-duplication.

    Lowercases the scheme and host, strips a trailing dot from the host (FQDN
    form), and removes the URL fragment which is never part of the document.
    """

    if not url:
        return ""
    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return url.strip()
    scheme = (parts.scheme or "").lower()
    host = (parts.hostname or "").strip().rstrip(".").lower()
    if not host:
        return url.strip()
    # Rebuild from components so default port is dropped and userinfo is
    # removed (userinfo is rejected earlier by the security validator anyway).
    netloc = host
    if parts.port:
        default_port = 443 if scheme == "https" else 80
        if parts.port != default_port:
            netloc = f"{host}:{parts.port}"
    path = parts.path or ""
    query = parts.query or ""
    rebuilt = f"{scheme}://{netloc}{path}"
    if query:
        rebuilt = f"{rebuilt}?{query}"
    return rebuilt


@dataclass
class SearchResult:
    """A single search-engine result, before any content is fetched."""

    title: str
    url: str
    snippet: str = ""
    domain: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        return cls(
            title=data.get("title", ""),
            url=data.get("url", ""),
            snippet=data.get("snippet", ""),
            domain=data.get("domain", ""),
        )


@dataclass
class FetchedContent:
    """Raw content returned by the safe fetcher.

    ``content`` is the (possibly decompressed) response body. It is bounded by
    the fetcher's ``max_bytes`` and is never stored on :class:`WorkflowState`.
    """

    url: str
    content: bytes
    content_type: str
    status_code: int
    final_url: str


@dataclass
class ExtractedContent:
    """Text extracted from a fetched document."""

    title: str = ""
    text: str = ""
    headings: List[str] = field(default_factory=list)
    truncated: bool = False


@dataclass
class WebSource:
    """A source that was actually consulted during research.

    ``source_id`` is a deterministic, 1-based integer used as the citation
    label (``[1]``, ``[2]``, ...). The final source list is generated from the
    application code (not the LLM) so citations always correspond to sources
    that were really consulted.
    """

    source_id: int
    url: str
    title: str = ""
    domain: str = ""
    snippet: str = ""
    status: str = "fetched"
    retrieved_at: str = ""
    content_type: str = ""
    text_excerpt: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebSource":
        return cls(
            source_id=int(data.get("source_id", 0) or 0),
            url=data.get("url", "") or "",
            title=data.get("title", "") or "",
            domain=data.get("domain", "") or "",
            snippet=data.get("snippet", "") or "",
            status=data.get("status", "fetched") or "fetched",
            retrieved_at=data.get("retrieved_at", "") or "",
            content_type=data.get("content_type", "") or "",
            text_excerpt=data.get("text_excerpt", "") or "",
        )


@dataclass
class ResearchOutcome:
    """Result of a single web-research pass.

    ``used_web`` is ``False`` when web research was disabled, failed, or
    produced no usable sources; in that case callers must fall back to the
    existing LLM-only research behavior.
    """

    used_web: bool
    sources: List[WebSource] = field(default_factory=list)
    evidence: str = ""
    diagnostics: Dict[str, Any] = field(default_factory=dict)

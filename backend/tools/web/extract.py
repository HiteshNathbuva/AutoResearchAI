"""Lightweight HTML/text extraction.

Uses only the standard library. Page content is always treated as untrusted
data: this module never executes script, never follows links, and only never
attempts to render anything. Webpage content is never turned into code.

The extractor removes common chrome (``script``, ``style``, ``noscript``,
``template``, ``nav``, ``footer``, ``aside``, ``form``, ``iframe``, ...) and
keeps the document title, headings and readable text.
"""

import html as html_module
import re
from html.parser import HTMLParser
from typing import List, Optional, Tuple

from backend.tools.web.models import ExtractedContent

__all__ = ["extract_page", "decode_content", "extract_html", "extract_plain_text"]

#: Tags whose content is never user-facing page text.
_SKIP_TAGS = {
    "script",
    "style",
    "noscript",
    "template",
    "nav",
    "footer",
    "aside",
    "form",
    "iframe",
    "svg",
    "select",
    "button",
    "textarea",
    "audio",
    "canvas",
    "dialog",
}

#: Heading tags used to surface the document structure.
_HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

_WHITESPACE_RE = re.compile(r"[ \t\r\f\v]+")
_MULTINEWLINE_RE = re.compile(r"\n{3,}")


class _TextExtractor(HTMLParser):
    """Collect title, headings and body text while skipping chrome tags."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: List[str] = []
        self.heading_lines: List[str] = []
        self.text_parts: List[str] = []
        self._skip_depth = 0
        self._in_title = False
        self._heading_tag: Optional[str] = None
        self._heading_buffer: List[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        normalized = tag.lower()
        if normalized in _SKIP_TAGS:
            self._skip_depth += 1
        elif normalized == "title":
            self._in_title = True
        elif normalized in _HEADING_TAGS:
            self._heading_tag = normalized
            self._heading_buffer = []

    def handle_startendtag(self, tag: str, attrs) -> None:
        # <script /> etc.: treat as a skipped void element if appropriate.
        normalized = tag.lower()
        if normalized in _SKIP_TAGS:
            self._skip_depth += 1
            self._skip_depth -= 1

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        if normalized in _SKIP_TAGS:
            if self._skip_depth > 0:
                self._skip_depth -= 1
        elif normalized == "title":
            self._in_title = False
        elif normalized in _HEADING_TAGS:
            if self._heading_buffer:
                self.heading_lines.append(
                    _WHITESPACE_RE.sub(" ", " ".join(self._heading_buffer)).strip()
                )
            self._heading_tag = None
            self._heading_buffer = []

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        if not data or not data.strip():
            return
        if self._in_title:
            # <title> content belongs in the document title, not the body text.
            self.title_parts.append(data)
            return
        if self._heading_tag is not None and self._heading_buffer is not None:
            self._heading_buffer.append(data)
        self.text_parts.append(data)

    @staticmethod
    def _join(parts: List[str]) -> str:
        text = " ".join(parts)
        text = _WHITESPACE_RE.sub(" ", text)
        # Preserve paragraph breaks as single newlines between sentences.
        text = text.replace(" . ", ". ")
        text = _MULTINEWLINE_RE.sub("\n\n", text)
        return text.strip()

    def title(self) -> str:
        return _WHITESPACE_RE.sub(" ", " ".join(self.title_parts)).strip()

    def text(self) -> str:
        return self._join(self.text_parts)


def _charset_from_content_type(content_type: str) -> Optional[str]:
    """Pull an explicit charset out of a Content-Type header value."""

    if not content_type:
        return None
    for part in content_type.split(";")[1:]:
        part = part.strip()
        if "=" in part:
            key, value = part.split("=", 1)
            if key.strip().lower() == "charset":
                return value.strip().strip("\"'")
    return None


def _sniff_charset(content: bytes) -> Optional[str]:
    """Heuristically read a ``<meta charset=...>`` from the head bytes."""

    head = content[:2048].decode("ascii", errors="ignore").lower()
    for match in re.finditer(r"charset\s*=\s*[\"']?([\w.-]+)", head):
        return match.group(1)
    return None


def decode_content(content: bytes, content_type: str = "") -> str:
    """Decode page bytes to text, preferring declared/encoded charsets.

    Falls back to UTF-8 (replacing invalid sequences) and finally Latin-1 so a
    mislabelled encoding never hard-crashes extraction.
    """

    if not content:
        return ""
    charset = _charset_from_content_type(content_type) or _sniff_charset(content)
    if charset:
        try:
            return content.decode(charset, errors="replace")
        except (LookupError, ValueError):
            pass
    for encoding in ("utf-8", "latin-1"):
        try:
            return content.decode(encoding, errors="replace")
        except (LookupError, ValueError):
            continue
    return content.decode("utf-8", errors="replace")


def _truncate(text: str, limit: int) -> Tuple[str, bool]:
    if limit and text and len(text) > limit:
        return text[:limit].rstrip(), True
    return text, False


def extract_html(raw: str, max_chars: int = 0) -> ExtractedContent:
    """Extract readabable content from an HTML string."""

    parser = _TextExtractor()
    try:
        parser.feed(raw or "")
        parser.close()
    except Exception:  # noqa: BLE001 - malformed input must never crash research
        # Even if the parser chokes mid-stream, salvage whatever was collected.
        pass

    title = html_module.unescape(parser.title())
    text, was_truncated = _truncate(parser.text(), max_chars)
    headings = [
        html_module.unescape(line) for line in parser.heading_lines
    ]
    return ExtractedContent(title=title, text=text, headings=headings, truncated=was_truncated)


def extract_plain_text(raw: str, max_chars: int = 0) -> ExtractedContent:
    """Extract content from a plain/text document."""

    title = ""
    text = html_module.unescape(raw or "")
    text, was_truncated = _truncate(text, max_chars)
    return ExtractedContent(title=title, text=text, headings=[], truncated=was_truncated)


def extract_page(content: bytes, content_type: str = "", max_chars: int = 0) -> ExtractedContent:
    """Dispatch to the right extractor based on ``content_type``."""

    normalized_type = (content_type or "").split(";")[0].strip().lower()
    raw = decode_content(content, content_type)
    if normalized_type in ("text/html", "application/xhtml+xml"):
        return extract_html(raw, max_chars=max_chars)
    return extract_plain_text(raw, max_chars=max_chars)

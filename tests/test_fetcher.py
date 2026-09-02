"""Offline SafeFetcher tests using httpx.MockTransport.

No real network access. URL resolution is stubbed to a public IP so hostname
validation never touches DNS.
"""

import logging

import httpx
import pytest

from backend.tools.web.extract import extract_page
from backend.tools.web.fetch import (
    FetchError,
    OversizedResponseError,
    SafeFetcher,
    TooManyRedirectsError,
    UnsafeContentTypeError,
)
from backend.tools.web.security import UnsafeURLError

PUBLIC_RESOLVER = lambda host, port: ["93.184.216.34"]  # noqa: E731


def _client(handler) -> httpx.Client:
    return httpx.Client(
        transport=httpx.MockTransport(handler), trust_env=False,
        follow_redirects=False,
    )


def test_successful_html_fetch():
    def handler(request):
        return httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text="<html><head><title>Title</title></head><body><p>Hello world</p></body></html>",
        )

    client = _client(handler)
    fetcher = SafeFetcher(client=client, resolver=PUBLIC_RESOLVER)
    result = fetcher.fetch("http://example.com/")
    assert result.status_code == 200
    assert result.content_type == "text/html"
    assert b"Hello world" in result.content
    extracted = extract_page(result.content, result.content_type)
    assert extracted.title == "Title"
    assert "Hello world" in extracted.text


def test_plain_text_fetch():
    def handler(request):
        return httpx.Response(200, headers={"content-type": "text/plain"}, text="just text")

    fetcher = SafeFetcher(client=_client(handler), resolver=PUBLIC_RESOLVER)
    result = fetcher.fetch("http://example.com/plain")
    assert result.content_type == "text/plain"
    assert result.content == b"just text"


def test_redirect_followed_and_validated():
    calls = []

    def handler(request):
        calls.append(str(request.url))
        if str(request.url).endswith("/start"):
            return httpx.Response(302, headers={"location": "/end", "content-type": "text/html"})
        return httpx.Response(200, headers={"content-type": "text/html"}, text="done")

    fetcher = SafeFetcher(client=_client(handler), resolver=PUBLIC_RESOLVER, max_redirects=3)
    result = fetcher.fetch("http://example.com/start")
    assert result.final_url == "http://example.com/end"
    assert calls == ["http://example.com/start", "http://example.com/end"]


def test_blocked_redirect_is_rejected_before_network():
    """A redirect to a private/metadata address must never be followed."""

    def handler(request):
        return httpx.Response(301, headers={"location": "http://169.254.169.254/", "content-type": "text/html"})

    fetcher = SafeFetcher(client=_client(handler), resolver=PUBLIC_RESOLVER)
    with pytest.raises(UnsafeURLError):
        fetcher.fetch("http://example.com/start")
    # The redirect target is validated before connecting, so only the initial
    # URL is ever requested.


def test_redirect_limit_enforced():
    def handler(request):
        return httpx.Response(302, headers={"location": "/next", "content-type": "text/html"})

    fetcher = SafeFetcher(client=_client(handler), resolver=PUBLIC_RESOLVER, max_redirects=2)
    with pytest.raises(TooManyRedirectsError):
        fetcher.fetch("http://example.com/start")


def test_initial_unsafe_url_rejected():
    """A blocked initial URL raises before any request is made."""

    client = _client(lambda request: httpx.Response(200, text="x"))
    fetcher = SafeFetcher(client=client, resolver=PUBLIC_RESOLVER)
    with pytest.raises(UnsafeURLError):
        fetcher.fetch("http://127.0.0.1/")


def test_unsupported_content_type_rejected():
    def handler(request):
        return httpx.Response(200, headers={"content-type": "application/pdf"}, content=b"%PDF")

    fetcher = SafeFetcher(client=_client(handler), resolver=PUBLIC_RESOLVER)
    with pytest.raises(UnsafeContentTypeError):
        fetcher.fetch("http://example.com/file.pdf")


def test_oversized_response_rejected():
    def handler(request):
        return httpx.Response(200, headers={"content-type": "text/html"}, content=b"x" * 5000)

    fetcher = SafeFetcher(client=_client(handler), resolver=PUBLIC_RESOLVER, max_bytes=1000)
    with pytest.raises(OversizedResponseError):
        fetcher.fetch("http://example.com/big")


def test_empty_response_is_allowed():
    def handler(request):
        return httpx.Response(200, headers={"content-type": "text/html"}, content=b"")

    fetcher = SafeFetcher(client=_client(handler), resolver=PUBLIC_RESOLVER)
    result = fetcher.fetch("http://example.com/empty")
    assert result.content == b""


def test_connection_error_raises_fetch_error():
    class BoomTransport(httpx.BaseTransport):
        def handle_request(self, request):
            raise httpx.ConnectError("boom")

    client = httpx.Client(transport=BoomTransport(), trust_env=False, follow_redirects=False)
    fetcher = SafeFetcher(client=client, resolver=PUBLIC_RESOLVER)
    with pytest.raises(FetchError):
        fetcher.fetch("http://example.com/")


def test_timeout_raises_fetch_error():
    class SlowTransport(httpx.BaseTransport):
        def handle_request(self, request):
            raise httpx.ReadTimeout("slow")

    client = httpx.Client(transport=SlowTransport(), trust_env=False, follow_redirects=False)
    fetcher = SafeFetcher(client=client, resolver=PUBLIC_RESOLVER)
    with pytest.raises(FetchError):
        fetcher.fetch("http://example.com/")


def test_trust_env_is_false(monkeypatch):
    """The fetcher must not read proxy environment variables by default."""

    import httpx as _httpx
    seen = {}

    original = _httpx.Client

    def capturing_client(**kwargs):
        seen.update(kwargs)
        # Delegate to the real client so construction still works.
        return original(**kwargs)

    monkeypatch.setattr(_httpx, "Client", capturing_client)
    SafeFetcher(timeout=5, max_redirects=2)
    assert seen.get("trust_env") is False


def test_fetcher_never_logs_page_contents(monkeypatch, caplog):
    """Fetching success or failure must not emit page content to logs."""

    logger = logging.getLogger("backend.tools.web.fetch")
    handler = logging.Handler()
    recorder = []
    handler.emit = lambda record: recorder.append(record.getMessage())
    logger.addHandler(handler)
    try:
        fetcher = SafeFetcher(
            client=_client(
                lambda request: httpx.Response(200, headers={"content-type": "text/html"}, text="TOP SECRET PAGE BODY")
            ),
            resolver=PUBLIC_RESOLVER,
        )
        fetcher.fetch("http://example.com/")
    finally:
        logger.removeHandler(handler)

    assert all("TOP SECRET PAGE BODY" not in message for message in recorder)

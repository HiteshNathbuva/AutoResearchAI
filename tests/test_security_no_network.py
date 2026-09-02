"""Prove that blocked URLs can never cause network access.

The safe fetcher validates the URL (and every redirect) BEFORE any HTTP call.
These tests use a recording transport and assert zero network requests are made
for blocked destinations.
"""

import httpx

from backend.tools.web.fetch import SafeFetcher
from backend.tools.web.security import UnsafeURLError, is_safe_url


class RecordingTransport(httpx.BaseTransport):
    """Records every request that would hit the network."""

    def __init__(self, response=None):
        self.response = response or httpx.Response(200, text="ok")
        self.requests = []

    def handle_request(self, request):
        self.requests.append(request)
        return self.response


BLOCKED_URLS = [
    "http://127.0.0.1/",
    "http://localhost/",
    "http://10.0.0.1/",
    "http://169.254.169.254/",
    "http://100.64.0.1/",
    "http://[::1]/",
    "http://[::ffff:127.0.0.1]/",
    "http://2130706433/",
    "http://0x7f000001/",
    "http://metadata.google.internal/",
    "ftp://example.com/",
    "file:///etc/passwd",
]


def _fetcher_with(transport):
    return SafeFetcher(
        client=httpx.Client(transport=transport, trust_env=False, follow_redirects=False),
    )


def test_blocked_urls_never_reach_transport():
    for url in BLOCKED_URLS:
        transport = RecordingTransport()
        fetcher = _fetcher_with(transport)
        try:
            fetcher.fetch(url)
            raise AssertionError(f"{url} should have been blocked")
        except UnsafeURLError:
            pass
        assert transport.requests == [], f"{url} produced a network request"
        assert not is_safe_url(url)


def test_blocked_redirect_never_reaches_second_hop():
    # The first hop is allowed; the redirect target is blocked.
    def handler(request):
        return httpx.Response(301, headers={"location": "http://169.254.169.254/", "content-type": "text/html"})

    transport = httpx.MockTransport(handler)
    fetcher = _fetcher_with(transport)
    try:
        fetcher.fetch("http://example.com/start")
        raise AssertionError("redirect to metadata IP should be blocked")
    except UnsafeURLError:
        pass


def test_public_url_does_reach_transport():
    transport = RecordingTransport()
    fetcher = SafeFetcher(
        client=httpx.Client(transport=transport, trust_env=False, follow_redirects=False),
        resolver=lambda host, port: ["93.184.216.34"],
    )
    result = fetcher.fetch("http://safe.example.com/")
    assert result.status_code == 200
    assert len(transport.requests) == 1

"""Controlled HTTP fetching.

``SafeFetcher`` is the ONLY place in the application that fetches a remote
document. Every URL — the initial one and each redirect target — is validated
with :func:`~backend.tools.web.security.validate_url` *before* any connection,
so a blocked URL (local/private/link-local/metadata/etc.) can never produce
network egress.

Security / resource guarantees:

* HTTP/HTTPS only (protocol allowlist enforced by the validator)
* rejects URL credentials/userinfo, invalid ports, blocked hostnames/IPs
* resolves hostnames and verifies every resolved address
* validates each redirect destination; redirects cannot bypass SSRF checks
* bounded redirect count
* bounded response + decompressed size (streamed, then capped)
* Content-Type allowlist
* ``trust_env=False`` (no proxy/environment egress)
* never logs page contents
"""

from typing import Dict, List, Optional

import httpx

from backend.tools.web.models import FetchedContent
from backend.tools.web.security import Resolver, UnsafeURLError, validate_url

__all__ = [
    "FetchError",
    "UnsafeContentTypeError",
    "OversizedResponseError",
    "TooManyRedirectsError",
    "SafeFetcher",
    "DEFAULT_ALLOWED_CONTENT_TYPES",
]

DEFAULT_ALLOWED_CONTENT_TYPES = frozenset(
    {
        "text/html",
        "text/plain",
        "text/markdown",
        "application/xhtml+xml",
        "application/xml",
        "text/xml",
    }
)

DEFAULT_USER_AGENT = "AutoResearchAI/0.2 (+research; offline-safe fetcher)"

_REDIRECT_STATUS = frozenset({301, 302, 303, 307, 308})


class FetchError(Exception):
    """Base exception for all fetch-time failures."""


class UnsafeContentTypeError(FetchError):
    """Raised when a response has a Content-Type outside the allowlist."""


class OversizedResponseError(FetchError):
    """Raised when a response exceeds the configured byte limit."""


class TooManyRedirectsError(FetchError):
    """Raised when the redirect limit is exceeded."""


class SafeFetcher:
    """Fetch documents safely with SSRF validation at every hop."""

    def __init__(
        self,
        client: Optional[httpx.Client] = None,
        *,
        timeout: float = 10.0,
        max_redirects: int = 3,
        max_bytes: int = 2_000_000,
        allowed_content_types: Optional[set] = None,
        headers: Optional[Dict[str, str]] = None,
        resolver: Optional[Resolver] = None,
    ) -> None:
        # trust_env=False ensures no proxy or HTTP(S)_PROXY environment variable
        # can be used to smuggle traffic through an arbitrary endpoint.
        self._client = client or httpx.Client(
            trust_env=False, timeout=httpx.Timeout(timeout), follow_redirects=False
        )
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.max_bytes = max_bytes
        self.allowed_content_types = frozenset(
            allowed_content_types or DEFAULT_ALLOWED_CONTENT_TYPES
        )
        self.headers = {
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": (
                "text/html,text/plain,text/markdown,application/xhtml+xml"
                ",application/xml;q=0.9,*/*;q=0.5"
            ),
        }
        if headers:
            self.headers.update(headers)
        self.resolver = resolver

    def close(self) -> None:
        """Close the underlying HTTP client (if this fetcher owns it)."""

        if self._client is not None:
            self._client.close()

    @staticmethod
    def _is_redirect(status_code: int) -> bool:
        return status_code in _REDIRECT_STATUS

    def _content_type_allowed(self, content_type: str) -> bool:
        base = (content_type or "").split(";")[0].strip().lower()
        return base in self.allowed_content_types

    def _read_bounded(self, response: httpx.Response) -> bytes:
        chunks: List[bytes] = []
        total = 0
        for chunk in response.iter_bytes():
            total += len(chunk)
            if self.max_bytes > 0 and total > self.max_bytes:
                raise OversizedResponseError(
                    f"response exceeded {self.max_bytes} bytes"
                )
            chunks.append(chunk)
        return b"".join(chunks)

    def fetch(self, url: str) -> FetchedContent:
        """Fetch ``url``, validating it and every redirect before connecting.

        Returns a :class:`FetchedContent` (bounded body + final URL + content
        type), or raises a :class:`FetchError` subclass.
        """

        # The URL validator runs BEFORE any request. This single check makes it
        # impossible for a blocked destination to produce network egress.
        validate_url(url, resolver=self.resolver)

        current_url = url
        redirects_followed = 0

        while True:
            # Validate the current hop (the initial URL and each redirect
            # target) before any connection.
            validate_url(current_url, resolver=self.resolver)

            try:
                with self._client.stream(
                    "GET", current_url, headers=self.headers
                ) as response:
                    if self._is_redirect(response.status_code):
                        location = response.headers.get("location")
                        if not location:
                            raise FetchError(
                                f"redirect from {current_url} without Location header"
                            )
                        if redirects_followed >= self.max_redirects:
                            raise TooManyRedirectsError(
                                f"exceeded {self.max_redirects} redirects"
                            )
                        current_url = httpx.URL(
                            httpx.URL(current_url).join(location)
                        ).__str__()
                        redirects_followed += 1
                        # Loop to validate + fetch the redirect target.
                        continue

                    if response.status_code < 200 or response.status_code >= 400:
                        raise FetchError(
                            f"unexpected status {response.status_code} for {current_url}"
                        )

                    content_type = (
                        response.headers.get("content-type", "")
                        .split(";")[0]
                        .strip()
                        .lower()
                    )
                    if not self._content_type_allowed(content_type):
                        raise UnsafeContentTypeError(
                            f"unsupported content type {content_type!r}"
                        )

                    body = self._read_bounded(response)
                    return FetchedContent(
                        url=url,
                        final_url=current_url,
                        content=body,
                        content_type=content_type,
                        status_code=response.status_code,
                    )
            except (httpx.TimeoutException, httpx.ConnectError, httpx.TransportError) as error:
                raise FetchError(f"network error fetching {current_url}: {error}") from error
            except (FetchError, UnsafeURLError) as error:
                # Re-raise our own errors unchanged.
                raise error from error

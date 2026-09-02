"""URL security validation (SSRF protection).

Every URL that the application will fetch — the initial URL and every redirect
target — must pass :func:`validate_url` BEFORE any network connection is made.

The checks are intentionally strict:

* scheme must be ``http`` or ``https``
* URL userinfo (``user:pass@host``) is rejected
* port must be a valid 1..65535 value
* the host must resolve to a public address; private, loopback, link-local,
  reserved, multicast, unspecified, CGNAT and cloud-metadata networks are
  blocked
* hostnames are resolved first, and every resolved address is verified
* IPv4-mapped IPv6 addresses are normalized to their IPv4 form before checking
* common numeric/hex/octal/dotted IPv4 encodings are decoded and checked
* ``localhost`` and friends are always blocked

The module only inspects URLs and DNS metadata; it never initiates an HTTP
connection itself. Calling :func:`validate_url` therefore has no network side
effect beyond (optionally) a DNS resolution, which is deliberately the check
that must happen before connecting.
"""

import ipaddress
import socket
from typing import Callable, List, Optional, Tuple
from urllib.parse import urlsplit

__all__ = [
    "UnsafeURLError",
    "validate_url",
    "is_safe_url",
    "check_ip",
    "is_public_ip",
]

#: Address families we block. Kept as (network, prefixlen) strings and compiled
#: once at import so lookups are cheap.
_BLOCKED_NETWORKS: List[ipaddress.IPv4Network | ipaddress.IPv6Network] = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),          # CGNAT
    ipaddress.ip_network("127.0.0.0/8"),            # loopback
    ipaddress.ip_network("169.254.0.0/16"),         # link-local (+ metadata)
    ipaddress.ip_network("172.16.0.0/12"),          # private
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),           # TEST-NET
    ipaddress.ip_network("192.168.0.0/16"),         # private
    ipaddress.ip_network("198.18.0.0/15"),          # benchmarking
    ipaddress.ip_network("198.51.100.0/24"),        # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),         # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),            # multicast
    ipaddress.ip_network("240.0.0.0/4"),            # reserved
    ipaddress.ip_network("255.255.255.255/32"),
    ipaddress.ip_network("::/128"),                 # unspecified
    ipaddress.ip_network("::1/128"),                # loopback
    ipaddress.ip_network("fc00::/7"),               # unique local (ULA)
    ipaddress.ip_network("fe80::/10"),              # link-local
    ipaddress.ip_network("ff00::/8"),               # multicast
    ipaddress.ip_network("2001:db8::/32"),          # documentation
]

#: Explicit cloud metadata endpoints, checked by hostname as well as by IP.
_BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "metadata",
}


class UnsafeURLError(ValueError):
    """Raised when a URL is unsafe to fetch (SSRF risk).

    Subclasses :class:`ValueError` so callers that already handle ``ValueError``
    (e.g. the API's 422 mapping) keep working, while still being distinguishable.
    """


#: A resolver maps ``(host, port)`` to a list of IP address strings. Tests and
#: the fetcher inject a controllable resolver to stay fully offline.
Resolver = Callable[[str, int], List[str]]


def _default_resolver(host: str, port: int) -> List[str]:
    """Resolve ``host`` using the system resolver, returning IP addresses."""

    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except (socket.gaierror, socket.timeout) as error:
        raise UnsafeURLError(f"could not resolve host {host!r}: {error}") from error
    # De-duplicate while preserving order.
    seen: set = set()
    addresses: List[str] = []
    for info in infos:
        address = info[4][0]
        if address not in seen:
            seen.add(address)
            addresses.append(address)
    return addresses


def _coerce_ip(
    value: str | int | ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    """Normalize any IP-like value into an :class:`ipaddress` object.

    IPv4-mapped IPv6 addresses are unwrapped to their embedded IPv4 form so the
    private-network checks apply to the real address.
    """

    if isinstance(value, int):
        ip = ipaddress.ip_address(value)
    elif isinstance(value, ipaddress.IPv4Address | ipaddress.IPv6Address):
        ip = value
    else:
        ip = ipaddress.ip_address(str(value))
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped is not None:
        return mapped
    return ip


def _is_blocked(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Return ``True`` when ``ip`` falls inside any blocked network."""

    ip = _coerce_ip(ip)
    for network in _BLOCKED_NETWORKS:
        try:
            if ip in network:
                return True
        except TypeError:
            # Version mismatch between a v4 address and a v6 network, etc.
            continue
    return False


def is_public_ip(value: str | int | ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Return ``True`` for a non-blocked (public) IP address."""

    try:
        ip = _coerce_ip(value)
    except (ValueError, TypeError):
        return False
    return not _is_blocked(ip)


def check_ip(
    value: str | int | ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    """Raise :class:`UnsafeURLError` when ``value`` is a blocked IP."""

    ip = _coerce_ip(value)
    if _is_blocked(ip):
        raise UnsafeURLError(f"blocked IP address {ip}")
    return ip


def _parse_literal_ip(host: str) -> Optional[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    """Decode an IP literal, including common numeric-encoded SSRF bypasses.

    Handles dotted IPv4 (including short forms such as ``127.1`` and octal
    ``0177.0.0.1``), integer ``2130706433``, hexadecimal ``0x7f000001``, and
    plain IPv6 literals (``::1``, ``[::ffff:127.0.0.1]`` is passed bracketless
    by :func:`urllib.parse.urlsplit`).
    """

    if not host:
        return None
    candidate = host.strip().lower()
    # A fully-qualified hostname ends with a dot; strip it for literal forms.
    candidate = candidate.rstrip(".")

    # Plain IP literal (IPv4 or IPv6).
    try:
        return ipaddress.ip_address(candidate)
    except ValueError:
        pass

    # Hex-encoded IPv4, e.g. 0x7f000001.
    if candidate.startswith("0x"):
        try:
            return ipaddress.ip_address(int(candidate[2:], 16))
        except ValueError:
            return None

    # Decimal integer IPv4, e.g. 2130706433.
    if candidate.isdigit():
        try:
            return ipaddress.ip_address(int(candidate))
        except ValueError:
            return None

    # Dotted numeric forms, including octal (0177.0.0.1) and short (127.1).
    if "." in candidate and all(part.isdigit() for part in candidate.split(".")):
        parts = candidate.split(".")
        if 1 <= len(parts) <= 4:
            octets: List[int] = []
            for part in parts:
                try:
                    if len(part) > 1 and part.startswith("0"):
                        octets.append(int(part, 8))
                    else:
                        octets.append(int(part, 10))
                except ValueError:
                    return None
            if any(octet < 0 or octet > 255 for octet in octets):
                return None
            # Reconstruct the 32-bit value the way inet_aton would: the last
            # part is the least-significant octet, earlier parts fill the high
            # bytes, missing parts are zero.
            value = 0
            for octet in octets:
                value = (value << 8) | octet
            try:
                return ipaddress.ip_address(value)
            except ValueError:
                return None
    return None


def _host_to_check(
    host: str,
    port: int,
    resolver: Optional[Resolver],
) -> Tuple[ipaddress.IPv4Address | ipaddress.IPv6Address, ...]:
    """Return the set of addresses that must be verified for a host.

    IP literals are verified directly; hostnames are resolved and every
    resulting address is verified (this is what makes DNS-rebinding-style
    attacks against the final connect address ineffective).
    """

    literal = _parse_literal_ip(host)
    if literal is not None:
        return (literal,)

    resolver_fn = resolver or _default_resolver
    addresses = resolver_fn(host, port)
    if not addresses:
        raise UnsafeURLError(f"host {host!r} did not resolve to any address")
    seen: set = set()
    result: List[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
    for address in addresses:
        ip = _coerce_ip(address)
        if ip not in seen:
            seen.add(ip)
            result.append(ip)
    return tuple(result)


_ALLOWED_SCHEMES = {"http", "https"}


def validate_url(url: str, *, resolver: Optional[Resolver] = None) -> str:
    """Validate ``url`` for SSRF safety and return the normalized URL.

    Raises :class:`UnsafeURLError` for any unsafe or malformed URL. This must be
    called before any network connection — doing so is the reactor's guarantee
    that an unsafe URL can never be fetched.

    Args:
        url: The absolute URL to validate.
        resolver: Optional host resolver; defaults to the system resolver.
    """

    if not url or not url.strip():
        raise UnsafeURLError("empty URL")

    try:
        parts = urlsplit(url)
    except ValueError as error:
        raise UnsafeURLError(f"malformed URL: {error}") from error

    scheme = (parts.scheme or "").lower()
    if scheme not in _ALLOWED_SCHEMES:
        raise UnsafeURLError(f"unsupported URL scheme {parts.scheme!r}")

    if parts.username is not None or parts.password is not None:
        raise UnsafeURLError("URL userinfo is not allowed")

    try:
        host = parts.hostname
        port = parts.port
    except ValueError as error:
        # urllib.parse raises this for malformed host/port combinations (e.g.
        # an unbracketed IPv6 literal or a non-numeric port).
        raise UnsafeURLError(f"malformed URL host/port: {error}") from error

    if not host:
        raise UnsafeURLError("URL has no host")

    if port is not None:
        if port < 1 or port > 65535:
            raise UnsafeURLError(f"invalid port {port}")

    host = host.strip().rstrip(".").lower()
    if not host:
        raise UnsafeURLError("URL has no host")

    if host in _BLOCKED_HOSTNAMES:
        raise UnsafeURLError(f"blocked hostname {host!r}")

    default_port = 443 if scheme == "https" else 80
    if port is None:
        port = default_port

    addresses = _host_to_check(host, port, resolver)
    for ip in addresses:
        check_ip(ip)

    return url


def is_safe_url(url: str, *, resolver: Optional[Resolver] = None) -> bool:
    """Return ``True`` when ``url`` passes :func:`validate_url`."""

    try:
        validate_url(url, resolver=resolver)
    except UnsafeURLError:
        return False
    return True

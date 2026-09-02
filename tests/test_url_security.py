"""Offline URL security (SSRF) validation tests.

No DNS lookup beyond an injected fake resolver; no network access ever occurs.
"""

import pytest

from backend.tools.web.security import (
    UnsafeURLError,
    check_ip,
    is_public_ip,
    is_safe_url,
    validate_url,
)

PUBLIC_RESOLVER = lambda host, port: ["93.184.216.34"]  # noqa: E731


# ----------------------------------------------------------------------
# Scheme / userinfo / host
# ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com/",
        "file:///etc/passwd",
        "data:text/html,hi",
        "javascript:alert(1)",
        "gopher://example.com/",
        "mailto:user@example.com",
        "ws://example.com/",
        "",
        "   ",
        "not-a-url",
        "http://",
    ],
)
def test_rejects_unsupported_schemes_and_malformed(url):
    assert not is_safe_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "http://user:pass@example.com/",
        "http://user@example.com/",
        "http://:pass@example.com/",
    ],
)
def test_rejects_url_userinfo(url):
    assert not is_safe_url(url)


def test_rejects_invalid_ports():
    assert not is_safe_url("http://example.com:0/")
    assert not is_safe_url("http://example.com:70000/")
    assert not is_safe_url("http://example.com:-1/")


# ----------------------------------------------------------------------
# Blocked IP families
# ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "host_or_ip",
    ["127.0.0.1", "127.0.0.2", "10.0.0.1", "172.16.0.1", "192.168.1.1",
     "169.254.169.254", "100.64.0.1", "0.0.0.0", "224.0.0.1", "255.255.255.255",
     "2130706433", "0x7f000001", "0177.0.0.1", "127.1", "127.0.1",
     "192.168.1", "[::1]", "[::]", "[fe80::1]", "[fc00::1]", "[2001:db8::1]"],
)
def test_blocks_private_loopback_linklocal_metadata_and_encoded_ips(host_or_ip):
    assert not is_safe_url(f"http://{host_or_ip}/")


@pytest.mark.parametrize(
    "ip",
    ["93.184.216.34", "8.8.8.8", "1.1.1.1", "2606:4700:4700::1111"],
)
def test_allows_public_ips(ip):
    assert is_public_ip(ip)
    host = f"[{ip}]" if ":" in ip else ip
    assert is_safe_url(f"http://{host}/")


def test_blocks_ipv4_mapped_ipv6_loopback():
    assert not is_safe_url("http://[::ffff:127.0.0.1]/")
    assert not is_safe_url("http://[::ffff:10.0.0.1]/")


def test_ipv4_mapped_public_is_allowed():
    assert is_safe_url("http://[::ffff:8.8.8.8]/")


# ----------------------------------------------------------------------
# Blocked hostnames
# ----------------------------------------------------------------------

def test_localhost_hostname_always_blocked():
    assert not is_safe_url("http://localhost/")
    assert not is_safe_url("HTTP://LOCALHOST/")
    assert not is_safe_url("http://localhost:8080/")


def test_metadata_hostname_blocked():
    assert not is_safe_url("http://metadata.google.internal/")


def test_hostname_resolving_to_private_ip_blocked():
    resolver = lambda host, port: ["192.168.0.5"]  # noqa: E731
    with pytest.raises(UnsafeURLError):
        validate_url("http://public.example.com/", resolver=resolver)


def test_hostname_resolving_to_loopback_blocked():
    resolver = lambda host, port: ["127.0.0.1"]  # noqa: E731
    assert not is_safe_url("http://public.example.com/", resolver=resolver)


def test_hostname_resolving_to_public_ip_allowed():
    assert is_safe_url("http://public.example.com/", resolver=PUBLIC_RESOLVER)


def test_hostname_with_multiple_a_records_any_blocked():
    resolver = lambda host, port: ["93.184.216.34", "10.0.0.1"]  # noqa: E731
    with pytest.raises(UnsafeURLError):
        validate_url("http://multi.example.com/", resolver=resolver)


def test_unresolvable_hostname_rejected():
    resolver = lambda host, port: []  # noqa: E731
    assert not is_safe_url("http://no-such-host.example.com/", resolver=resolver)


def test_check_ip_raises_for_blocked():
    with pytest.raises(UnsafeURLError):
        check_ip("10.0.0.1")
    # Public IPs do not raise.
    check_ip("93.184.216.34")


def test_validate_url_returns_url_unchanged_for_public():
    url = "http://93.184.216.34/path"
    assert validate_url(url) == url

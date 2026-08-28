"""Block fetches to localhost, private networks, and cloud metadata.

Used before any outbound HTTP request to an attacker-controlled URL.
"""

import ipaddress
import socket
from urllib.parse import urlparse
from typing import Optional

BLOCKED_HOSTS = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "metadata",
    "instance-data",
}

METADATA_IPS = {
    "169.254.169.254",
    "fd00:ec2::254",
}


class UnsafeURLError(ValueError):
    pass


def _is_blocked_ip(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    if str(addr) in METADATA_IPS:
        return True
    return bool(
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_multicast
        or addr.is_reserved
        or addr.is_unspecified
    )


def hostname_from(url: str) -> str:
    parsed = urlparse(url)
    return (parsed.hostname or "").lower().rstrip(".")


def assert_public_http_url(url: str) -> None:
    """Raise UnsafeURLError if this URL must not be fetched."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise UnsafeURLError("Only http and https URLs can be fetched.")
    host = hostname_from(url)
    if not host:
        raise UnsafeURLError("URL is missing a host.")
    if host in BLOCKED_HOSTS or host.endswith(".localhost") or host.endswith(".local"):
        raise UnsafeURLError("Local or metadata hosts cannot be fetched.")
    if host == "0.0.0.0":
        raise UnsafeURLError("This address cannot be fetched.")

    try:
        ipaddress.ip_address(host)
        if _is_blocked_ip(host):
            raise UnsafeURLError("Private or local addresses cannot be fetched.")
        return
    except ValueError:
        pass

    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return

    for info in infos:
        ip = info[4][0]
        if _is_blocked_ip(ip):
            raise UnsafeURLError("This host resolves to a private or metadata address.")


def safe_to_fetch(url: str) -> tuple[bool, Optional[str]]:
    try:
        assert_public_http_url(url)
        return True, None
    except UnsafeURLError as exc:
        return False, str(exc)

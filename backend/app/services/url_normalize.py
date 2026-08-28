"""Consistent URL parsing for threat-intel matching and scans.

Keeps path information. Drops only fragments and default ports.
Query strings are stored separately so
https://host/login and https://host/login?session=1 can still match.
"""

from typing import Dict
from urllib.parse import unquote, urlparse

MULTI_TLDS = {
    "co.in", "com.au", "co.uk", "org.in", "net.in", "gov.in",
    "ac.in", "edu.in", "co.jp", "com.br",
}


def get_registrable_domain(netloc: str) -> str:
    """sbi.co.in stays together; www.google.com becomes google.com."""
    host = (netloc or "").split(":")[0].lower().strip(".")
    if host.startswith("www."):
        host = host[4:]
    parts = [p for p in host.split(".") if p]
    if len(parts) >= 3 and ".".join(parts[-2:]) in MULTI_TLDS:
        return ".".join(parts[-3:])
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return host


def _idna_host(host: str) -> str:
    host = (host or "").strip(".").lower()
    if not host:
        return ""
    try:
        return host.encode("idna").decode("ascii")
    except (UnicodeError, UnicodeDecodeError):
        return host


def _split_host_port(netloc: str):
    netloc = (netloc or "").strip()
    if not netloc:
        return "", None
    if netloc.startswith("[") and "]" in netloc:
        host, rest = netloc[1:].split("]", 1)
        port = rest[1:] if rest.startswith(":") else None
        return host.lower(), port
    if netloc.count(":") == 1:
        host, port = netloc.rsplit(":", 1)
        if port.isdigit():
            return host.lower(), port
    return netloc.lower(), None


def normalize_url(url: str) -> Dict:
    """Return original plus comparable host / path fields. Never fetches the URL."""
    original = (url or "").strip()
    empty = {
        "original": original,
        "normalized_full_url": "",
        "scheme": "",
        "hostname": "",
        "registered_domain": "",
        "path": "",
        "query": "",
        "port": None,
        "valid": False,
    }
    if not original:
        return empty

    candidate = original
    if "://" not in candidate:
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    scheme = (parsed.scheme or "https").lower()
    if scheme not in {"http", "https"}:
        return {**empty, "scheme": scheme}

    netloc = parsed.netloc
    if not netloc and parsed.path and "." in parsed.path and not parsed.path.startswith("/"):
        # urlparse("https://google.com") is fine; "google.com" already got a scheme.
        # "https://google.com" works. Bare "google.com" becomes https://google.com.
        pass
    if "@" in netloc:
        netloc = netloc.rsplit("@", 1)[-1]

    host, port = _split_host_port(netloc)
    if not host and parsed.path and "." in parsed.path.split("/")[0]:
        host, port = _split_host_port(parsed.path.split("/")[0])
    host = _idna_host(host)
    if not host:
        return empty

    if port and ((scheme == "http" and port == "80") or (scheme == "https" and port == "443")):
        port = None

    raw_path = parsed.path or "/"
    if host and parsed.path.startswith(host) and not netloc:
        remainder = parsed.path[len(host):]
        raw_path = remainder if remainder.startswith("/") else f"/{remainder}" if remainder else "/"
    path = unquote(raw_path)
    if not path.startswith("/"):
        path = "/" + path
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    query = parsed.query or ""
    netloc_out = f"{host}:{port}" if port else host
    path_for_url = "" if path == "/" else path
    normalized_full_url = f"{scheme}://{netloc_out}{path_for_url}"

    return {
        "original": original,
        "normalized_full_url": normalized_full_url,
        "scheme": scheme,
        "hostname": host,
        "registered_domain": get_registrable_domain(host),
        "path": path,
        "query": query,
        "port": port,
        "valid": True,
    }

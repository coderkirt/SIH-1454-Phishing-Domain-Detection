"""Unwrap short links so the real destination can be scanned.

Scammers hide fake bank / PayPal pages behind bit.ly, tinyurl, and similar
services. This module follows redirects hop-by-hop after SSRF checks.
"""

import re
from urllib.parse import parse_qsl, unquote, urljoin, urlparse
from typing import Dict, List, Optional

import requests

from app.services.ssrf import UnsafeURLError, assert_public_http_url, safe_to_fetch

SHORTENER_DOMAINS = {
    "bit.ly", "bitly.com", "j.mp", "tinyurl.com", "tiny.cc", "t.co",
    "goo.gl", "ow.ly", "is.gd", "cutt.ly", "rebrand.ly", "shorturl.at",
    "rb.gy", "lnkd.in", "fb.me", "amzn.to", "youtu.be", "pin.it",
    "buff.ly", "adf.ly", "bc.vc", "s.id", "v.gd", "trib.al",
    "t.ly", "short.gy", "u.to", "cli.re", "bl.ink", "short.io",
    "soo.gd", "chilp.it", "qr.ae", "wa.link",
}

HEADERS = {
    "User-Agent": "PHISHEYE/1.0 (+https://localhost; URL safety expander)",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}


_EMBED_KEYS = {
    "url", "u", "q", "redirect", "redirect_url", "dest", "destination",
    "target", "to", "link", "continue", "shortlink", "href",
}


def is_shortener(url_or_host: str) -> bool:
    host = urlparse(url_or_host).netloc.lower() or url_or_host.lower()
    host = host.split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    return host in SHORTENER_DOMAINS


def embedded_target(url: str) -> Optional[str]:
    """Return an http(s) address hidden in a redirect query, if the host differs."""
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    for key, value in parse_qsl(parsed.query, keep_blank_values=False):
        if key.lower() not in _EMBED_KEYS:
            continue
        candidate = unquote(value).strip()
        if not candidate.startswith(("http://", "https://")):
            continue
        target_host = (urlparse(candidate).netloc or "").lower().split(":")[0]
        if target_host.startswith("www."):
            target_host = target_host[4:]
        if target_host and target_host != host:
            return candidate
    return None


def should_unwrap(url: str) -> bool:
    """True when the visible address is a mask for a different site."""
    if is_shortener(url) or embedded_target(url):
        return True
    path = (urlparse(url).path or "").lower()
    return path.startswith(("/url", "/redirect", "/out", "/away", "/link"))


def _hop_from_html(body: str, current: str) -> Optional[str]:
    refresh = re.search(
        r"""http-equiv=["']refresh["'][^>]*content=["'][^"']*url=([^"'>\s]+)""",
        body,
        re.I,
    )
    script = re.search(
        r"""(?:window\.location|location\.href)\s*=\s*['"](https?://[^'"]+)['"]""",
        body,
        re.I,
    )
    raw = ""
    if refresh:
        raw = refresh.group(1)
    elif script:
        raw = script.group(1)
    if not raw:
        return None
    return urljoin(current, unquote(raw.strip()))


def expand_url(url: str, max_hops: int = 8) -> Dict:
    """
    Follow redirects and return:
    original_url, final_url, chain, shortened, hops, expanded
    """
    original = url
    result = {
        "original_url": original,
        "final_url": original,
        "chain": [original],
        "shortened": is_shortener(url) or bool(embedded_target(url)),
        "hops": 0,
        "expanded": False,
        "error": None,
    }
    if not url.startswith("http://") and not url.startswith("https://"):
        return result

    allowed, reason = safe_to_fetch(url)
    if not allowed:
        result["error"] = reason
        return result

    session = requests.Session()
    session.headers.update(HEADERS)
    current = url
    chain: List[str] = [original]
    seen = {original}
    hidden = embedded_target(current)
    if hidden and hidden not in seen:
        chain.append(hidden)
        seen.add(hidden)
        current = hidden

    try:
        for _ in range(max_hops):
            assert_public_http_url(current)
            resp = session.head(current, allow_redirects=False, timeout=4)
            if resp.status_code in (403, 405, 501):
                resp = session.get(
                    current,
                    allow_redirects=False,
                    timeout=6,
                    stream=True,
                )
                resp.close()

            location = resp.headers.get("Location")
            nxt = ""
            if location and resp.status_code in (301, 302, 303, 307, 308):
                nxt = urljoin(current, location)
            elif result["shortened"] or is_shortener(current):
                page = session.get(current, allow_redirects=False, timeout=6, stream=True)
                chunk = page.raw.read(20000, decode_content=True) if page.raw else b""
                page.close()
                html_hop = _hop_from_html(chunk.decode("utf-8", errors="ignore"), current)
                if html_hop:
                    nxt = html_hop
            if not nxt:
                result["final_url"] = current
                break
            if nxt in seen:
                result["error"] = "Redirect loop detected"
                break
            allowed, reason = safe_to_fetch(nxt)
            if not allowed:
                result["error"] = f"Redirect blocked: {reason}"
                result["final_url"] = current
                break
            seen.add(nxt)
            chain.append(nxt)
            current = nxt
        else:
            result["error"] = "Too many redirects"

        result["chain"] = chain
        result["final_url"] = result.get("final_url") or current
        result["hops"] = max(len(chain) - 1, 0)
        result["expanded"] = result["final_url"].rstrip("/") != original.rstrip("/")
    except UnsafeURLError as exc:
        result["error"] = str(exc)
    except requests.TooManyRedirects:
        result["error"] = "Too many redirects"
        result["shortened"] = True
    except requests.RequestException as exc:
        result["error"] = str(exc)[:160]
        if result["shortened"]:
            result["error"] = "Could not reveal the hidden destination of this short link"

    return result

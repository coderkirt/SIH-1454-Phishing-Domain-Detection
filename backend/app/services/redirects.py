"""Unwrap short links so the real destination can be scanned.

Scammers hide fake bank / PayPal pages behind bit.ly, tinyurl, and similar
services. This module follows redirects hop-by-hop after SSRF checks.
"""

from urllib.parse import urljoin, urlparse
from typing import Dict, List

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


def is_shortener(url_or_host: str) -> bool:
    host = urlparse(url_or_host).netloc.lower() or url_or_host.lower()
    host = host.split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    return host in SHORTENER_DOMAINS


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
        "shortened": is_shortener(url),
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

    try:
        for _ in range(max_hops):
            assert_public_http_url(current)
            resp = session.head(current, allow_redirects=False, timeout=6)
            if resp.status_code in (403, 405, 501):
                resp = session.get(
                    current,
                    allow_redirects=False,
                    timeout=6,
                    stream=True,
                )
                resp.close()

            location = resp.headers.get("Location")
            if not location or resp.status_code not in (301, 302, 303, 307, 308):
                result["final_url"] = current
                break

            nxt = urljoin(current, location)
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
        result["shortened"] = result["shortened"] or result["expanded"]
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

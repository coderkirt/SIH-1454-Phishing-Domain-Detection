"""Extract every URL from free text or HTML. Does not fetch destinations."""

import html
import re
from typing import List, Dict
from urllib.parse import urlparse, unquote

from app.services.url_checker import get_registrable_domain
from app.services.redirects import is_shortener

URL_RE = re.compile(
    r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s<>'\"\]\)]+))",
)
HREF_RE = re.compile(r"""(?i)href\s*=\s*["']([^"']+)["']""")
SHORT_RE = re.compile(
    r"(?i)\b((?:bit\.ly|t\.co|tinyurl\.com|is\.gd|cutt\.ly|ow\.ly|j\.mp|rb\.gy|s\.id)/[^\s<>'\"]+)"
)


def _clean(raw: str) -> str:
    value = html.unescape(unquote(raw or "")).strip().rstrip(".,;:!?)")
    if value.lower().startswith("www."):
        value = "https://" + value
    return value


def extract_urls(text: str) -> List[Dict]:
    """Return unique URLs in appearance order with position and domain."""
    text = text or ""
    found = []
    seen = set()

    def add(raw: str, position: int):
        url = _clean(raw)
        if not url or url.lower() in seen:
            return
        if not url.startswith("http://") and not url.startswith("https://"):
            if "." not in url:
                return
            url = "https://" + url
        host = urlparse(url).netloc.lower().split(":")[0]
        if not host:
            return
        seen.add(url.lower())
        found.append({
            "url": url,
            "position": position,
            "domain": get_registrable_domain(host),
            "shortened": is_shortener(url),
        })

    for match in HREF_RE.finditer(text):
        add(match.group(1), match.start())
    for match in URL_RE.finditer(text):
        add(match.group(1), match.start())
    for match in SHORT_RE.finditer(text):
        add(match.group(1), match.start())

    found.sort(key=lambda item: item["position"])
    return found[:15]

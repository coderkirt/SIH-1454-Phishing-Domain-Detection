"""Threat-intelligence lookups with explicit match vs unavailable vs no-match.

Providers are independent. A miss in one feed is NOT "safe".
A timeout is NOT "no match". Confirmed hits use URL normalization, not
raw-string equality only.

This module never fetches the submitted page itself.
"""

import os
import time
from typing import Dict, Iterable, List, Optional
from urllib.parse import parse_qsl, quote

import requests
from dotenv import load_dotenv

from app.services.trusted import TRUSTED_DOMAINS, is_generic_trusted_path, is_trusted_destination
from app.services.url_normalize import normalize_url

load_dotenv()

GSB_API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "").strip()
PHISHTANK_API_KEY = os.getenv("PHISHTANK_API_KEY", "").strip()
URLHAUS_AUTH_KEY = os.getenv("URLHAUS_AUTH_KEY", "").strip()
ENABLE_ONLINE_CHECKS = os.getenv("ENABLE_ONLINE_CHECKS", "true").strip().lower() != "false"

GSB_ENDPOINT = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
OPENPHISH_FEED = "https://openphish.com/feed.txt"
PHISHTANK_ENDPOINT = "https://checkurl.phishtank.com/checkurl/"
URLHAUS_ENDPOINT = "https://urlhaus-api.abuse.ch/v1/url/"

FEED_TTL_SEC = 30 * 60
HIT_TTL_SEC = 15 * 60

_openphish_state = {"fetched_at": 0.0, "index": None, "error": None}
_lookup_cache: dict = {}


def _provider_result(
    provider: str,
    *,
    found: bool = False,
    match_type: str = "no_match",
    confidence: float = 0.0,
    status: str = "no_match",
    detail: str = "",
    matched_url: str = "",
) -> Dict:
    return {
        "provider": provider,
        "found": found,
        "match_type": match_type,
        "confidence": round(float(confidence), 3),
        "status": status,
        "source": provider,
        "detail": detail,
        "matched_url": matched_url,
    }


def _is_root_path(path: str) -> bool:
    return (path or "/") in {"", "/"}


def _queries_overlap(user_q: str, feed_q: str) -> bool:
    user_q = user_q or ""
    feed_q = feed_q or ""
    if user_q == feed_q:
        return True
    if not user_q or not feed_q:
        return False
    user = dict(parse_qsl(user_q, keep_blank_values=True))
    feed = dict(parse_qsl(feed_q, keep_blank_values=True))
    for key in ("q", "url", "u", "shortlink", "continue", "dest", "redirect"):
        if key in feed and key in user and feed[key] == user[key]:
            return True
    return feed_q in user_q or user_q in feed_q


def _root_query_compatible(user_info: Dict, feed_info: Dict) -> bool:
    """Do not treat google.com/?phishing=1 as the Google homepage."""
    if not _is_root_path(user_info.get("path")):
        return True
    if user_info.get("registered_domain") not in TRUSTED_DOMAINS:
        return True
    return _queries_overlap(user_info.get("query") or "", feed_info.get("query") or "")


def paths_related(user_path: str, feed_path: str, *, allow_parent: bool = True) -> bool:
    user = (user_path or "/").rstrip("/") or "/"
    feed = (feed_path or "/").rstrip("/") or "/"
    if user == feed:
        return True
    if feed != "/" and (user == feed or user.startswith(feed + "/")):
        return True
    if allow_parent and user != "/" and (feed == user or feed.startswith(user + "/")):
        return True
    return False


def build_feed_index(urls: Iterable[str]) -> Dict:
    normalized_map: Dict[str, list] = {}
    by_host: Dict[str, list] = {}
    by_registered: Dict[str, list] = {}
    raw = set()
    for item in urls:
        text = (item or "").strip()
        if not text:
            continue
        raw.add(text.lower().rstrip("/"))
        info = normalize_url(text)
        if not info["valid"]:
            continue
        normalized_map.setdefault(info["normalized_full_url"], []).append(info)
        by_host.setdefault(info["hostname"], []).append(info)
        host = info["hostname"]
        alt = host[4:] if host.startswith("www.") else f"www.{host}"
        by_host.setdefault(alt, []).append(info)
        registered = info.get("registered_domain") or ""
        if registered:
            by_registered.setdefault(registered, []).append(info)
    return {
        "raw": raw,
        "normalized": normalized_map,
        "by_host": by_host,
        "by_registered_domain": by_registered,
    }


def _trusted_entry_compatible(user_info: Dict, feed_info: Dict) -> bool:
    """On famous sites, a dump row for one /watch or /search must not flag all of them."""
    user_path = (user_info.get("path") or "/").rstrip("/") or "/"
    feed_path = (feed_info.get("path") or "/").rstrip("/") or "/"
    if user_path != feed_path:
        return False
    user_q = user_info.get("query") or ""
    feed_q = feed_info.get("query") or ""
    if user_q or feed_q:
        return _queries_overlap(user_q, feed_q)
    return not is_generic_trusted_path(user_path)


def match_against_index(user_info: Dict, index: Dict) -> Dict:
    """Compare a normalized URL to a feed index. Does not treat a miss as safe."""
    if not user_info or not user_info.get("valid") or not index:
        return {"match_type": "no_match", "confidence": 0.0, "matched_url": ""}

    trusted = is_trusted_destination(
        hostname=user_info.get("hostname"),
        registered_domain=user_info.get("registered_domain"),
    )
    user_norm = user_info["normalized_full_url"]
    raw_key = (user_info.get("original") or "").lower().rstrip("/")
    if raw_key and raw_key in (index.get("raw") or set()):
        if (not trusted) or (user_info.get("query") or not is_generic_trusted_path(user_info.get("path") or "/")):
            return {"match_type": "exact_url", "confidence": 1.0, "matched_url": raw_key}

    stored = (index.get("normalized") or {}).get(user_norm)
    entries = stored if isinstance(stored, list) else ([stored] if stored else [])
    for hit in entries:
        if trusted:
            if _trusted_entry_compatible(user_info, hit):
                return {
                    "match_type": "normalized_url",
                    "confidence": 1.0,
                    "matched_url": hit.get("normalized_full_url") or user_norm,
                }
            continue
        if _root_query_compatible(user_info, hit):
            return {
                "match_type": "normalized_url",
                "confidence": 1.0,
                "matched_url": hit.get("normalized_full_url") or user_norm,
            }

    host = user_info["hostname"]
    candidates = list((index.get("by_host") or {}).get(host) or [])
    related = []
    for entry in candidates:
        if trusted:
            if _trusted_entry_compatible(user_info, entry):
                related.append(entry)
            continue
        if not paths_related(user_info["path"], entry.get("path") or "/", allow_parent=True):
            continue
        if not _root_query_compatible(user_info, entry):
            continue
        related.append(entry)
    if related:
        hit = related[0]
        return {
            "match_type": "normalized_url",
            "confidence": 0.97,
            "matched_url": hit.get("normalized_full_url") or "",
        }

    if (not trusted) and candidates:
        hit = candidates[0]
        return {
            "match_type": "hostname",
            "confidence": 0.82,
            "matched_url": hit.get("normalized_full_url") or "",
        }

    registered = user_info.get("registered_domain") or ""
    if (not trusted) and registered:
        domain_hits = list((index.get("by_registered_domain") or {}).get(registered) or [])
        apex = {registered, f"www.{registered}"}
        apex_hits = [hit for hit in domain_hits if (hit.get("hostname") or "") in apex]
        if apex_hits:
            hit = apex_hits[0]
            return {
                "match_type": "registered_domain",
                "confidence": 0.78,
                "matched_url": hit.get("normalized_full_url") or "",
            }

    return {"match_type": "no_match", "confidence": 0.0, "matched_url": ""}


def match_domain_list(user_info: Dict, index: Dict) -> Dict:
    """Match hostname against a domain blocklist. Skips official trusted sites."""
    if not user_info or not user_info.get("valid") or not index:
        return {"match_type": "no_match", "confidence": 0.0, "matched_url": ""}
    if is_trusted_destination(
        hostname=user_info.get("hostname"),
        registered_domain=user_info.get("registered_domain"),
    ):
        return {"match_type": "no_match", "confidence": 0.0, "matched_url": ""}
    domains = index.get("domains") or set()
    host = user_info.get("hostname") or ""
    labels = [part for part in host.split(".") if part]
    for i in range(0, max(len(labels) - 1, 1)):
        candidate = ".".join(labels[i:])
        if candidate in domains:
            return {
                "match_type": "hostname" if i == 0 else "registered_domain",
                "confidence": 0.9 if i == 0 else 0.78,
                "matched_url": candidate,
            }
    return {"match_type": "no_match", "confidence": 0.0, "matched_url": ""}


def _cache_get(key: str):
    row = _lookup_cache.get(key)
    if not row:
        return None
    saved, expires_at = row
    if time.time() > expires_at:
        _lookup_cache.pop(key, None)
        return None
    return saved


def _cache_set(key: str, value: Dict, ttl: int) -> Dict:
    if value.get("status") == "unavailable":
        ttl = min(ttl, 60)
    _lookup_cache[key] = (value, time.time() + ttl)
    return value


def _get_openphish_index(fetch_lines=None) -> Optional[Dict]:
    now = time.time()
    cached = _openphish_state["index"]
    if cached and now - _openphish_state["fetched_at"] < FEED_TTL_SEC:
        return cached

    fetcher = fetch_lines or _download_openphish_lines
    try:
        lines = fetcher()
        if not lines:
            if cached:
                return cached
            _openphish_state["error"] = "empty_feed"
            return None
        index = build_feed_index(lines)
        _openphish_state["index"] = index
        _openphish_state["fetched_at"] = now
        _openphish_state["error"] = None
        return index
    except Exception as exc:
        _openphish_state["error"] = str(exc)
        return cached


def _download_openphish_lines() -> List[str]:
    resp = requests.get(OPENPHISH_FEED, timeout=8)
    resp.raise_for_status()
    return [line.strip() for line in resp.text.splitlines() if line.strip().startswith("http")]


def lookup_openphish(url_info: Dict, *, fetch_lines=None, index: Optional[Dict] = None, allow_public: bool = True) -> Dict:
    provider = "OpenPhish"
    if not url_info.get("valid"):
        return _provider_result(provider, match_type="no_match", status="no_match", detail="URL could not be normalized")
    if index is None:
        if fetch_lines is not None:
            index = _get_openphish_index(fetch_lines=fetch_lines)
        elif not ENABLE_ONLINE_CHECKS:
            return _provider_result(
                provider, match_type="unavailable", status="unavailable",
                detail="Online checks disabled",
            )
        elif not allow_public:
            return _provider_result(
                provider, match_type="unavailable", status="unavailable",
                detail="OpenPhish public feed skipped",
            )
        else:
            from app.services.feed_cache import OPENPHISH_FEED, get_url_index
            index = get_url_index("openphish", OPENPHISH_FEED, timeout=20)
        if index is None:
            return _provider_result(
                provider, match_type="unavailable", status="unavailable",
                detail="OpenPhish feed unavailable",
            )
    hit = match_against_index(url_info, index)
    if hit["match_type"] == "no_match":
        return _provider_result(
            provider, status="no_match", match_type="no_match",
            detail="No match in OpenPhish feed",
        )
    return _provider_result(
        provider,
        found=True,
        match_type=hit["match_type"],
        confidence=hit["confidence"],
        status="confirmed_malicious",
        detail=f"OpenPhish match ({hit['match_type']})",
        matched_url=hit["matched_url"],
    )


def _phishtank_flag(value) -> Optional[bool]:
    """PhishTank uses true/false, y/n, yes/no, and 1/0 depending on the endpoint."""
    if value is True or value is False:
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"true", "t", "y", "yes", "1", "valid", "verified"}:
        return True
    if text in {"false", "f", "n", "no", "0", "u", "unverified", "invalid"}:
        return False
    return None


def _phishtank_from_payload(url_info: Dict, runner) -> Dict:
    provider = "PhishTank"
    cache_key = f"phishtank:{url_info['normalized_full_url']}"
    cached = _cache_get(cache_key)
    if cached:
        return cached
    try:
        payload = runner(url_info["original"] or url_info["normalized_full_url"])
    except Exception as exc:
        return _provider_result(
            provider, match_type="unavailable", status="unavailable",
            detail=f"PhishTank lookup failed: {exc}",
        )
    if not isinstance(payload, dict):
        return _cache_set(cache_key, _provider_result(
            provider, match_type="unavailable", status="unavailable",
            detail="PhishTank returned an invalid response",
        ), 60)
    results = payload.get("results") if isinstance(payload.get("results"), dict) else payload
    in_database = _phishtank_flag(results.get("in_database"))
    if in_database is True:
        valid = _phishtank_flag(results.get("valid"))
        verified = _phishtank_flag(results.get("verified"))
        if valid is False:
            return _cache_set(cache_key, _provider_result(
                provider, status="no_match", match_type="no_match",
                detail="PhishTank entry is marked invalid",
            ), HIT_TTL_SEC)
        if verified is False:
            return _cache_set(cache_key, _provider_result(
                provider, found=True, match_type="normalized_url", confidence=0.72,
                status="reported_malicious",
                detail="PhishTank has an unverified/suspected report for this URL",
                matched_url=url_info["normalized_full_url"],
            ), HIT_TTL_SEC)
        return _cache_set(cache_key, _provider_result(
            provider, found=True, match_type="normalized_url", confidence=1.0,
            status="confirmed_malicious",
            detail="PhishTank confirmed this URL",
            matched_url=url_info["normalized_full_url"],
        ), HIT_TTL_SEC)
    if in_database is False:
        return _cache_set(cache_key, _provider_result(
            provider, status="no_match", match_type="no_match",
            detail="No match in PhishTank",
        ), HIT_TTL_SEC)
    return _cache_set(cache_key, _provider_result(
        provider, match_type="unavailable", status="unavailable",
        detail="PhishTank response missing in_database",
    ), 60)


def _phishtank_dump_url() -> str:
    if PHISHTANK_API_KEY:
        return f"https://data.phishtank.com/data/{PHISHTANK_API_KEY}/online-valid.csv"
    return "https://data.phishtank.com/data/online-valid.csv"


def _phishtank_dump_candidates() -> List[str]:
    primary = _phishtank_dump_url()
    urls = [primary]
    if PHISHTANK_API_KEY:
        base = f"https://data.phishtank.com/data/{PHISHTANK_API_KEY}"
        urls.extend([
            f"{base}/online-valid.csv.gz",
            f"{base}/online-valid.json",
            f"{base}/online-valid.json.gz",
        ])
    else:
        urls.extend([
            "https://data.phishtank.com/data/online-valid.csv.gz",
            "https://data.phishtank.com/data/online-valid.json",
            "https://data.phishtank.com/data/online-valid.json.gz",
        ])
    seen = set()
    unique = []
    for item in urls:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def _fetch_phishtank_dump_text() -> str:
    from app.services.feed_cache import download_text, parse_phishtank_payload

    last_error: Optional[Exception] = None
    for url in _phishtank_dump_candidates():
        try:
            text = download_text(url, timeout=30)
            if parse_phishtank_payload(text):
                return text
            last_error = ValueError(f"PhishTank dump at {url} had no URLs")
        except Exception as exc:
            last_error = exc
    raise last_error or ValueError("PhishTank dump unavailable")


def _phishtank_from_public_dump(url_info: Dict, index: Optional[Dict] = None) -> Dict:
    provider = "PhishTank"
    if index is None:
        from app.services.feed_cache import get_url_index, parse_phishtank_payload
        index = get_url_index(
            "phishtank_dump",
            _phishtank_dump_url(),
            parser=parse_phishtank_payload,
            fetch=_fetch_phishtank_dump_text,
            timeout=30,
        )
    if index is None:
        return _provider_result(
            provider, match_type="unavailable", status="unavailable",
            detail="PhishTank public dump unavailable",
        )
    hit = match_against_index(url_info, index)
    if hit["match_type"] == "no_match":
        return _provider_result(
            provider, status="no_match", match_type="no_match",
            detail="No match in PhishTank verified dump; checking live reports next if enabled",
        )
    return _provider_result(
        provider, found=True, match_type=hit["match_type"],
        confidence=hit["confidence"], status="confirmed_malicious",
        detail=f"PhishTank dump match ({hit['match_type']})",
        matched_url=hit["matched_url"],
    )


def _prefer_phishtank_hit(dump_hit: Dict, live_hit: Dict) -> Dict:
    """Verified dump wins; otherwise keep live suspected/confirmed reports."""
    if dump_hit.get("status") == "confirmed_malicious":
        return dump_hit
    if live_hit.get("status") in {"confirmed_malicious", "reported_malicious"}:
        return live_hit
    if dump_hit.get("status") == "unavailable":
        return live_hit
    if live_hit.get("status") == "unavailable":
        return dump_hit
    return live_hit


def lookup_phishtank(url_info: Dict, *, query=None, index=None, allow_public: bool = True) -> Dict:
    provider = "PhishTank"
    if not url_info.get("valid"):
        return _provider_result(provider, match_type="unavailable", status="unavailable", detail="URL could not be normalized")
    if query is not None and index is None:
        return _phishtank_from_payload(url_info, query)
    if index is not None and query is None:
        return _phishtank_from_public_dump(url_info, index=index)
    if query is not None and index is not None:
        dump_hit = _phishtank_from_public_dump(url_info, index=index)
        live_hit = _phishtank_from_payload(url_info, query)
        return _prefer_phishtank_hit(dump_hit, live_hit)
    if not ENABLE_ONLINE_CHECKS:
        return _provider_result(provider, match_type="unavailable", status="unavailable", detail="Online checks disabled")
    if not allow_public:
        return _provider_result(
            provider, match_type="unavailable", status="unavailable",
            detail="PhishTank public dump skipped",
        )
    dump_hit = _phishtank_from_public_dump(url_info)
    if dump_hit["status"] == "confirmed_malicious":
        return dump_hit
    live_hit = _phishtank_from_payload(url_info, _query_phishtank)
    return _prefer_phishtank_hit(dump_hit, live_hit)


def _query_phishtank(url: str) -> Dict:
    data = {
        "url": url,
        "format": "json",
    }
    if PHISHTANK_API_KEY:
        data["app_key"] = PHISHTANK_API_KEY
    resp = requests.post(
        PHISHTANK_ENDPOINT,
        data=data,
        timeout=8,
        headers={"User-Agent": "phisheye/1.8 (SIH-1454 academic phishing detector)"},
    )
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError as exc:
        raise RuntimeError("PhishTank returned a non-JSON response") from exc


def lookup_urlhaus(url_info: Dict, *, query=None, index=None, fetch_lines=None, allow_public: bool = True) -> Dict:
    provider = "URLhaus"
    if not url_info.get("valid"):
        return _provider_result(provider, match_type="unavailable", status="unavailable", detail="URL could not be normalized")
    if query is not None:
        return _urlhaus_from_payload(url_info, query)
    if index is not None or fetch_lines is not None:
        return _urlhaus_from_public_feed(url_info, index=index, fetch_lines=fetch_lines)
    if not ENABLE_ONLINE_CHECKS:
        return _provider_result(provider, match_type="unavailable", status="unavailable", detail="Online checks disabled")
    if not allow_public:
        return _provider_result(
            provider, match_type="unavailable", status="unavailable",
            detail="URLhaus public feed skipped",
        )
    if URLHAUS_AUTH_KEY:
        api_hit = _urlhaus_from_payload(url_info, _query_urlhaus)
        if api_hit["status"] == "confirmed_malicious":
            return api_hit
    return _urlhaus_from_public_feed(url_info)


def _urlhaus_from_payload(url_info: Dict, runner) -> Dict:
    provider = "URLhaus"
    cache_key = f"urlhaus:{url_info['normalized_full_url']}"
    cached = _cache_get(cache_key)
    if cached:
        return cached
    try:
        payload = runner(url_info["original"] or url_info["normalized_full_url"])
    except Exception as exc:
        return _provider_result(
            provider, match_type="unavailable", status="unavailable",
            detail=f"URLhaus lookup failed: {exc}",
        )
    if not isinstance(payload, dict):
        return _cache_set(cache_key, _provider_result(
            provider, match_type="unavailable", status="unavailable",
            detail="URLhaus returned an invalid response",
        ), 60)
    status = str(payload.get("query_status") or "").lower()
    if status in {"no_results", "not_found"}:
        return _cache_set(cache_key, _provider_result(
            provider, status="no_match", match_type="no_match",
            detail="No match in URLhaus",
        ), HIT_TTL_SEC)
    if status in {"ok", "found"}:
        threat = payload.get("threat") or payload.get("url_status") or "malware"
        return _cache_set(cache_key, _provider_result(
            provider, found=True, match_type="normalized_url", confidence=1.0,
            status="confirmed_malicious",
            detail=f"URLhaus confirmed this URL ({threat})",
            matched_url=payload.get("url") or url_info["normalized_full_url"],
        ), HIT_TTL_SEC)
    if status in {"invalid_url"}:
        return _cache_set(cache_key, _provider_result(
            provider, status="no_match", match_type="no_match",
            detail="URLhaus rejected the URL format",
        ), HIT_TTL_SEC)
    return _cache_set(cache_key, _provider_result(
        provider, match_type="unavailable", status="unavailable",
        detail=f"URLhaus status: {status or 'unknown'}",
    ), 60)


def _urlhaus_from_public_feed(url_info: Dict, index: Optional[Dict] = None, fetch_lines=None) -> Dict:
    provider = "URLhaus"
    if index is None:
        if fetch_lines is not None:
            try:
                index = build_feed_index(fetch_lines())
            except Exception as exc:
                return _provider_result(
                    provider, match_type="unavailable", status="unavailable",
                    detail=f"URLhaus feed unavailable: {exc}",
                )
        else:
            from app.services.feed_cache import URLHAUS_ONLINE_FEED, get_url_index
            index = get_url_index("urlhaus_online", URLHAUS_ONLINE_FEED, timeout=25)
    if index is None:
        return _provider_result(
            provider, match_type="unavailable", status="unavailable",
            detail="URLhaus public feed unavailable",
        )
    hit = match_against_index(url_info, index)
    if hit["match_type"] == "no_match":
        return _provider_result(
            provider, status="no_match", match_type="no_match",
            detail="No match in URLhaus feed",
        )
    return _provider_result(
        provider, found=True, match_type=hit["match_type"],
        confidence=hit["confidence"], status="confirmed_malicious",
        detail=f"URLhaus feed match ({hit['match_type']})",
        matched_url=hit["matched_url"],
    )


def _query_urlhaus(url: str) -> Dict:
    headers = {"User-Agent": "phisheye/1.4"}
    if URLHAUS_AUTH_KEY:
        headers["Auth-Key"] = URLHAUS_AUTH_KEY
    resp = requests.post(URLHAUS_ENDPOINT, data={"url": url}, timeout=8, headers=headers)
    resp.raise_for_status()
    return resp.json()


def lookup_google_safe_browsing(url_info: Dict, *, query=None) -> Dict:
    provider = "Google Safe Browsing"
    if not url_info.get("valid"):
        return _provider_result(provider, match_type="unavailable", status="unavailable", detail="URL could not be normalized")
    if query is None and not ENABLE_ONLINE_CHECKS:
        return _provider_result(provider, match_type="unavailable", status="unavailable", detail="Online checks disabled")
    if not GSB_API_KEY and query is None:
        return _provider_result(
            provider, match_type="unavailable", status="unavailable",
            detail="Google Safe Browsing API key not configured",
        )

    cache_key = f"gsb:{url_info['normalized_full_url']}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    runner = query or _query_gsb
    try:
        threats = runner(url_info["normalized_full_url"])
    except Exception as exc:
        return _provider_result(
            provider, match_type="unavailable", status="unavailable",
            detail=f"Google Safe Browsing lookup failed: {exc}",
        )

    if threats is None:
        return _provider_result(
            provider, match_type="unavailable", status="unavailable",
            detail="Google Safe Browsing lookup failed",
        )
    if threats:
        return _cache_set(cache_key, _provider_result(
            provider, found=True, match_type="normalized_url", confidence=1.0,
            status="confirmed_malicious",
            detail=f"Google Safe Browsing: {', '.join(threats)}",
            matched_url=url_info["normalized_full_url"],
        ), HIT_TTL_SEC)
    return _cache_set(cache_key, _provider_result(
        provider, status="no_match", match_type="no_match",
        detail="No match in Google Safe Browsing",
    ), HIT_TTL_SEC)


def _query_gsb(url: str) -> Optional[List[str]]:
    body = {
        "client": {"clientId": "phisheye", "clientVersion": "1.4.0"},
        "threatInfo": {
            "threatTypes": [
                "MALWARE", "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION",
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    resp = requests.post(f"{GSB_ENDPOINT}?key={quote(GSB_API_KEY)}", json=body, timeout=5)
    resp.raise_for_status()
    matches = resp.json().get("matches") or []
    return sorted({m.get("threatType", "UNKNOWN") for m in matches})


def lookup_phishing_army(url_info: Dict, *, index: Optional[Dict] = None, fetch_lines=None, allow_public: bool = True) -> Dict:
    provider = "Phishing Army"
    if not url_info.get("valid"):
        return _provider_result(provider, match_type="no_match", status="no_match", detail="URL could not be normalized")
    if index is None:
        if fetch_lines is not None:
            try:
                from app.services.feed_cache import build_domain_index, parse_domain_lines
                index = build_domain_index(parse_domain_lines("\n".join(fetch_lines())))
            except Exception as exc:
                return _provider_result(
                    provider, match_type="unavailable", status="unavailable",
                    detail=f"Phishing Army feed unavailable: {exc}",
                )
        elif not ENABLE_ONLINE_CHECKS:
            return _provider_result(
                provider, match_type="unavailable", status="unavailable",
                detail="Online checks disabled",
            )
        elif not allow_public:
            return _provider_result(
                provider, match_type="unavailable", status="unavailable",
                detail="Phishing Army public feed skipped",
            )
        else:
            from app.services.feed_cache import PHISHING_ARMY, get_domain_index
            index = get_domain_index("phishing_army", PHISHING_ARMY, timeout=20)
    if index is None:
        return _provider_result(
            provider, match_type="unavailable", status="unavailable",
            detail="Phishing Army feed unavailable",
        )
    hit = match_domain_list(url_info, index)
    if hit["match_type"] == "no_match":
        return _provider_result(
            provider, status="no_match", match_type="no_match",
            detail="No match in Phishing Army domain list",
        )
    return _provider_result(
        provider, found=True, match_type=hit["match_type"],
        confidence=hit["confidence"], status="confirmed_malicious",
        detail=f"Phishing Army domain match ({hit['match_type']})",
        matched_url=hit["matched_url"],
    )


def warmup_feeds() -> Dict:
    """Download public feeds into disk cache. Safe to call on API startup."""
    from app.services.feed_cache import (
        OPENPHISH_FEED,
        PHISHING_ARMY,
        URLHAUS_ONLINE_FEED,
        feed_status,
        get_domain_index,
        get_url_index,
        parse_phishtank_payload,
    )
    if not ENABLE_ONLINE_CHECKS:
        return feed_status()
    get_url_index("openphish", OPENPHISH_FEED, timeout=20)
    get_url_index("urlhaus_online", URLHAUS_ONLINE_FEED, timeout=25)
    get_url_index(
        "phishtank_dump",
        _phishtank_dump_url(),
        parser=parse_phishtank_payload,
        fetch=_fetch_phishtank_dump_text,
        timeout=30,
    )
    get_domain_index("phishing_army", PHISHING_ARMY, timeout=20)
    return feed_status()


def lookup_threat_intelligence(url: str, *, providers: Optional[Dict] = None) -> Dict:
    """Query configured providers and aggregate. Never maps a miss to SAFE."""
    info = normalize_url(url)
    hooks = providers or {}
    isolated = providers is not None
    results = [
        lookup_phishtank(
            info,
            query=hooks.get("phishtank"),
            index=hooks.get("phishtank_index"),
            allow_public=not isolated,
        ),
        lookup_openphish(
            info,
            fetch_lines=hooks.get("openphish_lines"),
            index=hooks.get("openphish_index"),
            allow_public=not isolated,
        ),
        lookup_urlhaus(
            info,
            query=hooks.get("urlhaus"),
            index=hooks.get("urlhaus_index"),
            fetch_lines=hooks.get("urlhaus_lines"),
            allow_public=not isolated,
        ),
        lookup_google_safe_browsing(info, query=hooks.get("gsb")),
    ]
    if not isolated or hooks.get("phishing_army_index") is not None or hooks.get("phishing_army_lines"):
        results.append(lookup_phishing_army(
            info,
            index=hooks.get("phishing_army_index"),
            fetch_lines=hooks.get("phishing_army_lines"),
            allow_public=not isolated,
        ))

    confirmed = [row for row in results if row["status"] == "confirmed_malicious"]
    reported = [row for row in results if row["status"] == "reported_malicious"]
    unavailable = [row for row in results if row["status"] == "unavailable"]
    no_match = [row for row in results if row["status"] == "no_match"]
    best = None

    if confirmed:
        best = max(confirmed, key=lambda row: row.get("confidence") or 0)
        overall = "confirmed_malicious"
        summary = best["detail"]
    elif reported:
        best = max(reported, key=lambda row: row.get("confidence") or 0)
        overall = "reported_malicious"
        summary = best["detail"]
    elif no_match and not unavailable:
        overall = "no_match"
        summary = "No match in queried threat-intelligence feeds"
    elif unavailable and not no_match:
        overall = "unavailable"
        summary = "Threat intelligence unavailable"
    else:
        overall = "partial"
        summary = "Some feeds had no match; other feeds were unavailable"

    return {
        "url": info["original"],
        "normalized_url": info["normalized_full_url"],
        "hostname": info["hostname"],
        "registered_domain": info["registered_domain"],
        "providers": results,
        "overall_status": overall,
        "confirmed": bool(confirmed),
        "reported": bool(reported),
        "best_match": best,
        "summary": summary,
        "unavailable_count": len(unavailable),
        "no_match_count": len(no_match),
    }

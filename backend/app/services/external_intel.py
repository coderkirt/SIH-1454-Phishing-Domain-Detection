"""Live domain and threat-intelligence lookups.

These run during a scan (short timeouts, fail softly if the internet is down):

1. DNS — does this domain exist?
2. RDAP — how old is the domain?
3. Google Safe Browsing — if GOOGLE_SAFE_BROWSING_API_KEY is set
4. URLhaus — free malware URL check used when Google is not configured
"""

import os
import re
import socket
import time
from datetime import datetime, timezone
from typing import Optional, List
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()

GSB_API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "").strip()
ENABLE_ONLINE_CHECKS = os.getenv("ENABLE_ONLINE_CHECKS", "true").strip().lower() != "false"
GSB_ENDPOINT = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
OPENPHISH_FEED = "https://openphish.com/feed.txt"

_domain_age_cache: dict = {}
_exists_cache: dict = {}
_sb_cache: dict = {}
_openphish_cache = {"urls": set(), "fetched_at": 0.0}


def check_domain_exists(host: str) -> Optional[bool]:
    """
    DNS lookup.
    True = domain resolves, False = does not exist, None = could not verify.
    """
    if not ENABLE_ONLINE_CHECKS:
        return None
    host = (host or "").split(":")[0].strip().lower().strip(".")
    if not host or host in {"localhost"}:
        return None
    if re.match(r"^[\d.]+$", host):
        return True
    if host in _exists_cache:
        return _exists_cache[host]

    exists: Optional[bool] = None
    try:
        socket.setdefaulttimeout(3)
        socket.getaddrinfo(host, None)
        exists = True
    except socket.gaierror:
        exists = False
    except OSError:
        exists = None

    _exists_cache[host] = exists
    return exists


def check_google_safe_browsing(url: str) -> Optional[List[str]]:
    """Google Safe Browsing. None = not configured / failed, [] = clean, list = threats."""
    if not ENABLE_ONLINE_CHECKS or not GSB_API_KEY:
        return None

    body = {
        "client": {"clientId": "cyberguard", "clientVersion": "1.0.0"},
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
    try:
        resp = requests.post(f"{GSB_ENDPOINT}?key={GSB_API_KEY}", json=body, timeout=5)
        resp.raise_for_status()
        matches = resp.json().get("matches", [])
        return sorted({m.get("threatType", "UNKNOWN") for m in matches})
    except requests.RequestException:
        return None


def _check_openphish(url: str, host: str) -> Optional[List[str]]:
    """Check the public OpenPhish feed. None = failed, [] = clean, list = flagged."""
    now = time.time()
    if now - _openphish_cache["fetched_at"] > 1800 or not _openphish_cache["urls"]:
        try:
            resp = requests.get(OPENPHISH_FEED, timeout=8)
            resp.raise_for_status()
            urls = {line.strip().lower() for line in resp.text.splitlines() if line.strip().startswith("http")}
            if urls:
                _openphish_cache["urls"] = urls
                _openphish_cache["fetched_at"] = now
        except requests.RequestException:
            if not _openphish_cache["urls"]:
                return None

    feed = _openphish_cache["urls"]
    if not feed:
        return None
    needle = (url or "").strip().lower().rstrip("/")
    host = (host or "").strip().lower()
    if needle in feed or (needle + "/") in {u.rstrip("/") for u in feed}:
        return ["PHISHING"]
    if host:
        for item in feed:
            item_host = urlparse(item).netloc.lower().split(":")[0]
            if item_host == host or item_host.endswith("." + host):
                return ["PHISHING"]
    return []


def check_safe_browsing(url: str, host: str = "") -> dict:
    """Backward-compatible wrapper around lookup_threat_intelligence.

    status is flagged / no_match / unavailable / partial. Never "clean".
    """
    from app.services.threat_intel import lookup_threat_intelligence

    intel = lookup_threat_intelligence(url)
    overall = intel.get("overall_status") or "unavailable"
    if overall == "confirmed_malicious":
        return {
            "status": "flagged",
            "label": intel.get("summary") or "Confirmed by threat intelligence",
            "threats": ["PHISHING"],
            "source": (intel.get("best_match") or {}).get("provider"),
        }
    if overall == "no_match":
        return {
            "status": "no_match",
            "label": "No match in queried threat-intelligence feeds",
            "threats": [],
            "source": None,
        }
    if overall == "partial":
        return {
            "status": "partial",
            "label": intel.get("summary") or "Partial threat-intelligence results",
            "threats": [],
            "source": None,
        }
    return {
        "status": "unavailable",
        "label": "Threat intelligence unavailable",
        "threats": [],
        "source": None,
    }


def get_domain_age_days(registrable_domain: str) -> Optional[int]:
    """Days since domain registration via public RDAP. None if unknown."""
    if not ENABLE_ONLINE_CHECKS:
        return None
    if not registrable_domain or "." not in registrable_domain:
        return None
    if re.match(r"^[\d.]+$", registrable_domain):
        return None

    if registrable_domain in _domain_age_cache:
        return _domain_age_cache[registrable_domain]

    age_days = None
    urls = [f"https://rdap.org/domain/{registrable_domain}"]
    if registrable_domain.endswith(".com"):
        urls.append(f"https://rdap.verisign.com/com/v1/domain/{registrable_domain}")
    elif registrable_domain.endswith(".net"):
        urls.append(f"https://rdap.verisign.com/net/v1/domain/{registrable_domain}")

    for url in urls:
        try:
            resp = requests.get(url, timeout=4, headers={"Accept": "application/rdap+json, application/json"})
            if resp.status_code != 200:
                continue
            events = resp.json().get("events") or []
            for event in events:
                action = (event.get("eventAction") or "").lower()
                if action in {"registration", "registered"}:
                    registered = datetime.fromisoformat(event["eventDate"].replace("Z", "+00:00"))
                    age_days = max((datetime.now(timezone.utc) - registered).days, 0)
                    break
            if age_days is not None:
                break
        except (requests.RequestException, ValueError, KeyError, TypeError):
            continue

    _domain_age_cache[registrable_domain] = age_days
    return age_days

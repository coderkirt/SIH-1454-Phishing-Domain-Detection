"""Detect aggressive / malware-style ads, not normal website ads.

News sites and shops often use Google Ads. That is not treated as a threat.
Piracy and scam pages often use popup / pop-under ad networks that push
malware. Those are the signals we score.
"""

import ipaddress
import os
import socket
from typing import Dict, List
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()

ENABLE_ONLINE_CHECKS = os.getenv("ENABLE_ONLINE_CHECKS", "true").strip().lower() != "false"

# High-risk popup / malvertising networks. Not Google Ads or Facebook Ads.
AGGRESSIVE_AD_NETWORKS = (
    "popads.net",
    "popads.com",
    "propellerads.com",
    "propellerads.net",
    "adsterra.com",
    "popcash.net",
    "hilltopads.com",
    "clickadu.com",
    "exoclick.com",
    "juicyads.com",
    "trafficjunky.net",
    "adcash.com",
    "popunder.net",
    "popunder.com",
    "ad-maven.com",
    "admaven.com",
    "revenuehits.com",
    "clickaine.com",
)

POPUP_PATTERNS = (
    "popunder",
    "pop-under",
    "window.open(",
    "onclick=\"window.open",
    "push notification",
    "enable notifications to continue",
    "allow notifications",
)

_ad_cache: dict = {}


def _is_private_host(host: str) -> bool:
    host = (host or "").split(":")[0].strip().lower()
    if not host or host in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError:
        return False
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return True
        except ValueError:
            continue
    return False


def count_html_clutter(text: str) -> Dict:
    """Count buttons, iframes, popup scripts, and overlay-style markup in HTML.

    This is a string count, not a rendered DOM. Normal Google Ads snippets
    do not match these thresholds by themselves.
    """
    blob = (text or "").lower()
    return {
        "buttons": (
            blob.count("<button")
            + blob.count('type="submit"')
            + blob.count("type='submit'")
            + blob.count('role="button"')
            + blob.count("role='button'")
        ),
        "iframes": blob.count("<iframe"),
        "popups": blob.count("window.open(") + blob.count("popunder") + blob.count("pop-under"),
        "overlays": (
            blob.count("position:fixed")
            + blob.count("position: fixed")
            + blob.count('aria-modal="true"')
            + blob.count("<dialog")
        ),
        "links": blob.count("<a "),
    }


def merge_clutter_counts(html_counts: Dict = None, page_signals: Dict = None) -> Dict:
    """Prefer the higher of fetched HTML counts and live page counts from the extension."""
    keys = ("buttons", "iframes", "popups", "overlays", "links")
    html_counts = html_counts or {}
    page_signals = page_signals or {}
    return {
        key: max(int(html_counts.get(key) or 0), int(page_signals.get(key) or 0))
        for key in keys
    }


def score_page_clutter(html_counts: Dict = None, page_signals: Dict = None) -> Dict:
    """Turn clutter counts into a capped fishy score.

    Busy legitimate shops can have many buttons. Thresholds stay high so
    normal pages are not marked FISHY. Aggressive popup pages still score.
    """
    counts = merge_clutter_counts(html_counts, page_signals)
    buttons = counts["buttons"]
    iframes = counts["iframes"]
    popups = counts["popups"]
    overlays = counts["overlays"]
    points = 0
    reasons = []

    if buttons >= 30:
        points += 15
        reasons.append(f"Unusually many buttons ({buttons}) — common on scam and prize pages")
    elif buttons >= 18:
        points += 8
        reasons.append(f"Busy page with many clickable buttons ({buttons})")

    if iframes >= 10:
        points += 12
        reasons.append(f"Many embedded frames ({iframes}) — often used for ads and popups")
    elif iframes >= 5:
        points += 6
        reasons.append(f"Several embedded frames ({iframes})")

    if popups >= 2:
        points += 15
        reasons.append("Page script tries to open extra windows or pop-unders")
    elif popups == 1:
        points += 8
        reasons.append("Page script can open another window")

    if overlays >= 8 and (buttons >= 10 or popups):
        points += 8
        reasons.append("Many overlay / modal popups on the page")

    points = min(points, 32)
    return {
        "points": points,
        "flagged": points >= 6,
        "reasons": reasons,
        "counts": counts,
        "label": reasons[0] if reasons else "Page layout does not look like a popup farm",
    }


def scan_text_for_ads(text: str) -> Dict:
    """Score HTML or a URL string for aggressive ad networks. No page JS is run."""
    blob = (text or "").lower()
    networks = [name for name in AGGRESSIVE_AD_NETWORKS if name in blob]
    popups = [name for name in POPUP_PATTERNS if name in blob]
    return {
        "networks": networks,
        "popup_tricks": popups,
        "flagged": bool(networks or popups),
        "clutter": count_html_clutter(text),
    }


def check_ad_signals(url: str) -> Dict:
    """
    Look at the URL, then optionally fetch a small HTML sample.
    Fails softly: if the page cannot be read, no extra points are added.
    """
    result = {
        "status": "skipped",
        "flagged": False,
        "networks": [],
        "popup_tricks": [],
        "clutter": count_html_clutter(""),
        "label": "Not checked",
    }
    if not url:
        return result

    from_url = scan_text_for_ads(url)
    if from_url["flagged"]:
        result.update({
            "status": "flagged",
            "flagged": True,
            "networks": from_url["networks"],
            "popup_tricks": from_url["popup_tricks"],
            "clutter": from_url.get("clutter") or count_html_clutter(url),
            "label": "Aggressive ad / popup network in the URL",
        })
        return result

    if not ENABLE_ONLINE_CHECKS:
        result["label"] = "Disabled"
        return result

    if url in _ad_cache:
        return _ad_cache[url]

    parsed = urlparse(url if "://" in url else f"https://{url}")
    if parsed.scheme not in {"http", "https"}:
        result["label"] = "Skipped"
        return result
    host = (parsed.hostname or "").lower()
    if _is_private_host(host):
        result["label"] = "Skipped — local address"
        _ad_cache[url] = result
        return result

    try:
        session = requests.Session()
        session.max_redirects = 3
        resp = session.get(
            parsed.geturl(),
            timeout=4,
            headers={"User-Agent": "CyberGuard/1.0 threat-check"},
            allow_redirects=True,
        )
        html = (resp.text or "")[:150000]
        found = scan_text_for_ads(html)
        clutter = found.get("clutter") or count_html_clutter(html)
        if found["flagged"]:
            result = {
                "status": "flagged",
                "flagged": True,
                "networks": found["networks"],
                "popup_tricks": found["popup_tricks"],
                "clutter": clutter,
                "label": "Page uses aggressive popup / malware-style ads",
            }
        else:
            result = {
                "status": "clean",
                "flagged": False,
                "networks": [],
                "popup_tricks": [],
                "clutter": clutter,
                "label": "No aggressive ad networks found",
            }
    except requests.RequestException:
        result = {
            "status": "unavailable",
            "flagged": False,
            "networks": [],
            "popup_tricks": [],
            "clutter": count_html_clutter(""),
            "label": "Could not read page ads",
        }

    _ad_cache[url] = result
    return result

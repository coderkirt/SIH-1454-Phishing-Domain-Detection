"""Offline threat-intel hooks so unit tests never call live feeds."""

from app.services.threat_intel import build_feed_index


def offline_providers(openphish_urls=None, phishtank=None, urlhaus=None, gsb=None):
    return {
        "openphish_index": build_feed_index(openphish_urls or []),
        "phishtank": phishtank or (lambda url: {"results": {"in_database": False}}),
        "urlhaus": urlhaus or (lambda url: {"query_status": "no_results"}),
        "gsb": gsb if gsb is not None else (lambda url: []),
    }


def failing_providers():
    def boom(_url=None):
        raise RuntimeError("simulated provider timeout")

    def boom_feed():
        raise RuntimeError("simulated feed unavailable")

    return {
        "openphish_lines": boom_feed,
        "phishtank": boom,
        "urlhaus": boom,
        "gsb": boom,
    }

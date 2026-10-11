"""Unit tests for the scan explanation caching layer."""

import time
from app.cache import (
    ScanExplanationCache,
    make_cache_key,
    normalize_url,
)
from app.schemas import (
    ExplainScanRequest,
    ExplainScanResponse,
    ThreatIndicatorItem,
)


def _sample_response(verdict: str = "PHISHING", summary: str = "Test summary") -> ExplainScanResponse:
    return ExplainScanResponse(
        verdict=verdict,
        risk_score=88.5,
        summary=summary,
        threat_breakdown=[
            ThreatIndicatorItem(tag="urgency_detected", explanation="High pressure detected", severity="high")
        ],
        actionable_recommendations=["Do not click", "Report to security team"],
        cached=False,
    )


def test_normalize_url():
    # Trailing slash and scheme
    assert normalize_url("HTTP://EXAMPLE.COM/login/") == "http://example.com/login"
    
    # Tracking parameters stripped and sorted query
    url_with_utm = "https://bank.com/portal?utm_source=ad&b=2&a=1&utm_medium=cpc"
    normalized = normalize_url(url_with_utm)
    assert "utm_source" not in normalized
    assert "utm_medium" not in normalized
    assert normalized == "https://bank.com/portal?a=1&b=2"

    # None and empty
    assert normalize_url(None) == ""
    assert normalize_url("   ") == ""


def test_make_cache_key_deterministic():
    req1 = ExplainScanRequest(
        scan_url="https://sbi-fake.top/login",
        content_text="Update KYC immediately",
        detected_brands=["SBI", "State Bank"],
        threat_tags=["Urgency_Detected", "Credential_Pressure"],
        risk_score=90.0,
        channel="SMS",
        top_k=4,
    )

    req2 = ExplainScanRequest(
        scan_url="HTTPS://sbi-fake.top/login/",  # casing and trailing slash differ
        content_text="Update   KYC immediately ",  # whitespace differs
        detected_brands=["state bank", "sbi"],   # order and casing differ
        threat_tags=["credential_pressure", "urgency_detected"], # order differs
        risk_score=90.04,                        # rounds to same 90.0
        channel="sms",                           # casing differs
        top_k=4,
    )

    req_diff = ExplainScanRequest(
        scan_url="https://different-domain.com",
        risk_score=10.0,
    )

    key1 = make_cache_key(req1)
    key2 = make_cache_key(req2)
    key_diff = make_cache_key(req_diff)

    assert key1 == key2
    assert key1.startswith("scan_exp_")
    assert key1 != key_diff


def test_cache_set_and_get():
    cache = ScanExplanationCache(max_size=10, default_ttl_seconds=60)
    req = ExplainScanRequest(scan_url="https://phish.xyz")
    key = make_cache_key(req)

    # Initial miss
    assert cache.get(key) is None

    # Store
    resp = _sample_response()
    cache.set(key, resp)

    # Cache hit
    cached = cache.get(key)
    assert cached is not None
    assert cached.verdict == "PHISHING"
    assert cached.cached is True
    # Ensure deepcopy isolation
    cached.verdict = "ALTERED"
    fresh_fetch = cache.get(key)
    assert fresh_fetch.verdict == "PHISHING"


def test_cache_ttl_expiration():
    cache = ScanExplanationCache(max_size=10, default_ttl_seconds=1)
    key = "test_expire_key"
    cache.set(key, _sample_response(), ttl_seconds=1)

    assert cache.get(key) is not None

    # Sleep past expiration
    time.sleep(1.1)

    assert cache.get(key) is None
    stats = cache.stats()
    assert stats["expirations"] >= 1


def test_cache_lru_eviction():
    # Capacity of 3 items
    cache = ScanExplanationCache(max_size=3, default_ttl_seconds=300)

    cache.set("key1", _sample_response(summary="First"))
    cache.set("key2", _sample_response(summary="Second"))
    cache.set("key3", _sample_response(summary="Third"))

    assert len(cache) == 3

    # Access key1 to make it most recently used (Order becomes: key2, key3, key1)
    assert cache.get("key1") is not None

    # Insert key4 -> should evict key2 (the oldest unaccessed)
    cache.set("key4", _sample_response(summary="Fourth"))

    assert len(cache) == 3
    assert cache.get("key2") is None  # evicted!
    assert cache.get("key1") is not None  # kept!
    assert cache.get("key3") is not None
    assert cache.get("key4") is not None

    stats = cache.stats()
    assert stats["evictions"] == 1


def test_cache_cleanup_and_stats():
    cache = ScanExplanationCache(max_size=5, default_ttl_seconds=1)
    cache.set("exp1", _sample_response(), ttl_seconds=1)
    cache.set("exp2", _sample_response(), ttl_seconds=1)
    cache.set("valid", _sample_response(), ttl_seconds=300)

    time.sleep(1.1)

    # Cleanup expired
    purged = cache.cleanup_expired()
    assert purged == 2
    assert len(cache) == 1
    assert "valid" in cache

    stats = cache.stats()
    assert stats["size"] == 1
    assert stats["expirations"] == 2

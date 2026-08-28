from tests.intel_fixtures import offline_providers
import pytest
from app.services.url_checker import URLChecker


def test_safe_url():
    """Test that legitimate URLs return LOW risk"""
    checker = URLChecker()
    result = checker.analyze("https://www.google.com", intel_providers=offline_providers())

    assert result["risk_level"] == "LOW"
    assert result["safe"] == True
    assert result["risk_score"] < 30


def test_phishing_url():
    """Test that phishing URLs return HIGH/CRITICAL risk"""
    checker = URLChecker()
    result = checker.analyze("https://paypa1.com", intel_providers=offline_providers())

    assert result["risk_level"] in ["HIGH", "CRITICAL"]
    assert result["safe"] == False
    assert result["risk_score"] >= 30
    assert len(result["reasons"]) > 0


def test_ip_based_url():
    """Test IP-based URLs are flagged"""
    checker = URLChecker()
    result = checker.analyze("http://192.168.1.1/login", intel_providers=offline_providers())

    assert result["risk_level"] in ["HIGH", "CRITICAL"]
    assert result["safe"] == False


def test_empty_url():
    """Test empty URL handling"""
    checker = URLChecker()
    # Should not crash
    result = checker.analyze("", intel_providers=offline_providers())
    assert isinstance(result, dict)


def test_url_without_protocol():
    """Test URL without protocol"""
    checker = URLChecker()
    # Should handle gracefully
    result = checker.analyze("google.com", intel_providers=offline_providers())
    assert isinstance(result, dict)


def test_piracy_url():
    """Piracy / streaming scam domains should be flagged"""
    checker = URLChecker()
    result = checker.analyze("https://hdhub4u.med", intel_providers=offline_providers())
    assert result["risk_level"] in ["HIGH", "CRITICAL"]
    assert result["safe"] is False
    assert "piracy_scam" in result["threat_tags"] or "suspicious_tld" in result["threat_tags"]


def test_brand_impersonation_sbi():
    """Fake bank domains should get a plain-language brand warning"""
    checker = URLChecker()
    result = checker.analyze("https://sbi-login.xyz", intel_providers=offline_providers())
    assert result["safe"] is False
    assert result["brand_impersonated"] == "sbi"
    assert "SBI" in result["simple_view"]["warning"]
    assert result["safe"] is False


def test_simple_and_technical_views():
    """Every analysis includes Simple View + Technical View"""
    checker = URLChecker()
    result = checker.analyze("https://paypa1.com", intel_providers=offline_providers())
    assert "simple_view" in result
    assert "technical_view" in result
    assert result["simple_view"]["verdict"]
    assert result["technical_view"]["risk_score"] >= 30


def test_aggressive_ads_in_url():
    """Popup / malware ad networks in the URL should be flagged."""
    from app.services.ad_signals import scan_text_for_ads

    found = scan_text_for_ads("https://tracker.propellerads.com/click?id=1")
    assert found["flagged"] is True
    assert "propellerads.com" in found["networks"]

    clean = scan_text_for_ads("https://www.google.com/search?q=news")
    assert clean["flagged"] is False


def test_page_clutter_is_fishy():
    """Crowded buttons / iframes / popups raise a fishy clutter score."""
    from app.services.ad_signals import score_page_clutter, scan_text_for_ads

    html = ("<button>Win</button>" * 40) + ("<iframe></iframe>" * 12) + ("window.open(" * 3)
    found = scan_text_for_ads(html)
    assert found["flagged"] is True
    scored = score_page_clutter(found["clutter"])
    assert scored["flagged"] is True
    assert scored["points"] >= 12
    assert scored["counts"]["buttons"] >= 30

    google_ads = scan_text_for_ads("googlesyndication.com pagead doubleclick.net")
    assert google_ads["flagged"] is False
    assert score_page_clutter(google_ads["clutter"])["flagged"] is False

    checker = URLChecker()
    result = checker.analyze(
        "https://example.com",
        page_signals={"buttons": 48, "iframes": 14, "popups": 3, "overlays": 12, "links": 80},
        intel_providers=offline_providers(),
    )
    assert result["risk_score"] >= 30
    assert result["risk_level"] == "MEDIUM"
    assert result["safe"] is False
    assert "page_clutter" in result["threat_tags"]


def test_shortener_detected():
    from app.services.redirects import is_shortener

    assert is_shortener("https://bit.ly/abc123") is True
    assert is_shortener("https://tinyurl.com/abc") is True
    assert is_shortener("https://www.google.com") is False


def test_nonexistent_domain():
    """Made-up domains should be reported as not existing."""
    checker = URLChecker()
    result = checker.analyze(
        "https://this-domain-does-not-exist-zzqwxk123.com",
        intel_providers=offline_providers(),
    )
    assert result["details"]["domain_exists"] is False
    assert result["safe"] is False
    assert "domain_not_found" in result["threat_tags"]
    assert "does not exist" in result["simple_view"]["warning"].lower()


def test_cloudflare_phishing_interstitial_is_not_safe():
    """PhishTank suspected sites often show a Cloudflare 'Suspected Phishing' page."""
    checker = URLChecker()
    result = checker.analyze(
        "https://recent-bank-login.test/session",
        page_signals={
            "title": "Warning | Suspected Phishing",
            "heading": "Suspected Phishing",
            "snippet": "This website has been reported for potential phishing. Phishing is when a site attempts to steal sensitive information.",
            "buttons": 2,
            "iframes": 1,
            "popups": 0,
            "overlays": 0,
            "links": 2,
        },
        intel_providers=offline_providers(),
    )
    assert result["safe"] is False
    assert result["risk_level"] in {"HIGH", "CRITICAL"}
    assert result["risk_score"] >= 50
    assert "vendor_phishing_interstitial" in result["threat_tags"]


def test_phishtank_website_is_not_flagged_for_the_word_phishing():
    checker = URLChecker()
    result = checker.analyze(
        "https://www.phishtank.com/phish_detail.php?phish_id=1",
        page_signals={
            "title": "PhishTank > Search",
            "heading": "PhishTank",
            "snippet": "Suspected phishing URLs submitted by the community.",
        },
        intel_providers=offline_providers(),
    )
    assert result["risk_level"] == "LOW"
    assert result["safe"] is True
    assert "vendor_phishing_interstitial" not in result["threat_tags"]


def test_unverified_phishtank_report_overrides_empty_dump():
    from app.services.threat_intel import build_feed_index

    checker = URLChecker()
    result = checker.analyze(
        "https://suspected-phish.test/login",
        intel_providers={
            "openphish_index": build_feed_index([]),
            "phishtank_index": build_feed_index([]),
            "phishtank": lambda url: {"results": {"in_database": True, "verified": False, "valid": True}},
            "urlhaus": lambda url: {"query_status": "no_results"},
            "gsb": lambda url: [],
        },
    )
    assert result["safe"] is False
    assert result["risk_level"] in {"MEDIUM", "HIGH", "CRITICAL"}
    assert "reported_phish" in result["threat_tags"] or "threat_intel" in result["threat_tags"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

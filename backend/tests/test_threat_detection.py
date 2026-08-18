import pytest
from app.services.url_checker import URLChecker


def test_safe_url():
    """Test that legitimate URLs return LOW risk"""
    checker = URLChecker()
    result = checker.analyze("https://www.google.com")

    assert result["risk_level"] == "LOW"
    assert result["safe"] == True
    assert result["risk_score"] < 30


def test_phishing_url():
    """Test that phishing URLs return HIGH/CRITICAL risk"""
    checker = URLChecker()
    result = checker.analyze("https://paypa1.com")

    assert result["risk_level"] in ["HIGH", "CRITICAL"]
    assert result["safe"] == False
    assert result["risk_score"] >= 30
    assert len(result["reasons"]) > 0


def test_ip_based_url():
    """Test IP-based URLs are flagged"""
    checker = URLChecker()
    result = checker.analyze("http://192.168.1.1/login")

    assert result["risk_level"] in ["HIGH", "CRITICAL"]
    assert result["safe"] == False


def test_empty_url():
    """Test empty URL handling"""
    checker = URLChecker()
    # Should not crash
    result = checker.analyze("")
    assert isinstance(result, dict)


def test_url_without_protocol():
    """Test URL without protocol"""
    checker = URLChecker()
    # Should handle gracefully
    result = checker.analyze("google.com")
    assert isinstance(result, dict)


def test_piracy_url():
    """Piracy / streaming scam domains should be flagged"""
    checker = URLChecker()
    result = checker.analyze("https://hdhub4u.med")
    assert result["risk_level"] in ["HIGH", "CRITICAL"]
    assert result["safe"] is False
    assert "piracy_scam" in result["threat_tags"] or "suspicious_tld" in result["threat_tags"]


def test_brand_impersonation_sbi():
    """Fake bank domains should get a plain-language brand warning"""
    checker = URLChecker()
    result = checker.analyze("https://sbi-login.xyz")
    assert result["safe"] is False
    assert result["brand_impersonated"] == "sbi"
    assert "SBI" in result["simple_view"]["warning"]
    assert result["safe"] is False


def test_simple_and_technical_views():
    """Every analysis includes Simple View + Technical View"""
    checker = URLChecker()
    result = checker.analyze("https://paypa1.com")
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


def test_shortener_detected():
    from app.services.redirects import is_shortener

    assert is_shortener("https://bit.ly/abc123") is True
    assert is_shortener("https://tinyurl.com/abc") is True
    assert is_shortener("https://www.google.com") is False


def test_nonexistent_domain():
    """Made-up domains should be reported as not existing."""
    checker = URLChecker()
    result = checker.analyze("https://this-domain-does-not-exist-zzqwxk123.com")
    assert result["details"]["domain_exists"] is False
    assert result["safe"] is False
    assert "domain_not_found" in result["threat_tags"]
    assert "does not exist" in result["simple_view"]["warning"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

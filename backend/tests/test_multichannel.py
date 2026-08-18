from app.services.url_extractor import extract_urls
from app.services.content_normalizer import normalize_content
from app.services.risk_engine import fuse
from app.services.brand_detector import detect_impersonation
from app.services.sender_analyzer import analyze_sender
from app.services.ssrf import safe_to_fetch, UnsafeURLError, assert_public_http_url
from app.services.attachments import inspect_filename
from app.services.mobile_source import MobileMessageSource
from app.services.report_service import build_export
from app.services.reputation import get_reputation
import pytest


def test_extracts_multiple_urls():
    text = """
    Your account will be blocked.
    Verify here: https://example1.com
    Backup: https://example2.com/login
    Click: bit.ly/abc123
    """
    urls = extract_urls(text)
    found = {item["url"] for item in urls}
    assert any("example1.com" in u for u in found)
    assert any("example2.com" in u for u in found)
    assert any("bit.ly" in u for u in found)


def test_extracts_html_href():
    urls = extract_urls('<a href="https://phish.example/login">click</a>')
    assert any("phish.example" in item["url"] for item in urls)


def test_normalize_email():
    data = normalize_content("email", "Urgent KYC https://sbi-secure.example")
    assert data["source_type"] == "email"
    assert data["urls"]
    assert data["store_raw"] is False


def test_psych_alone_not_critical():
    fused = fuse({
        "url": 0, "domain": 0, "ml": 0, "nlp": 80, "psychological": 80,
        "threat_intel": 0, "brand": 0, "redirect": 0, "sender": 0, "community": 0,
    })
    assert fused["risk_level"] in ("LOW", "MEDIUM")
    assert fused["risk_score"] <= 35
    assert "accuracy" not in fused["methodology"].lower() or "not" in fused["methodology"].lower()


def test_multi_signal_can_be_high():
    fused = fuse({
        "url": 85, "domain": 90, "ml": 80, "nlp": 70, "psychological": 78,
        "threat_intel": 80, "brand": 80, "redirect": 40, "sender": 40, "community": 70,
    })
    assert fused["risk_score"] >= 50
    assert fused["risk_level"] in ("HIGH", "CRITICAL")


def test_impersonation_needs_signals():
    weak = detect_impersonation("Visit SBI website for offers", ["https://news.example"], {})
    strong = detect_impersonation(
        "Your SBI account requires verification. Enter OTP.",
        ["https://sbi-secure-random.example"],
        {"credential": True, "urgency": True, "suspicious_domain": True},
    )
    assert strong["impersonated"] == "sbi"
    assert strong["score"] >= weak["score"]
    assert weak["impersonated"] is None or weak["score"] < strong["score"]


def test_sender_mismatch():
    result = analyze_sender(
        {"display_name": "SBI Bank", "email": "support@random-domain.example"},
        "Your SBI account requires verification",
    )
    assert result["available"] is True
    assert result["mismatch"] is True


def test_sender_skipped_without_metadata():
    result = analyze_sender({}, "hello")
    assert result["available"] is False
    assert result["score"] == 0


def test_ssrf_blocks_localhost():
    ok, reason = safe_to_fetch("http://127.0.0.1/secret")
    assert ok is False
    assert reason
    ok, _ = safe_to_fetch("http://localhost/admin")
    assert ok is False
    with pytest.raises(UnsafeURLError):
        assert_public_http_url("http://169.254.169.254/latest/meta-data/")


def test_ssrf_allows_public_https():
    ok, reason = safe_to_fetch("https://example.com")
    assert ok is True
    assert reason is None


def test_attachment_metadata_only():
    result = inspect_filename("invoice.exe", "application/octet-stream")
    assert result["executed"] is False
    assert result["deep_scan"] == "PLANNED"
    assert result["risk_score"] >= 80


def test_mobile_sms_is_planned():
    info = MobileMessageSource().collect()
    assert info["implemented"] is False


def test_export_omits_raw_text():
    payload = {
        "scan_id": 1,
        "source_type": "whatsapp",
        "risk_score": 92,
        "risk_level": "CRITICAL",
        "scam_risk": 92,
        "model_confidence": 80,
        "threat_tags": ["urgency_detected"],
        "reasons": ["Urgency"],
        "explanation": {"what_to_do": "Do not enter OTP."},
        "links": [{"url": "https://evil.example", "domain": "evil.example", "risk_score": 90, "classification": "CRITICAL"}],
        "community": {"summary": "No community reports yet.", "total_reports": 0},
        "raw_text": "secret OTP 123456",
    }
    exported = build_export(payload)
    assert "raw_text" not in exported
    assert "123456" not in str(exported)
    assert exported["risk_score"] == 92


def test_reputation_empty_domain():
    data = get_reputation("no-such-domain-for-test.example")
    assert data["total_reports"] == 0
    assert "proof" not in (data["summary"] or "").lower() or "not" in data["summary"].lower()

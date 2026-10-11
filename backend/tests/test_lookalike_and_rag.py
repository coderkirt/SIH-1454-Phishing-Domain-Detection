from app.services.decision_engine import calculate_final_risk
from app.services.explanation import build_explanation
from app.services.url_checker import URLChecker
from app.services.url_normalize import normalize_url
from tests.intel_fixtures import offline_providers


def test_paypa1_is_not_safe():
    result = URLChecker().analyze("https://paypa1.com", intel_providers=offline_providers())
    assert result["safe"] is False
    assert result["risk_level"] in {"MEDIUM", "HIGH", "CRITICAL"}
    assert result["classification"] in {"SUSPICIOUS", "CONFIRMED_MALICIOUS"}
    assert result["risk_score"] >= 50
    assert "brand_impersonation" in result["threat_tags"] or "phishing" in result["threat_tags"]


def test_reset_score_cannot_clear_lookalike_tags():
    decision = calculate_final_risk(
        threat_intelligence={
            "overall_status": "no_match",
            "confirmed": False,
            "providers": [],
        },
        heuristic_score=20,
        ml_score=20,
        heuristic_tags=["brand_impersonation", "phishing"],
        heuristic_reasons=["Error parsing URL: tls failed"],
        url_features=normalize_url("https://paypa1.com"),
        rag_assessment={
            "status": "ok",
            "suspicion_score": 0,
            "rule_id": "https-not-enough",
            "rule_summary": "HTTPS is not proof of safety.",
            "citations": [],
        },
    )
    assert decision["safe"] is False
    assert decision["classification"] == "SUSPICIOUS"
    assert decision["risk_score"] >= 50


def test_rag_benign_cannot_rewrite_unsafe_lookalike(monkeypatch):
    monkeypatch.setattr(
        "app.services.explanation.fetch_rag_explanation_sync",
        lambda **_kwargs: {
            "verdict": "BENIGN",
            "summary": "This destination looks safe.",
            "threat_breakdown": [],
            "actionable_recommendations": ["No action needed."],
            "citations": [],
        },
    )
    explained = build_explanation({
        "url": "https://paypa1.com",
        "risk_level": "HIGH",
        "risk_score": 80,
        "safe": False,
        "threat_tags": ["brand_impersonation", "phishing"],
        "brand_impersonated": "paypal",
        "reasons": ["Looks like a fake paypal website"],
    })
    assert explained["rag_grounded"] is False
    assert "safe" not in explained["headline"].lower()
    assert "benign" not in explained["headline"].lower()
    assert "paypal" in explained["what"].lower() or "pretending" in explained["what"].lower()


def test_rag_phishing_explanation_is_used_when_scan_is_unsafe(monkeypatch):
    monkeypatch.setattr(
        "app.services.explanation.fetch_rag_explanation_sync",
        lambda **_kwargs: {
            "verdict": "PHISHING",
            "summary": "Lookalike PayPal domain used to steal credentials.",
            "threat_breakdown": [{"explanation": "paypa1 impersonates paypal.com"}],
            "actionable_recommendations": ["Close the page."],
            "citations": [{"source": "brand-guidance"}],
        },
    )
    explained = build_explanation({
        "url": "https://paypa1.com",
        "risk_level": "HIGH",
        "risk_score": 80,
        "safe": False,
        "threat_tags": ["brand_impersonation"],
        "brand_impersonated": "paypal",
        "reasons": ["Looks like a fake paypal website"],
    })
    assert explained["rag_grounded"] is True
    assert "PHISHING" in explained["headline"]
    assert "lookalike" in explained["what"].lower()

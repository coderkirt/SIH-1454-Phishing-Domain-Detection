from app.services.explanation import build_explanation


def test_blank_rag_summary_is_not_grounded(monkeypatch):
    monkeypatch.setattr(
        "app.services.explanation.fetch_rag_explanation_sync",
        lambda **_kwargs: {"verdict": "PHISHING", "summary": "   ", "citations": []},
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
    assert explained["rag_grounded"] is False

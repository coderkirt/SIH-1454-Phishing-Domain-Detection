from app.search import assess_facts


def test_lookalike_facts_fire_brand_rule():
    result = assess_facts({
        "url": "https://paypa1.com/secure-login",
        "hostname": "paypa1.com",
        "registered_domain": "paypa1.com",
        "path": "/secure-login",
        "lookalike": True,
        "secure_login_tokens": True,
        "brand_impersonated": "paypal",
        "official_brand_domain": False,
        "https": True,
        "heuristic_tags": ["brand_impersonation"],
        "local_activity": {"status": "unknown", "scans": 0, "scam_reports": 0, "risky_reports": 0, "safe_reports": 0},
    })
    assert result["status"] == "ok"
    assert result["rule_id"] in {"lookalike-brand", "brand-vs-domain", "secure-login-tokens"}
    assert result["suspicion_score"] >= 48
    assert result["citations"]


def test_trusted_homepage_ignores_vague_notes():
    result = assess_facts({
        "url": "https://www.google.com",
        "hostname": "www.google.com",
        "registered_domain": "google.com",
        "trusted_destination": True,
        "official_brand_domain": True,
        "https": True,
        "lookalike": False,
        "heuristic_tags": [],
        "local_activity": {"status": "unknown", "scans": 0, "scam_reports": 0, "risky_reports": 0, "safe_reports": 0},
    })
    assert result["status"] == "ok"
    assert result["suspicion_score"] == 0
    assert result["rule_id"] is None


def test_explains_provided_30day_counts_without_inventing():
    result = assess_facts({
        "url": "https://odd.example.test",
        "hostname": "odd.example.test",
        "registered_domain": "example.test",
        "heuristic_tags": [],
        "local_activity": {
            "window_days": 30,
            "status": "observed",
            "scans": 6,
            "signed_in_users": 2,
            "high_risk_scans": 1,
            "scam_reports": 3,
            "risky_reports": 1,
            "safe_reports": 0,
        },
    })
    assert result["status"] == "ok"
    assert result["rule_id"] == "local-scam-reports"
    assert "3 scam reports" in result["rule_summary"]
    assert "6 scans" in result["activity_note"]

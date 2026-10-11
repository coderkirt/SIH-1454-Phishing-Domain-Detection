from app.services.decision_engine import _activity_floor, _activity_suspicion, calculate_final_risk
from app.services.url_normalize import normalize_url


def _intel():
    return {"overall_status": "no_match", "confirmed": False, "providers": []}


def test_repeat_visits_do_not_raise_a_legitimate_site():
    activity = {
        "scans": 40,
        "this_browser_opens": 12,
        "opens": 20,
        "users_opened": 8,
        "scam_reports": 0,
        "risky_reports": 0,
        "high_risk_scans": 0,
    }
    assert _activity_suspicion(activity) == 0
    assert _activity_floor(_activity_suspicion(activity)) == 0
    decision = calculate_final_risk(
        threat_intelligence=_intel(),
        heuristic_score=0,
        ml_score=0,
        heuristic_tags=[],
        heuristic_reasons=[],
        url_features=normalize_url("https://www.youtube.com"),
        local_activity={**activity, "status": "observed", "window_days": 30},
        trusted_destination=True,
    )
    assert decision["risk_score"] == 0
    assert decision["risk_level"] == "LOW"
    assert decision["safe"] is True


def test_github_danger_counts_are_ignored_unless_link_is_already_suspicious():
    activity = {
        "status": "observed",
        "scans": 18,
        "this_browser_opens": 9,
        "opens": 14,
        "users_opened": 6,
        "scam_reports": 4,
        "risky_reports": 2,
        "high_risk_scans": 8,
        "window_days": 30,
    }
    github = calculate_final_risk(
        threat_intelligence=_intel(),
        heuristic_score=0,
        ml_score=0,
        heuristic_tags=[],
        heuristic_reasons=[],
        url_features=normalize_url("https://github.com"),
        local_activity=activity,
        trusted_destination=True,
    )
    assert github["risk_score"] == 0
    assert github["risk_level"] == "LOW"
    assert github["safe"] is True
    assert github["evidence"]["local_activity"]["used"] is False
    assert github["evidence"]["local_activity"]["suspicion_score"] == 0

    lookalike = calculate_final_risk(
        threat_intelligence=_intel(),
        heuristic_score=40,
        ml_score=40,
        heuristic_tags=["brand_impersonation", "phishing"],
        heuristic_reasons=["Looks like a fake paypal website"],
        url_features=normalize_url("https://paypa1.com"),
        local_activity=activity,
    )
    assert lookalike["risk_score"] >= 50
    assert lookalike["safe"] is False
    assert lookalike["evidence"]["local_activity"]["used"] is True


def test_empty_activity_does_not_raise_score():
    decision = calculate_final_risk(
        threat_intelligence=_intel(),
        heuristic_score=8,
        ml_score=8,
        heuristic_tags=[],
        heuristic_reasons=[],
        url_features=normalize_url("https://example.com"),
        local_activity={"status": "unknown", "scans": 0, "opens": 0, "this_browser_opens": 0},
    )
    assert decision["evidence"]["local_activity"]["used"] is False
    assert decision["risk_score"] == 8

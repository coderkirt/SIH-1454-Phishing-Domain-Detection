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

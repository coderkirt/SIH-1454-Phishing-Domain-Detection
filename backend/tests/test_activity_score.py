from app.services.decision_engine import _activity_floor, _activity_suspicion, calculate_final_risk
from app.services.url_normalize import normalize_url


def _intel():
    return {"overall_status": "no_match", "confirmed": False, "providers": []}


def test_activity_suspicion_uses_browser_opens():
    suspicion = _activity_suspicion({
        "scans": 2,
        "this_browser_opens": 4,
        "opens": 0,
        "users_opened": 0,
        "scam_reports": 0,
        "risky_reports": 0,
        "high_risk_scans": 0,
    })
    assert suspicion >= 8 + 4 * 3
    assert _activity_floor(suspicion) >= 12


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

import sqlite3
from datetime import datetime, timedelta

from app.services.decision_engine import calculate_final_risk
from app.services.local_activity import empty_activity, get_local_activity_30d
from app.services.url_normalize import normalize_url
from app.services.visit_service import count_visits_30d, record_visit


def _intel_no_match():
    return {
        "overall_status": "no_match",
        "confirmed": False,
        "providers": [
            {
                "provider": "OpenPhish",
                "status": "no_match",
                "found": False,
                "match_type": "",
                "confidence": 0,
                "detail": "no match",
            }
        ],
    }


def _memory_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE url_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            normalized_url VARCHAR(500) NOT NULL,
            registered_domain VARCHAR(200),
            client_id VARCHAR(80) NOT NULL,
            user_id INTEGER,
            opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE url_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            url VARCHAR(500) NOT NULL,
            risk_level VARCHAR(20),
            risk_score FLOAT,
            ml_confidence FLOAT DEFAULT 0.0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE content_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE extracted_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER,
            url VARCHAR(500),
            domain VARCHAR(200),
            classification VARCHAR(20)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE user_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url VARCHAR(500),
            domain VARCHAR(200),
            user_label VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return conn


def test_same_client_within_10_minutes_is_one_visit():
    conn = _memory_db()
    now = datetime(2026, 10, 11, 12, 0, 0)
    first = record_visit("https://paypa1.com/login", "install-aaaa-1111", conn=conn, now=now)
    second = record_visit(
        "https://paypa1.com/login/?x=1",
        "install-aaaa-1111",
        conn=conn,
        now=now + timedelta(minutes=3),
    )
    later = record_visit(
        "https://paypa1.com/login",
        "install-aaaa-1111",
        conn=conn,
        now=now + timedelta(minutes=11),
    )
    conn.commit()
    assert first["recorded"] is True
    assert second["deduped"] is True
    assert later["recorded"] is True
    counts = count_visits_30d("https://paypa1.com/login", "paypa1.com", conn=conn, now=now + timedelta(minutes=12))
    assert counts["opens"] == 2
    assert counts["users_opened"] == 1
    conn.close()


def test_distinct_clients_increment_users_opened():
    conn = _memory_db()
    now = datetime(2026, 10, 11, 12, 0, 0)
    record_visit("https://odd.example.test/a", "install-client-one", conn=conn, now=now)
    record_visit("https://odd.example.test/a", "install-client-two", conn=conn, now=now)
    conn.commit()
    counts = count_visits_30d("https://odd.example.test/a", "example.test", conn=conn, now=now)
    assert counts["opens"] == 2
    assert counts["users_opened"] == 2
    conn.close()


def test_visit_log_does_not_need_a_scan_row():
    conn = _memory_db()
    now = datetime(2026, 10, 11, 12, 0, 0)
    record_visit("https://cached.example.test", "install-cached-999", conn=conn, now=now)
    conn.commit()
    activity = get_local_activity_30d("https://cached.example.test", "example.test", conn=conn, now=now)
    assert activity["opens"] == 1
    assert activity["users_opened"] == 1
    assert activity["scans"] == 0
    assert activity["status"] == "observed"
    conn.close()


def test_zero_visits_is_unknown():
    conn = _memory_db()
    now = datetime(2026, 10, 11, 12, 0, 0)
    activity = get_local_activity_30d("https://never-opened.test", "never-opened.test", conn=conn, now=now)
    assert activity["opens"] == 0
    assert activity["users_opened"] == 0
    assert activity["status"] == "unknown"
    conn.close()


def test_high_opens_do_not_clear_lookalike():
    decision = calculate_final_risk(
        threat_intelligence=_intel_no_match(),
        heuristic_score=40,
        ml_score=40,
        heuristic_tags=["brand_impersonation"],
        heuristic_reasons=["Looks like a fake paypal website"],
        url_features=normalize_url("https://paypa1.com"),
        local_activity={
            "status": "observed",
            "opens": 80,
            "users_opened": 25,
            "this_browser_opens": 12,
            "this_browser_status": "observed",
            "scans": 0,
            "scam_reports": 0,
            "risky_reports": 0,
            "safe_reports": 0,
            "signed_in_users": 0,
            "high_risk_scans": 0,
            "window_days": 30,
        },
    )
    assert decision["safe"] is False
    assert decision["risk_score"] >= 40
    assert "do not clear" in " ".join(decision["reasons"]).lower()


def test_browser_opens_do_not_flip_trusted_site():
    decision = calculate_final_risk(
        threat_intelligence=_intel_no_match(),
        heuristic_score=5,
        ml_score=5,
        heuristic_tags=[],
        heuristic_reasons=[],
        url_features=normalize_url("https://www.google.com"),
        local_activity={
            **empty_activity("google.com"),
            "this_browser_opens": 40,
            "this_browser_status": "observed",
        },
        trusted_destination=True,
    )
    assert decision["safe"] is True
    assert decision["risk_level"] == "LOW"
    assert decision["evidence"]["local_activity"]["this_browser_opens"] == 40
    assert decision["evidence"]["local_activity"]["this_browser_status"] == "observed"


def test_javascript_url_is_not_recorded():
    result = record_visit("javascript:alert(1)", "client-abcdef")
    assert result["recorded"] is False
    assert result["reason"] == "invalid_url"

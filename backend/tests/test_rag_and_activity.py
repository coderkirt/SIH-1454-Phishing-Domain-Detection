import sqlite3
from datetime import datetime, timedelta

from app.services.decision_engine import calculate_final_risk
from app.services.local_activity import empty_activity, get_local_activity_30d
from app.services.rag_client import assess_link, collect_facts, unavailable
from app.services.risk_engine import fuse
from app.services.url_checker import URLChecker
from app.services.url_normalize import normalize_url
from app.services.warnings import build_simple_view, build_technical_view
from tests.intel_fixtures import offline_providers


def _intel(status, provider="OpenPhish", match_type="exact_url"):
    found = status in {"confirmed_malicious", "reported_malicious"}
    return {
        "overall_status": status,
        "confirmed": status == "confirmed_malicious",
        "providers": [
            {
                "provider": provider,
                "status": status,
                "found": found,
                "match_type": match_type,
                "confidence": 0.9 if found else 0,
                "detail": f"{provider} {status}",
            }
        ],
    }


def _memory_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE url_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            url VARCHAR(500) NOT NULL,
            risk_level VARCHAR(20),
            risk_score FLOAT,
            ml_confidence FLOAT DEFAULT 0.0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE content_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            source_type VARCHAR(30),
            url VARCHAR(500),
            risk_level VARCHAR(20),
            risk_score FLOAT,
            scam_risk FLOAT,
            confidence FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE extracted_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER,
            url VARCHAR(500),
            domain VARCHAR(200),
            risk_score FLOAT,
            classification VARCHAR(20)
        );
        CREATE TABLE user_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            url VARCHAR(500),
            domain VARCHAR(200),
            user_label VARCHAR(20),
            reason VARCHAR(300),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE url_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            normalized_url VARCHAR(500) NOT NULL,
            registered_domain VARCHAR(200),
            client_id VARCHAR(80) NOT NULL,
            user_id INTEGER,
            opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    return conn


def test_confirmed_intel_not_overruled_by_low_rag():
    decision = calculate_final_risk(
        threat_intelligence=_intel("confirmed_malicious"),
        heuristic_score=8,
        ml_score=8,
        heuristic_tags=[],
        heuristic_reasons=[],
        url_features=normalize_url("https://phish.example.test/login"),
        rag_assessment={
            "status": "ok",
            "suspicion_score": 5,
            "rule_id": "https-not-enough",
            "rule_summary": "HTTPS is not proof of safety.",
            "citations": ["https-not-enough"],
        },
        local_activity={"status": "observed", "scans": 40, "safe_reports": 20, "scam_reports": 0, "risky_reports": 0, "signed_in_users": 8, "high_risk_scans": 0, "window_days": 30},
    )
    assert decision["classification"] == "CONFIRMED_MALICIOUS"
    assert decision["safe"] is False
    assert decision["risk_score"] >= 70


def test_trusted_google_not_flipped_by_vague_rag():
    decision = calculate_final_risk(
        threat_intelligence=_intel("no_match"),
        heuristic_score=5,
        ml_score=5,
        heuristic_tags=[],
        heuristic_reasons=[],
        url_features=normalize_url("https://www.google.com"),
        rag_assessment={
            "status": "ok",
            "suspicion_score": 78,
            "rule_id": "lookalike-brand",
            "rule_summary": "Vague lookalike note.",
            "citations": ["lookalike-brand"],
        },
        local_activity=empty_activity("google.com"),
        trusted_destination=True,
    )
    assert decision["classification"] != "CONFIRMED_MALICIOUS"
    assert decision["safe"] is True
    assert decision["risk_level"] == "LOW"
    assert "rag_suspicious" not in decision["threat_tags"]


def test_rag_timeout_omits_weight_and_does_not_lower_score():
    heuristics = calculate_final_risk(
        threat_intelligence=_intel("no_match"),
        heuristic_score=44,
        ml_score=44,
        heuristic_tags=["suspicious_tld"],
        heuristic_reasons=["Suspicious domain ending (.xyz)"],
        url_features=normalize_url("https://odd.xyz/home"),
    )
    timed_out = calculate_final_risk(
        threat_intelligence=_intel("no_match"),
        heuristic_score=44,
        ml_score=44,
        heuristic_tags=["suspicious_tld"],
        heuristic_reasons=["Suspicious domain ending (.xyz)"],
        url_features=normalize_url("https://odd.xyz/home"),
        rag_assessment=unavailable("timeout"),
    )
    assert timed_out["evidence"]["rag"]["status"] == "unavailable"
    assert timed_out["evidence"]["rag"]["suspicion_score"] is None
    assert timed_out["risk_score"] >= heuristics["risk_score"]
    assert timed_out["classification"] == heuristics["classification"]


def test_zero_30day_activity_is_unknown_not_safe_by_history():
    activity = empty_activity("newphish.test")
    assert activity["status"] == "unknown"
    decision = calculate_final_risk(
        threat_intelligence=_intel("no_match"),
        heuristic_score=55,
        ml_score=55,
        heuristic_tags=["brand_impersonation"],
        heuristic_reasons=["Looks like a fake paypal website"],
        url_features=normalize_url("https://paypa1.com"),
        local_activity=activity,
    )
    assert decision["evidence"]["local_activity"]["status"] == "unknown"
    assert decision["safe"] is False
    assert decision["classification"] == "SUSPICIOUS"


def test_scam_reports_raise_and_scan_volume_does_not_clear_lookalike():
    baseline = calculate_final_risk(
        threat_intelligence=_intel("no_match"),
        heuristic_score=40,
        ml_score=40,
        heuristic_tags=["brand_impersonation"],
        heuristic_reasons=["Looks like a fake paypal website"],
        url_features=normalize_url("https://paypa1.com"),
        local_activity={"status": "unknown", "scans": 0, "scam_reports": 0, "risky_reports": 0, "safe_reports": 0, "signed_in_users": 0, "high_risk_scans": 0, "window_days": 30},
    )
    busy_but_clean = calculate_final_risk(
        threat_intelligence=_intel("no_match"),
        heuristic_score=40,
        ml_score=40,
        heuristic_tags=["brand_impersonation"],
        heuristic_reasons=["Looks like a fake paypal website"],
        url_features=normalize_url("https://paypa1.com"),
        local_activity={"status": "observed", "scans": 80, "scam_reports": 0, "risky_reports": 0, "safe_reports": 12, "signed_in_users": 20, "high_risk_scans": 0, "window_days": 30},
    )
    scammy = calculate_final_risk(
        threat_intelligence=_intel("no_match"),
        heuristic_score=20,
        ml_score=20,
        heuristic_tags=["brand_impersonation"],
        heuristic_reasons=["Looks like a fake paypal website"],
        url_features=normalize_url("https://paypa1.com"),
        local_activity={"status": "observed", "scans": 4, "scam_reports": 4, "risky_reports": 1, "safe_reports": 0, "signed_in_users": 3, "high_risk_scans": 2, "window_days": 30},
    )
    assert busy_but_clean["risk_score"] >= baseline["risk_score"]
    assert busy_but_clean["safe"] is False
    assert "do not clear" in " ".join(busy_but_clean["reasons"]).lower()
    assert scammy["risk_score"] > 20
    assert scammy["safe"] is False
    assert "local_scam_reports" in scammy["threat_tags"]


def test_rag_only_cannot_mark_safe():
    decision = calculate_final_risk(
        threat_intelligence=_intel("no_match"),
        heuristic_score=0,
        ml_score=0,
        heuristic_tags=[],
        heuristic_reasons=[],
        url_features=normalize_url("https://odd-login.example.test/secure"),
        rag_assessment={
            "status": "ok",
            "suspicion_score": 78,
            "rule_id": "lookalike-brand",
            "rule_summary": "Lookalike brand domain.",
            "citations": ["lookalike-brand"],
        },
        local_activity=empty_activity("example.test"),
    )
    assert decision["safe"] is False
    assert decision["classification"] == "SUSPICIOUS"
    assert "rag_suspicious" in decision["threat_tags"]
    assert decision["reasons"][0].startswith("Lookalike")


def test_rag_client_disabled_is_unavailable_not_zero():
    result = assess_link({"url": "https://example.test"})
    assert result["status"] == "unavailable"
    assert result["suspicion_score"] is None


def test_local_activity_counts_and_unknown_when_empty():
    conn = _memory_db()
    now = datetime(2026, 10, 11, 12, 0, 0)
    recent = (now - timedelta(days=2)).isoformat(sep=" ", timespec="seconds")
    old = (now - timedelta(days=40)).isoformat(sep=" ", timespec="seconds")
    conn.execute(
        "INSERT INTO url_checks (user_id, url, risk_level, risk_score, timestamp) VALUES (1, ?, 'HIGH', 70, ?)",
        ("https://paypa1.com/login", recent),
    )
    conn.execute(
        "INSERT INTO url_checks (user_id, url, risk_level, risk_score, timestamp) VALUES (2, ?, 'LOW', 10, ?)",
        ("https://paypa1.com/login", recent),
    )
    conn.execute(
        "INSERT INTO url_checks (user_id, url, risk_level, risk_score, timestamp) VALUES (1, ?, 'HIGH', 80, ?)",
        ("https://paypa1.com/login", old),
    )
    conn.execute(
        "INSERT INTO user_reports (user_id, url, domain, user_label, created_at) VALUES (1, ?, 'paypa1.com', 'scam', ?)",
        ("https://paypa1.com/login", recent),
    )
    conn.execute(
        "INSERT INTO user_reports (user_id, url, domain, user_label, created_at) VALUES (2, ?, 'paypa1.com', 'safe', ?)",
        ("https://paypa1.com/login", recent),
    )
    conn.commit()

    observed = get_local_activity_30d("https://paypa1.com/login", "paypa1.com", conn=conn, now=now)
    assert observed["status"] == "observed"
    assert observed["scans"] == 2
    assert observed["signed_in_users"] == 2
    assert observed["high_risk_scans"] == 1
    assert observed["scam_reports"] == 1
    assert observed["safe_reports"] == 1

    unknown = get_local_activity_30d("https://never-seen.test", "never-seen.test", conn=conn, now=now)
    assert unknown["status"] == "unknown"
    assert unknown["scans"] == 0
    conn.close()


def test_views_surface_rag_and_30day():
    decision = calculate_final_risk(
        threat_intelligence=_intel("no_match"),
        heuristic_score=20,
        ml_score=20,
        heuristic_tags=[],
        heuristic_reasons=[],
        url_features=normalize_url("https://odd.example.test"),
        rag_assessment={
            "status": "ok",
            "suspicion_score": 70,
            "rule_id": "lookalike-brand",
            "rule_summary": "Lookalike brand domain.",
            "citations": ["lookalike-brand"],
        },
        local_activity={"status": "observed", "scans": 3, "scam_reports": 3, "risky_reports": 1, "safe_reports": 0, "signed_in_users": 2, "high_risk_scans": 1, "window_days": 30},
    )
    result = {
        **decision,
        "brand_impersonated": None,
        "details": {"threat_intelligence": _intel("no_match"), "local_activity": decision["evidence"]["local_activity"], "rag_assessment": decision["evidence"]["rag"]},
    }
    simple = build_simple_view(result)
    technical = build_technical_view(result)
    assert "knowledge-base" in simple["warning"].lower() or "reported" in simple["warning"].lower()
    assert technical["rag"]["rule_id"] == "lookalike-brand"
    assert technical["local_activity"]["status"] == "observed"


def test_fuse_omits_unavailable_rag():
    without = fuse({
        "url": 40, "domain": 20, "ml": 40, "nlp": 0, "psychological": 0,
        "threat_intel": 0, "brand": 0, "redirect": 0, "sender": 0, "community": 0,
    })
    omitted = fuse({
        "url": 40, "domain": 20, "ml": 40, "nlp": 0, "psychological": 0,
        "threat_intel": 0, "brand": 0, "redirect": 0, "sender": 0, "community": 0,
    })
    assert "rag" not in without["weights"]
    assert without["risk_score"] == omitted["risk_score"]


def test_observed_activity_is_cited_in_reasons():
    decision = calculate_final_risk(
        threat_intelligence=_intel("no_match"),
        heuristic_score=10,
        ml_score=10,
        heuristic_tags=[],
        heuristic_reasons=[],
        url_features=normalize_url("https://erp.psit.ac.in/"),
        local_activity={
            "status": "observed",
            "scans": 10,
            "high_risk_scans": 0,
            "opens": 2,
            "users_opened": 1,
            "this_browser_opens": 3,
            "this_browser_status": "observed",
            "window_days": 30,
        },
    )
    assert decision["evidence"]["local_activity"]["this_browser_opens"] == 3
    assert decision["evidence"]["local_activity"]["used"] is False
    assert decision["evidence"]["local_activity"]["suspicion_score"] == 0
    assert decision["risk_score"] == 10
    assert decision["safe"] is True


def test_collect_facts_marks_erp_login_portal():
    facts = collect_facts(
        "https://erp.psit.ac.in/",
        features={"hostname": "erp.psit.ac.in", "registered_domain": "psit.ac.in", "path": "/"},
        details={"https": True},
        local_activity={"status": "observed", "scans": 3},
    )
    assert facts["login_portal"] is True
    assert facts["lookalike"] is False


def test_kb_checked_rag_does_not_raise_score():
    decision = calculate_final_risk(
        threat_intelligence=_intel("no_match"),
        heuristic_score=10,
        ml_score=10,
        heuristic_tags=[],
        heuristic_reasons=[],
        url_features=normalize_url("https://erp.psit.ac.in/"),
        rag_assessment={
            "status": "ok",
            "suspicion_score": 0,
            "rule_id": "login-portal-hygiene",
            "rule_summary": "Login portal was checked.",
            "citations": ["login-portal-hygiene"],
        },
        local_activity={"status": "observed", "scans": 3, "window_days": 30},
    )
    assert decision["evidence"]["rag"]["status"] == "ok"
    assert decision["evidence"]["rag"]["rule_id"] == "login-portal-hygiene"
    assert decision["evidence"]["rag"]["used"] is False
    assert decision["safe"] is True


def test_url_checker_google_stays_low_with_optional_signals_disabled():
    result = URLChecker().analyze("https://www.google.com", intel_providers=offline_providers())
    assert result["safe"] is True
    assert result["risk_level"] == "LOW"
    assert result["evidence"]["rag"]["status"] == "unavailable"
    assert result["evidence"]["local_activity"]["scans"] >= 1
    assert result["safe"] is True


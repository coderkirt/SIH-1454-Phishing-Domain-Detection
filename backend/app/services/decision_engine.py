"""Final risk decision. Threat intelligence is not averaged away by heuristics.

There is no trained sklearn/TensorFlow classifier in this repo. `ml_score`
is the lexical/heuristic URL score, exposed separately so a low value cannot
be read as proof that a URL is safe.
"""

from typing import Dict, List, Optional

INTEL_FLOOR = {
    "exact_url": 85,
    "normalized_url": 80,
    "hostname": 72,
    "registered_domain": 55,
}

RAG_FLOOR = (
    (70, 50),
    (50, 40),
    (35, 32),
)

ACTIVITY_FLOOR = (
    (70, 50),
    (50, 40),
    (35, 32),
    (20, 20),
    (8, 12),
)

TRUSTED_RAG_RULES = {
    "trusted-host-phish-path",
    "trusted-host-phish-query",
    "path-phishing-on-trusted-host",
}

LOOKALIKE_TAGS = {"phishing", "brand_impersonation", "ip_url"}


def _level(score: int) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def _rag_floor(suspicion: int) -> int:
    for threshold, floor in RAG_FLOOR:
        if suspicion >= threshold:
            return floor
    return 0


def _activity_floor(suspicion: int) -> int:
    for threshold, floor in ACTIVITY_FLOOR:
        if suspicion >= threshold:
            return floor
    return 0


def _link_already_suspicious(score: int, tags: List[str], trusted_destination: bool = False) -> bool:
    """Danger counts apply only when this scan is already suspicious."""
    lookalike = any(tag in tags for tag in LOOKALIKE_TAGS) or "lookalike" in tags
    rag_flag = "rag_suspicious" in tags
    if trusted_destination and not lookalike and not rag_flag:
        return False
    return lookalike or rag_flag or score >= 30


def _activity_suspicion(activity: Optional[Dict], *, count_dangers: bool = True) -> int:
    if not count_dangers:
        return 0
    activity = activity or {}
    scam = int(activity.get("scam_reports") or 0)
    risky = int(activity.get("risky_reports") or 0)
    high_risk = int(activity.get("high_risk_scans") or 0)
    suspicion = 0
    if scam:
        suspicion = max(suspicion, min(80, 36 + scam * 10 + risky * 3))
    elif risky:
        suspicion = max(suspicion, min(55, 22 + risky * 4))
    if high_risk:
        suspicion = max(suspicion, min(52, 16 + high_risk * 5))
    # Repeat scans and ordinary opens are not evidence. GitHub and other
    # legitimate sites are visited often and must not pick up a floor.
    return suspicion


def _apply_local_activity(
    score: int,
    tags: List[str],
    activity: Optional[Dict],
    trusted_destination: bool = False,
) -> tuple:
    """30-day danger counts raise only when the current link is already suspicious."""
    activity = activity or {}
    extra_reasons = []
    extra_tags = []
    meta = {"used": False, "suspicion_score": 0, "this_browser_used": False}
    status = activity.get("status") or "unknown"
    scam = int(activity.get("scam_reports") or 0)
    risky = int(activity.get("risky_reports") or 0)
    scans = int(activity.get("scans") or 0)
    opens = int(activity.get("opens") or 0)
    users_opened = int(activity.get("users_opened") or 0)
    browser_opens = int(activity.get("this_browser_opens") or 0)
    high_risk = int(activity.get("high_risk_scans") or 0)
    has_signal = scans or opens or users_opened or browser_opens or scam or risky or high_risk
    if status == "unknown" and not has_signal:
        return score, extra_reasons, extra_tags, meta

    meta["this_browser_used"] = browser_opens > 0
    count_dangers = _link_already_suspicious(score, tags, trusted_destination)
    suspicion = _activity_suspicion(activity, count_dangers=count_dangers)
    floor = _activity_floor(suspicion)
    meta["suspicion_score"] = suspicion

    lookalike = any(tag in tags for tag in ("brand_impersonation", "phishing", "ip_url", "lookalike"))
    if lookalike and (scans >= 5 or opens >= 5 or users_opened >= 3 or browser_opens >= 5):
        extra_reasons.append(
            f"{opens} PhishEye opens ({users_opened} users) in 30 days do not clear a lookalike or impersonation domain."
        )

    if not count_dangers:
        return score, extra_reasons, extra_tags, meta

    if suspicion:
        meta["used"] = True
        extra_reasons.append(
            f"PhishEye 30-day danger counts contributed {suspicion} suspicion "
            f"({high_risk} high-risk scans, {scam} scam reports, {risky} risky reports). "
            f"Ordinary opens and scan volume are not counted."
        )
        extra_tags.append("local_activity")
    if floor:
        score = max(score, floor)

    if high_risk >= 3 and not lookalike:
        raised = min(46, 28 + high_risk * 2)
        if raised > score:
            score = raised
        extra_reasons.append(
            f"{high_risk} high-risk PhishEye scans in 30 days raised suspicion."
        )
        extra_tags.append("local_high_risk_scans")

    if scam >= 3 or (scam >= 1 and scam + risky >= 3):
        raised = min(70, 40 + scam * 5 + risky * 2)
        if raised > score:
            score = raised
        extra_reasons.append(
            f"PhishEye users reported this domain as scam/risky "
            f"{scam + risky} time(s) in the last {activity.get('window_days') or 30} days."
        )
        extra_tags.append("local_scam_reports")
    elif risky >= 5:
        raised = min(55, 32 + risky * 2)
        if raised > score:
            score = raised
        extra_reasons.append(
            f"PhishEye users flagged this domain as risky "
            f"{risky} time(s) in the last {activity.get('window_days') or 30} days."
        )
        extra_tags.append("local_scam_reports")
    return score, extra_reasons, extra_tags, meta


def calculate_final_risk(
    threat_intelligence: Optional[Dict] = None,
    heuristic_score: int = 0,
    heuristic_tags: Optional[List[str]] = None,
    ml_score: Optional[int] = None,
    url_features: Optional[Dict] = None,
    heuristic_reasons: Optional[List[str]] = None,
    rag_assessment: Optional[Dict] = None,
    local_activity: Optional[Dict] = None,
    trusted_destination: bool = False,
) -> Dict:
    intel = threat_intelligence or {}
    tags = list(heuristic_tags or [])
    reasons = list(heuristic_reasons or [])
    heuristic = max(0, min(100, int(heuristic_score or 0)))
    ml = heuristic if ml_score is None else max(0, min(100, int(ml_score)))
    features = url_features or {}

    providers = intel.get("providers") or []
    confirmed = [row for row in providers if row.get("status") == "confirmed_malicious" and row.get("found")]
    reported = [row for row in providers if row.get("status") == "reported_malicious" and row.get("found")]
    overall = intel.get("overall_status") or "unavailable"

    classification = "NO_MALICIOUS_EVIDENCE"
    explanation = "No confirmed threat-intelligence match and no strong heuristic phishing indicators."
    score = heuristic

    if confirmed:
        best = max(confirmed, key=lambda row: (row.get("confidence") or 0, INTEL_FLOOR.get(row.get("match_type"), 70)))
        floor = INTEL_FLOOR.get(best.get("match_type"), 70)
        score = max(heuristic, floor)
        classification = "CONFIRMED_MALICIOUS"
        explanation = (
            f"{best.get('provider')} confirmed this URL as malicious "
            f"({best.get('match_type')}). Heuristics and ML cannot override that."
        )
        intel_reason = best.get("detail") or explanation
        if intel_reason not in reasons:
            reasons.insert(0, intel_reason)
        if "threat_intel" not in tags:
            tags.insert(0, "threat_intel")
        if "confirmed_malicious" not in tags:
            tags.insert(0, "confirmed_malicious")
    elif reported:
        best = max(reported, key=lambda row: row.get("confidence") or 0)
        score = max(heuristic, 58)
        classification = "SUSPICIOUS"
        explanation = (
            f"{best.get('provider')} has an unverified report for this URL. "
            "That is not a community-confirmed phish, but it is not safe to treat as clean."
        )
        intel_reason = best.get("detail") or explanation
        if intel_reason not in reasons:
            reasons.insert(0, intel_reason)
        if "threat_intel" not in tags:
            tags.insert(0, "threat_intel")
        if "reported_phish" not in tags:
            tags.insert(0, "reported_phish")
    elif heuristic >= 50:
        classification = "SUSPICIOUS"
        explanation = "No confirmed feed match. Deterministic / heuristic indicators are strong."
    elif heuristic >= 30:
        classification = "SUSPICIOUS"
        explanation = "No confirmed feed match. Heuristic indicators look fishy."
    elif overall == "unavailable":
        classification = "NO_MALICIOUS_EVIDENCE"
        explanation = (
            "Threat intelligence is unavailable. Heuristics did not find strong phishing "
            "indicators. Unavailable intel is not a clean bill of health."
        )
    elif overall == "partial":
        classification = "NO_MALICIOUS_EVIDENCE"
        explanation = (
            "Some threat-intelligence feeds had no match; others were unavailable. "
            "Heuristics did not find strong phishing indicators."
        )
    else:
        classification = "NO_MALICIOUS_EVIDENCE"
        explanation = (
            "Queried threat-intelligence feeds had no match, and heuristics did not "
            "find strong phishing indicators. Absence from a feed does not guarantee safety."
        )

    if classification != "CONFIRMED_MALICIOUS" and any(tag in tags for tag in LOOKALIKE_TAGS):
        score = max(score, 50)
        if classification == "NO_MALICIOUS_EVIDENCE":
            classification = "SUSPICIOUS"
            explanation = (
                "Lookalike, phishing-fragment, or IP-host indicators are present. "
                "A low numeric score or a later parse error cannot mark this address safe."
            )

    rag = rag_assessment if isinstance(rag_assessment, dict) else {}
    rag_status = rag.get("status") or "unavailable"
    rag_score = rag.get("suspicion_score")
    rag_ok = rag_status == "ok" and rag_score is not None
    rag_used = False
    if rag_ok:
        try:
            rag_score = int(rag_score)
        except (TypeError, ValueError):
            rag_ok = False
            rag_score = None
    if trusted_destination and rag_ok:
        rule_id = rag.get("rule_id") or ""
        if rule_id not in TRUSTED_RAG_RULES:
            rag_ok = False

    if rag_ok and classification != "CONFIRMED_MALICIOUS":
        floor = _rag_floor(int(rag_score))
        if floor:
            score = max(score, floor)
            rag_used = True
            if classification == "NO_MALICIOUS_EVIDENCE":
                classification = "SUSPICIOUS"
            summary = rag.get("rule_summary") or "Knowledge-base rule raised suspicion."
            if summary not in reasons:
                reasons.insert(0, summary)
            if "rag_suspicious" not in tags:
                tags.insert(0, "rag_suspicious")
            explanation = (
                f"{explanation} Local knowledge-base rule '{rag.get('rule_id')}' "
                "raised suspicion. RAG cannot mark a link safe and cannot override confirmed intel."
            )

    activity = local_activity if isinstance(local_activity, dict) else {}
    activity_meta = {"used": False, "suspicion_score": 0, "this_browser_used": False}
    if classification != "CONFIRMED_MALICIOUS":
        score, activity_reasons, activity_tags, activity_meta = _apply_local_activity(
            score, tags, activity, trusted_destination
        )
        for reason in activity_reasons:
            if reason not in reasons:
                reasons.append(reason)
        for tag in activity_tags:
            if tag not in tags:
                tags.append(tag)
            if classification == "NO_MALICIOUS_EVIDENCE" and tag == "local_scam_reports":
                classification = "SUSPICIOUS"
                explanation = (
                    f"{explanation} Recent PhishEye scam/risky reports raised suspicion. "
                    "Local history cannot mark a link safe."
                )

    score = max(0, min(100, int(score)))
    if any(tag in tags for tag in LOOKALIKE_TAGS):
        score = max(score, 50)
        if classification == "NO_MALICIOUS_EVIDENCE":
            classification = "SUSPICIOUS"
    level = _level(score)
    blocking = classification in {"CONFIRMED_MALICIOUS", "SUSPICIOUS"} or level != "LOW"
    if "domain_not_found" in tags or any(tag in tags for tag in LOOKALIKE_TAGS):
        blocking = True

    evidence = {
        "threat_intelligence": {
            "overall_status": overall,
            "confirmed": bool(confirmed),
            "providers": [
                {
                    "provider": row.get("provider"),
                    "status": row.get("status"),
                    "match_type": row.get("match_type"),
                    "detail": row.get("detail"),
                    "confidence": row.get("confidence"),
                }
                for row in providers
            ],
        },
        "ml": {
            "score": ml,
            "label": "Lexical / heuristic URL score (no trained classifier in this build)",
        },
        "heuristics": {
            "score": heuristic,
            "tags": tags,
        },
        "rag": {
            "status": rag_status,
            "suspicion_score": rag_score if rag_ok or rag_status == "ok" else None,
            "rule_id": rag.get("rule_id") if rag else None,
            "rule_summary": rag.get("rule_summary") if rag else None,
            "citations": list(rag.get("citations") or []) if rag else [],
            "used": rag_used,
        },
        "local_activity": {
            "window_days": activity.get("window_days") or 30,
            "scans": int(activity.get("scans") or 0),
            "signed_in_users": int(activity.get("signed_in_users") or 0),
            "high_risk_scans": int(activity.get("high_risk_scans") or 0),
            "scam_reports": int(activity.get("scam_reports") or 0),
            "risky_reports": int(activity.get("risky_reports") or 0),
            "safe_reports": int(activity.get("safe_reports") or 0),
            "opens": int(activity.get("opens") or 0),
            "users_opened": int(activity.get("users_opened") or 0),
            "this_browser_opens": int(activity.get("this_browser_opens") or 0),
            "this_browser_status": activity.get("this_browser_status") or "unavailable",
            "this_browser_used": bool(activity_meta.get("this_browser_used")),
            "suspicion_score": int(activity_meta.get("suspicion_score") or 0),
            "used": bool(activity_meta.get("used")),
            "status": activity.get("status") or "unknown",
        },
        "url": {
            "original": features.get("original") or intel.get("url"),
            "normalized_full_url": features.get("normalized_full_url") or intel.get("normalized_url"),
            "hostname": features.get("hostname") or intel.get("hostname"),
            "registered_domain": features.get("registered_domain") or intel.get("registered_domain"),
            "path": features.get("path"),
            "query": features.get("query"),
        },
    }

    return {
        "classification": classification,
        "risk_score": score,
        "risk_level": level,
        "confidence": _confidence(confirmed, tags, overall),
        "safe": (not blocking) and level == "LOW" and "domain_not_found" not in tags,
        "evidence": evidence,
        "explanation": explanation,
        "reasons": reasons[:8],
        "threat_tags": _unique(tags),
        "ml_score": ml,
        "heuristic_score": heuristic,
    }


def _confidence(confirmed: List[Dict], tags: List[str], overall: str) -> int:
    if confirmed:
        return min(95, 70 + int(10 * (confirmed[0].get("confidence") or 1)))
    if "reported_phish" in tags:
        return 62
    if "brand_impersonation" in tags or "phishing" in tags:
        return 70
    if overall == "unavailable":
        return 35
    return 50


def _unique(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out

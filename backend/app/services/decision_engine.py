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


def _level(score: int) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def calculate_final_risk(
    threat_intelligence: Optional[Dict] = None,
    heuristic_score: int = 0,
    heuristic_tags: Optional[List[str]] = None,
    ml_score: Optional[int] = None,
    url_features: Optional[Dict] = None,
    heuristic_reasons: Optional[List[str]] = None,
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

    score = max(0, min(100, int(score)))
    level = _level(score)
    blocking = classification in {"CONFIRMED_MALICIOUS", "SUSPICIOUS"} or level != "LOW"
    if "domain_not_found" in tags:
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

"""Keyword + lightweight semantic (TF-IDF cosine) search, merged with RRF."""

import math
import re
from collections import Counter
from typing import Dict, List, Tuple

from app.knowledge import NOTES

TOKEN_RE = re.compile(r"[a-z0-9]+")
RRF_K = 60
VAGUE_RULES = {
    "lookalike-brand",
    "brand-vs-domain",
    "new-domain",
    "https-not-enough",
    "suspicious-tld",
    "secure-login-tokens",
    "message-urgency",
    "local-unknown",
    "local-scan-volume",
    "login-portal-hygiene",
    "kb-checked",
}
TRUSTED_SPECIFIC = {"trusted-host-phish-path"}


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall((text or "").lower())


def _note_text(note: Dict) -> str:
    return " ".join([note.get("title") or "", " ".join(note.get("keywords") or []), note.get("body") or ""])


def _idf(docs: List[List[str]]) -> Dict[str, float]:
    n = len(docs)
    df = Counter()
    for doc in docs:
        df.update(set(doc))
    return {token: math.log((n + 1) / (count + 1)) + 1.0 for token, count in df.items()}


def _tfidf(tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
    tf = Counter(tokens)
    length = max(len(tokens), 1)
    return {token: (tf[token] / length) * idf.get(token, 0.0) for token in tf}


def _cosine(left: Dict[str, float], right: Dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    shared = set(left) & set(right)
    num = sum(left[key] * right[key] for key in shared)
    da = math.sqrt(sum(value * value for value in left.values()))
    db = math.sqrt(sum(value * value for value in right.values()))
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)


_NOTE_DOCS = [tokenize(_note_text(note)) for note in NOTES]
_IDF = _idf(_NOTE_DOCS) if _NOTE_DOCS else {}
_NOTE_VECS = [_tfidf(doc, _IDF) for doc in _NOTE_DOCS]


def _facts_blob(facts: Dict) -> str:
    activity = facts.get("local_activity") or {}
    tags = facts.get("heuristic_tags") or []
    tls = facts.get("tls") or {}
    parts = [
        facts.get("url") or "",
        facts.get("hostname") or "",
        facts.get("registered_domain") or "",
        facts.get("path") or "",
        facts.get("query") or "",
        facts.get("brand_impersonated") or "",
        facts.get("message_context") or "",
        " ".join(str(tag) for tag in tags),
        "login portal erp sso webmail" if facts.get("login_portal") else "",
        "lookalike" if facts.get("lookalike") else "",
        "secure login verify" if facts.get("secure_login_tokens") else "",
        "ip address host" if facts.get("ip_host") else "",
        "shortener redirect" if facts.get("shortened") else "",
        "new domain age" if _is_new_domain(facts) else "",
        "https tls certificate" if facts.get("https") else "no https",
        " ".join(str(item) for item in (tls.get("findings") or tls.get("tags") or [])),
        "scam reports" if int(activity.get("scam_reports") or 0) else "",
        "risky reports" if int(activity.get("risky_reports") or 0) else "",
        "unknown visits" if activity.get("status") == "unknown" else "30-day scans history",
        "trusted official" if facts.get("trusted_destination") or facts.get("official_brand_domain") else "",
        "free host" if "free_host_phish" in tags else "",
    ]
    return " ".join(part for part in parts if part)


def _is_new_domain(facts: Dict) -> bool:
    age = facts.get("domain_age_days")
    return age is not None and int(age) < 90


def keyword_search(facts: Dict, limit: int = 8) -> List[Tuple[Dict, float]]:
    blob = _facts_blob(facts).lower()
    tokens = set(tokenize(blob))
    ranked = []
    for note in NOTES:
        hits = 0
        for keyword in note["keywords"]:
            if " " in keyword:
                if keyword in blob:
                    hits += 2
            elif keyword in tokens or keyword in blob:
                hits += 1
        if hits:
            ranked.append((note, float(hits)))
    ranked.sort(key=lambda item: (-item[1], item[0]["id"]))
    return ranked[:limit]


def semantic_search(facts: Dict, limit: int = 8) -> List[Tuple[Dict, float]]:
    query = _tfidf(tokenize(_facts_blob(facts)), _IDF)
    ranked = []
    for note, vector in zip(NOTES, _NOTE_VECS):
        score = _cosine(query, vector)
        if score > 0.02:
            ranked.append((note, score))
    ranked.sort(key=lambda item: (-item[1], item[0]["id"]))
    return ranked[:limit]


def _rrf(keyword_hits: List[Tuple[Dict, float]], semantic_hits: List[Tuple[Dict, float]]) -> List[Tuple[Dict, float]]:
    scores = {}
    notes = {}
    for rank, (note, _) in enumerate(keyword_hits, start=1):
        notes[note["id"]] = note
        scores[note["id"]] = scores.get(note["id"], 0.0) + 1.0 / (RRF_K + rank)
    for rank, (note, _) in enumerate(semantic_hits, start=1):
        notes[note["id"]] = note
        scores[note["id"]] = scores.get(note["id"], 0.0) + 1.0 / (RRF_K + rank)
    ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return [(notes[note_id], score) for note_id, score in ordered]


def _applies(note: Dict, facts: Dict) -> bool:
    note_id = note["id"]
    tags = set(facts.get("heuristic_tags") or [])
    activity = facts.get("local_activity") or {}
    trusted = bool(facts.get("trusted_destination") or facts.get("official_brand_domain"))
    tls = facts.get("tls") or {}
    path_query = f"{facts.get('path') or ''} {facts.get('query') or ''}".lower()
    phishing_path = any(token in path_query for token in ("return_to=", "continue=", "redirect=", "next="))

    if note_id == "lookalike-brand":
        return bool(facts.get("lookalike") or facts.get("brand_impersonated")) and not trusted
    if note_id == "brand-vs-domain":
        return bool(facts.get("brand_impersonated")) and not trusted
    if note_id == "login-portal-hygiene":
        return bool(facts.get("login_portal")) and not trusted
    if note_id == "kb-checked":
        return False
    if note_id == "secure-login-tokens":
        return bool(facts.get("secure_login_tokens")) and not trusted
    if note_id == "ip-url":
        return bool(facts.get("ip_host") or "ip_url" in tags)
    if note_id == "shortener":
        return bool(facts.get("shortened") or "shortened_url" in tags)
    if note_id == "new-domain":
        return _is_new_domain(facts) and not trusted
    if note_id == "https-not-enough":
        return bool(facts.get("https")) and (
            facts.get("lookalike") or facts.get("ip_host") or facts.get("secure_login_tokens")
        ) and not trusted
    if note_id == "tls-problems":
        return bool(tls.get("findings") or tls.get("tags"))
    if note_id == "message-urgency":
        text = (facts.get("message_context") or "").lower()
        return any(token in text for token in ("urgent", "immediately", "otp", "password", "suspend", "blocked", "verify now"))
    if note_id == "local-scam-reports":
        return int(activity.get("scam_reports") or 0) + int(activity.get("risky_reports") or 0) > 0
    if note_id == "local-unknown":
        return (activity.get("status") or "unknown") == "unknown"
    if note_id == "local-scan-volume":
        return int(activity.get("scans") or 0) >= 5 and (
            facts.get("lookalike") or facts.get("brand_impersonated") or facts.get("ip_host")
        )
    if note_id == "trusted-host-phish-path":
        return trusted and phishing_path
    if note_id == "free-host-phish":
        return "free_host_phish" in tags
    if note_id == "suspicious-tld":
        return "suspicious_tld" in tags and not trusted
    return True


def _suspicion_for(note: Dict, facts: Dict) -> int:
    activity = facts.get("local_activity") or {}
    score = int(note.get("suspicion") or 0)
    if note["id"] == "local-scam-reports":
        scam = int(activity.get("scam_reports") or 0)
        risky = int(activity.get("risky_reports") or 0)
        score = min(80, 40 + scam * 10 + risky * 4)
    if note["id"] in {"local-unknown", "local-scan-volume", "login-portal-hygiene", "kb-checked"}:
        return 0
    if note["id"] == "trusted-host-phish-path":
        return max(score, 46)
    return score


def _explain_activity(facts: Dict) -> str:
    activity = facts.get("local_activity") or {}
    if not activity:
        return ""
    status = activity.get("status") or "unknown"
    if status == "unknown":
        return (
            "PhishEye has no scans or reports for this address in the last "
            f"{activity.get('window_days') or 30} days (unknown, not safe)."
        )
    return (
        f"PhishEye 30-day counts: {int(activity.get('scans') or 0)} scans, "
        f"{int(activity.get('signed_in_users') or 0)} signed-in users, "
        f"{int(activity.get('high_risk_scans') or 0)} high-risk, "
        f"{int(activity.get('scam_reports') or 0)} scam reports, "
        f"{int(activity.get('risky_reports') or 0)} risky reports, "
        f"{int(activity.get('safe_reports') or 0)} safe reports. "
        "These numbers were supplied by PhishEye; they were not invented."
    )


def assess_facts(facts: Dict) -> Dict:
    facts = facts or {}
    trusted = bool(facts.get("trusted_destination") or facts.get("official_brand_domain"))
    merged = _rrf(keyword_search(facts), semantic_search(facts))
    applicable = [(note, rank) for note, rank in merged if _applies(note, facts)]
    if trusted:
        applicable = [
            (note, rank)
            for note, rank in applicable
            if note["id"] in TRUSTED_SPECIFIC or note["id"] in {"local-scam-reports", "tls-problems"}
        ]

    if not applicable:
        return {
            "suspicion_score": 0,
            "rule_id": "kb-checked",
            "rule_summary": (
                "The knowledge-base compared this URL to its phishing notes. "
                "No pattern in those notes applied to the supplied facts. "
                "That is an evaluation result, not a clean bill of health."
            ),
            "status": "ok",
            "citations": ["kb-checked"],
            "activity_note": _explain_activity(facts),
        }

    best = None
    best_score = -1
    for note, _rank in applicable:
        score = _suspicion_for(note, facts)
        if score > best_score or (score == best_score and best and note["id"] < best["id"]):
            if best is None or score > best_score:
                best = note
                best_score = score
    if best is None:
        best = applicable[0][0]
        best_score = _suspicion_for(best, facts)

    if trusted and best["id"] in VAGUE_RULES:
        return {
            "suspicion_score": 0,
            "rule_id": None,
            "rule_summary": "Vague knowledge-base notes were ignored for a trusted official site.",
            "status": "ok",
            "citations": [],
            "activity_note": _explain_activity(facts),
        }

    citations = [item[0]["id"] for item in applicable[:4]]
    summary = best["body"]
    activity_note = _explain_activity(facts)
    if activity_note and best["id"].startswith("local-"):
        summary = f"{summary} {activity_note}"
    elif activity_note and int((facts.get("local_activity") or {}).get("scam_reports") or 0):
        summary = f"{summary} {activity_note}"

    return {
        "suspicion_score": max(0, min(100, int(best_score))),
        "rule_id": best["id"],
        "rule_summary": summary,
        "status": "ok",
        "citations": citations,
        "activity_note": activity_note,
    }

"""Unified multi-channel analysis. All sources share this pipeline."""

from typing import Dict, Optional

from app.services.content_normalizer import normalize_content
from app.services.url_checker import URLChecker
from app.services.psychology import analyze_message
from app.services.brand_detector import detect_impersonation
from app.services.sender_analyzer import analyze_sender
from app.services.risk_engine import fuse
from app.services.explanation import build_explanation
from app.services.reputation import get_reputation
from app.services.warnings import build_simple_view, build_technical_view
from app.services.report_service import build_export
from app.database.connection import get_db_connection

url_checker = URLChecker()


def _domain_risk(url_result: dict) -> int:
    details = url_result.get("details") or {}
    score = 0
    if details.get("domain_exists") is False:
        score += 60
    age = details.get("domain_age_days")
    if age is not None and age < 30:
        score += 40
    elif age is not None and age < 90:
        score += 20
    if details.get("suspicious_tld"):
        score += 25
    if url_result.get("brand_impersonated"):
        score += 40
    return min(score, 100)


def analyze_content(
    source_type: str,
    text: str = "",
    urls: Optional[list] = None,
    sender: Optional[dict] = None,
    language: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Dict:
    normalized = normalize_content(source_type, text, urls, sender, language)
    psych = analyze_message(normalized["raw_text"])
    extra = {
        "credential": "credential_pressure" in psych["tags"],
        "urgency": "urgency_detected" in psych["tags"],
        "fear": "fear_tactics" in psych["tags"],
    }

    link_results = []
    for item in normalized["urls"]:
        analyzed = url_checker.analyze(item["url"])
        extra["suspicious_domain"] = extra.get("suspicious_domain") or analyzed.get("safe") is False
        classification = analyzed.get("risk_level", "LOW")
        details = analyzed.get("details") or {}
        link_results.append({
            "url": analyzed.get("url") or item["url"],
            "position": item.get("position", 0),
            "domain": item.get("domain") or details.get("domain"),
            "risk_score": analyzed.get("risk_score", 0),
            "classification": classification,
            "threat_tags": analyzed.get("threat_tags", []),
            "reasons": analyzed.get("reasons", []),
            "safe": analyzed.get("safe", True),
            "shortened": details.get("shortened", item.get("shortened")),
            "final_url": details.get("final_url"),
            "simple_view": analyzed.get("simple_view"),
            "details": details,
        })

    if not link_results and source_type == "url" and text:
        analyzed = url_checker.analyze(text)
        details = analyzed.get("details") or {}
        link_results.append({
            "url": analyzed.get("url") or text,
            "position": 0,
            "domain": details.get("domain"),
            "risk_score": analyzed.get("risk_score", 0),
            "classification": analyzed.get("risk_level", "LOW"),
            "threat_tags": analyzed.get("threat_tags", []),
            "reasons": analyzed.get("reasons", []),
            "safe": analyzed.get("safe", True),
            "shortened": details.get("shortened"),
            "final_url": details.get("final_url"),
            "simple_view": analyzed.get("simple_view"),
            "details": details,
        })

    top = max(link_results, key=lambda row: row["risk_score"]) if link_results else None
    url_risk = top["risk_score"] if top else 0
    domain_risk = _domain_risk({"details": (top or {}).get("details") or {}, "brand_impersonated": False, "safe": (top or {}).get("safe", True)}) if top else 0
    if top:
        domain_risk = max(domain_risk, int(url_risk * 0.6))
    intel = 80 if top and "safe_browsing" in (top.get("threat_tags") or []) else (url_risk if top else 0)
    redirect_risk = 40 if any(link.get("shortened") for link in link_results) else 0
    brand = detect_impersonation(
        normalized["raw_text"],
        [link["url"] for link in link_results],
        extra,
    )
    sender_info = analyze_sender(normalized["sender"], normalized["raw_text"])
    community = get_reputation(top["domain"]) if top and top.get("domain") else get_reputation("")

    fused = fuse({
        "url": url_risk,
        "domain": domain_risk,
        "ml": url_risk,
        "nlp": psych["score"],
        "psychological": psych["score"],
        "threat_intel": intel,
        "brand": brand["score"],
        "redirect": redirect_risk,
        "sender": sender_info["score"],
        "community": community.get("reputation_score", 0),
    })

    tags = list(psych["tags"])
    if brand["impersonated"]:
        tags.append("brand_impersonation")
    if sender_info.get("mismatch"):
        tags.append("sender_mismatch")
    if top:
        for tag in top.get("threat_tags") or []:
            if tag not in tags:
                tags.append(tag)

    counts = {"total": len(link_results), "safe": 0, "suspicious": 0, "risky": 0, "phishing": 0}
    for link in link_results:
        level = link["classification"]
        if level == "LOW":
            counts["safe"] += 1
        elif level == "MEDIUM":
            counts["suspicious"] += 1
        elif level == "HIGH":
            counts["risky"] += 1
        else:
            counts["phishing"] += 1

    payload = {
        "source_type": normalized["source_type"],
        "language": normalized["language"],
        "risk_score": fused["risk_score"],
        "risk_level": fused["risk_level"],
        "scam_risk": fused["scam_risk"],
        "model_probability": fused["model_probability"],
        "model_confidence": fused["model_confidence"],
        "safe": fused["risk_level"] == "LOW",
        "threat_tags": tags,
        "brand_impersonated": brand["impersonated"],
        "reasons": (psych["findings"] + brand["findings"] + sender_info.get("findings", []))[:8],
        "signals": fused["signals"],
        "weights": fused["weights"],
        "methodology": fused["methodology"],
        "message_risk_score": psych["score"],
        "links": link_results,
        "link_summary": counts,
        "sender": sender_info,
        "community": community,
        "normalized": {
            "source_type": normalized["source_type"],
            "url_count": len(normalized["urls"]),
            "domains": normalized["domains"],
            "language": normalized["language"],
        },
    }
    payload["explanation"] = build_explanation(payload)
    payload["simple_view"] = build_simple_view(payload, source="message" if normalized["raw_text"] else "url")
    payload["url"] = (top or {}).get("url") or ""
    payload["technical_view"] = {
        **build_technical_view({
            "risk_score": payload["risk_score"],
            "risk_level": payload["risk_level"],
            "threat_tags": tags,
            "reasons": payload["reasons"],
            "brand_impersonated": brand["impersonated"],
            "details": (top or {}).get("details") or {},
        }),
        "signals": fused["signals"],
        "model_probability": fused["model_probability"],
        "model_confidence": fused["model_confidence"],
        "message_risk_score": psych["score"],
        "community": community,
        "weights": fused["weights"],
        "methodology": fused["methodology"],
    }
    payload["privacy"] = {
        "raw_message_stored": False,
        "passwords_collected": False,
        "otp_collected": False,
        "cookies_collected": False,
    }

    scan_id = _store_scan(payload, user_id, top["url"] if top else "")
    payload["scan_id"] = scan_id
    payload["export"] = build_export(payload)
    return payload


def _store_scan(payload: Dict, user_id: Optional[int], url: str) -> Optional[int]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO content_scans (user_id, source_type, url, risk_level, risk_score, scam_risk, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                payload["source_type"],
                url[:500],
                payload["risk_level"],
                payload["risk_score"],
                payload["scam_risk"],
                payload["model_confidence"],
            ),
        )
        scan_id = cursor.lastrowid
        for link in payload.get("links") or []:
            cursor.execute(
                """
                INSERT INTO extracted_links (scan_id, url, domain, risk_score, classification)
                VALUES (?, ?, ?, ?, ?)
                """,
                (scan_id, (link.get("url") or "")[:500], (link.get("domain") or "")[:200],
                 link.get("risk_score"), link.get("classification")),
            )
        conn.commit()
        conn.close()
        return scan_id
    except Exception:
        return None

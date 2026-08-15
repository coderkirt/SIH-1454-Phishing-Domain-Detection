from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.url_checker import URLChecker
from app.services.psychology import analyze_text
from app.services.warnings import build_simple_view
from app.database.connection import get_db_connection

router = APIRouter(prefix="/api/v1/threat", tags=["threat"])

url_checker = URLChecker()


class URLCheckRequest(BaseModel):
    url: str
    view: str = "both"  # simple | technical | both


class MessageCheckRequest(BaseModel):
    message: str
    url: Optional[str] = None


def classify_threat_type(result: dict) -> str:
    tags = result.get("threat_tags") or []
    if "phishing" in tags or "brand_impersonation" in tags:
        return "phishing"
    if "piracy_scam" in tags:
        return "malware"
    if "ip_url" in tags:
        return "malware"
    if "urgency_detected" in tags or "fear_tactics" in tags:
        return "fake_login"
    joined = " ".join(result.get("reasons") or []).lower()
    if "phishing" in joined or "typo" in joined or "fake" in joined:
        return "phishing"
    if "ip-based" in joined:
        return "malware"
    if "keyword" in joined:
        return "fake_login"
    return "credential_theft"


def _pick_view(result: dict, view: str) -> dict:
    """Return Simple View, Technical View, or both (for the dashboard toggle)."""
    payload = {
        "url": result.get("url"),
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "reasons": result["reasons"],
        "safe": result["safe"],
        "threat_tags": result.get("threat_tags", []),
        "brand_impersonated": result.get("brand_impersonated"),
    }
    view = (view or "both").lower()
    if view in ("simple", "both"):
        payload["simple_view"] = result["simple_view"]
    if view in ("technical", "both"):
        payload["technical_view"] = result["technical_view"]
    return payload


@router.post("/check-url")
async def check_url(request: URLCheckRequest):
    """
    Check if a URL is phishing / piracy / a brand fake.

    Returns a technical score AND a plain-English Simple View
    for non-technical users.
    """
    try:
        url = request.url.strip()

        if not url:
            raise HTTPException(status_code=400, detail="URL cannot be empty")

        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"

        result = url_checker.analyze(url)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO url_checks (url, risk_level, risk_score) VALUES (?, ?, ?)",
            (url, result["risk_level"], result["risk_score"])
        )

        if result["risk_level"] in ["HIGH", "CRITICAL"]:
            cursor.execute(
                "INSERT INTO threats (threat_type, threat_data, severity) VALUES (?, ?, ?)",
                (classify_threat_type(result), url, result["risk_level"].lower())
            )

        conn.commit()
        conn.close()

        result["url"] = url
        return _pick_view(result, request.view)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/check-message")
async def check_message(request: MessageCheckRequest):
    """
    Psychological Threat Detection.

    Scan an SMS / WhatsApp / email message for urgency, fear and greed
    language (English + Hinglish). Optionally also check a URL inside it.
    """
    message = (request.message or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    psych = analyze_text(message)
    url_result = None
    combined_score = psych["score"]
    tags = list(psych["tags"])
    findings = list(psych["findings"])

    if request.url:
        url = request.url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        url_result = url_checker.analyze(url)
        combined_score = min(combined_score + url_result["risk_score"], 100)
        for tag in url_result.get("threat_tags", []):
            if tag not in tags:
                tags.append(tag)
        findings.extend(url_result.get("reasons", []))

    if combined_score >= 70:
        risk_level = "CRITICAL"
    elif combined_score >= 50:
        risk_level = "HIGH"
    elif combined_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    merged = {
        "risk_score": combined_score,
        "risk_level": risk_level,
        "reasons": findings[:5],
        "safe": risk_level == "LOW",
        "threat_tags": tags,
        "brand_impersonated": (url_result or {}).get("brand_impersonated"),
        "details": (url_result or {}).get("details", {}),
    }
    simple_view = build_simple_view(merged, source="message")

    return {
        "message": message,
        "risk_score": combined_score,
        "risk_level": risk_level,
        "safe": risk_level == "LOW",
        "threat_tags": tags,
        "findings": findings,
        "url_check": url_result,
        "simple_view": simple_view,
    }


@router.get("/stats")
async def get_stats():
    """Get current statistics (computed from the database)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    total = cursor.execute("SELECT COUNT(*) FROM url_checks").fetchone()[0]
    threats = cursor.execute(
        "SELECT COUNT(*) FROM url_checks WHERE risk_level IN ('HIGH', 'CRITICAL')"
    ).fetchone()[0]
    recent = cursor.execute(
        "SELECT url, risk_level, timestamp FROM url_checks ORDER BY id DESC LIMIT 10"
    ).fetchall()
    conn.close()

    safety_rate = ((total - threats) / max(total, 1) * 100)

    return {
        "total_urls_checked": total,
        "threats_detected": threats,
        "safety_rate": f"{safety_rate:.1f}%",
        "recent_urls": [dict(row) for row in recent]
    }


@router.get("/recent-urls")
async def get_recent_urls(limit: int = 20):
    """Get recent checked URLs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT url, risk_level, risk_score, timestamp FROM url_checks ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()

    return {
        "recent_urls": [dict(row) for row in rows]
    }

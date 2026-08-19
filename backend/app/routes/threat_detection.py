from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.url_checker import URLChecker
from app.services.content_analyzer import analyze_content
from app.database.connection import get_db_connection

router = APIRouter(prefix="/api/v1/threat", tags=["threat"])

url_checker = URLChecker()


class PageSignals(BaseModel):
    buttons: int = Field(0, ge=0, le=10000)
    iframes: int = Field(0, ge=0, le=10000)
    popups: int = Field(0, ge=0, le=10000)
    overlays: int = Field(0, ge=0, le=10000)
    links: int = Field(0, ge=0, le=100000)


class URLCheckRequest(BaseModel):
    url: str
    view: str = "both"  # simple | technical | both
    page_signals: Optional[PageSignals] = None


class MessageCheckRequest(BaseModel):
    message: str
    url: Optional[str] = None


def classify_threat_type(result: dict) -> str:
    tags = result.get("threat_tags") or []
    if "confirmed_malicious" in tags or "threat_intel" in tags:
        return "phishing"
    if "phishing" in tags or "brand_impersonation" in tags:
        return "phishing"
    if "piracy_scam" in tags or "malvertising" in tags:
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
        "classification": result.get("classification"),
        "explanation": result.get("explanation"),
        "threat_tags": result.get("threat_tags", []),
        "brand_impersonated": result.get("brand_impersonated"),
        "original_url": (result.get("details") or {}).get("original_url"),
        "final_url": (result.get("details") or {}).get("final_url"),
        "redirect_chain": (result.get("details") or {}).get("redirect_chain", []),
        "shortened": (result.get("details") or {}).get("shortened", False),
        "debug": result.get("debug"),
        "evidence": result.get("evidence"),
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

        result = url_checker.analyze(
            url,
            page_signals=request.page_signals.model_dump() if request.page_signals else None,
        )

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

    payload = analyze_content(
        source_type="text",
        text=message,
        urls=[request.url] if request.url else [],
    )
    return {
        "message": message,
        "risk_score": payload["risk_score"],
        "risk_level": payload["risk_level"],
        "safe": payload["safe"],
        "threat_tags": payload["threat_tags"],
        "findings": payload["reasons"],
        "url_check": payload["links"][0] if payload.get("links") else None,
        "simple_view": payload.get("simple_view"),
        "scan_id": payload.get("scan_id"),
        "model_confidence": payload.get("model_confidence"),
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


@router.get("/intel-status")
async def intel_status():
    """Show which public threat feeds are loaded. Does not fetch the scanned page."""
    from app.services.feed_cache import feed_status
    from app.services.threat_intel import GSB_API_KEY, PHISHTANK_API_KEY, URLHAUS_AUTH_KEY
    status = feed_status()
    status["api_keys"] = {
        "google_safe_browsing": bool(GSB_API_KEY),
        "phishtank": bool(PHISHTANK_API_KEY),
        "urlhaus": bool(URLHAUS_AUTH_KEY),
    }
    status["note"] = (
        "OpenPhish, URLhaus, and Phishing Army use public lists. "
        "The PhishTank dump is verified-only; PHISHTANK_API_KEY enables live lookup of unverified reports. "
        "Google Safe Browsing needs GOOGLE_SAFE_BROWSING_API_KEY. A missing key does not invent matches."
    )
    return status


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

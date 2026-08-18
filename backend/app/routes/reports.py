from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from app.services.auth import verify_token
from app.services.reputation import add_report, get_reputation
from app.database.connection import get_db_connection

router = APIRouter(prefix="/api/v1", tags=["reports"])
bearer = HTTPBearer()


class ReportRequest(BaseModel):
    url: str
    domain: Optional[str] = ""
    label: str
    reason: Optional[str] = ""


class FeedbackRequest(BaseModel):
    scan_id: Optional[int] = None
    helpful: bool


def _require_user(credentials: HTTPAuthorizationCredentials) -> int:
    payload = verify_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Sign in to continue.")
    conn = get_db_connection()
    row = conn.execute("SELECT id FROM users WHERE username = ?", (payload["sub"],)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="User not found.")
    return row["id"]


@router.post("/report")
async def report(request: ReportRequest, credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    user_id = _require_user(credentials)
    from urllib.parse import urlparse
    from app.services.url_checker import get_registrable_domain
    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")
    domain = request.domain or get_registrable_domain(urlparse(url if "://" in url else f"https://{url}").netloc)
    try:
        reputation = add_report(user_id, url, domain, request.label, request.reason or "")
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": "Report saved. It is one signal, not proof.", "reputation": reputation}


@router.get("/reputation/domain/{domain}")
async def reputation(domain: str):
    return get_reputation(domain)


@router.post("/feedback")
async def feedback(request: FeedbackRequest, credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    user_id = _require_user(credentials)
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO scan_feedback (scan_id, helpful) VALUES (?, ?)",
        (request.scan_id, 1 if request.helpful else 0),
    )
    conn.commit()
    conn.close()
    return {"message": "Thanks. This helps us review false positives later.", "user_id": user_id}


@router.get("/reports/mine")
async def my_reports(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    user_id = _require_user(credentials)
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT url, domain, user_label, reason, created_at FROM user_reports WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
        (user_id,),
    ).fetchall()
    conn.close()
    return {"reports": [dict(row) for row in rows]}

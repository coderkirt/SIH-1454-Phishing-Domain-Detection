from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.services.auth import verify_token
from app.database.connection import get_db_connection

router = APIRouter(prefix="/api/v1", tags=["scans"])
optional_bearer = HTTPBearer(auto_error=False)
bearer = HTTPBearer()


def _user_id(credentials: Optional[HTTPAuthorizationCredentials]) -> Optional[int]:
    if not credentials:
        return None
    payload = verify_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    conn = get_db_connection()
    row = conn.execute("SELECT id FROM users WHERE username = ?", (payload["sub"],)).fetchone()
    conn.close()
    return row["id"] if row else None


def _require_user(credentials: HTTPAuthorizationCredentials) -> int:
    user_id = _user_id(credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Sign in to continue.")
    return user_id


@router.get("/scans")
async def list_scans(limit: int = Query(50, ge=1, le=200)):
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT id, source_type, url, risk_level, risk_score, scam_risk, confidence, created_at
        FROM content_scans
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return {"scans": [dict(row) for row in rows], "total": len(rows)}


@router.get("/scans/{scan_id}")
async def get_scan(scan_id: int):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM content_scans WHERE id = ?", (scan_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Scan not found.")
    links = conn.execute(
        "SELECT url, domain, risk_score, classification FROM extracted_links WHERE scan_id = ?",
        (scan_id,),
    ).fetchall()
    conn.close()
    data = dict(row)
    data["links"] = [dict(item) for item in links]
    data["privacy"] = "Raw message text is not stored."
    return data


@router.delete("/scans/{scan_id}")
async def delete_scan(scan_id: int, credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    user_id = _require_user(credentials)
    conn = get_db_connection()
    row = conn.execute("SELECT id, user_id FROM content_scans WHERE id = ?", (scan_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Scan not found.")
    if row["user_id"] not in (None, user_id):
        conn.close()
        raise HTTPException(status_code=403, detail="You can only delete your own scans.")
    conn.execute("DELETE FROM extracted_links WHERE scan_id = ?", (scan_id,))
    conn.execute("DELETE FROM scan_feedback WHERE scan_id = ?", (scan_id,))
    conn.execute("DELETE FROM content_scans WHERE id = ?", (scan_id,))
    conn.commit()
    conn.close()
    return {"message": "Analysis deleted.", "scan_id": scan_id}


@router.delete("/scans")
async def delete_history(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    user_id = _require_user(credentials)
    conn = get_db_connection()
    ids = [row["id"] for row in conn.execute(
        "SELECT id FROM content_scans WHERE user_id = ?", (user_id,)
    ).fetchall()]
    for scan_id in ids:
        conn.execute("DELETE FROM extracted_links WHERE scan_id = ?", (scan_id,))
        conn.execute("DELETE FROM scan_feedback WHERE scan_id = ?", (scan_id,))
    conn.execute("DELETE FROM content_scans WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "Your content-scan history was deleted.", "deleted": len(ids)}

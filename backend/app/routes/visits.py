"""Cheap page-open telemetry. Does not run heuristics or RAG."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.database.connection import get_db_connection
from app.services.auth import verify_token
from app.services.visit_service import record_visit

router = APIRouter(prefix="/api/v1", tags=["visits"])
optional_bearer = HTTPBearer(auto_error=False)


class VisitRequest(BaseModel):
    url: str
    client_id: str = Field(..., min_length=8, max_length=80)


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


@router.post("/visits")
async def create_visit(
    request: VisitRequest,
    credentials: HTTPAuthorizationCredentials = Depends(optional_bearer),
):
    url = (request.url or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"
    result = record_visit(url, request.client_id, user_id=_user_id(credentials))
    if result.get("reason") == "invalid_url":
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    if result.get("reason") == "invalid_client_id":
        raise HTTPException(status_code=400, detail="client_id is required")
    return result

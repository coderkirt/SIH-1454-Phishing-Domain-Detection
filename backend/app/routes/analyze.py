from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from app.services.auth import verify_token
from app.services.content_analyzer import analyze_content
from app.services.qr_analyzer import extract_qr_urls
from app.database.connection import get_db_connection

router = APIRouter(prefix="/api/v1/analyze", tags=["analyze"])
optional_bearer = HTTPBearer(auto_error=False)


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


class ContentRequest(BaseModel):
    source_type: str = "text"
    text: str = ""
    urls: list = []
    language: Optional[str] = None
    sender: Optional[dict] = None


@router.post("/content")
async def analyze_any(request: ContentRequest, credentials: HTTPAuthorizationCredentials = Depends(optional_bearer)):
    if not (request.text or "").strip() and not request.urls:
        raise HTTPException(status_code=400, detail="Provide text or at least one URL.")
    return analyze_content(
        source_type=request.source_type,
        text=request.text,
        urls=request.urls,
        sender=request.sender,
        language=request.language,
        user_id=_user_id(credentials),
    )


@router.post("/url")
async def analyze_url(request: ContentRequest, credentials: HTTPAuthorizationCredentials = Depends(optional_bearer)):
    url = request.text or (request.urls[0] if request.urls else "")
    if not url:
        raise HTTPException(status_code=400, detail="Provide a URL.")
    return analyze_content("url", text=url, urls=[url], user_id=_user_id(credentials))


@router.post("/email")
async def analyze_email(request: ContentRequest, credentials: HTTPAuthorizationCredentials = Depends(optional_bearer)):
    return analyze_content("email", request.text, request.urls, request.sender, request.language, _user_id(credentials))


@router.post("/qr")
async def analyze_qr(file: UploadFile = File(...), credentials: HTTPAuthorizationCredentials = Depends(optional_bearer)):
    data = await file.read()
    if len(data) > 5_000_000:
        raise HTTPException(status_code=400, detail="Image is too large (max 5 MB).")
    decoded = extract_qr_urls(data)
    urls = decoded.get("urls") or []
    payloads = decoded.get("payloads") or []
    if not urls and not payloads:
        raise HTTPException(
            status_code=400,
            detail=decoded.get("error") or "No QR code was found in that image. Try a closer, sharper photo of the code.",
        )
    text = " ".join(payloads) if payloads else " ".join(urls)
    return analyze_content("qr", text=text, urls=urls, user_id=_user_id(credentials))


@router.post("/screenshot")
async def analyze_screenshot(
    file: UploadFile = File(...),
    hint: str = Form(""),
    credentials: HTTPAuthorizationCredentials = Depends(optional_bearer),
):
    """Decode QR codes in screenshots, OCR visible text when Tesseract is installed, and score any pasted hint URL."""
    data = await file.read()
    if len(data) > 5_000_000:
        raise HTTPException(status_code=400, detail="Image is too large (max 5 MB).")
    decoded = extract_qr_urls(data)
    text = ""
    try:
        import pytesseract
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(data))
        text = pytesseract.image_to_string(image) or ""
    except Exception:
        text = ""
    urls = list(decoded.get("urls") or [])
    payloads = decoded.get("payloads") or []
    hint_url = (hint or "").strip()
    if hint_url:
        text = f"{text}\n{hint_url}".strip()
        urls.append(hint_url)
    if payloads:
        extra = " ".join(payloads)
        text = f"{text}\n{extra}".strip()
    if not text.strip() and not urls:
        raise HTTPException(
            status_code=400,
            detail="No QR code or readable link was found in that image. Paste the visible URL in the optional link field, or paste the message text on the Message tab.",
        )
        raise HTTPException(
            status_code=400,
            detail="No QR code or readable link was found in that image. Paste the visible URL in the optional link field, or paste the message text on the Message tab.",
        )
    return analyze_content("screenshot", text=text, urls=urls, user_id=_user_id(credentials))

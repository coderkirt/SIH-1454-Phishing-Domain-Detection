"""Normalize email / WhatsApp / SMS / pasted text / webpage into one structure."""

from typing import Dict, Optional
from app.services.url_extractor import extract_urls

VALID_SOURCES = {
    "url", "text", "email", "whatsapp", "sms", "webpage", "screenshot", "qr",
}


def detect_language(text: str) -> str:
    sample = text or ""
    hindi = sum(1 for ch in sample if "\u0900" <= ch <= "\u097F")
    if hindi >= 8:
        return "hi"
    lower = sample.lower()
    hinglish = ("hai", "karo", "account", "otp", "kyc")
    if hindi > 0 or sum(1 for w in hinglish if w in lower) >= 2:
        return "en-hi"
    return "en"


def normalize_content(
    source_type: str,
    text: str = "",
    urls: Optional[list] = None,
    sender: Optional[dict] = None,
    language: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Dict:
    source = (source_type or "text").lower().strip()
    if source not in VALID_SOURCES:
        source = "text"

    raw = (text or "").strip()
    extracted = extract_urls(raw)
    extra = []
    for item in urls or []:
        if isinstance(item, str) and item.strip():
            extra.append(item.strip())
        elif isinstance(item, dict) and item.get("url"):
            extra.append(item["url"])

    merged = list(extracted)
    seen = {item["url"].lower() for item in merged}
    for url in extra:
        if url.lower() not in seen:
            from urllib.parse import urlparse
            from app.services.url_checker import get_registrable_domain
            host = urlparse(url if "://" in url else f"https://{url}").netloc
            merged.append({
                "url": url if "://" in url else f"https://{url}",
                "position": -1,
                "domain": get_registrable_domain(host),
                "shortened": False,
            })
            seen.add(url.lower())

    return {
        "source_type": source,
        "raw_text": raw[:8000],
        "urls": merged[:15],
        "domains": list({item["domain"] for item in merged if item.get("domain")}),
        "sender": sender or {},
        "language": language or detect_language(raw),
        "metadata": metadata or {},
        "store_raw": False,
    }

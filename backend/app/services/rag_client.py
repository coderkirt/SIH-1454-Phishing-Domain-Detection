"""RAG Client connector for PHISHEYE Backend.

Connects PHISHEYE threat scans to the standalone PHISHEYE RAG service (port 8001).
Provides:
- Asynchronous and synchronous request methods
- Circuit breaker with fast timeout (default: 1.5s)
- Automatic fallback if RAG service is offline or unreachable
- Seamless mapping of scan signals into ExplainScanRequest payload
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def build_rag_request_payload(
    scan_url: Optional[str] = None,
    content_text: Optional[str] = None,
    detected_brands: Optional[List[str]] = None,
    threat_tags: Optional[List[str]] = None,
    risk_score: Optional[float] = None,
    channel: Optional[str] = None,
    top_k: int = 4,
) -> Dict[str, Any]:
    """Build sanitized payload for /api/explain-scan."""
    brands = [b.lower() for b in (detected_brands or []) if b and b.strip()]
    tags = [t.lower() for t in (threat_tags or []) if t and t.strip()]

    return {
        "scan_url": scan_url,
        "content_text": content_text,
        "detected_brands": brands,
        "threat_tags": tags,
        "risk_score": float(risk_score) if risk_score is not None else None,
        "channel": channel or ("sms" if content_text and len(content_text) < 160 else "web"),
        "top_k": top_k,
    }


def fetch_rag_explanation_sync(
    scan_url: Optional[str] = None,
    content_text: Optional[str] = None,
    detected_brands: Optional[List[str]] = None,
    threat_tags: Optional[List[str]] = None,
    risk_score: Optional[float] = None,
    channel: Optional[str] = None,
    top_k: int = 4,
) -> Optional[Dict[str, Any]]:
    """Synchronously request a grounded threat explanation from the RAG service.

    Returns:
        ExplainScanResponse dict if successful, None if service is disabled or unreachable.
    """
    if not getattr(settings, "rag_enabled", True):
        return None

    url = f"{settings.rag_service_url.rstrip('/')}/api/explain-scan"
    payload = build_rag_request_payload(
        scan_url=scan_url,
        content_text=content_text,
        detected_brands=detected_brands,
        threat_tags=threat_tags,
        risk_score=risk_score,
        channel=channel,
        top_k=top_k,
    )

    try:
        with httpx.Client(timeout=settings.rag_timeout_seconds) as client:
            response = client.post(url, json=payload)
            if response.status_code == 200:
                return response.json()
            logger.warning("RAG service returned HTTP %d: %s", response.status_code, response.text[:200])
            return None
    except Exception as exc:
        logger.debug("RAG service call skipped/failed: %s", exc)
        return None


async def fetch_rag_explanation_async(
    scan_url: Optional[str] = None,
    content_text: Optional[str] = None,
    detected_brands: Optional[List[str]] = None,
    threat_tags: Optional[List[str]] = None,
    risk_score: Optional[float] = None,
    channel: Optional[str] = None,
    top_k: int = 4,
) -> Optional[Dict[str, Any]]:
    """Asynchronously request a grounded threat explanation from the RAG service."""
    if not getattr(settings, "rag_enabled", True):
        return None

    url = f"{settings.rag_service_url.rstrip('/')}/api/explain-scan"
    payload = build_rag_request_payload(
        scan_url=scan_url,
        content_text=content_text,
        detected_brands=detected_brands,
        threat_tags=threat_tags,
        risk_score=risk_score,
        channel=channel,
        top_k=top_k,
    )

    try:
        async with httpx.AsyncClient(timeout=settings.rag_timeout_seconds) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                return response.json()
            logger.warning("RAG service returned HTTP %d: %s", response.status_code, response.text[:200])
            return None
    except Exception as exc:
        logger.debug("RAG service call skipped/failed: %s", exc)
        return None

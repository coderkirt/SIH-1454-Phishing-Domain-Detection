"""RAG Client connector for PHISHEYE Backend.

Connects PHISHEYE threat scans to the standalone PHISHEYE RAG service (port 8001).
Provides:
- Asynchronous and synchronous request methods
- Circuit breaker with fast timeout (default: 1.5s)
- Automatic fallback if RAG service is offline or unreachable
- Seamless mapping of scan signals into ExplainScanRequest payload
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import httpx

from app.config import settings

ENABLE_RAG = os.getenv("ENABLE_RAG", "true").strip().lower() in {"1", "true", "yes", "on"}
RAG_ASSESS_URL = os.getenv("RAG_ASSESS_URL", "http://127.0.0.1:8091/assess-link")
RAG_TIMEOUT_SECONDS = float(os.getenv("RAG_TIMEOUT_SECONDS", "2"))
CACHE_TTL_SECONDS = 300
_LOGIN_PORTAL_MARKERS = {"erp", "portal", "sso", "webmail", "campus", "ess", "login", "signin"}
_cache: Dict[str, tuple] = {}

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


def unavailable(reason: str = "unavailable") -> Dict:
    return {
        "suspicion_score": None,
        "rule_id": None,
        "rule_summary": None,
        "status": "unavailable",
        "citations": [],
        "reason": reason,
    }


def _cache_key(facts: Dict) -> str:
    payload = {
        "url": facts.get("url"),
        "normalized": facts.get("normalized_url") or facts.get("url"),
        "lookalike": bool(facts.get("lookalike")),
        "secure_login_tokens": bool(facts.get("secure_login_tokens")),
        "ip_host": bool(facts.get("ip_host")),
        "shortened": bool(facts.get("shortened")),
        "brand": facts.get("brand_impersonated"),
        "age": facts.get("domain_age_days"),
        "https": facts.get("https"),
        "tags": list(facts.get("heuristic_tags") or []),
        "trusted": bool(facts.get("trusted_destination") or facts.get("official_brand_domain")),
        "activity": facts.get("local_activity") or {},
        "message": (facts.get("message_context") or "")[:400],
    }
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _valid_payload(data) -> Optional[Dict]:
    if not isinstance(data, dict):
        return None
    status = data.get("status") or "ok"
    if status != "ok":
        return unavailable(str(status))
    score = data.get("suspicion_score")
    if score is None:
        return unavailable("missing_score")
    try:
        score = int(score)
    except (TypeError, ValueError):
        return unavailable("invalid_score")
    return {
        "suspicion_score": max(0, min(100, score)),
        "rule_id": data.get("rule_id"),
        "rule_summary": data.get("rule_summary") or "",
        "status": "ok",
        "citations": list(data.get("citations") or []),
        "activity_note": data.get("activity_note") or "",
    }


def assess_link(facts: Optional[Dict] = None) -> Dict:
    """POST facts to the local assess-link RAG. Soft-fail on disable, timeout, or bad payload."""
    if not ENABLE_RAG:
        return unavailable("disabled")
    facts = facts or {}
    key = _cache_key(facts)
    now = time.time()
    cached = _cache.get(key)
    if cached and now - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]

    body = json.dumps(facts, default=str).encode("utf-8")
    request = Request(
        RAG_ASSESS_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=RAG_TIMEOUT_SECONDS) as response:
            raw = response.read()
        parsed = _valid_payload(json.loads(raw.decode("utf-8")))
        result = parsed if parsed is not None else unavailable("invalid_payload")
    except TimeoutError:
        result = unavailable("timeout")
    except HTTPError as exc:
        result = unavailable(f"http_{exc.code}")
    except (URLError, OSError, ValueError, json.JSONDecodeError):
        result = unavailable("error")

    if result.get("status") != "unavailable":
        _cache[key] = (now, result)
    return result


def collect_facts(
    url: str,
    features: Optional[Dict] = None,
    details: Optional[Dict] = None,
    tags: Optional[list] = None,
    brand_impersonated: Optional[str] = None,
    message_context: Optional[str] = None,
    local_activity: Optional[Dict] = None,
    trusted_destination: bool = False,
) -> Dict:
    features = features or {}
    details = details or {}
    tags = list(tags or [])
    hostname = features.get("hostname") or details.get("domain") or ""
    path = features.get("path") or ""
    query = features.get("query") or ""
    blob = f"{hostname} {path} {query}".lower()
    tokens = ("secure", "login", "signin", "verify", "update", "account")
    host_tokens = set(part for part in hostname.lower().replace("-", ".").split(".") if part)
    path_tokens = set(part for part in path.lower().replace("/", " ").replace("-", " ").split() if part)
    return {
        "url": url or features.get("original") or "",
        "normalized_url": features.get("normalized_full_url") or "",
        "hostname": hostname,
        "registered_domain": features.get("registered_domain") or "",
        "path": path,
        "query": query,
        "lookalike": "brand_impersonation" in tags or bool(brand_impersonated),
        "login_portal": bool(_LOGIN_PORTAL_MARKERS & (host_tokens | path_tokens)),
        "secure_login_tokens": any(token in blob for token in tokens),
        "ip_host": "ip_url" in tags or bool(hostname and hostname.replace(".", "").isdigit()),
        "shortened": bool(details.get("shortened") or "shortened_url" in tags),
        "brand_impersonated": brand_impersonated,
        "official_brand_domain": bool(trusted_destination),
        "domain_age_days": details.get("domain_age_days"),
        "https": details.get("https"),
        "tls": details.get("tls") or {},
        "message_context": (message_context or "")[:2000],
        "local_activity": local_activity or {},
        "heuristic_tags": tags,
        "trusted_destination": bool(trusted_destination),
    }

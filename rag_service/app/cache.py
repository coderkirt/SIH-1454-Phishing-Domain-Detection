"""In-memory LRU and TTL scan explanation cache for the PHISHEYE RAG service."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from app.config import settings
from app.schemas import ExplainScanRequest, ExplainScanResponse


def normalize_url(url: Optional[str]) -> str:
    """Normalize a URL for deterministic caching (lowercases host, strips trailing slash, sorts query params)."""
    if not url or not url.strip():
        return ""
    url = url.strip()
    url_lower = url.lower()
    if not (url_lower.startswith("http://") or url_lower.startswith("https://")):
        url = "http://" + url

    try:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        # Remove standard default ports
        if netloc.endswith(":80") and scheme == "http":
            netloc = netloc[:-3]
        elif netloc.endswith(":443") and scheme == "https":
            netloc = netloc[:-4]

        path = parsed.path.rstrip("/") if parsed.path != "/" else "/"
        
        # Sort query params
        query_items = sorted(parse_qsl(parsed.query, keep_blank_values=True))
        # Filter out volatile tracking params (e.g. utm_*, fbclid, _ga)
        tracking_prefixes = ("utm_", "fbclid", "gclid", "_ga", "_gl")
        clean_query = [
            (k, v) for k, v in query_items
            if not any(k.lower().startswith(prefix) for prefix in tracking_prefixes)
        ]
        query = urlencode(clean_query)
        
        return urlunparse((scheme, netloc, path, parsed.params, query, ""))
    except Exception:
        return url.strip().lower()


def make_cache_key(request: ExplainScanRequest) -> str:
    """Generate a deterministic SHA-256 cache key from an ExplainScanRequest."""
    norm_url = normalize_url(request.scan_url)
    norm_text = " ".join((request.content_text or "").strip().split()).lower()
    norm_brands = sorted({b.strip().lower() for b in request.detected_brands if b.strip()})
    norm_tags = sorted({t.strip().lower() for t in request.threat_tags if t.strip()})
    norm_score = f"{round(request.risk_score, 1)}" if request.risk_score is not None else "none"
    norm_channel = (request.channel or "").strip().lower()
    top_k = request.top_k

    key_payload = {
        "url": norm_url,
        "text": norm_text,
        "brands": norm_brands,
        "tags": norm_tags,
        "score": norm_score,
        "channel": norm_channel,
        "top_k": top_k,
    }

    serialized = json.dumps(key_payload, sort_keys=True, separators=(",", ":"))
    key_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"scan_exp_{key_hash[:32]}"


@dataclass
class CacheEntry:
    response: ExplainScanResponse
    created_at: float
    expires_at: float


class ScanExplanationCache:
    """Thread-safe in-memory cache with LRU eviction and per-item TTL expiration."""

    def __init__(self, max_size: int = 512, default_ttl_seconds: int = 3600):
        self.max_size = max(1, max_size)
        self.default_ttl = max(1, default_ttl_seconds)
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # Telemetry stats
        self._hits: int = 0
        self._misses: int = 0
        self._evictions: int = 0
        self._expirations: int = 0

    def get(self, key: str) -> Optional[ExplainScanResponse]:
        """Retrieve a cached response by key. Returns None on miss or expiration."""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]
            now = time.time()

            if now >= entry.expires_at:
                del self._cache[key]
                self._expirations += 1
                self._misses += 1
                return None

            # Mark as most recently used (move to end)
            self._cache.move_to_end(key)
            self._hits += 1

            # Return a copy marked as cached
            cached_resp = entry.response.model_copy(deep=True)
            cached_resp.cached = True
            return cached_resp

    def set(
        self,
        key: str,
        response: ExplainScanResponse,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Store an explanation response with TTL and enforce LRU capacity limit."""
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        now = time.time()
        entry = CacheEntry(
            response=response.model_copy(deep=True),
            created_at=now,
            expires_at=now + ttl,
        )

        with self._lock:
            if key in self._cache:
                self._cache[key] = entry
                self._cache.move_to_end(key)
                return

            # Check capacity limit and evict least recently used (first item)
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
                self._evictions += 1

            self._cache[key] = entry

    def delete(self, key: str) -> bool:
        """Remove a specific key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all entries and reset telemetry counters."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
            self._expirations = 0

    def cleanup_expired(self) -> int:
        """Prune all expired entries from cache. Returns count of purged items."""
        now = time.time()
        with self._lock:
            expired_keys = [
                k for k, v in self._cache.items() if now >= v.expires_at
            ]
            for k in expired_keys:
                del self._cache[k]
                self._expirations += 1
            return len(expired_keys)

    def stats(self) -> Dict[str, Any]:
        """Return cache health metrics, capacity, and hit-rate telemetry."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests) if total_requests > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "default_ttl_seconds": self.default_ttl,
                "hits": self._hits,
                "misses": self._misses,
                "total_requests": total_requests,
                "hit_rate_pct": round(hit_rate * 100, 2),
                "evictions": self._evictions,
                "expirations": self._expirations,
            }

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)

    def __contains__(self, key: str) -> bool:
        with self._lock:
            return key in self._cache


# Shared service cache instance configured via Settings
scan_cache = ScanExplanationCache(
    max_size=settings.CACHE_SIZE,
    default_ttl_seconds=settings.CACHE_TTL_SECONDS,
)

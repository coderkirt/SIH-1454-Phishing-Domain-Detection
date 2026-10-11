"""Cryptographic provenance, source hashing, and deduplication for knowledge feeds.

Ensures every claim in the RAG service traces back to an auditable source:
- SHA-256 content hashing for integrity verification
- ISO 8601 fetch timestamps and license tracking
- Token-based Jaccard similarity deduplication across multiple threat feeds
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class ProvenanceRecord:
    source_id: str
    source_url: str
    fetched_at: str
    source_hash: str
    license: str
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_url": self.source_url,
            "fetched_at": self.fetched_at,
            "source_hash": self.source_hash,
            "license": self.license,
            "version": self.version,
        }


def compute_source_hash(content: str) -> str:
    """Compute deterministic SHA-256 hash of normalized document content."""
    normalized = re.sub(r"\s+", " ", content.strip()).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def get_current_iso_timestamp() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _shingle_tokens(text: str, k: int = 3) -> Set[str]:
    """Generate k-gram token shingles for similarity calculation."""
    words = re.findall(r"\b[a-z0-9]+\b", text.lower())
    if len(words) < k:
        return set(words)
    return {" ".join(words[i : i + k]) for i in range(len(words) - k + 1)}


def jaccard_similarity(text1: str, text2: str, k: int = 3) -> float:
    """Compute Jaccard similarity coefficient between two text bodies."""
    s1 = _shingle_tokens(text1, k=k)
    s2 = _shingle_tokens(text2, k=k)
    if not s1 or not s2:
        return 0.0
    intersection = len(s1 & s2)
    union = len(s1 | s2)
    return intersection / union if union > 0 else 0.0


class FeedDeduplicator:
    """Detects duplicate and near-duplicate knowledge items across multiple feeds."""

    def __init__(self, similarity_threshold: float = 0.80):
        self.threshold = similarity_threshold
        self.indexed_items: List[Tuple[str, str, Set[str]]] = []  # (id, hash, shingles)

    def is_duplicate(self, doc_id: str, content: str) -> Tuple[bool, Optional[str], float]:
        """Check if content is duplicate of an existing indexed item.

        Returns:
            (is_dup, canonical_id, max_similarity)
        """
        content_hash = compute_source_hash(content)
        shingles = _shingle_tokens(content)

        # Exact SHA-256 match
        for existing_id, existing_hash, existing_shingles in self.indexed_items:
            if existing_hash == content_hash:
                return True, existing_id, 1.0

        # Near-duplicate Jaccard match
        max_sim = 0.0
        canonical_id = None
        for existing_id, _, existing_shingles in self.indexed_items:
            if not shingles or not existing_shingles:
                continue
            sim = len(shingles & existing_shingles) / len(shingles | existing_shingles)
            if sim > max_sim:
                max_sim = sim
                canonical_id = existing_id

        if max_sim >= self.threshold:
            return True, canonical_id, round(max_sim, 4)

        # Not a duplicate; register this item
        self.indexed_items.append((doc_id, content_hash, shingles))
        return False, None, round(max_sim, 4)

    def reset(self) -> None:
        self.indexed_items.clear()

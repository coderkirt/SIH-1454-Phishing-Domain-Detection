"""Tests for cryptographic provenance, source hashing, and feed deduplication."""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.provenance import (
    FeedDeduplicator,
    compute_source_hash,
    jaccard_similarity,
    get_current_iso_timestamp,
)


def test_compute_source_hash():
    text1 = "Urgent: Your account is suspended. Verify now."
    text2 = "Urgent:  Your account  is suspended. Verify now. "
    # Normalized whitespace should yield identical hash
    assert compute_source_hash(text1) == compute_source_hash(text2)
    assert len(compute_source_hash(text1)) == 64  # SHA-256 length


def test_get_current_iso_timestamp():
    ts = get_current_iso_timestamp()
    assert "T" in ts
    assert ts.endswith("Z")


def test_jaccard_similarity():
    s1 = "Adversary-in-the-middle phishing kit intercepts session cookies and tokens."
    s2 = "Adversary-in-the-middle phishing kit intercepts session cookies and passwords."
    s3 = "Unrelated lottery prize winning SMS text message."

    sim_high = jaccard_similarity(s1, s2)
    sim_low = jaccard_similarity(s1, s3)

    assert sim_high > 0.40
    assert sim_low == 0.0


def test_feed_deduplicator():
    dedup = FeedDeduplicator(similarity_threshold=0.85)

    doc_a = "CISA reports adversary in the middle attacks bypassing multi-factor authentication with reverse proxy kits."
    doc_a_dup = "CISA reports adversary in the middle attacks bypassing multi-factor authentication with reverse proxy kits."
    doc_b = "CERT-In alerts citizens against installing suspicious electricity bill update APKs from messaging apps."

    # 1. First insert should be unique
    is_dup, canon, score = dedup.is_duplicate("doc-1", doc_a)
    assert not is_dup
    assert canon is None

    # 2. Duplicate insert should be detected
    is_dup, canon, score = dedup.is_duplicate("doc-2", doc_a_dup)
    assert is_dup
    assert canon == "doc-1"
    assert score == 1.0

    # 3. Different content should be unique
    is_dup, canon, score = dedup.is_duplicate("doc-3", doc_b)
    assert not is_dup
    assert canon is None

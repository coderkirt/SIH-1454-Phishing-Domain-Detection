"""Tests for sparse BM25 retrieval, RRF rank fusion, and hybrid filtering."""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.bm25 import BM25Index, tokenize
from app.chunker import Chunk
from app.retrieval import HybridRetriever, compute_rrf_score, get_retriever


def test_tokenize():
    tokens = tokenize("Urgent: Your SBI net-banking account is blocked! Check https://onlinesbi.sbi")
    assert "urgent" in tokens
    assert "sbi" in tokens
    assert "net-banking" in tokens or "banking" in tokens
    # Common stopwords should be excluded
    assert "is" not in tokens
    assert "your" not in tokens


def test_bm25_fit_and_search():
    chunks = [
        Chunk(
            chunk_id="chunk-1",
            doc_id="doc-1",
            doc_title="Doc 1",
            category="playbook",
            section_title="Sec 1",
            chunk_type="section",
            text="Attacker claims account is suspended and urges immediate verification.",
            metadata={"category": "playbook", "brands": ["_none_"]},
        ),
        Chunk(
            chunk_id="chunk-2",
            doc_id="doc-2",
            doc_title="Doc 2",
            category="brand_guidance",
            section_title="Sec 2",
            chunk_type="section",
            text="PayPal refund scam targets buyers with fake invoice email.",
            metadata={"category": "brand_guidance", "brands": ["paypal"]},
        ),
    ]

    index = BM25Index().fit(chunks)
    res = index.search("PayPal invoice refund", n_results=2)
    assert len(res) == 1
    assert res[0]["chunk_id"] == "chunk-2"
    assert res[0]["score"] > 0.0


def test_compute_rrf_score():
    # Rank 1 dense only
    score_dense_1 = compute_rrf_score(dense_rank=1, sparse_rank=None, k=60, w_dense=0.6, w_sparse=0.4)
    expected_dense_1 = 0.6 / 61
    assert pytest.approx(score_dense_1, rel=1e-4) == expected_dense_1

    # Rank 1 in both modalities
    score_both_1 = compute_rrf_score(dense_rank=1, sparse_rank=1, k=60, w_dense=0.6, w_sparse=0.4)
    expected_both_1 = (0.6 / 61) + (0.4 / 61)
    assert pytest.approx(score_both_1, rel=1e-4) == expected_both_1
    assert score_both_1 > score_dense_1


def test_hybrid_retriever_sbi():
    retriever = get_retriever()
    results = retriever.retrieve(
        query="SBI KYC update required to prevent immediate account block",
        brands=["sbi"],
        threat_tags=["urgency_detected"],
        top_k=3,
    )

    assert len(results) > 0
    top = results[0]
    assert top.score > 0.0
    # Top result should match bank impersonation or KYC playbook
    assert "sbi" in top.doc_title.lower() or "bank" in top.doc_title.lower() or "kyc" in top.doc_title.lower()
    assert top.source_url.startswith("http")


def test_hybrid_retriever_hard_filter():
    retriever = get_retriever()
    results = retriever.retrieve(
        query="urgent security notice verify password",
        categories=["brand_guidance"],
        top_k=5,
        hard_filter=True,
    )

    assert len(results) > 0
    for r in results:
        assert r.category == "brand_guidance", f"Expected only brand_guidance, got {r.category}"


def test_hybrid_retriever_signal_boosting():
    retriever = get_retriever()
    # Without brand filter
    unboosted = retriever.retrieve(
        query="fake lottery prize money won",
        top_k=5,
        signal_boost=1.0,
    )
    # With greed_bait signal boost
    boosted = retriever.retrieve(
        query="fake lottery prize money won",
        threat_tags=["greed_bait"],
        top_k=5,
        signal_boost=1.5,
    )

    assert len(unboosted) > 0
    assert len(boosted) > 0
    # Top boosted result should have matched signal
    assert any("tag:greed_bait" in b.matched_signals for b in boosted)

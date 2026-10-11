"""Unit and integration tests for ChromaDB knowledge ingestion and chunking."""

import sys
from pathlib import Path
import pytest
import chromadb

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chunker import chunk_document, chunk_corpus, _slugify
from app.chroma_store import get_or_create_collection, ingest_corpus, query_similar
from app.corpus import CorpusDocument, load_corpus


def test_slugify():
    assert _slugify("How the scam works") == "how-the-scam-works"
    assert _slugify("Warning signs for analysts!") == "warning-signs-for-analysts"
    assert _slugify("T1566 – Phishing") == "t1566-phishing"


def test_chunk_document():
    doc = CorpusDocument(
        id="test-doc-1",
        title="Test Phishing Lure",
        category="playbook",
        source="Test Source",
        source_url="https://example.com/test",
        last_verified="2026-10-11",
        summary="A test phishing lure explanation.",
        language="en",
        region="global",
        channels=["email", "sms"],
        brands=["paypal"],
        threat_tags=["urgency_detected"],
        mitre=["T1566"],
        body="## How it works\n\nAttacker sends a fake message.\n\n## User guidance\n\nDo not click links.",
    )

    chunks = chunk_document(doc)
    assert len(chunks) == 3  # 1 overview + 2 sections

    # Check overview chunk
    overview = chunks[0]
    assert overview.chunk_id == "test-doc-1#overview"
    assert overview.chunk_type == "overview"
    assert "Test Phishing Lure" in overview.text
    assert overview.metadata["doc_id"] == "test-doc-1"
    assert overview.metadata["brands"] == ["paypal"]

    # Check section chunks
    sec1 = chunks[1]
    assert sec1.chunk_id == "test-doc-1#how-it-works"
    assert sec1.section_title == "How it works"
    assert "Attacker sends a fake message." in sec1.text

    sec2 = chunks[2]
    assert sec2.chunk_id == "test-doc-1#user-guidance"
    assert sec2.section_title == "User guidance"


def test_chunk_corpus_unique_ids():
    docs = load_corpus()
    chunks = chunk_corpus(docs)
    assert len(chunks) >= len(docs)
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids)), "All chunk IDs must be globally unique"


def test_chroma_ephemeral_ingest_and_query():
    client = chromadb.EphemeralClient()
    docs = load_corpus()
    test_collection_name = "test_phishing_knowledge"

    # Ingest into ephemeral client
    stats = ingest_corpus(
        docs=docs,
        reset=True,
        collection_name=test_collection_name,
    )
    assert stats["total_chunks"] == len(chunk_corpus(docs))
    assert stats["indexed_chunks"] > 0

    # Query for bank kyc
    results = query_similar(
        query_text="SBI account blocked KYC required",
        n_results=2,
        collection_name=test_collection_name,
    )
    assert len(results) > 0
    top = results[0]
    assert top["score"] > 0.0
    assert "metadata" in top
    assert "chunk_id" in top

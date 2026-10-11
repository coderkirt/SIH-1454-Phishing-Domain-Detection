"""Unit and integration tests for the citation resolution and synthesis engine."""

import asyncio
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.generator import generate_explanation, resolve_citations, synthesize_deterministic
from app.retrieval import RetrievedChunk, get_retriever
from app.schemas import ExplainScanRequest


def test_resolve_citations():
    chunk1 = RetrievedChunk(
        chunk_id="brand-sbi#recurring-lures",
        doc_id="brand-bank-impersonation-india",
        doc_title="Indian Bank Impersonation",
        section_title="Recurring lures",
        category="brand_guidance",
        source="RBI",
        source_url="https://www.rbi.org.in/",
        last_verified="2026-10-11",
        text="Banks never ask for OTP or PAN card over SMS.",
        score=0.9,
    )
    citation_map = {"[cite-1]": chunk1}

    citations = resolve_citations(
        text="This message matches known bank fraud lures [cite-1].",
        citation_map=citation_map,
        retrieved_chunks=[chunk1],
    )

    assert len(citations) >= 1
    c = citations[0]
    assert c.doc_id == "brand-bank-impersonation-india"
    assert c.source == "RBI"
    assert c.source_url == "https://www.rbi.org.in/"
    assert "Banks never ask for OTP" in c.snippet


def test_synthesize_deterministic_phishing():
    req = ExplainScanRequest(
        scan_url="https://secure-login.onlinesbi-kyc.top/verify",
        content_text="Your SBI NetBanking account will be blocked today due to pending KYC.",
        detected_brands=["sbi"],
        threat_tags=["urgency_detected", "credential_pressure"],
        risk_score=92.0,
        channel="sms",
    )

    retriever = get_retriever()
    chunks = retriever.retrieve(req.content_text, brands=req.detected_brands, top_k=2)
    citation_map = {f"[cite-{i}]": c for i, c in enumerate(chunks, 1)}

    resp = synthesize_deterministic(req, chunks, citation_map)

    assert resp.verdict == "PHISHING"
    assert resp.risk_score == 92.0
    assert len(resp.citations) >= 1
    assert resp.brand_analysis is not None
    assert "onlinesbi.sbi" in resp.brand_analysis.official_domains
    assert len(resp.actionable_recommendations) >= 2


def test_synthesize_deterministic_benign():
    req = ExplainScanRequest(
        scan_url="https://google.com/search",
        content_text="Search for general news",
        risk_score=10.0,
    )

    resp = synthesize_deterministic(req, [], {})
    assert resp.verdict == "BENIGN"
    assert resp.risk_score == 10.0


def test_generate_explanation_async():
    req = ExplainScanRequest(
        scan_url="https://paypal-invoice-dispute.example.com",
        content_text="PayPal: You authorized payment of $450 to unknown seller.",
        detected_brands=["paypal"],
        threat_tags=["fear_tactics", "financial_pressure"],
        risk_score=85.0,
        channel="email",
    )

    retriever = get_retriever()
    chunks = retriever.retrieve(req.content_text, brands=req.detected_brands, top_k=2)

    resp = asyncio.run(generate_explanation(req, chunks))

    assert resp.verdict == "PHISHING"
    assert resp.latency_ms >= 0.0
    assert len(resp.citations) >= 1
    assert resp.model_used is not None
    assert any("paypal" in c.source_url.lower() or "paypal" in c.title.lower() for c in resp.citations)

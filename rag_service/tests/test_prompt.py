"""Unit tests for grounded prompt generation."""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.prompt import build_grounded_prompt, format_context_chunk, format_scan_indicators
from app.retrieval import RetrievedChunk
from app.schemas import ExplainScanRequest


def test_format_scan_indicators():
    req = ExplainScanRequest(
        scan_url="https://fake-sbi-portal.com",
        content_text="Update KYC now",
        detected_brands=["sbi"],
        threat_tags=["urgency_detected"],
        risk_score=88.0,
        channel="sms",
    )
    formatted = format_scan_indicators(req)
    assert "https://fake-sbi-portal.com" in formatted
    assert "sbi" in formatted
    assert "88.0/100" in formatted
    assert "sms" in formatted


def test_format_context_chunk():
    chunk = RetrievedChunk(
        chunk_id="test-doc#section-1",
        doc_id="test-doc",
        doc_title="Test Phishing Doc",
        section_title="How it works",
        category="playbook",
        source="CERT-In",
        source_url="https://cert-in.org.in/",
        last_verified="2026-10-11",
        text="Never share OTP with anyone.",
        score=0.9,
    )
    formatted = format_context_chunk(1, chunk)
    assert "[cite-1]" in formatted
    assert "Test Phishing Doc" in formatted
    assert "CERT-In" in formatted
    assert "https://cert-in.org.in/" in formatted
    assert "Never share OTP with anyone." in formatted


def test_build_grounded_prompt():
    req = ExplainScanRequest(
        scan_url="https://paypal-security-alert.net",
        content_text="Unauthorized payment of $500 detected.",
        detected_brands=["paypal"],
        threat_tags=["fear_tactics"],
    )

    chunk = RetrievedChunk(
        chunk_id="brand-paypal#common-patterns",
        doc_id="brand-paypal",
        doc_title="PayPal Impersonation",
        section_title="Common impersonation patterns",
        category="brand_guidance",
        source="PayPal Advisory",
        source_url="https://www.paypal.com/security",
        last_verified="2026-10-11",
        text="PayPal never uses third party domains.",
        score=0.85,
    )

    prompt = build_grounded_prompt(req, [chunk])
    assert "STRICT GROUNDING RULES" in prompt["system_prompt"]
    assert "ANTI-HALLUCINATION POLICY" in prompt["system_prompt"]
    assert "[cite-1]" in prompt["user_prompt"]
    assert "[cite-1]" in prompt["citation_map"]
    assert prompt["citation_map"]["[cite-1]"].doc_id == "brand-paypal"

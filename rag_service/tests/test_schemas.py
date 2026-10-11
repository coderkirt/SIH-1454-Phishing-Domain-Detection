"""Tests for Pydantic request and response schemas."""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas import (
    Citation,
    ExplainScanRequest,
    ExplainScanResponse,
    HealthResponse,
    PlaybookMatch,
    BrandAnalysis,
)


def test_explain_scan_request_validation():
    req = ExplainScanRequest(
        scan_url="https://fake-login.example.com",
        content_text="Verify account immediately",
        detected_brands=["paypal"],
        threat_tags=["urgency_detected"],
        risk_score=90.0,
        channel="email",
    )
    assert req.scan_url == "https://fake-login.example.com"
    assert req.risk_score == 90.0
    assert "paypal" in req.detected_brands

    # Invalid risk score should raise validation error
    with pytest.raises(Exception):
        ExplainScanRequest(risk_score=150.0)


def test_explain_scan_response_serialization():
    citation = Citation(
        doc_id="playbook-account-suspension-lure",
        chunk_id="playbook-account-suspension-lure#overview",
        title="Account Suspension Lures",
        source="FTC",
        source_url="https://consumer.ftc.gov/",
        section="Overview",
        snippet="Attackers claim account will be suspended.",
    )

    playbook = PlaybookMatch(
        playbook_id="playbook-account-suspension-lure",
        title="Account Suspension Lures",
        mechanism="Harvesting credentials via lookalike login forms.",
        warning_signs=["Urgent deadline", "Lookalike domain"],
    )

    resp = ExplainScanResponse(
        verdict="PHISHING",
        risk_score=92.0,
        summary="This is an account suspension phishing lure.",
        matched_playbook=playbook,
        citations=[citation],
        actionable_recommendations=["Do not enter credentials."],
    )

    data = resp.model_dump()
    assert data["verdict"] == "PHISHING"
    assert len(data["citations"]) == 1
    assert data["citations"][0]["source"] == "FTC"
    assert data["matched_playbook"]["playbook_id"] == "playbook-account-suspension-lure"

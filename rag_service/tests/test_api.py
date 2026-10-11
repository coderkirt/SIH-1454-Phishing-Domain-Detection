"""Integration tests for the PHISHEYE FastAPI RAG Service endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.cache import scan_cache
from app.main import app


@pytest.fixture(scope="module")
def client():
    """Create a test client that runs the FastAPI app lifespan events."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_cache():
    """Ensure clean cache before each test."""
    scan_cache.clear()
    yield
    scan_cache.clear()


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "PHISHEYE Standalone RAG Service"
    assert "/api/explain-scan" in data["explain_scan_url"]


def test_health_endpoint(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "phisheye-rag-service"
    assert data["version"] == "1.0.0"
    assert data["indexed_chunks"] > 0
    assert data["corpus_documents"] > 0


def test_explain_scan_phishing_pipeline(client: TestClient):
    payload = {
        "scan_url": "https://secure-login.onlinesbi-kyc.top/update",
        "content_text": "Dear customer, your SBI account is blocked. Update PAN card immediately to avoid permanent deactivation.",
        "detected_brands": ["sbi"],
        "threat_tags": ["urgency_detected", "credential_pressure", "brand_impersonation"],
        "risk_score": 92.5,
        "channel": "sms",
        "top_k": 4,
    }

    # 1. First execution - Cache Miss
    res1 = client.post("/api/explain-scan", json=payload)
    assert res1.status_code == 200
    data1 = res1.json()

    assert data1["verdict"] == "PHISHING"
    assert data1["risk_score"] == 92.5
    assert len(data1["summary"]) > 20
    assert len(data1["citations"]) >= 1
    assert data1["cached"] is False
    assert data1["latency_ms"] >= 0.0

    # Verify citation fields
    citation = data1["citations"][0]
    assert "doc_id" in citation
    assert "source_url" in citation
    assert len(citation["snippet"]) > 5

    # Verify brand analysis was generated
    assert data1["brand_analysis"] is not None
    assert "onlinesbi.sbi" in data1["brand_analysis"]["official_domains"]

    # Verify playbook match
    assert data1["matched_playbook"] is not None

    # 2. Second execution - Cache Hit
    res2 = client.post("/api/explain-scan", json=payload)
    assert res2.status_code == 200
    data2 = res2.json()

    assert data2["cached"] is True
    assert data2["verdict"] == "PHISHING"
    # Latency of cached response should be very low
    assert data2["latency_ms"] < 100.0


def test_explain_scan_benign(client: TestClient):
    payload = {
        "scan_url": "https://www.google.com/search?q=cybersecurity",
        "content_text": "Official search results for cybersecurity best practices",
        "detected_brands": [],
        "threat_tags": [],
        "risk_score": 5.0,
        "channel": "web",
        "top_k": 2,
    }

    res = client.post("/api/explain-scan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["verdict"] == "BENIGN"
    assert data["risk_score"] == 5.0
    assert any(term in data["summary"].lower() for term in ["did not detect", "benign", "safe", "low risk"])


def test_cache_stats_and_clear_endpoints(client: TestClient):
    payload = {
        "scan_url": "https://fake-lottery.top/claim",
        "content_text": "Congratulations! You won 1,000,000 INR prize. Click here to claim your reward.",
        "detected_brands": [],
        "threat_tags": ["prize_lottery", "urgency_detected"],
        "risk_score": 85.0,
        "channel": "sms",
    }

    # Query to populate cache
    client.post("/api/explain-scan", json=payload)

    # Check stats
    stats_res = client.get("/api/cache/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["size"] == 1

    # Clear cache
    clear_res = client.post("/api/cache/clear")
    assert clear_res.status_code == 200
    assert clear_res.json()["status"] == "cleared"

    # Verify cleared
    stats_after = client.get("/api/cache/stats").json()
    assert stats_after["size"] == 0

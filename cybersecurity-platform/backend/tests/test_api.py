import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Unique username per test run so signup never conflicts with old data
TEST_USER = f"testuser_{uuid.uuid4().hex[:8]}"
TEST_EMAIL = f"{TEST_USER}@example.com"
TEST_PASSWORD = "pass123"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_check_safe_url():
    response = client.post("/api/v1/threat/check-url", json={"url": "https://www.google.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "LOW"
    assert data["safe"] == True


def test_check_phishing_url():
    response = client.post("/api/v1/threat/check-url", json={"url": "https://paypa1.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] in ["HIGH", "CRITICAL"]
    assert data["safe"] == False
    assert len(data["reasons"]) > 0
    assert "simple_view" in data
    assert "technical_view" in data
    assert "PayPal" in data["simple_view"]["warning"]


def test_check_piracy_url():
    response = client.post("/api/v1/threat/check-url", json={"url": "https://hdhub4u.med"})
    assert response.status_code == 200
    data = response.json()
    assert data["safe"] is False
    assert data["risk_level"] in ["HIGH", "CRITICAL"]


def test_check_message_urgency():
    response = client.post("/api/v1/threat/check-message", json={
        "message": "Aapka account block ho jayega. Abhi click karo. Act now!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "urgency_detected" in data["threat_tags"] or "fear_tactics" in data["threat_tags"]
    assert data["safe"] is False
    assert "simple_view" in data


def test_threat_stats():
    response = client.get("/api/v1/threat/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_urls_checked"] >= 1
    assert "safety_rate" in data


def test_recent_urls():
    response = client.get("/api/v1/threat/recent-urls")
    assert response.status_code == 200
    assert "recent_urls" in response.json()


def test_signup():
    response = client.post("/api/v1/user/signup", json={
        "username": TEST_USER,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User created successfully"
    assert "access_token" in data


def test_signup_duplicate():
    response = client.post("/api/v1/user/signup", json={
        "username": TEST_USER,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 400


def test_login():
    response = client.post("/api/v1/user/login", json={
        "username": TEST_USER,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password():
    response = client.post("/api/v1/user/login", json={
        "username": TEST_USER,
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_profile():
    login = client.post("/api/v1/user/login", json={
        "username": TEST_USER,
        "password": TEST_PASSWORD
    })
    token = login.json()["access_token"]
    response = client.get("/api/v1/user/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == TEST_USER
    assert data["email"] == TEST_EMAIL


def test_stats_overview():
    response = client.get("/api/v1/stats/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_urls_checked" in data
    assert "safety_rate" in data


def test_stats_threat_types():
    response = client.get("/api/v1/stats/threat-types")
    assert response.status_code == 200
    assert "threat_types" in response.json()


def test_stats_risk_distribution():
    response = client.get("/api/v1/stats/risk-distribution")
    assert response.status_code == 200
    data = response.json()
    assert set(data["risk_distribution"].keys()) == {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def test_stats_daily_summary():
    response = client.get("/api/v1/stats/daily-summary")
    assert response.status_code == 200
    data = response.json()
    assert "urls_checked_today" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

import cv2
from fastapi.testclient import TestClient
from app.main import app
from app.services.qr_analyzer import extract_qr_urls

client = TestClient(app)


def _png_qr(text: str) -> bytes:
    encoder = cv2.QRCodeEncoder.create()
    image = encoder.encode(text)
    ok, encoded = cv2.imencode(".png", image)
    assert ok
    return encoded.tobytes()


def test_extracts_small_qr_url():
    decoded = extract_qr_urls(_png_qr("https://paypa1.com/login"))
    assert any("paypa1.com" in url for url in decoded["urls"])


def test_extracts_www_qr_as_https():
    decoded = extract_qr_urls(_png_qr("www.example.com"))
    assert any(url.startswith("https://www.example.com") for url in decoded["urls"])


def test_analyze_qr_endpoint():
    response = client.post(
        "/api/v1/analyze/qr",
        files={"file": ("qr.png", _png_qr("https://paypa1.com"), "image/png")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["source_type"] == "qr"
    assert data.get("url") or (data.get("links") or [])
    assert any("paypa1.com" in (url or "") for url in (data.get("qr_urls") or [data.get("url")]))
    assert data.get("decoded_text")


def test_analyze_qr_plain_payload_is_returned():
    response = client.post(
        "/api/v1/analyze/qr",
        files={"file": ("qr.png", _png_qr("UPI:merchant@okaxis"), "image/png")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "UPI:merchant@okaxis" in (data.get("decoded_text") or "")
    assert data.get("qr_payloads")

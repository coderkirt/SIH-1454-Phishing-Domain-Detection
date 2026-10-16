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
        files={"file": ("qr.png", _png_qr("upi://pay?pa=merchant@okaxis&pn=Shop&am=10"), "image/png")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "merchant@okaxis" in (data.get("decoded_text") or "")
    assert data.get("qr_payloads")
    code = (data.get("qr_codes") or [{}])[0]
    labels = {item.get("label"): item.get("value") for item in code.get("details") or []}
    assert labels.get("Payee") == "merchant@okaxis"
    assert labels.get("Amount") == "10"


def _png_two(left: str, right: str) -> bytes:
    import numpy as np

    encoder = cv2.QRCodeEncoder.create()
    first = encoder.encode(left)
    second = encoder.encode(right)
    canvas = np.full((max(first.shape[0], second.shape[0]) + 80, first.shape[1] + second.shape[1] + 120), 255, np.uint8)
    canvas[40:40 + first.shape[0], 40:40 + first.shape[1]] = first
    canvas[40:40 + second.shape[0], 80 + first.shape[1]:80 + first.shape[1] + second.shape[1]] = second
    ok, encoded = cv2.imencode(".png", canvas)
    assert ok
    return encoded.tobytes()


def test_analyze_qr_returns_every_code():
    image = _png_two("https://paypa1.com/a", "https://evil.example/b")
    decoded = extract_qr_urls(image)
    assert any("paypa1.com" in url for url in decoded["urls"])
    assert any("evil.example" in url for url in decoded["urls"])
    response = client.post(
        "/api/v1/analyze/qr",
        files={"file": ("qr.png", image, "image/png")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    joined = " ".join(data.get("qr_payloads") or [])
    assert "paypa1.com" in joined and "evil.example" in joined
    scored = " ".join(link.get("url") or "" for link in data.get("links") or [])
    assert "paypa1.com" in scored and "evil.example" in scored

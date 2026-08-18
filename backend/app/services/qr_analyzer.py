"""QR decode from an uploaded image. Does not visit the destination."""

import re
from typing import Dict, List, Optional

from app.services.url_extractor import extract_urls

HTTP_IN_TEXT = re.compile(r"(?i)https?://[^\s<>'\"\]]+")
BARE_HOST = re.compile(r"(?i)^(?:www\.)?[a-z0-9][a-z0-9.-]+\.[a-z]{2,}(?:/[^\s]*)?$")


def _normalize_payload(raw: str) -> Optional[str]:
    text = (raw or "").strip().strip("\x00")
    if not text:
        return None
    match = HTTP_IN_TEXT.search(text)
    if match:
        return match.group(0).rstrip(".,;:!?)")
    if text.lower().startswith("www."):
        return "https://" + text
    if BARE_HOST.match(text):
        return "https://" + text
    return None


def _collect_urls(payloads: List[str]) -> List[str]:
    found: List[str] = []
    seen = set()

    def add(url: str):
        value = (url or "").strip()
        if not value:
            return
        if not value.lower().startswith(("http://", "https://")):
            value = "https://" + value
        key = value.lower()
        if key in seen:
            return
        seen.add(key)
        found.append(value)

    for payload in payloads:
        normalized = _normalize_payload(payload)
        if normalized:
            add(normalized)
        for item in extract_urls(payload):
            add(item.get("url") or "")
    return found[:15]


def _variants(image):
    import cv2

    yield image
    gray = image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    yield gray
    yield cv2.bitwise_not(gray)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    yield blurred
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    yield otsu
    yield cv2.bitwise_not(otsu)
    try:
        adaptive = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 5
        )
        yield adaptive
        yield cv2.bitwise_not(adaptive)
    except Exception:
        return


def _scaled(image):
    import cv2

    height, width = image.shape[:2]
    longest = max(height, width)
    yield image
    if longest < 480:
        factor = 480 / max(longest, 1)
        yield cv2.resize(image, None, fx=factor, fy=factor, interpolation=cv2.INTER_NEAREST)
        yield cv2.resize(image, None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)
    if longest > 1800:
        factor = 1400 / longest
        yield cv2.resize(image, None, fx=factor, fy=factor, interpolation=cv2.INTER_AREA)


def _decode_with_detector(image) -> List[str]:
    import cv2

    detector = cv2.QRCodeDetector()
    payloads: List[str] = []
    data, _points, _ = detector.detectAndDecode(image)
    if data:
        payloads.append(data.strip())
    if hasattr(detector, "detectAndDecodeMulti"):
        try:
            ok, decoded, _pts, _ = detector.detectAndDecodeMulti(image)
            if ok and decoded is not None:
                for item in decoded:
                    if item and str(item).strip():
                        payloads.append(str(item).strip())
        except Exception:
            pass
    return payloads


def extract_qr_urls(image_bytes: bytes) -> Dict:
    payloads: List[str] = []
    error = None
    try:
        import numpy as np
        import cv2

        array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if image is None:
            image = cv2.imdecode(array, cv2.IMREAD_UNCHANGED)
        if image is None:
            return {"urls": [], "payloads": [], "error": "Could not read that image."}

        padded = cv2.copyMakeBorder(image, 16, 16, 16, 16, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        seen = set()
        for scaled in _scaled(padded):
            for variant in _variants(scaled):
                for payload in _decode_with_detector(variant):
                    if payload and payload not in seen:
                        seen.add(payload)
                        payloads.append(payload)
                if payloads:
                    break
            if payloads:
                break
    except ImportError:
        error = "QR scanning needs opencv-python-headless. Paste the URL instead."
    except Exception as exc:
        error = str(exc)[:160]

    urls = _collect_urls(payloads)
    if not payloads and not error:
        error = "No QR code was found in that image."
    return {"urls": urls, "payloads": payloads, "error": error}

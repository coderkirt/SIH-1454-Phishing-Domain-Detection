"""QR decode from an uploaded image. Does not visit the destination."""

import re
from typing import Dict, List, Optional
from urllib.parse import parse_qs, unquote, urlparse

from app.services.url_extractor import extract_urls

HTTP_IN_TEXT = re.compile(r"(?i)https?://[^\s<>'\"\]]+")
BARE_HOST = re.compile(r"(?i)^(?:www\.)?[a-z0-9][a-z0-9.-]+\.[a-z]{2,}(?:/[^\s]*)?$")


def _normalize_payload(raw: str) -> Optional[str]:
    text = (raw or "").strip().strip("\x00").replace("\r", " ").replace("\n", "").strip()
    if not text:
        return None
    match = HTTP_IN_TEXT.search(text)
    if match:
        return match.group(0).rstrip(".,;:!?)")
    lower = text.lower()
    if lower.startswith("www."):
        return "https://" + text.split()[0]
    if BARE_HOST.match(text.split()[0]):
        return "https://" + text.split()[0]
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
    try:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        yield clahe.apply(gray)
    except Exception:
        pass
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    yield otsu
    yield cv2.bitwise_not(otsu)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    yield cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, kernel)
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
    if longest < 720:
        factor = 720 / max(longest, 1)
        yield cv2.resize(image, None, fx=factor, fy=factor, interpolation=cv2.INTER_NEAREST)
        yield cv2.resize(image, None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)
    if 200 < longest < 900:
        yield cv2.resize(image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
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


def _read_image(image_bytes: bytes):
    import numpy as np
    import cv2

    array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        image = cv2.imdecode(array, cv2.IMREAD_UNCHANGED)
    if image is not None:
        if len(image.shape) == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        return image
    try:
        from PIL import Image
        import io

        pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        rgb = np.array(pil)
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    except Exception:
        return None


UPI_LABELS = {
    "pa": "Payee",
    "pn": "Name",
    "am": "Amount",
    "cu": "Currency",
    "tn": "Note",
    "mc": "Merchant code",
    "url": "Website",
    "mode": "Mode",
    "tr": "Reference",
}


def _detail(label: str, value: str) -> Optional[Dict]:
    text = (value or "").strip()
    if not text:
        return None
    return {"label": label, "value": text}


def _describe_payload(payload: str) -> Dict:
    text = (payload or "").strip()
    lower = text.lower()
    details: List[Dict] = []
    kind = "Text"
    if lower.startswith("upi://") or (lower.startswith("upi:") and "pa=" in lower):
        kind = "UPI"
        query = urlparse(text if "://" in text else "upi://pay?" + text.split("?", 1)[-1]).query
        fields = parse_qs(query)
        for key, label in UPI_LABELS.items():
            values = fields.get(key) or []
            item = _detail(label, unquote(values[0]) if values else "")
            if item:
                details.append(item)
    elif lower.startswith("wifi:"):
        kind = "Wi-Fi"
        for key, label in (("S", "Network"), ("T", "Security"), ("P", "Password"), ("H", "Hidden")):
            match = re.search(rf"(?:^|;){key}:([^;]*)", text, re.I)
            item = _detail(label, match.group(1) if match else "")
            if item:
                details.append(item)
    elif lower.startswith("mailto:"):
        kind = "Email"
        item = _detail("Address", text.split(":", 1)[1].split("?", 1)[0])
        if item:
            details.append(item)
    elif lower.startswith("tel:"):
        kind = "Phone"
        item = _detail("Number", text.split(":", 1)[1])
        if item:
            details.append(item)
    elif lower.startswith("sms:"):
        kind = "SMS"
        item = _detail("To", text.split(":", 1)[1].split("?", 1)[0])
        if item:
            details.append(item)
    elif lower.startswith("begin:vcard"):
        kind = "Contact"
        for key, label in (("FN", "Name"), ("TEL", "Phone"), ("EMAIL", "Email"), ("ORG", "Organization")):
            match = re.search(rf"(?im)^{key}[^:]*:(.+)$", text)
            item = _detail(label, match.group(1) if match else "")
            if item:
                details.append(item)
    elif lower.startswith(("http://", "https://")):
        kind = "Website"
    return {"type": kind, "details": details}


def _remember(found: List[str], seen: set, text: str):
    payload = (text or "").strip().strip("\x00")
    if payload and payload not in seen:
        seen.add(payload)
        found.append(payload)


def _decode_zxing(image) -> List[str]:
    import zxingcpp

    found: List[str] = []
    seen = set()
    views = [image]
    height, width = image.shape[:2]
    longest = max(height, width)
    import cv2

    if longest < 900:
        views.append(cv2.resize(image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_NEAREST))
    if longest > 2200:
        factor = 1600 / longest
        views.append(cv2.resize(image, None, fx=factor, fy=factor, interpolation=cv2.INTER_AREA))
    for view in views:
        for result in zxingcpp.read_barcodes(view):
            label = str(getattr(result, "format", "") or "").upper()
            if label and "QR" not in label and "AZTEC" not in label and "DATA" not in label and "PDF" not in label:
                continue
            _remember(found, seen, getattr(result, "text", "") or "")
        if found:
            break
    return found


def _decode_opencv(image) -> List[str]:
    import cv2

    found: List[str] = []
    seen = set()
    padded = cv2.copyMakeBorder(image, 24, 24, 24, 24, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    detectors = [cv2.QRCodeDetector()]
    if hasattr(cv2, "QRCodeDetectorAruco"):
        detectors.append(cv2.QRCodeDetectorAruco())
    for scaled in _scaled(padded):
        for variant in _variants(scaled):
            for detector in detectors:
                try:
                    ok, decoded, _points, _straight = detector.detectAndDecodeMulti(variant)
                except Exception:
                    ok, decoded = False, ()
                if ok and decoded is not None:
                    for item in decoded:
                        _remember(found, seen, str(item or ""))
                data, _points, _straight = detector.detectAndDecode(variant)
                _remember(found, seen, data if isinstance(data, str) else "")
            if found:
                return found
    return found


def _build_codes(payloads: List[str]) -> List[Dict]:
    codes = []
    for payload in payloads:
        described = _describe_payload(payload)
        codes.append({
            "payload": payload,
            "type": described["type"],
            "urls": _collect_urls([payload]),
            "details": described["details"],
        })
    return codes


def extract_qr_urls(image_bytes: bytes) -> Dict:
    payloads: List[str] = []
    error = None
    try:
        image = _read_image(image_bytes)
        if image is None:
            return {"urls": [], "payloads": [], "codes": [], "error": "Could not read that image."}
        try:
            payloads = _decode_zxing(image)
        except ImportError:
            payloads = []
        if not payloads:
            payloads = _decode_opencv(image)
    except ImportError:
        error = "QR scanning needs opencv-python-headless. Paste the URL instead."
    except Exception as exc:
        error = str(exc)[:160]

    codes = _build_codes(payloads)
    urls = _collect_urls(payloads)
    if not payloads and not error:
        error = "No QR code was found in that image."
    return {"urls": urls, "payloads": payloads, "codes": codes, "error": error}

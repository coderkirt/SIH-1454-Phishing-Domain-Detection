"""Attachment safety — metadata only. Files are never executed or opened as documents."""

from typing import Dict

DANGEROUS_EXTENSIONS = {
    "exe", "apk", "bat", "cmd", "scr", "js", "vbs", "ps1", "dll", "jar", "msi",
}
ARCHIVE_EXTENSIONS = {"zip", "rar", "7z", "gz"}
DOC_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"}

DEEP_SCAN_STATUS = "PLANNED"


def inspect_filename(filename: str, mime_type: str = "") -> Dict:
    name = (filename or "").strip()
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    tags = []
    score = 0
    if ext in DANGEROUS_EXTENSIONS:
        tags.append("dangerous_executable")
        score = 90
    elif ext in ARCHIVE_EXTENSIONS:
        tags.append("archive")
        score = 40
    elif ext in DOC_EXTENSIONS:
        tags.append("document")
        score = 15
    return {
        "filename": name[:200],
        "extension": ext,
        "mime_type": (mime_type or "")[:100],
        "risk_score": score,
        "threat_tags": tags,
        "deep_scan": DEEP_SCAN_STATUS,
        "executed": False,
        "note": "Deep content scanning of attachments is planned. This check only looks at the filename and type.",
    }

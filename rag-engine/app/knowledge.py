"""Load markdown/JSON knowledge-base notes."""

import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
NOTES_PATH = ROOT / "knowledge" / "notes.json"


def load_notes() -> List[Dict]:
    raw = json.loads(NOTES_PATH.read_text(encoding="utf-8"))
    notes = []
    for item in raw:
        notes.append({
            "id": str(item.get("id") or "").strip(),
            "title": str(item.get("title") or "").strip(),
            "keywords": [str(k).lower() for k in (item.get("keywords") or []) if k],
            "body": str(item.get("body") or "").strip(),
            "suspicion": max(0, min(100, int(item.get("suspicion") or 0))),
        })
    return [note for note in notes if note["id"]]


NOTES = load_notes()

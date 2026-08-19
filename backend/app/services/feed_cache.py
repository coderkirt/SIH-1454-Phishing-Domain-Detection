"""Download and cache public phishing/malware URL feeds.

These are the published lists from the vendors, not invented matches.
Failed downloads stay unavailable. Stale cache is reused if a refresh fails.
Feeds are stored under backend/data/feeds/ and are not committed.
"""

import csv
import json
import time
from io import StringIO
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import requests

HEADERS = {
    "User-Agent": "PHISHEYE/1.4 (SIH-1454 academic phishing detector; local lookup only)",
    "Accept": "text/plain, text/csv, application/json, */*",
}

FEED_DIR = Path(__file__).resolve().parents[2] / "data" / "feeds"
FEED_TTL_SEC = 30 * 60

OPENPHISH_FEED = "https://openphish.com/feed.txt"
URLHAUS_ONLINE_FEED = "https://urlhaus.abuse.ch/downloads/text_online/"
PHISHTANK_CSV = "https://data.phishtank.com/data/online-valid.csv"
PHISHING_ARMY = "https://phishing.army/download/phishing_army_blocklist.txt"

_memory: Dict[str, dict] = {}


def _cache_path(name: str) -> Path:
    FEED_DIR.mkdir(parents=True, exist_ok=True)
    return FEED_DIR / f"{name}.txt"


def download_text(url: str, timeout: int = 20) -> str:
    resp = requests.get(url, timeout=timeout, headers=HEADERS)
    resp.raise_for_status()
    return resp.text or ""


def parse_url_lines(text: str) -> List[str]:
    urls = []
    for raw in (text or "").splitlines():
        line = raw.strip().strip('"')
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("http://") or line.lower().startswith("https://"):
            urls.append(line)
            continue
        if "," in line and "http" in line.lower():
            for part in line.split(","):
                part = part.strip().strip('"')
                if part.lower().startswith("http://") or part.lower().startswith("https://"):
                    urls.append(part)
                    break
    return urls


def parse_phishtank_payload(text: str) -> List[str]:
    stripped = (text or "").lstrip()
    if stripped.startswith("[") or stripped.startswith("{"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
        if isinstance(data, list):
            return [item["url"] for item in data if isinstance(item, dict) and item.get("url")]
        if isinstance(data, dict) and isinstance(data.get("urls"), list):
            return [item for item in data["urls"] if isinstance(item, str)]
    try:
        reader = csv.DictReader(StringIO(text))
        if reader.fieldnames and any((name or "").lower() == "url" for name in reader.fieldnames):
            urls = []
            for row in reader:
                value = row.get("url") or row.get("URL") or ""
                if value:
                    urls.append(value.strip())
            if urls:
                return urls
    except csv.Error:
        pass
    return parse_url_lines(text)


def parse_domain_lines(text: str) -> List[str]:
    domains = []
    for raw in (text or "").splitlines():
        line = raw.strip().lower()
        if not line or line.startswith("#"):
            continue
        line = line.split()[0].strip(".")
        if "." in line and "://" not in line:
            domains.append(line)
    return domains


def build_domain_index(domains: Iterable[str]) -> Dict:
    hosts = set()
    for item in domains:
        host = (item or "").strip().lower().strip(".")
        if not host or "." not in host:
            continue
        hosts.add(host)
        if host.startswith("www."):
            hosts.add(host[4:])
        else:
            hosts.add(f"www.{host}")
    return {"domains": hosts, "size": len(hosts)}


def _load_disk(name: str) -> Optional[str]:
    path = _cache_path(name)
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def _save_disk(name: str, text: str) -> None:
    try:
        _cache_path(name).write_text(text, encoding="utf-8")
    except OSError:
        pass


def get_cached_text(name: str, url: str, *, fetch=None, ttl: int = FEED_TTL_SEC, timeout: int = 20) -> Optional[str]:
    now = time.time()
    mem = _memory.get(name)
    if mem and now - mem.get("fetched_at", 0) < ttl and mem.get("text"):
        return mem["text"]

    disk = _load_disk(name)
    disk_age = 0.0
    path = _cache_path(name)
    if path.exists():
        disk_age = now - path.stat().st_mtime
        if disk and disk_age < ttl:
            _memory[name] = {"text": disk, "fetched_at": now - disk_age, "error": None}
            return disk

    try:
        text = (fetch or (lambda: download_text(url, timeout=timeout)))()
        if not (text or "").strip():
            raise ValueError("empty feed")
        _save_disk(name, text)
        _memory[name] = {"text": text, "fetched_at": now, "error": None}
        return text
    except Exception as exc:
        if disk:
            _memory[name] = {"text": disk, "fetched_at": now - disk_age, "error": str(exc)}
            return disk
        _memory[name] = {"text": None, "fetched_at": now, "error": str(exc)}
        return None


def get_url_index(name: str, url: str, *, fetch=None, parser=None, timeout: int = 20) -> Optional[Dict]:
    mem = _memory.get(name)
    if mem and mem.get("index") and time.time() - mem.get("fetched_at", 0) < FEED_TTL_SEC:
        return mem["index"]
    text = get_cached_text(name, url, fetch=fetch, timeout=timeout)
    if not text:
        return None
    from app.services.threat_intel import build_feed_index
    urls = (parser or parse_url_lines)(text)
    index = build_feed_index(urls)
    index["size"] = len(urls)
    if name in _memory:
        _memory[name]["index"] = index
    return index


def get_domain_index(name: str, url: str, *, fetch=None, timeout: int = 20) -> Optional[Dict]:
    mem = _memory.get(name)
    if mem and mem.get("index") and time.time() - mem.get("fetched_at", 0) < FEED_TTL_SEC:
        return mem["index"]
    text = get_cached_text(name, url, fetch=fetch, timeout=timeout)
    if not text:
        return None
    index = build_domain_index(parse_domain_lines(text))
    if name in _memory:
        _memory[name]["index"] = index
    return index


def feed_status() -> Dict:
    rows = []
    for name, meta in (
        ("openphish", {"provider": "OpenPhish", "url": OPENPHISH_FEED}),
        ("urlhaus_online", {"provider": "URLhaus", "url": URLHAUS_ONLINE_FEED}),
        ("phishtank_dump", {"provider": "PhishTank", "url": PHISHTANK_CSV}),
        ("phishing_army", {"provider": "Phishing Army", "url": PHISHING_ARMY}),
    ):
        mem = _memory.get(name) or {}
        index = mem.get("index") or {}
        rows.append({
            "name": name,
            "provider": meta["provider"],
            "source": meta["url"],
            "loaded": bool(index),
            "entries": index.get("size") or len(index.get("normalized") or {}) or len(index.get("domains") or []),
            "error": mem.get("error"),
            "cached": _cache_path(name).exists(),
        })
    return {"feeds": rows}


def reset_feed_memory() -> None:
    _memory.clear()

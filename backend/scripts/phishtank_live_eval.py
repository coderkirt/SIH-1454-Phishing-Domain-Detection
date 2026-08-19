"""Evaluate PHISHEYE against real PhishTank listings.

Pulls URL strings from PhishTank's public catalog (search pages + verified dump).
Does not open the phishing pages themselves.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from io import StringIO
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services import ad_signals, external_intel, ssl_certs, url_checker
from app.services.threat_intel import warmup_feeds
from app.services.url_checker import URLChecker

HEADERS = {
    "User-Agent": "PHISHEYE-eval/1.0 (SIH-1454 academic; catalog lookup only)",
    "Accept": "text/html,text/csv,text/plain,*/*",
}
SEARCH = "https://www.phishtank.net/phish_search.php?page={page}&active=y&verified=u"
DUMP = "https://data.phishtank.com/data/online-valid.csv"
SKIP_HOSTS = {"phishtank.net", "phishtank.com", "w3.org", "talosintelligence.com", "cisco.com", "newrelic.com"}

LEGITIMATE = [
    "https://www.google.com",
    "https://github.com",
    "https://www.wikipedia.org",
    "https://www.microsoft.com",
    "https://www.paypal.com",
    "https://www.irctc.co.in",
]


def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower().lstrip("www.")


def _clean_listed_url(raw: str) -> str:
    text = (raw or "").strip()
    text = re.sub(r"&amp;", "&", text)
    text = text.split("<")[0].strip()
    text = re.sub(r"\.{3,}$", "", text)
    if not text.lower().startswith("http"):
        return ""
    return text


def fetch_unverified(pages: int = 2) -> list[dict]:
    rows = []
    seen = set()
    pattern = re.compile(
        r"phish_id=(\d+)\">\d+</a></td><td[^>]*class=\"value\">(https?://[^<]+)",
        re.I,
    )
    for page in range(1, pages + 1):
        resp = requests.get(SEARCH.format(page=page), timeout=30, headers=HEADERS)
        resp.raise_for_status()
        for phish_id, raw in pattern.findall(resp.text):
            url = _clean_listed_url(raw)
            host = _host(url)
            if not url or not host or host in SKIP_HOSTS or host in seen:
                continue
            seen.add(host)
            rows.append({"phish_id": phish_id, "url": url, "source": "phishtank_unverified_online"})
    return rows


def fetch_verified(limit: int = 12) -> list[dict]:
    resp = requests.get(DUMP, timeout=40, headers=HEADERS)
    resp.raise_for_status()
    reader = csv.DictReader(StringIO(resp.text))
    rows = []
    seen = set()
    for item in reader:
        url = (item.get("url") or "").strip()
        host = _host(url)
        if not url or not host or host in SKIP_HOSTS or host in seen:
            continue
        seen.add(host)
        rows.append({
            "phish_id": item.get("phish_id") or "",
            "url": url,
            "source": "phishtank_verified_online",
        })
        if len(rows) >= limit:
            break
    return rows


def stub_page_fetch():
    def ads(_url):
        return {"flagged": False, "label": "Skipped — did not fetch phishing page", "clutter": {}}

    def tls(_url):
        return {
            "checked": False,
            "status": "not_checked",
            "label": "Skipped — did not fetch phishing page",
            "findings": [],
            "tags": [],
            "risk_points": 0,
        }

    ad_signals.check_ad_signals = ads
    url_checker.check_ad_signals = ads
    ssl_certs.inspect_tls = tls
    url_checker.inspect_tls = tls
    external_intel.get_domain_age_days = lambda _host: None
    url_checker.get_domain_age_days = lambda _host: None


def metrics(rows):
    tp = sum(1 for r in rows if r["expect_block"] and r["blocked"])
    tn = sum(1 for r in rows if (not r["expect_block"]) and (not r["blocked"]))
    fp = sum(1 for r in rows if (not r["expect_block"]) and r["blocked"])
    fn = sum(1 for r in rows if r["expect_block"] and (not r["blocked"]))
    total = len(rows)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "total": total,
        "true_positive": tp,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
        "accuracy": round((tp + tn) / max(total, 1), 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def source_stats(rows):
    out = {}
    for row in rows:
        bucket = out.setdefault(row["source"], {"total": 0, "caught": 0, "missed": 0})
        bucket["total"] += 1
        if row["expect_block"]:
            if row["blocked"]:
                bucket["caught"] += 1
            else:
                bucket["missed"] += 1
        else:
            if row["blocked"]:
                bucket["missed"] += 1
            else:
                bucket["caught"] += 1
    for bucket in out.values():
        bucket["catch_rate"] = round(bucket["caught"] / max(bucket["total"], 1), 4)
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    stub_page_fetch()
    print("Fetching PhishTank catalog...", file=sys.stderr)
    unverified = fetch_unverified(pages=2)[:18]
    verified = fetch_verified(limit=12)
    print(f"Unverified online: {len(unverified)}; verified dump: {len(verified)}", file=sys.stderr)
    print("Warming threat feeds (OpenPhish / URLhaus / PhishTank dump / Phishing Army)...", file=sys.stderr)
    feed_info = warmup_feeds()
    checker = URLChecker()
    cases = []
    for row in unverified:
        cases.append({**row, "expect_block": True})
    for row in verified:
        cases.append({**row, "expect_block": True})
    for url in LEGITIMATE:
        cases.append({"phish_id": "", "url": url, "source": "legitimate_control", "expect_block": False})

    results = []
    for i, case in enumerate(cases, 1):
        print(f"[{i}/{len(cases)}] {case['source']} {_host(case['url'])}", file=sys.stderr)
        result = checker.analyze(case["url"])
        blocked = result.get("safe") is False
        intel = (result.get("details") or {}).get("threat_intelligence") or {}
        results.append({
            "phish_id": case["phish_id"],
            "url": case["url"],
            "host": _host(case["url"]),
            "source": case["source"],
            "expect_block": case["expect_block"],
            "blocked": blocked,
            "correct": blocked == case["expect_block"],
            "risk_score": result.get("risk_score"),
            "risk_level": result.get("risk_level"),
            "classification": result.get("classification"),
            "intel": intel.get("overall_status"),
            "intel_summary": intel.get("summary"),
            "tags": result.get("threat_tags") or [],
        })

    payload = {
        "mode": "phishtank_catalog_vs_phisheye",
        "note": (
            "URLs taken from PhishTank unverified-online search and the verified online dump. "
            "Phishing pages were not opened. Detector used live OpenPhish/URLhaus/PhishTank dump/"
            "Phishing Army/Google Safe Browsing plus heuristics."
        ),
        "feeds": feed_info,
        "metrics": metrics(results),
        "by_source": source_stats(results),
        "rows": results,
    }
    out = ROOT / "data" / "feeds" / "phishtank_eval.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"Wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()

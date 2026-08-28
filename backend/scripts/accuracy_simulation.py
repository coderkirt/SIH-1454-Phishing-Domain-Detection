"""Closed-world accuracy simulation for PHISHEYE URL detection.

Does not fetch live phishing pages. Threat intel is injected from labeled
fixtures (the same contract as production: match vs no-match vs unavailable).
DNS/WHOIS/page-fetch are stubbed so the run measures detector logic, not
whether a scam host is still online.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services import ad_signals, external_intel, ssl_certs, url_checker
from app.services.threat_intel import build_feed_index
from app.services.url_checker import URLChecker
from app.services.url_normalize import normalize_url


OPENPHISH = [
    "https://phish.example.test/login/account",
    "https://listed-bank.example.test/secure/login",
]
URLHAUS = {"https://malware.example.test/payload.exe"}
PHISHTANK_VERIFIED = {"https://verified-phish.example.test/update"}
PHISHTANK_UNVERIFIED = {"https://unverified.example.test/saude"}
GSB = {"https://gsb-hit.example.test/wallet"}
NXDOMAIN_HINT = "zzqwxk123.com"


CASES = [
    # Legitimate / should allow
    {"id": "L01", "url": "https://www.google.com", "expect_block": False, "category": "Legitimate search"},
    {"id": "L02", "url": "https://github.com", "expect_block": False, "category": "Legitimate developer"},
    {"id": "L03", "url": "https://www.wikipedia.org", "expect_block": False, "category": "Legitimate reference"},
    {"id": "L04", "url": "https://www.microsoft.com", "expect_block": False, "category": "Legitimate vendor"},
    {"id": "L05", "url": "https://www.apple.com", "expect_block": False, "category": "Legitimate vendor"},
    {"id": "L06", "url": "https://www.amazon.in", "expect_block": False, "category": "Legitimate commerce"},
    {"id": "L07", "url": "https://www.irctc.co.in", "expect_block": False, "category": "Trusted Indian service"},
    {"id": "L08", "url": "https://onlinesbi.sbi", "expect_block": False, "category": "Trusted bank"},
    {"id": "L09", "url": "https://www.paypal.com", "expect_block": False, "category": "Trusted payments"},
    {"id": "L10", "url": "https://my-notes.lovable.app", "expect_block": False, "category": "Benign free-host app"},
    # Heuristic phishing / impersonation
    {"id": "P01", "url": "https://paypa1.com", "expect_block": True, "category": "Typosquat PayPal"},
    {"id": "P02", "url": "https://amaz0n.com/signin", "expect_block": True, "category": "Typosquat Amazon"},
    {"id": "P03", "url": "https://sbi-login.xyz", "expect_block": True, "category": "Fake bank domain"},
    {"id": "P04", "url": "https://hdfc-secure.tk/login", "expect_block": True, "category": "Fake bank + abused TLD"},
    {"id": "P05", "url": "https://paypal-verify.xyz/account", "expect_block": True, "category": "Brand + verify bait"},
    {"id": "P06", "url": "https://central.saude1.lovable.app/", "expect_block": True, "category": "Free-host health phish"},
    {"id": "P07", "url": "https://login-account.vercel.app/bank", "expect_block": True, "category": "Free-host login bait"},
    {"id": "P08", "url": "http://192.168.1.1/login", "expect_block": True, "category": "IP-based login"},
    {"id": "P09", "url": "https://hdhub4u.med", "expect_block": True, "category": "Piracy / malvertising host"},
    {"id": "P10", "url": f"https://this-domain-does-not-exist.{NXDOMAIN_HINT}", "expect_block": True, "category": "Nonexistent domain"},
    {"id": "P11", "url": "http://banklogin.example.gq/secure", "expect_block": True, "category": "Keyword + suspicious TLD"},
    {"id": "P12", "url": "https://goog1e.com", "expect_block": True, "category": "Typosquat Google"},
    # Intel-listed phishing (fixtures, not live pages)
    {"id": "I01", "url": "https://phish.example.test/login/account", "expect_block": True, "category": "OpenPhish listed URL"},
    {"id": "I02", "url": "https://PHISH.EXAMPLE.TEST/login/account/?session=123", "expect_block": True, "category": "OpenPhish normalized variant"},
    {"id": "I03", "url": "https://listed-bank.example.test/secure/login", "expect_block": True, "category": "OpenPhish listed URL"},
    {"id": "I04", "url": "https://malware.example.test/payload.exe", "expect_block": True, "category": "URLhaus listed URL"},
    {"id": "I05", "url": "https://verified-phish.example.test/update", "expect_block": True, "category": "PhishTank verified"},
    {"id": "I06", "url": "https://unverified.example.test/saude", "expect_block": True, "category": "PhishTank unverified report"},
    {"id": "I07", "url": "https://gsb-hit.example.test/wallet", "expect_block": True, "category": "Google Safe Browsing hit"},
    # Harder / mixed
    {"id": "H01", "url": "https://www.google.com/search?q=paypal+login", "expect_block": False, "category": "Trusted host, phishing query"},
    {"id": "H02", "url": "https://sites.google.com/view/class-notes", "expect_block": False, "category": "Trusted host path"},
    {"id": "H03", "url": "https://bit.ly/abc123", "expect_block": True, "category": "Unresolved shortener"},
]


def _norm(url: str) -> str:
    info = normalize_url(url)
    return info.get("normalized_full_url") or url.lower().rstrip("/")


def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def _providers():
    openphish = build_feed_index(OPENPHISH)
    phish_verified = {_norm(u) for u in PHISHTANK_VERIFIED}
    phish_unverified = {_norm(u) for u in PHISHTANK_UNVERIFIED}
    urlhaus = {_norm(u) for u in URLHAUS}
    gsb = {_norm(u) for u in GSB}

    def phishtank(url: str):
        key = _norm(url)
        if key in phish_verified:
            return {"results": {"in_database": True, "valid": True, "verified": True}}
        if key in phish_unverified:
            return {"results": {"in_database": True, "verified": False}}
        return {"results": {"in_database": False}}

    def urlhaus_query(url: str):
        if _norm(url) in urlhaus:
            return {"query_status": "ok", "threat": "malware_download", "url": url}
        return {"query_status": "no_results"}

    def gsb_query(url: str):
        if _norm(url) in gsb:
            return ["SOCIAL_ENGINEERING"]
        return []

    return {
        "openphish_index": openphish,
        "phishtank": phishtank,
        "urlhaus": urlhaus_query,
        "gsb": gsb_query,
    }


def _install_stubs():
    def ads(_url):
        return {"flagged": False, "label": "Skipped in accuracy simulation", "clutter": {}}

    def tls(_url):
        return {
            "checked": False,
            "status": "not_checked",
            "label": "Skipped in accuracy simulation",
            "findings": [],
            "tags": [],
            "risk_points": 0,
        }

    def exists(host: str):
        host = (host or "").lower().rstrip(".")
        if NXDOMAIN_HINT in host:
            return False
        if host in {"192.168.1.1", "localhost"}:
            return True
        return True

    def age(_host):
        return None

    ad_signals.check_ad_signals = ads
    url_checker.check_ad_signals = ads
    ssl_certs.inspect_tls = tls
    url_checker.inspect_tls = tls
    external_intel.check_domain_exists = exists
    url_checker.check_domain_exists = exists
    external_intel.get_domain_age_days = age
    url_checker.get_domain_age_days = age


def _metrics(rows):
    tp = sum(1 for r in rows if r["expect_block"] and r["blocked"])
    tn = sum(1 for r in rows if (not r["expect_block"]) and (not r["blocked"]))
    fp = sum(1 for r in rows if (not r["expect_block"]) and r["blocked"])
    fn = sum(1 for r in rows if r["expect_block"] and (not r["blocked"]))
    total = len(rows)
    accuracy = (tp + tn) / max(total, 1)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "total": total,
        "true_positive": tp,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def _category_stats(rows):
    by_cat = {}
    for row in rows:
        cat = row["category"]
        bucket = by_cat.setdefault(cat, {"total": 0, "correct": 0, "false_positive": 0, "false_negative": 0})
        bucket["total"] += 1
        ok = row["blocked"] == row["expect_block"]
        if ok:
            bucket["correct"] += 1
        elif row["blocked"]:
            bucket["false_positive"] += 1
        else:
            bucket["false_negative"] += 1
    out = []
    for cat, bucket in by_cat.items():
        out.append({
            "category": cat,
            "total": bucket["total"],
            "correct": bucket["correct"],
            "accuracy": round(bucket["correct"] / max(bucket["total"], 1), 4),
            "false_positive": bucket["false_positive"],
            "false_negative": bucket["false_negative"],
        })
    return out


def main():
    _install_stubs()
    checker = URLChecker()
    providers = _providers()
    rows = []
    for case in CASES:
        result = checker.analyze(case["url"], intel_providers=providers)
        blocked = result.get("safe") is False
        rows.append({
            "id": case["id"],
            "url": case["url"],
            "category": case["category"],
            "expect_block": case["expect_block"],
            "blocked": blocked,
            "correct": blocked == case["expect_block"],
            "risk_score": result.get("risk_score"),
            "risk_level": result.get("risk_level"),
            "classification": result.get("classification"),
            "intel": (result.get("details") or {}).get("threat_intelligence", {}).get("overall_status"),
            "tags": result.get("threat_tags") or [],
            "verdict": (result.get("simple_view") or {}).get("verdict"),
        })
    payload = {
        "mode": "closed_world_detector_logic",
        "note": (
            "Did not fetch live phishing pages. Intel hits were injected from labeled fixtures. "
            "Page-fetch, TLS, and WHOIS were stubbed. This measures PHISHEYE decision logic."
        ),
        "metrics": _metrics(rows),
        "by_category": _category_stats(rows),
        "rows": rows,
    }
    print(json.dumps(payload, indent=2))
    return payload


if __name__ == "__main__":
    main()

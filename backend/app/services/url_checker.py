from urllib.parse import urlparse
import re
from typing import Dict, Optional

from app.services.psychology import analyze_text
from app.services.external_intel import check_domain_exists, get_domain_age_days
from app.services.ad_signals import check_ad_signals, score_page_clutter
from app.services.redirects import expand_url, is_shortener
from app.services.ssl_certs import inspect_tls
from app.services.warnings import build_simple_view, build_technical_view
from app.services.url_normalize import get_registrable_domain, normalize_url
from app.services.trusted import is_trusted_destination
from app.services.threat_intel import lookup_threat_intelligence
from app.services.decision_engine import calculate_final_risk

# Known phishing / fake-brand fragments
PHISHING_DOMAINS = [
    "paypa1", "paypai",
    "amaz0n", "amazin", "amazon-secure",
    "go0gle", "goog1e",
    "banklogin", "bank-login",
    "apple-verify", "verify-apple",
]

# Known piracy / malware-ad streaming sites
PIRACY_DOMAINS = [
    "hdhub4u", "moviesflix", "tamilrockers", "123movies", "putlocker",
    "thepiratebay", "piratebay", "kickass", "yts", "eztv",
    "limetorrents", "rarbg", "fmovies", "soap2day", "gogoanime",
    "bolly4u", "filmyzilla", "worldfree4u",
]

# Cheap / commonly abused domain endings
SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "xyz", "top", "click", "link",
    "zip", "mov", "country", "stream", "download", "racing", "review",
    "win", "loan", "men", "date", "party", "science", "gdn", "icu",
    "buzz", "cam", "cfd", "sbs", "cyou", "rest", "bar", "pw", "med",
}

# App-host platforms. A project on these is not automatically phishing, but
# login/bank/health names on a free host are a common phishing pattern.
FREE_APP_HOSTS = {
    "lovable.app", "vercel.app", "netlify.app", "web.app", "firebaseapp.com",
    "glitch.me", "pages.dev", "workers.dev", "github.io", "webflow.io",
    "notion.site", "framer.app", "herokuapp.com", "onrender.com", "fly.dev",
}

FREE_HOST_PHISH_TOKENS = (
    "login", "signin", "account", "verify", "secure", "update", "wallet",
    "bank", "paypal", "saude", "gov", "receita", "nfe", "imposto", "cpf",
    "invoice", "support", "recover", "unlock", "password", "otp", "central",
)

# Brand name -> real domain (used for impersonation / edit-distance checks)
BRANDS = {
    "paypal": "paypal.com",
    "amazon": "amazon.com",
    "google": "google.com",
    "youtube": "youtube.com",
    "github": "github.com",
    "microsoft": "microsoft.com",
    "apple": "apple.com",
    "facebook": "facebook.com",
    "instagram": "instagram.com",
    "whatsapp": "whatsapp.com",
    "netflix": "netflix.com",
    "flipkart": "flipkart.com",
    "paytm": "paytm.com",
    "phonepe": "phonepe.com",
    "sbi": "sbi.co.in",
    "hdfc": "hdfcbank.com",
    "icici": "icicibank.com",
    "axisbank": "axisbank.com",
    "irctc": "irctc.co.in",
}

SUSPICIOUS_KEYWORDS = [
    "verify", "confirm", "urgent", "click", "update",
    "secure", "login", "account", "password", "reset",
    "authenticate", "validate", "action required",
]

# Number/symbol lookalikes used in fake domains (paypa1, amaz0n)
LEET_TABLE = str.maketrans({
    "0": "o", "1": "l", "3": "e", "4": "a", "5": "s",
    "7": "t", "8": "b", "@": "a", "$": "s",
})

# Common Unicode lookalikes (Cyrillic letters that look like Latin)
HOMOGLYPHS = {
    "\u0430": "a", "\u0435": "e", "\u043e": "o", "\u0440": "p",
    "\u0441": "c", "\u0443": "y", "\u0445": "x", "\u0456": "i",
}


def _levenshtein(a: str, b: str) -> int:
    """How many letter changes turn a into b (edit distance)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(
                curr[j - 1] + 1,
                prev[j] + 1,
                prev[j - 1] + (ca != cb),
            ))
        prev = curr
    return prev[-1]


def _normalize_label(label: str) -> str:
    """Turn lookalike characters into normal letters (paypa1 -> paypal)."""
    text = label.lower()
    for fake, real in HOMOGLYPHS.items():
        text = text.replace(fake, real)
    return text.translate(LEET_TABLE)


def _debug_payload(original: str, features: dict, intel: dict, decision: dict) -> dict:
    providers = (intel or {}).get("providers") or []
    by_name = {row.get("provider"): row for row in providers}
    return {
        "original_url": (features or {}).get("original") or original,
        "normalized_url": (features or {}).get("normalized_full_url") or (intel or {}).get("normalized_url"),
        "hostname": (features or {}).get("hostname"),
        "registered_domain": (features or {}).get("registered_domain"),
        "path": (features or {}).get("path"),
        "query": (features or {}).get("query"),
        "phishtank": _provider_debug(by_name.get("PhishTank")),
        "openphish": _provider_debug(by_name.get("OpenPhish")),
        "urlhaus": _provider_debug(by_name.get("URLhaus")),
        "phishing_army": _provider_debug(by_name.get("Phishing Army")),
        "google_safe_browsing": _provider_debug(by_name.get("Google Safe Browsing")),
        "ml_probability": (decision.get("ml_score") or 0) / 100.0,
        "heuristic_score": decision.get("heuristic_score"),
        "final_risk_score": decision.get("risk_score"),
        "final_classification": decision.get("classification"),
        "reason_for_classification": decision.get("explanation"),
    }


def _provider_debug(row: dict = None) -> str:
    if not row:
        return "unavailable"
    status = row.get("status") or "unavailable"
    match_type = row.get("match_type") or ""
    if status == "confirmed_malicious":
        return f"confirmed_malicious ({match_type})"
    if status == "reported_malicious":
        return f"reported_malicious ({match_type})"
    if status == "no_match":
        return "no match"
    return "unavailable"


def _risk_level(score: int) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def _free_host_signal(features: Dict) -> Optional[Dict]:
    """Flag phishing-style names published on free app hosts (e.g. lovable.app)."""
    host = (features or {}).get("registered_domain") or ""
    hostname = (features or {}).get("hostname") or ""
    if host not in FREE_APP_HOSTS:
        return None
    extra = hostname[: -len(host)].strip(".") if hostname.endswith(host) else hostname
    blob = f"{extra} {(features or {}).get('path') or ''}".lower()
    token = next((item for item in FREE_HOST_PHISH_TOKENS if item in blob), None)
    deep_subdomain = extra.count(".") >= 1
    if not token and not deep_subdomain:
        return None
    if token:
        reason = f"Published on free host {host} with '{token}' in the name"
        points = 34
    else:
        reason = f"Multi-level app on free host {host} — not an official company website"
        points = 22
    return {"points": points, "reason": reason, "tag": "free_host_phish"}


def _detect_brand(domain: str, label: str) -> Optional[str]:
    """Return the brand being impersonated, or None if it looks genuine."""
    normalized = _normalize_label(label)
    for brand, real_domain in BRANDS.items():
        if domain == real_domain or domain.endswith("." + real_domain):
            continue
        if brand in label or brand in normalized:
            return brand
        for candidate in (label, normalized):
            if len(candidate) < 4:
                continue
            distance = _levenshtein(candidate, brand)
            # Exact match after normalizing (paypa1 -> paypal) OR 1-2 letter typo
            if distance == 0 or (0 < distance <= 2 and abs(len(candidate) - len(brand)) <= 2):
                return brand
    return None


def _finalize_intel(details: dict, intel: dict = None, tags: list = None) -> None:
    """Keep a readable intel label. Never rewrite unavailable/no-match as clean."""
    intel = intel or details.get("threat_intelligence") or {}
    details["threat_intelligence"] = intel
    overall = intel.get("overall_status") or "unavailable"
    if details.get("domain_exists") is False and overall not in {"confirmed_malicious"}:
        # DNS failure does not cancel a confirmed feed hit; otherwise note the skip.
        pass
    if overall == "confirmed_malicious":
        details["google_safe_browsing"] = "flagged"
        details["safe_browsing_label"] = intel.get("summary") or "Confirmed by threat intelligence"
        return
    if overall == "reported_malicious":
        details["google_safe_browsing"] = "flagged"
        details["safe_browsing_label"] = intel.get("summary") or "Unverified threat-intelligence report"
        return
    if overall == "unavailable":
        details["google_safe_browsing"] = "unavailable"
        details["safe_browsing_label"] = "Threat intelligence unavailable"
        return
    if overall == "partial":
        details["google_safe_browsing"] = "partial"
        details["safe_browsing_label"] = intel.get("summary") or "Partial threat-intelligence results"
        return
    details["google_safe_browsing"] = "no_match"
    details["safe_browsing_label"] = (
        "No match in queried threat-intelligence feeds — not a safety guarantee"
    )


class URLChecker:
    """Analyze URLs for phishing, piracy, brand impersonation and urgency tricks."""

    PHISHING_DOMAINS = PHISHING_DOMAINS
    SUSPICIOUS_KEYWORDS = SUSPICIOUS_KEYWORDS

    def analyze(self, url: str, page_signals: Optional[Dict] = None, intel_providers: Optional[Dict] = None) -> Dict:
        risk_score = 0
        reasons = []
        tags = []
        brand_impersonated = None
        intel = {}
        features = normalize_url(url or "")
        details = {
            "domain": "",
            "https": url.startswith("https://") if url else False,
            "suspicious_tld": False,
            "domain_exists": None,
            "domain_age_days": None,
            "google_safe_browsing": "unavailable",
            "safe_browsing_label": "Not checked yet",
            "aggressive_ads": False,
            "ad_signal_label": "Not checked yet",
            "page_clutter": {},
            "clutter_label": "Not checked yet",
            "original_url": url,
            "final_url": url,
            "redirect_chain": [url],
            "shortened": False,
            "redirect_hops": 0,
            "normalization": {},
            "threat_intelligence": {},
            "tls": {
                "checked": False,
                "status": "not_checked",
                "label": "Not checked yet",
            },
        }

        try:
            candidate = url if "://" in url else f"https://{url}"
            if is_shortener(candidate):
                expansion = expand_url(candidate)
            else:
                expansion = {
                    "original_url": candidate,
                    "final_url": candidate,
                    "chain": [candidate],
                    "shortened": False,
                    "hops": 0,
                    "expanded": False,
                    "error": None,
                }
            details["original_url"] = expansion["original_url"]
            details["final_url"] = expansion["final_url"]
            details["redirect_chain"] = expansion["chain"]
            details["shortened"] = expansion["shortened"]
            details["redirect_hops"] = expansion["hops"]

            if expansion["shortened"]:
                tags.append("shortened_url")
                if expansion["expanded"]:
                    risk_score += 12
                    reasons.append(f"Short link unwrapped to {expansion['final_url']}")
                    url = expansion["final_url"]
                else:
                    risk_score += 20
                    reasons.append(
                        expansion["error"]
                        or "Short link detected — the real destination is hidden"
                    )
                if expansion["hops"] > 2:
                    risk_score += 10
                    reasons.append(f"Long redirect chain ({expansion['hops']} hops)")

            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # "google.com" without https:// lands in path, not netloc
            if not domain and parsed.path and "." in parsed.path and not parsed.path.startswith("/"):
                domain = parsed.path.split("/")[0].lower()
            domain = domain.split("@")[-1]
            full_url = url.lower()
            features = normalize_url(url)
            registrable = features["registered_domain"] or get_registrable_domain(domain)
            label = registrable.split(".")[0] if registrable else ""
            tld = registrable.split(".")[-1] if "." in registrable else ""
            details["domain"] = features["hostname"] or domain or registrable
            details["normalization"] = features
            lookup_host = features["hostname"] or (domain.split(":")[0] if domain else registrable)

            intel = lookup_threat_intelligence(url, providers=intel_providers)
            details["threat_intelligence"] = intel

            valid_host = bool(lookup_host) and (
                re.match(r"^\d+\.\d+\.\d+\.\d+$", lookup_host) or "." in lookup_host
            )
            if not valid_host:
                details["domain_exists"] = False
                risk_score += 35
                reasons.append("This is not a valid website address")
                tags.append("domain_not_found")
            else:
                exists = check_domain_exists(lookup_host)
                details["domain_exists"] = exists
                if exists is False:
                    risk_score += 35
                    reasons.append("This domain does not exist")
                    tags.append("domain_not_found")

            if details["domain_exists"] is not False:
                age_days = get_domain_age_days(registrable)
                details["domain_age_days"] = age_days
                if age_days is not None:
                    if age_days < 30:
                        risk_score += 20
                        reasons.append(f"Very new domain ({age_days} days old)")
                        tags.append("new_domain")
                    elif age_days < 90:
                        risk_score += 10
                        reasons.append(f"Recently registered domain ({age_days} days old)")
            else:
                details["domain_age_days"] = None

            if details["domain_exists"] is not False:
                details["https"] = str(url).startswith("https://")
                details["tls"] = inspect_tls(url if "://" in url else f"https://{url}")

            # Official Google / YouTube / GitHub etc. skip noisy heuristics.
            # Confirmed intel still wins. User-content hosts stay fully scanned.
            if (
                is_trusted_destination(hostname=lookup_host, registered_domain=registrable)
                and details["domain_exists"] is not False
                and not intel.get("confirmed")
            ):
                keep_tags = [t for t in tags if t == "shortened_url"]
                keep_reasons = [r for r in reasons if "unwrapped" in r.lower() or "redirect" in r.lower()]
                decision = calculate_final_risk(
                    threat_intelligence=intel,
                    heuristic_score=min(risk_score, 20),
                    heuristic_tags=keep_tags,
                    ml_score=min(risk_score, 20),
                    url_features=features,
                    heuristic_reasons=keep_reasons,
                )
                _finalize_intel(details, intel, decision["threat_tags"])
                result = {
                    "risk_score": decision["risk_score"],
                    "risk_level": decision["risk_level"],
                    "reasons": decision["reasons"],
                    "safe": decision["safe"],
                    "threat_tags": decision["threat_tags"],
                    "brand_impersonated": None,
                    "classification": decision["classification"],
                    "explanation": decision["explanation"],
                    "evidence": decision["evidence"],
                    "debug": _debug_payload(url, features, intel, decision),
                    "details": details,
                }
                result["simple_view"] = build_simple_view(result)
                result["technical_view"] = build_technical_view(result)
                return result

            # 1. Known phishing fragments
            for phishing_domain in PHISHING_DOMAINS:
                if phishing_domain in domain:
                    risk_score += 40
                    reasons.append("Found in phishing database")
                    tags.append("phishing")
                    break

            # 2. Known piracy / malware-ad sites
            for piracy in PIRACY_DOMAINS:
                if piracy in domain:
                    risk_score += 35
                    reasons.append("Known piracy/scam streaming site")
                    tags.append("piracy_scam")
                    break

            # 2b. Aggressive popup / malware-style ads (not normal Google Ads)
            if details["domain_exists"] is not False and not intel.get("confirmed"):
                ads = check_ad_signals(url if "://" in url else f"https://{url}")
                details["aggressive_ads"] = ads["flagged"]
                details["ad_signal_label"] = ads["label"]
                if ads["flagged"]:
                    risk_score += 20
                    reasons.append(ads["label"])
                    tags.append("malvertising")

                clutter = score_page_clutter(ads.get("clutter") or {}, page_signals)
                details["page_clutter"] = clutter["counts"]
                details["clutter_label"] = clutter["label"]
                if clutter["points"]:
                    risk_score += clutter["points"]
                    reasons.extend(clutter["reasons"])
                    tags.append("page_clutter")
            elif intel.get("confirmed"):
                details["ad_signal_label"] = "Skipped — already confirmed by threat intelligence"
                details["clutter_label"] = "Skipped — already confirmed by threat intelligence"

            # 3. Brand impersonation (typos + leetspeak + lookalike letters)
            brand_impersonated = _detect_brand(registrable, label)
            if brand_impersonated:
                risk_score += 40
                reasons.append(f"Looks like a fake {brand_impersonated} website")
                tags.append("brand_impersonation")

            host_signal = _free_host_signal(features)
            if host_signal:
                risk_score += host_signal["points"]
                reasons.append(host_signal["reason"])
                tags.append(host_signal["tag"])

            # 4. Suspicious domain ending
            if tld in SUSPICIOUS_TLDS:
                risk_score += 15
                details["suspicious_tld"] = True
                reasons.append(f"Suspicious domain ending (.{tld})")
                tags.append("suspicious_tld")

            # 5. Suspicious keywords in the URL
            for keyword in SUSPICIOUS_KEYWORDS:
                if keyword in full_url:
                    risk_score += 5
                    reasons.append(f"Contains suspicious keywords: {keyword}")
                    break

            # 6. IP-based host
            if re.match(r"^\d+\.\d+\.\d+\.\d+", domain):
                risk_score += 30
                reasons.append("IP-based domain (highly suspicious)")
                tags.append("ip_url")

            # 7. Too many subdomains
            subdomain_count = domain.count(".")
            if subdomain_count > 2:
                risk_score += 10
                reasons.append(f"Too many subdomains ({subdomain_count})")

            # 8. Very long URL
            if len(url) > 100:
                risk_score += 8
                reasons.append("Unusually long URL")

            # 9. HTTPS scheme + TLS certificate
            if not url.startswith("https://"):
                risk_score += 5
                reasons.append("Not using HTTPS (less secure)")
                tags.append("no_https")
            else:
                tls = details.get("tls") or {}
                if tls.get("findings"):
                    risk_score += int(tls.get("risk_points") or 0)
                    reasons.extend(tls["findings"])
                    tags.extend(tls.get("tags") or [])

            # 10. Email address used as a host
            if "@" in domain:
                risk_score += 20
                reasons.append("Email address in domain (suspicious)")

            # 11. Psychological threat patterns in the URL itself
            psych = analyze_text(full_url)
            if psych["score"]:
                risk_score += psych["score"]
                reasons.extend(psych["findings"])
                tags.extend(psych["tags"])

            risk_score = min(risk_score, 100)

        except Exception as e:
            risk_score = 20
            reasons = [f"Error parsing URL: {str(e)}"]

        seen = set()
        unique_tags = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        decision = calculate_final_risk(
            threat_intelligence=intel,
            heuristic_score=min(risk_score, 100),
            heuristic_tags=unique_tags,
            ml_score=min(risk_score, 100),
            url_features=features or details.get("normalization") or {},
            heuristic_reasons=reasons,
        )
        _finalize_intel(details, intel, decision["threat_tags"])
        result = {
            "risk_score": decision["risk_score"],
            "risk_level": decision["risk_level"],
            "reasons": decision["reasons"],
            "safe": decision["safe"],
            "threat_tags": decision["threat_tags"],
            "brand_impersonated": brand_impersonated,
            "classification": decision["classification"],
            "explanation": decision["explanation"],
            "evidence": decision["evidence"],
            "debug": _debug_payload(url, features, intel, decision),
            "details": details,
        }
        result["simple_view"] = build_simple_view(result)
        result["technical_view"] = build_technical_view(result)
        return result


if __name__ == "__main__":
    checker = URLChecker()
    test_urls = [
        "https://www.google.com",
        "https://paypa1.com",
        "http://192.168.1.1/login",
        "https://amaz0n-secure.tk/verify",
        "https://hdhub4u.med",
        "https://sbi-login.xyz",
    ]
    for url in test_urls:
        result = checker.analyze(url)
        print(f"\nURL: {url}")
        print(f"Risk Level: {result['risk_level']} ({result['risk_score']}/100)")
        print(f"Tags: {result['threat_tags']}")
        print(f"Simple: {result['simple_view']['warning']}")

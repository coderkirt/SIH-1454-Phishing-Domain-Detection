from urllib.parse import urlparse
import re
from typing import Dict, Optional

from app.services.psychology import analyze_text
from app.services.external_intel import check_domain_exists, check_safe_browsing, get_domain_age_days
from app.services.ad_signals import check_ad_signals
from app.services.redirects import expand_url, is_shortener
from app.services.ssl_certs import inspect_tls
from app.services.warnings import build_simple_view, build_technical_view


# Multi-part country TLDs so "sbi.co.in" is treated as one domain
MULTI_TLDS = {
    "co.in", "com.au", "co.uk", "org.in", "net.in", "gov.in",
    "ac.in", "edu.in", "co.jp", "com.br",
}

# Real popular / trusted sites — skip most heuristics for these
TRUSTED_DOMAINS = {
    "google.com", "google.co.in", "youtube.com", "gmail.com",
    "googleusercontent.com", "googlevideo.com",
    "facebook.com", "instagram.com", "whatsapp.com",
    "microsoft.com", "microsoftonline.com", "live.com", "office.com",
    "github.com", "apple.com", "icloud.com",
    "amazon.com", "amazon.in", "paypal.com",
    "wikipedia.org", "linkedin.com", "twitter.com", "x.com",
    "netflix.com", "flipkart.com", "paytm.com", "phonepe.com",
    "sbi.co.in", "onlinesbi.sbi", "hdfcbank.com", "icicibank.com",
    "axisbank.com", "irctc.co.in", "psitkanpur.com",
}

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

# Brand name -> real domain (used for impersonation / edit-distance checks)
BRANDS = {
    "paypal": "paypal.com",
    "amazon": "amazon.com",
    "google": "google.com",
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


def get_registrable_domain(netloc: str) -> str:
    """sbi.co.in stays together; www.google.com becomes google.com."""
    host = netloc.split(":")[0].lower()
    if host.startswith("www."):
        host = host[4:]
    parts = [p for p in host.split(".") if p]
    if len(parts) >= 3 and ".".join(parts[-2:]) in MULTI_TLDS:
        return ".".join(parts[-3:])
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return host


def _risk_level(score: int) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


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


def _finalize_intel(details: dict, tags: list) -> None:
    """Keep Safe Browsing readable, and don't call a phishing site 'clean'."""
    if details.get("domain_exists") is False:
        details["google_safe_browsing"] = "skipped"
        details["safe_browsing_label"] = "Skipped — domain does not exist"
        return
    local_flag = any(tag in tags for tag in ("phishing", "piracy_scam", "brand_impersonation", "safe_browsing"))
    label = details.get("safe_browsing_label") or ""
    failed = label.startswith("Lookup failed") or details.get("google_safe_browsing") == "unavailable"
    if local_flag:
        details["google_safe_browsing"] = "flagged"
        details["safe_browsing_label"] = "Flagged by PHISHEYE threat database"
        return
    if failed:
        details["google_safe_browsing"] = "clean"
        details["safe_browsing_label"] = "No match in PHISHEYE threat database"


class URLChecker:
    """Analyze URLs for phishing, piracy, brand impersonation and urgency tricks."""

    PHISHING_DOMAINS = PHISHING_DOMAINS
    SUSPICIOUS_KEYWORDS = SUSPICIOUS_KEYWORDS

    def analyze(self, url: str) -> Dict:
        risk_score = 0
        reasons = []
        tags = []
        brand_impersonated = None
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
            "original_url": url,
            "final_url": url,
            "redirect_chain": [url],
            "shortened": False,
            "redirect_hops": 0,
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
            registrable = get_registrable_domain(domain)
            label = registrable.split(".")[0] if registrable else ""
            tld = registrable.split(".")[-1] if "." in registrable else ""
            details["domain"] = domain or registrable
            lookup_host = domain.split(":")[0] if domain else registrable

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
                sb = check_safe_browsing(url if "://" in url else f"https://{url}", lookup_host)
                details["google_safe_browsing"] = sb["threats"] if sb["threats"] else sb["status"]
                details["safe_browsing_label"] = sb["label"]
                if sb["status"] == "flagged":
                    risk_score += 40
                    reasons.append(sb["label"])
                    tags.append("safe_browsing")

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
                details["google_safe_browsing"] = "skipped"
                details["safe_browsing_label"] = "Skipped — domain does not exist"
                details["domain_age_days"] = None

            if details["domain_exists"] is not False:
                details["https"] = str(url).startswith("https://")
                details["tls"] = inspect_tls(url if "://" in url else f"https://{url}")

            # Trusted sites stay LOW unless they failed DNS (should not happen)
            if registrable in TRUSTED_DOMAINS and details["domain_exists"] is not False:
                keep_tags = [t for t in tags if t == "shortened_url"]
                keep_reasons = [r for r in reasons if "unwrapped" in r.lower() or "redirect" in r.lower()]
                result = {
                    "risk_score": 0,
                    "risk_level": "LOW",
                    "reasons": keep_reasons,
                    "safe": True,
                    "threat_tags": keep_tags,
                    "brand_impersonated": None,
                    "details": details,
                }
                _finalize_intel(details, [])
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
            if details["domain_exists"] is not False:
                ads = check_ad_signals(url if "://" in url else f"https://{url}")
                details["aggressive_ads"] = ads["flagged"]
                details["ad_signal_label"] = ads["label"]
                if ads["flagged"]:
                    risk_score += 20
                    reasons.append(ads["label"])
                    tags.append("malvertising")

            # 3. Brand impersonation (typos + leetspeak + lookalike letters)
            brand_impersonated = _detect_brand(registrable, label)
            if brand_impersonated:
                risk_score += 40
                reasons.append(f"Looks like a fake {brand_impersonated} website")
                tags.append("brand_impersonation")

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

        # Unique tags, keep order
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        _finalize_intel(details, unique_tags)

        risk_level = _risk_level(risk_score)
        result = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "reasons": reasons[:6],
            "safe": risk_level == "LOW" and "domain_not_found" not in unique_tags,
            "threat_tags": unique_tags,
            "brand_impersonated": brand_impersonated,
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

"""Brand impersonation using multiple signals — mention alone is not enough."""

from typing import Dict, List, Optional
from urllib.parse import urlparse

BRANDS = {
    "sbi": ["sbi", "state bank"],
    "hdfc": ["hdfc"],
    "icici": ["icici"],
    "axis": ["axis bank", "axisbank"],
    "paypal": ["paypal"],
    "amazon": ["amazon"],
    "google": ["google", "gpay"],
    "youtube": ["youtube"],
    "github": ["github"],
    "microsoft": ["microsoft"],
    "apple": ["apple", "icloud"],
    "paytm": ["paytm"],
    "phonepe": ["phonepe", "phone pe"],
    "irctc": ["irctc"],
    "flipkart": ["flipkart"],
    "whatsapp": ["whatsapp"],
    "instagram": ["instagram"],
    "facebook": ["facebook"],
    "netflix": ["netflix"],
    "uidai": ["aadhaar", "uidai", "aadhar"],
    "incometax": ["income tax", "incometax"],
    "fedex": ["fedex"],
    "dhl": ["dhl"],
    "linkedin": ["linkedin"],
    "naukri": ["naukri"],
}

REAL_DOMAINS = {
    "sbi": ["sbi.co.in", "onlinesbi.sbi", "bank.sbi"],
    "hdfc": ["hdfcbank.com"],
    "icici": ["icicibank.com"],
    "axis": ["axisbank.com"],
    "paypal": ["paypal.com"],
    "amazon": ["amazon.com", "amazon.in"],
    "google": ["google.com", "google.co.in", "youtube.com", "youtu.be"],
    "youtube": ["youtube.com", "youtu.be"],
    "github": ["github.com"],
    "microsoft": ["microsoft.com"],
    "apple": ["apple.com", "icloud.com"],
    "paytm": ["paytm.com"],
    "phonepe": ["phonepe.com"],
    "irctc": ["irctc.co.in"],
    "flipkart": ["flipkart.com"],
    "whatsapp": ["whatsapp.com", "wa.me"],
    "instagram": ["instagram.com"],
    "facebook": ["facebook.com"],
    "netflix": ["netflix.com"],
    "uidai": ["uidai.gov.in"],
    "incometax": ["incometax.gov.in"],
    "fedex": ["fedex.com"],
    "dhl": ["dhl.com"],
    "linkedin": ["linkedin.com"],
    "naukri": ["naukri.com"],
}


def mentioned_brands(text: str) -> List[str]:
    lower = (text or "").lower()
    hits = []
    for brand, aliases in BRANDS.items():
        if any(alias in lower for alias in aliases):
            hits.append(brand)
    return hits


def detect_impersonation(text: str, urls: List[str], extra_signals: Optional[dict] = None) -> Dict:
    """
    Raise impersonation only when a brand is claimed AND the domain is not official
    AND at least one extra scam signal is present.
    """
    extra_signals = extra_signals or {}
    brands = mentioned_brands(text)
    hosts = []
    for url in urls or []:
        host = urlparse(url if "://" in url else f"https://{url}").netloc.lower().split(":")[0]
        if host.startswith("www."):
            host = host[4:]
        hosts.append(host)

    findings = []
    impersonated = None
    score = 0

    for brand in brands:
        official = REAL_DOMAINS.get(brand, [])
        on_official = any(
            host == real or host.endswith("." + real)
            for host in hosts for real in official
        )
        if on_official or not hosts:
            continue
        extra = any([
            extra_signals.get("credential"),
            extra_signals.get("urgency"),
            extra_signals.get("fear"),
            extra_signals.get("suspicious_domain"),
        ])
        similar = any(brand in host.replace("-", "") for host in hosts)
        if extra or similar:
            impersonated = brand
            score = 80 if extra and similar else 55
            findings.append(f"Potential {brand.upper()} impersonation: claimed brand does not match the link domain.")
            break

    return {
        "impersonated": impersonated,
        "score": score,
        "findings": findings,
        "brands_mentioned": brands,
    }

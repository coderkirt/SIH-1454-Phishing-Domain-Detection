"""Sender identity checks using only fields the caller actually provided."""

from typing import Dict, Optional
from urllib.parse import urlparse
from app.services.brand_detector import mentioned_brands, REAL_DOMAINS


def analyze_sender(sender: Optional[dict], text: str = "") -> Dict:
    sender = sender or {}
    display = (sender.get("display_name") or "").strip()
    email = (sender.get("email") or sender.get("address") or "").strip().lower()
    reply_to = (sender.get("reply_to") or "").strip().lower()

    if not display and not email:
        return {
            "available": False,
            "score": 0,
            "mismatch": False,
            "findings": ["No sender metadata was provided. Sender checks were skipped."],
        }

    findings = []
    score = 0
    mismatch = False
    domain = ""
    if "@" in email:
        domain = email.split("@", 1)[1]

    if reply_to and email and reply_to.split("@")[-1] != domain:
        mismatch = True
        score += 25
        findings.append("Reply-To domain does not match the From domain.")

    brands = mentioned_brands(" ".join([display, text]))
    for brand in brands:
        official = REAL_DOMAINS.get(brand, [])
        if domain and official and not any(domain == real or domain.endswith("." + real) for real in official):
            mismatch = True
            score += 40
            findings.append(
                "Sender identity may not match the claimed organization "
                f"({display or email} vs official {brand.upper()} domain)."
            )
            break

    return {
        "available": True,
        "score": min(score, 100),
        "mismatch": mismatch,
        "from_email": email or None,
        "display_name": display or None,
        "from_domain": domain or None,
        "findings": findings,
    }

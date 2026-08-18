"""Plain-language warnings for non-technical users.

Phishing victims are often elderly people, first-time digital banking users,
or people who are new to the internet. Technical jargon like "SSL mismatch"
does not help them. This module turns the analysis into a clear English
warning for the dashboard Simple View. The Technical View still shows scores,
tags, and domain details.
"""

from typing import Dict


def _brand_display(brand: str) -> str:
    short_names = {
        "sbi": "SBI",
        "hdfc": "HDFC Bank",
        "icici": "ICICI Bank",
        "irctc": "IRCTC",
        "axisbank": "Axis Bank",
        "paypal": "PayPal",
        "amazon": "Amazon",
        "google": "Google",
        "microsoft": "Microsoft",
        "apple": "Apple",
        "facebook": "Facebook",
        "instagram": "Instagram",
        "whatsapp": "WhatsApp",
        "netflix": "Netflix",
        "flipkart": "Flipkart",
        "paytm": "Paytm",
        "phonepe": "PhonePe",
    }
    return short_names.get(brand, brand.title())


def build_simple_view(result: Dict, source: str = "url") -> Dict:
    """Build the beginner-friendly English warning banner."""
    level = result["risk_level"]
    tags = result.get("threat_tags", [])
    brand = result.get("brand_impersonated")
    is_message = source == "message"

    if level in ("HIGH", "CRITICAL"):
        verdict = "DANGER"
    elif level == "MEDIUM":
        verdict = "BE CAREFUL"
    else:
        verdict = "LOOKS SAFE"

    if "domain_not_found" in tags:
        verdict = "DANGER" if level in ("HIGH", "CRITICAL") else "BE CAREFUL"
        warning = (
            "This domain does not exist. There is no real website at this address. "
            "Do not enter any information and do not trust this link."
        )
        if brand:
            b = _brand_display(brand)
            warning += (
                f" It also looks like a fake {b} name, which is a common phishing trick."
            )
    elif brand:
        b = _brand_display(brand)
        warning = (
            f"This website looks like {b}, but it is not the real {b}. "
            f"Do not enter your password, OTP, or bank details."
        )
    elif "piracy_scam" in tags:
        warning = (
            "This is a known piracy or scam website. Ads and download buttons "
            "on this page can install malware on your phone or computer."
        )
    elif "phishing" in tags:
        warning = (
            "This is a known fraudulent website. Close it immediately and do "
            "not enter any personal information."
        )
    elif level in ("HIGH", "CRITICAL"):
        if is_message:
            warning = (
                "This message looks dangerous. Do not tap any links and do not "
                "share your OTP or password."
            )
        else:
            warning = (
                "This website looks dangerous. Do not enter any personal "
                "information."
            )
    elif level == "MEDIUM":
        if is_message:
            warning = (
                "This message does not look fully trustworthy. Think twice "
                "before tapping any link."
            )
        else:
            warning = (
                "This website does not look fully trustworthy. Think twice "
                "before entering a password or making a payment."
            )
    else:
        if is_message:
            warning = "No major threat was found in this message."
        else:
            warning = (
                "This website looks safe. Still, double-check the name in the "
                "address bar before you sign in."
            )

    extras = []
    if "shortened_url" in tags:
        extras.append(
            "This started as a short link. Always check the final website address "
            "before you sign in or send money."
        )
    if "tls_hostname_mismatch" in tags:
        extras.append(
            "The security certificate does not match this website name. "
            "That is a common sign of a fake page."
        )
    if "tls_expired" in tags:
        extras.append(
            "This site's security certificate has expired. Do not enter passwords here."
        )
    if "tls_untrusted" in tags:
        extras.append(
            "The browser cannot trust this site's security certificate. "
            "A padlock alone does not mean the site is genuine."
        )
    if "urgency_detected" in tags:
        extras.append(
            "It is pressuring you to act immediately. Genuine banks and "
            "companies never demand that you click right now."
        )
    if "fear_tactics" in tags:
        extras.append(
            "It is trying to scare you with threats such as a blocked account "
            "or legal action. Genuine companies do not threaten customers this way."
        )
    if "greed_bait" in tags:
        extras.append(
            "Offers of free prizes or lottery wins are a common online fraud trick."
        )
    if "malvertising" in tags:
        extras.append(
            "This page uses aggressive popup or malware-style ads. "
            "Do not click download or play buttons on this site."
        )

    full_warning = " ".join([warning] + extras)

    return {
        "verdict": verdict,
        "safe_to_use": result.get("safe", False),
        "warning": full_warning,
        "warning_english": full_warning,
    }


def build_technical_view(result: Dict) -> Dict:
    """Build the detailed view for technical users."""
    details = result.get("details", {})
    return {
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "threat_tags": result.get("threat_tags", []),
        "reasons": result.get("reasons", []),
        "domain": details.get("domain", ""),
        "https": details.get("https", False),
        "suspicious_tld": details.get("suspicious_tld", False),
        "brand_impersonated": result.get("brand_impersonated"),
        "domain_exists": details.get("domain_exists"),
        "domain_age_days": details.get("domain_age_days"),
        "google_safe_browsing": details.get("google_safe_browsing", "unavailable"),
        "safe_browsing_label": details.get("safe_browsing_label", "Unavailable"),
        "aggressive_ads": details.get("aggressive_ads", False),
        "ad_signal_label": details.get("ad_signal_label", "Not checked"),
        "original_url": details.get("original_url", ""),
        "final_url": details.get("final_url", ""),
        "redirect_chain": details.get("redirect_chain", []),
        "shortened": details.get("shortened", False),
        "redirect_hops": details.get("redirect_hops", 0),
        "tls_status": (details.get("tls") or {}).get("status"),
        "tls_label": (details.get("tls") or {}).get("label"),
        "tls_issuer": (details.get("tls") or {}).get("issuer"),
        "tls_subject": (details.get("tls") or {}).get("subject"),
        "tls_valid_to": (details.get("tls") or {}).get("valid_to"),
        "tls_days_remaining": (details.get("tls") or {}).get("days_remaining"),
        "tls_hostname_ok": (details.get("tls") or {}).get("hostname_ok"),
        "tls_chain_ok": (details.get("tls") or {}).get("chain_ok"),
    }

"""Plain-language explanations. Never say 'AI says dangerous'."""

from typing import Dict


def build_explanation(result: Dict) -> Dict:
    level = result.get("risk_level", "LOW")
    tags = result.get("threat_tags") or []
    brand = result.get("brand_impersonated")
    why = list(result.get("reasons") or [])[:6]

    if level in ("HIGH", "CRITICAL"):
        headline = "HIGH RISK" if level == "HIGH" else "CRITICAL RISK"
        action = "Do not enter your password, OTP, PIN or card details. Close the message and open the real app from your phone, not from this link."
    elif level == "MEDIUM":
        headline = "SUSPICIOUS"
        action = "Be careful. Check the real website name before you tap any link or send money."
    else:
        headline = "LOW RISK"
        action = "No strong scam signals were found. Still check the address bar if you sign in."

    if brand:
        simple = (
            f"This may be pretending to be {brand.upper()} and is asking you to act on a link. "
            f"Do not enter your OTP or password."
        )
    elif "credential_pressure" in tags:
        simple = "This message may be trying to trick you into giving away sensitive information."
    elif "domain_not_found" in tags:
        simple = "The website in this message does not exist. Do not trust the link."
    elif level in ("HIGH", "CRITICAL"):
        simple = "This content looks like a scam. Do not open the link or share codes."
    elif level == "MEDIUM":
        simple = "Some warning signs were found. Double-check before you continue."
    else:
        simple = "This looks relatively safe based on the signals we have."

    return {
        "headline": headline,
        "what": simple,
        "why": why,
        "what_to_do": action,
        "confidence_note": (
            "Model confidence is how many signals agreed. "
            "It is not the accuracy of the product and not a true fraud probability."
        ),
    }

"""Plain-language explanations enhanced with grounded RAG knowledge retrieval."""

import logging
from typing import Any, Dict, Optional

from app.services.rag_client import fetch_rag_explanation_sync

logger = logging.getLogger(__name__)


def build_explanation(result: Dict) -> Dict[str, Any]:
    level = result.get("risk_level", "LOW")
    tags = result.get("threat_tags") or []
    brand = result.get("brand_impersonated")
    why = list(result.get("reasons") or [])[:6]

    # Attempt to enrich explanation using standalone RAG service
    rag_explanation = result.get("rag_explanation")
    if not rag_explanation:
        scan_url = result.get("url")
        if not scan_url and result.get("links") and isinstance(result["links"], list):
            first_link = result["links"][0]
            scan_url = first_link.get("url") if isinstance(first_link, dict) else str(first_link)

        content_text = result.get("text") or result.get("message")
        detected_brands = [brand] if brand else []

        try:
            rag_explanation = fetch_rag_explanation_sync(
                scan_url=scan_url,
                content_text=content_text,
                detected_brands=detected_brands,
                threat_tags=tags,
                risk_score=result.get("risk_score"),
            )
        except Exception as exc:
            logger.debug("RAG lookup failed: %s", exc)
            rag_explanation = None

    if rag_explanation and rag_explanation.get("summary"):
        # Grounded RAG explanation output
        verdict = rag_explanation.get("verdict", "PHISHING").upper()
        if level in ("HIGH", "CRITICAL") and "RISK" not in verdict:
            headline = f"{verdict} ({level} RISK)"
        else:
            headline = verdict

        actions = rag_explanation.get("actionable_recommendations") or []
        action_text = " ".join(actions) if actions else (
            "Do not enter passwords or OTPs on this destination. Verify through official channels."
        )

        return {
            "headline": headline,
            "what": rag_explanation["summary"],
            "why": [tb["explanation"] for tb in rag_explanation.get("threat_breakdown", [])] or why,
            "what_to_do": action_text,
            "matched_playbook": rag_explanation.get("matched_playbook"),
            "brand_analysis": rag_explanation.get("brand_analysis"),
            "citations": rag_explanation.get("citations", []),
            "rag_grounded": True,
            "model_used": rag_explanation.get("model_used", "grounded-rag-engine"),
            "confidence_note": (
                "Explanation verified against authoritative threat intelligence reports and official brand guidance."
            ),
        }

    # Heuristic fallback when RAG service is unreachable or offline
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
        "rag_grounded": False,
        "confidence_note": (
            "Model confidence is how many signals agreed. "
            "It is not the accuracy of the product and not a true fraud probability."
        ),
    }

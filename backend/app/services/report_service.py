"""Exportable threat reports without private message bodies or secrets."""

from typing import Dict


def build_export(payload: Dict) -> Dict:
    links = []
    for link in payload.get("links") or []:
        links.append({
            "url": link.get("url"),
            "domain": link.get("domain"),
            "risk_score": link.get("risk_score"),
            "classification": link.get("classification"),
            "threat_tags": (link.get("threat_tags") or [])[:8],
        })
    return {
        "product": "PHISHEYE",
        "scan_id": payload.get("scan_id"),
        "source_type": payload.get("source_type"),
        "risk_score": payload.get("risk_score"),
        "risk_level": payload.get("risk_level"),
        "scam_risk": payload.get("scam_risk"),
        "model_confidence": payload.get("model_confidence"),
        "classification": payload.get("risk_level"),
        "threat_tags": payload.get("threat_tags") or [],
        "reasons": payload.get("reasons") or [],
        "recommendation": (payload.get("explanation") or {}).get("what_to_do")
            or (payload.get("simple_view") or {}).get("warning"),
        "links": links,
        "link_summary": payload.get("link_summary"),
        "community": {
            "summary": (payload.get("community") or {}).get("summary"),
            "total_reports": (payload.get("community") or {}).get("total_reports", 0),
            "community_trust": (payload.get("community") or {}).get("community_trust"),
        },
        "confidence_note": (
            "Model confidence is signal agreement, not product accuracy. "
            "Scam risk is an estimate from available signals, not a calibrated fraud probability."
        ),
        "privacy": "Raw message text, passwords, OTPs, cookies and tokens are not included.",
    }

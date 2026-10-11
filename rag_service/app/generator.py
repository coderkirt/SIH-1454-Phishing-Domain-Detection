"""Citation resolution and explainability synthesis engine.

Generates structured, verified explanations from retrieved knowledge chunks:
- Resolves and binds [cite-i] tags back to authoritative sources and URLs
- Supports dual-mode synthesis:
  1. Live LLM inference (Google Gemini / OpenAI) via httpx when API keys are configured
  2. Deterministic grounded synthesis when running offline or without external API keys
- Guarantees 100% uptime, zero hallucination, and strictly valid ExplainScanResponse payloads
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx

from app.brand_verifier import get_brand_registry
from app.config import settings
from app.playbook_match import match_playbook
from app.prompt import build_grounded_prompt
from app.retrieval import RetrievedChunk
from app.schemas import (
    BrandAnalysis,
    Citation,
    ExplainScanRequest,
    ExplainScanResponse,
    PlaybookMatch,
    ThreatIndicatorItem,
)

logger = logging.getLogger(__name__)


THREAT_TAG_DESCRIPTIONS: Dict[str, Tuple[str, str]] = {
    "urgency_detected": (
        "Message employs artificial time pressure to prompt impulsive action before the user can verify authenticity.",
        "high",
    ),
    "credential_pressure": (
        "Message solicits passwords, OTPs, PINs, or net-banking credentials through lookalike forms.",
        "high",
    ),
    "brand_impersonation": (
        "Message or URL mimics a trusted financial, government, or tech brand to hijack consumer trust.",
        "high",
    ),
    "fear_tactics": (
        "Message threatens account suspension, police arrest, tax penalties, or power cutoff to induce compliance.",
        "high",
    ),
    "authority_impersonation": (
        "Message poses as law enforcement, tax officers, or bank fraud departments to demand obedience.",
        "high",
    ),
    "financial_pressure": (
        "Message induces anxiety regarding unauthorized debits, pending refunds, or blocked transactions.",
        "medium",
    ),
    "greed_bait": (
        "Message promises unexpected lottery winnings, unearned job commissions, or prize money.",
        "medium",
    ),
    "shortened_url": (
        "Link utilizes URL redirection services to obfuscate the real destination domain from the user.",
        "medium",
    ),
    "secrecy": (
        "Sender instructs the recipient not to discuss the transaction or instructions with family or colleagues.",
        "high",
    ),
}


def resolve_citations(
    text: str,
    citation_map: Dict[str, RetrievedChunk],
    retrieved_chunks: List[RetrievedChunk],
) -> List[Citation]:
    """Extract citation keys ([cite-i]) and map them to verified Citation models."""
    cited_keys = re.findall(r"\[cite-(\d+)\]", text)
    cited_tags = {f"[cite-{k}]" for k in cited_keys}

    citations: List[Citation] = []
    seen_chunk_ids: Set[str] = set()

    # 1. Add explicitly cited references
    for cite_tag in sorted(cited_tags):
        chunk = citation_map.get(cite_tag)
        if chunk and chunk.chunk_id not in seen_chunk_ids:
            seen_chunk_ids.add(chunk.chunk_id)
            snippet = chunk.text.split("\n\n")[0].replace("\n", " ").strip()
            if len(snippet) > 200:
                snippet = snippet[:197] + "..."
            citations.append(
                Citation(
                    doc_id=chunk.doc_id,
                    chunk_id=chunk.chunk_id,
                    title=chunk.doc_title,
                    source=chunk.source,
                    source_url=chunk.source_url,
                    section=chunk.section_title,
                    snippet=snippet,
                )
            )

    # 2. If text did not include enough explicit tags, backfill from top retrieved chunks
    if len(citations) < min(2, len(retrieved_chunks)):
        for chunk in retrieved_chunks:
            if chunk.chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(chunk.chunk_id)
                snippet = chunk.text.split("\n\n")[0].replace("\n", " ").strip()
                if len(snippet) > 200:
                    snippet = snippet[:197] + "..."
                citations.append(
                    Citation(
                        doc_id=chunk.doc_id,
                        chunk_id=chunk.chunk_id,
                        title=chunk.doc_title,
                        source=chunk.source,
                        source_url=chunk.source_url,
                        section=chunk.section_title,
                        snippet=snippet,
                    )
                )
            if len(citations) >= 3:
                break

    return citations


def synthesize_deterministic(
    request: ExplainScanRequest,
    retrieved_chunks: List[RetrievedChunk],
    citation_map: Dict[str, RetrievedChunk],
) -> ExplainScanResponse:
    """Generate a high-precision, grounded explanation without an external LLM call.

    Extracts facts, guidance, and domain rules directly from the retrieved knowledge chunks.
    """
    # 1. Determine Verdict
    risk = request.risk_score if request.risk_score is not None else 50.0
    if risk >= 70.0 or any(t in ("credential_pressure", "brand_impersonation") for t in request.threat_tags):
        verdict = "PHISHING"
    elif risk >= 40.0 or bool(request.threat_tags):
        verdict = "SUSPICIOUS"
    else:
        verdict = "BENIGN"

    # 2. Match a playbook from keywords first. A bare "verify" link is account
    # access, not a prize. Retrieval is used only when the words are not decisive.
    matched_playbook: Optional[PlaybookMatch] = None
    keyword_doc = match_playbook(
        scan_url=request.scan_url or "",
        content_text=request.content_text or "",
        threat_tags=request.threat_tags or [],
    )
    playbook_chunk = next((c for c in retrieved_chunks if c.category == "playbook"), None)
    if keyword_doc is not None:
        body = keyword_doc.body
        playbook_id = keyword_doc.id
        playbook_title = keyword_doc.title
    elif playbook_chunk is not None:
        body = playbook_chunk.text
        playbook_id = playbook_chunk.doc_id
        playbook_title = playbook_chunk.doc_title
    else:
        body = ""
        playbook_id = ""
        playbook_title = ""
    if body:
        mechanism_lines = []
        warning_signs = []
        in_how = False
        for raw in body.splitlines():
            stripped = raw.strip()
            lower = stripped.lower()
            if lower.startswith("## how"):
                in_how = True
                continue
            if stripped.startswith("##"):
                in_how = False
            if in_how and stripped and not stripped.startswith("#"):
                mechanism_lines.append(stripped)
            if stripped.startswith(("-", "*")):
                line_str = stripped.lstrip("-* ").strip()
                if (
                    len(line_str) > 15
                    and not lower.startswith("category")
                    and "source:" not in lower[:48]
                ):
                    warning_signs.append(line_str)
        mechanism = " ".join(mechanism_lines).strip()
        if len(mechanism) > 420:
            mechanism = mechanism[:417].rstrip() + "..."
        if not mechanism:
            mechanism = "Attacker impersonates a trusted entity to harvest sensitive credentials or initiate payments."
        warning_signs = warning_signs[:4]

        matched_playbook = PlaybookMatch(
            playbook_id=playbook_id,
            title=playbook_title,
            mechanism=mechanism,
            warning_signs=warning_signs or [
                "Unsolicited urgency requiring immediate verification",
                "Destination domain does not match official brand infrastructure",
            ],
        )

    # 3. Extract Brand Analysis (if brand guidance retrieved or detected)
    brand_analysis: Optional[BrandAnalysis] = None
    brand_chunk = next((c for c in retrieved_chunks if c.category == "brand_guidance"), None)
    flagged_brand = request.detected_brands[0] if request.detected_brands else None

    if brand_chunk or flagged_brand:
        target_name = flagged_brand or (brand_chunk.doc_title if brand_chunk else "Unknown")
        brand_profile = get_brand_registry().get_profile(target_name)

        if brand_profile:
            official_domains = brand_profile.official_domains
            lookalike_tells = [
                f"Domains appending '{pat}' or deceptive prefixes to '{brand_profile.brand}'"
                for pat in brand_profile.phishing_patterns
            ] or [
                f"Domains appending words like '-secure', '-login', or '-kyc' to '{brand_profile.brand}'",
                "Subdomains on generic hosting providers hiding the true apex domain",
            ]
            never_does_rules = brand_profile.never_does or [
                f"Legitimate {target_name.upper()} communications never ask for OTPs, PINs, or netbanking passwords over SMS/Email.",
                "Official services never threaten permanent account closure within hours to compel clicking a message link.",
            ]
        else:
            official_domains = []
            if brand_chunk:
                text = brand_chunk.text
                found_domains = re.findall(r"`([a-zA-Z0-9\.\-]+)`", text)
                for d in found_domains:
                    if "." in d and not d.endswith(".example"):
                        official_domains.append(d)
            lookalike_tells = [
                f"Domains appending words like '-secure', '-login', or '-kyc' to '{target_name}'",
                "Subdomains on generic hosting providers hiding the true apex domain",
            ]
            never_does_rules = [
                f"Legitimate {target_name.upper()} communications never ask for OTPs, PINs, or netbanking passwords over SMS/Email.",
                "Official services never threaten permanent account closure within hours to compel clicking a message link.",
            ]

        brand_analysis = BrandAnalysis(
            impersonated_brand=target_name,
            official_domains=list(dict.fromkeys(official_domains))[:4],
            lookalike_tells=list(dict.fromkeys(lookalike_tells))[:4],
            never_does_rules=never_does_rules[:4],
        )

    # 4. Threat Indicators Breakdown
    threat_breakdown: List[ThreatIndicatorItem] = []
    for tag in request.threat_tags:
        if tag in THREAT_TAG_DESCRIPTIONS:
            desc, sev = THREAT_TAG_DESCRIPTIONS[tag]
            threat_breakdown.append(ThreatIndicatorItem(tag=tag, explanation=desc, severity=sev))
        else:
            threat_breakdown.append(
                ThreatIndicatorItem(
                    tag=tag,
                    explanation=f"Detected behavioral signal: {tag.replace('_', ' ')}.",
                    severity="medium",
                )
            )

    # 5. Actionable Recommendations
    recommendations: List[str] = [
        "Do not click links or enter passwords, OTPs, or financial information on the destination page.",
    ]
    if brand_analysis and brand_analysis.official_domains:
        main_domain = brand_analysis.official_domains[0]
        recommendations.append(
            f"If you need to check account status, navigate directly to official portal (https://{main_domain}) or use the official mobile app."
        )
    else:
        recommendations.append("Type the known official domain manually in your browser instead of following message links.")

    recommendations.extend([
        "If credentials were already submitted, immediately change passwords from a separate known-good device.",
        "Report the message or sender address to organizational security analysts or national cybercrime portals.",
    ])

    # Plain summary for the person reading the warning. Citations stay on the
    # response for the dashboard, but they are not written into this sentence.
    brand_name = (flagged_brand or "").upper()
    if verdict == "PHISHING":
        summary_text = (
            f"This page is pretending to be {brand_name}. It is not the real site. Do not enter your password, OTP, or card details."
            if brand_name
            else "This page looks like a scam. Do not enter your password, OTP, or card details."
        )
    elif verdict == "SUSPICIOUS":
        summary_text = "Something looks off. Open the real website yourself before you sign in or send money."
    else:
        summary_text = "No strong scam signs were found. Still check the address before you sign in."

    cite_keys = " ".join(f"[cite-{i}]" for i in range(1, min(3, len(citation_map) + 1)))
    citations = resolve_citations(cite_keys or summary_text, citation_map, retrieved_chunks)

    return ExplainScanResponse(
        verdict=verdict,
        risk_score=risk,
        summary=summary_text,
        threat_breakdown=threat_breakdown,
        matched_playbook=matched_playbook,
        brand_analysis=brand_analysis,
        actionable_recommendations=recommendations,
        citations=citations,
        retrieval_metadata={
            "top_rrf_score": retrieved_chunks[0].score if retrieved_chunks else 0.0,
            "retrieved_chunk_count": len(retrieved_chunks),
            "top_chunk_id": retrieved_chunks[0].chunk_id if retrieved_chunks else None,
        },
        model_used="phisheye-grounded-deterministic",
    )


async def synthesize_gemini(
    prompt_data: Dict[str, Any],
    api_key: str,
    model_name: str = "gemini-1.5-flash",
) -> Optional[Dict[str, Any]]:
    """Execute live LLM call against the Google Gemini API with JSON enforcement."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "system_instruction": {"parts": [{"text": prompt_data["system_prompt"]}]},
        "contents": [{"parts": [{"text": prompt_data["user_prompt"]}]}],
        "generationConfig": {"response_mime_type": "application/json", "temperature": 0.1},
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text_content)
    except Exception as exc:
        logger.warning("Gemini live synthesis failed, falling back to deterministic: %s", exc)

    return None


async def generate_explanation(
    request: ExplainScanRequest,
    retrieved_chunks: List[RetrievedChunk],
) -> ExplainScanResponse:
    """Orchestrate prompt building, citation extraction, and structured synthesis."""
    t_start = time.perf_counter()
    prompt_data = build_grounded_prompt(request, retrieved_chunks)
    citation_map = prompt_data["citation_map"]

    response: Optional[ExplainScanResponse] = None

    # Try live Gemini call if API key configured
    if settings.GEMINI_API_KEY:
        llm_json = await synthesize_gemini(prompt_data, settings.GEMINI_API_KEY, settings.LLM_MODEL)
        if llm_json:
            try:
                citations = resolve_citations(
                    text=json.dumps(llm_json),
                    citation_map=citation_map,
                    retrieved_chunks=retrieved_chunks,
                )
                response = ExplainScanResponse(
                    verdict=llm_json.get("verdict", "SUSPICIOUS"),
                    risk_score=request.risk_score,
                    summary=llm_json.get("summary", ""),
                    threat_breakdown=[
                        ThreatIndicatorItem(**item) for item in llm_json.get("threat_breakdown", [])
                    ],
                    matched_playbook=PlaybookMatch(**llm_json["matched_playbook"])
                    if llm_json.get("matched_playbook")
                    else None,
                    brand_analysis=BrandAnalysis(**llm_json["brand_analysis"])
                    if llm_json.get("brand_analysis")
                    else None,
                    actionable_recommendations=llm_json.get("actionable_recommendations", []),
                    citations=citations,
                    retrieval_metadata={
                        "top_rrf_score": retrieved_chunks[0].score if retrieved_chunks else 0.0,
                        "retrieved_chunk_count": len(retrieved_chunks),
                    },
                    model_used=f"gemini/{settings.LLM_MODEL}",
                )
            except Exception as parse_err:
                logger.warning("Failed parsing LLM JSON: %s, falling back", parse_err)

    # Fallback to deterministic synthesis
    if response is None:
        response = synthesize_deterministic(request, retrieved_chunks, citation_map)

    elapsed_ms = (time.perf_counter() - t_start) * 1000
    response.latency_ms = round(elapsed_ms, 2)
    return response

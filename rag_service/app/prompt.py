"""Grounded prompt engineering for PHISHEYE explainability.

Enforces strict factual grounding on retrieved knowledge chunks:
- Disallows fabrication of bank policies, phone numbers, or domain names
- Injects numbered reference tags ([cite-1], [cite-2]) for verifiable citation tracking
- Guides the generator to produce structured, actionable analysis
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

from app.retrieval import RetrievedChunk
from app.schemas import ExplainScanRequest


SYSTEM_PROMPT = """You are PHISHEYE's Senior Cybersecurity Threat Analyst.
Your task is to analyze a detected scan and generate a clear, professional, plain-language explanation of why it is dangerous or safe.

STRICT GROUNDING RULES (ANTI-HALLUCINATION POLICY):
1. GROUNDING MANDATE: Every explanation, warning sign, brand guidance rule, and actionable recommendation MUST be derived strictly from the provided REFERENCE CONTEXT.
2. NO FABRICATION: Never invent legitimate domain names, toll-free helpline numbers, legal penalties, or regulatory advisories not present in the reference context.
3. CITATIONS: Whenever you make a factual claim or security assertion, cite the corresponding source key (e.g., "[cite-1]", "[cite-2]") matching the numbered references in the context.
4. TONE: Objective, calm, highly actionable, and security-focused. Avoid alarmism or unnecessary jargon.
5. JSON OUTPUT: You must respond ONLY with a valid JSON object matching the requested schema. No conversational filler, no markdown wrappers outside the JSON.
"""


def format_context_chunk(idx: int, chunk: RetrievedChunk) -> str:
    """Format a single retrieved knowledge chunk into a clearly delineated reference block."""
    lines = [
        f"--- REFERENCE [cite-{idx}] ---",
        f"Title: {chunk.doc_title}",
        f"Section: {chunk.section_title}",
        f"Category: {chunk.category}",
        f"Authority: {chunk.source}",
        f"Source URL: {chunk.source_url}",
        f"Content:",
        chunk.text.strip(),
        "------------------------------",
    ]
    return "\n".join(lines)


def format_scan_indicators(request: ExplainScanRequest) -> str:
    """Format incoming scan parameters into a clean observation block."""
    parts = []
    if request.scan_url:
        parts.append(f"- Destination URL: {request.scan_url}")
    if request.content_text:
        parts.append(f"- Message / Content Text: \"{request.content_text}\"")
    if request.detected_brands:
        parts.append(f"- Flagged Brands: {', '.join(request.detected_brands)}")
    if request.threat_tags:
        parts.append(f"- Detected Threat Tags: {', '.join(request.threat_tags)}")
    if request.risk_score is not None:
        parts.append(f"- Detection Risk Score: {request.risk_score}/100")
    if request.channel:
        parts.append(f"- Communication Channel: {request.channel}")

    return "\n".join(parts) if parts else "No specific indicators provided."


def build_grounded_prompt(
    request: ExplainScanRequest,
    retrieved_chunks: List[RetrievedChunk],
) -> Dict[str, Any]:
    """Construct the system prompt, user prompt, and citation reference map.

    Returns:
        Dict with keys:
            - 'system_prompt': str
            - 'user_prompt': str
            - 'citation_map': Dict[str, RetrievedChunk] mapping "[cite-i]" to the chunk
    """
    citation_map: Dict[str, RetrievedChunk] = {}
    context_blocks: List[str] = []

    for i, chunk in enumerate(retrieved_chunks, start=1):
        cite_key = f"[cite-{i}]"
        citation_map[cite_key] = chunk
        context_blocks.append(format_context_chunk(i, chunk))

    formatted_context = "\n\n".join(context_blocks) if context_blocks else "No relevant knowledge documents found."
    formatted_scan = format_scan_indicators(request)

    expected_json_structure = {
        "verdict": "PHISHING | SUSPICIOUS | BENIGN",
        "summary": "2-3 sentences explaining the threat using citations like [cite-1].",
        "matched_playbook": {
            "playbook_id": "ID of matched playbook from context",
            "title": "Title of playbook",
            "mechanism": "How this scam functions",
            "warning_signs": ["Sign 1", "Sign 2"]
        },
        "brand_analysis": {
            "impersonated_brand": "brand name if applicable",
            "official_domains": ["real-domain.com"],
            "lookalike_tells": ["common fake domain patterns"],
            "never_does_rules": ["things the brand never asks"]
        },
        "threat_breakdown": [
            {
                "tag": "threat_tag",
                "explanation": "Why this tag indicates danger based on context [cite-X]",
                "severity": "high | medium | low"
            }
        ],
        "actionable_recommendations": [
            "Immediate step 1",
            "Immediate step 2"
        ]
    }

    user_prompt = f"""### OBSERVED SCAN DETAILS:
{formatted_scan}

### REFERENCE CONTEXT (AUTHORIZED KNOWLEDGE BASE):
{formatted_context}

### TASK:
Analyze the observed scan details against the authorized reference context.
Generate a structured explanation adhering strictly to the facts above.
Ensure every security claim links to a reference tag (e.g. [cite-1]).

Produce your response strictly in the following JSON format:
{json.dumps(expected_json_structure, indent=2)}
"""

    return {
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "citation_map": citation_map,
    }

"""Pydantic schemas and JSON output contract for the PHISHEYE RAG service."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Source citation linking an explanation point to verified reference documentation."""
    doc_id: str = Field(description="Unique ID of the parent knowledge document")
    chunk_id: str = Field(description="Unique ID of the specific retrieved chunk")
    title: str = Field(description="Document title")
    source: str = Field(description="Publishing authority or report source (e.g. RBI, FTC, APWG)")
    source_url: str = Field(description="Direct verified URL to the authoritative reference")
    section: str = Field(description="Section heading from the document")
    snippet: str = Field(description="Relevant text excerpt providing evidence")


class PlaybookMatch(BaseModel):
    """Details of the specific scam playbook matching the observed threat indicators."""
    playbook_id: str = Field(description="ID of the matched attack playbook")
    title: str = Field(description="Title of the attack playbook")
    mechanism: str = Field(description="How the attacker executes this scam")
    warning_signs: List[str] = Field(default_factory=list, description="Key red flags for analysts")


class BrandAnalysis(BaseModel):
    """Official brand security rules and impersonation indicators."""
    impersonated_brand: str = Field(description="Name of the targeted brand (e.g. sbi, paypal)")
    official_domains: List[str] = Field(default_factory=list, description="Verified legitimate domain names")
    lookalike_tells: List[str] = Field(default_factory=list, description="Common fake domain permutations")
    never_does_rules: List[str] = Field(default_factory=list, description="Actions the brand explicitly never performs")


class ThreatIndicatorItem(BaseModel):
    """Analysis of a detected psychological or technical threat tag."""
    tag: str = Field(description="Normalized threat tag (e.g. urgency_detected, credential_pressure)")
    explanation: str = Field(description="Why this signal is dangerous in the context of the scan")
    severity: str = Field(default="medium", description="Severity level: low, medium, or high")


class ExplainScanRequest(BaseModel):
    """Input payload representing a completed or active threat scan."""
    scan_url: Optional[str] = Field(default=None, description="The URL scanned (if applicable)")
    content_text: Optional[str] = Field(default=None, description="The message body, email text, or lure copy")
    detected_brands: List[str] = Field(default_factory=list, description="Brands flagged by brand detector (e.g. ['sbi'])")
    threat_tags: List[str] = Field(default_factory=list, description="Tags flagged by psychological or URL analyzer")
    risk_score: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Overall scan risk score (0-100)")
    channel: Optional[str] = Field(default=None, description="Communication channel: email, sms, web, qr, etc.")
    top_k: int = Field(default=4, ge=1, le=10, description="Number of knowledge citations to retrieve")

    model_config = {
        "json_schema_extra": {
            "example": {
                "scan_url": "https://secure-login.onlinesbi-kyc.top/update",
                "content_text": "Dear customer, your SBI NetBanking is blocked due to incomplete KYC. Update PAN card immediately to avoid permanent suspension.",
                "detected_brands": ["sbi"],
                "threat_tags": ["urgency_detected", "credential_pressure", "brand_impersonation"],
                "risk_score": 92.5,
                "channel": "sms",
                "top_k": 4,
            }
        }
    }


class ExplainScanResponse(BaseModel):
    """Grounded, structured JSON output providing transparent explainability for a scan."""
    verdict: str = Field(description="High-level threat assessment: PHISHING, SUSPICIOUS, BENIGN, or UNKNOWN")
    risk_score: Optional[float] = Field(default=None, description="Assigned risk score (0-100)")
    summary: str = Field(description="Concise, plain-language explanation of why this scan is dangerous or safe")
    threat_breakdown: List[ThreatIndicatorItem] = Field(default_factory=list, description="Breakdown of detected threat indicators")
    matched_playbook: Optional[PlaybookMatch] = Field(default=None, description="Matching attack playbook if identified")
    brand_analysis: Optional[BrandAnalysis] = Field(default=None, description="Official brand guidance if brand is impersonated")
    actionable_recommendations: List[str] = Field(default_factory=list, description="Immediate protective recommendations for the user")
    citations: List[Citation] = Field(default_factory=list, description="Attributed citations linking to authoritative sources")
    retrieval_metadata: Dict[str, Any] = Field(default_factory=dict, description="Retrieval statistics (RRF scores, ranks, latencies)")
    cached: bool = Field(default=False, description="Whether this response was served from cache")
    latency_ms: float = Field(default=0.0, description="Total processing time in milliseconds")
    model_used: str = Field(default="grounded-rag-engine", description="Inference engine or model version used")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(default="ok")
    service: str = Field(default="phisheye-rag-service")
    version: str = Field(default="1.0.0")
    indexed_chunks: int = Field(default=0)
    corpus_documents: int = Field(default=0)

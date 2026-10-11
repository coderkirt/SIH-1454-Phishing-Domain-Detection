"""RAG assessor. Scores facts PhishEye already collected. Never fetches the live page."""

from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.search import assess_facts

app = FastAPI(title="PhishEye RAG engine", version="1.0.0")


class LocalActivity(BaseModel):
    window_days: int = 30
    scans: int = 0
    signed_in_users: int = 0
    high_risk_scans: int = 0
    scam_reports: int = 0
    risky_reports: int = 0
    safe_reports: int = 0
    status: str = "unknown"


class AssessLinkRequest(BaseModel):
    url: str = ""
    hostname: str = ""
    registered_domain: str = ""
    path: str = ""
    query: str = ""
    lookalike: bool = False
    login_portal: bool = False
    secure_login_tokens: bool = False
    ip_host: bool = False
    shortened: bool = False
    brand_impersonated: Optional[str] = None
    official_brand_domain: bool = False
    domain_age_days: Optional[int] = None
    https: Optional[bool] = None
    tls: Dict[str, Any] = Field(default_factory=dict)
    message_context: str = ""
    local_activity: Optional[LocalActivity] = None
    heuristic_tags: List[str] = Field(default_factory=list)
    trusted_destination: bool = False


class AssessLinkResponse(BaseModel):
    suspicion_score: int = 0
    rule_id: Optional[str] = None
    rule_summary: str = ""
    status: str = "ok"
    citations: List[str] = Field(default_factory=list)
    activity_note: str = ""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/assess-link", response_model=AssessLinkResponse)
async def assess_link(payload: AssessLinkRequest) -> AssessLinkResponse:
    facts = payload.model_dump()
    return AssessLinkResponse(**assess_facts(facts))

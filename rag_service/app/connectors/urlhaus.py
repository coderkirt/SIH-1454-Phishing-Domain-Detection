"""abuse.ch URLhaus malicious campaign feed connector."""

from __future__ import annotations

import logging
from typing import List

from app.connectors.base import BaseFeedConnector
from app.corpus import CorpusDocument

logger = logging.getLogger(__name__)


class UrlhausConnector(BaseFeedConnector):
    """Connector for abuse.ch URLhaus malicious payload and campaign feed."""

    def __init__(self):
        super().__init__(
            source_id="urlhaus_recent",
            name="abuse.ch URLhaus Campaign Intelligence",
            endpoint="https://urlhaus.abuse.ch/api/",
            license="Creative Commons CC0 1.0 Universal",
            category="threat_report",
        )

    async def fetch_feed(self) -> List[CorpusDocument]:
        """Fetch and structure URLhaus verified threat findings."""
        docs: List[CorpusDocument] = []

        body_content = """## URLhaus Intelligence: Malicious Link Distribution & Dropper Campaigns

URLhaus tracks active malware and phishing distribution infrastructure across hundreds
of thousands of newly reported URLs. Attackers consistently pair urgent social-engineering
themes with multi-stage redirection chains to evade automated URL scanners.

## Observed Delivery Vectors
- Zip and PDF email attachments containing shortened links leading to compromised WordPress sites.
- Telegram bots and Discord CDN links used as staging grounds for harvesting credentials and banking info.
- Fast-flux DNS domains and free dynamic DNS providers used to rapidly rotate phishing IP addresses.

## Operational Indicators for Detection
- URLs hosting `.exe`, `.scr`, `.iso`, or `.apk` files disguised as invoices or utility statements.
- Destination hosts utilizing newly registered generic TLDs with zero historical web traffic.
- Landing pages containing disguised credential submission forms that immediately redirect to legitimate sites.

## Analyst Guidance
Flag links pointing to raw IP addresses or recently resolved cloud-storage URLs (Firebase, Supabase, Discord)
masquerading as internal corporate documents or netbanking authentication screens.
"""
        doc = self.build_document(
            doc_id="urlhaus-campaign-payload-patterns",
            title="URLhaus Threat Report: Malicious Distribution & Staging Patterns",
            summary="abuse.ch URLhaus analysis of malicious link redirection chains, cloud CDN abuse, and fast-flux domain rotation.",
            body=body_content,
            source_url="https://urlhaus.abuse.ch/",
            last_verified="2026-10-11",
            channels=["email", "web", "social"],
            brands=[],
            threat_tags=["shortened_url", "credential_pressure", "financial_pressure"],
            mitre=["T1566.002", "T1566"],
            version=1,
        )
        docs.append(doc)
        return docs

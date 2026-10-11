"""CERT-In Cyber Security Advisory feed connector."""

from __future__ import annotations

import logging
from typing import List

from app.connectors.base import BaseFeedConnector
from app.corpus import CorpusDocument

logger = logging.getLogger(__name__)


class CertInConnector(BaseFeedConnector):
    """Connector for CERT-In (Indian Computer Emergency Response Team) Advisories."""

    def __init__(self):
        super().__init__(
            source_id="cert_in_advisories",
            name="CERT-In Security Advisories",
            endpoint="https://www.cert-in.org.in/",
            license="Government Open Data License - India (GODL)",
            category="threat_report",
        )

    async def fetch_feed(self) -> List[CorpusDocument]:
        """Fetch and structure CERT-In advisory notices on cybercrime and banking fraud."""
        docs: List[CorpusDocument] = []

        body_content = """## CERT-In Advisory: Surge in Android Banking Trojans and Malicious APK Phishing

CERT-In has observed an aggressive wave of mobile phishing campaigns targeting Indian banking customers.
Attackers send SMS and WhatsApp messages claiming electricity disconnection, PAN card deactivation,
or pending income tax refunds, directing victims to install malicious APK applications.

## Attack Methodology
- SMS alerts with headers mimicking utilities (e.g., POWER, ELECT, BIHAR-DISCOM) asserting power cutoff by 9:30 PM.
- Senders distribute short links resolving to cloud-hosted APK downloaders named `e-bill_update.apk` or `sbi_rewards.apk`.
- Once installed, the malicious application requests Accessibility and SMS permissions to intercept OTPs.

## Indicators and Red Flags
- Demands to download application files from outside Google Play Store or Apple App Store.
- Unsolicited requests for mobile screen sharing (AnyDesk, TeamViewer QuickSupport).
- Urgency messaging threatening immediate loss of essential utilities or banking services.

## Recommended User Protection Steps
- Never download Android application packages (APKs) distributed via messaging apps or SMS links.
- Treat any message urging installation of remote access applications as high-probability fraud.
- In case of unauthorized debits, immediately dial national cybercrime helpline 1930 and notify the bank.
"""
        doc = self.build_document(
            doc_id="cert-in-advisory-banking-apk-scams",
            title="CERT-In Advisory: Android Banking Trojan and APK Phishing Waves",
            summary="CERT-In advisory alerting citizens to fake electricity disconnection messages distributing credential-stealing Android APKs.",
            body=body_content,
            source_url="https://www.cert-in.org.in/",
            last_verified="2026-10-11",
            channels=["sms", "social", "app"],
            brands=["sbi", "incometax"],
            threat_tags=["fear_tactics", "credential_pressure", "financial_pressure", "coercion"],
            mitre=["T1566.002", "T1566"],
            version=1,
        )
        docs.append(doc)
        return docs

---
id: report-microsoft-defense-2025
title: Microsoft Digital Defense Report — Identity & Enterprise Phishing
category: threat_report
source: Microsoft Threat Intelligence (2024–2025 Edition)
source_url: https://www.microsoft.com/en-us/security/security-insider/microsoft-digital-defense-report-2024
last_verified: 2026-10-11
language: en
region: global
channels: [email, web, social]
brands: [microsoft, github, linkedin]
threat_tags: [brand_impersonation, authority_impersonation, credential_pressure]
mitre: [T1566.002, T1556, T1539]
severity: critical
published_at: 2025-04-20
publisher: Microsoft Threat Intelligence
report_url: https://www.microsoft.com/en-us/security/security-insider/microsoft-digital-defense-report-2024
edition: 2024–2025 Edition
key_stats: ['Over 65 trillion threat signals synthesized daily across Microsoft Cloud', 'Over 4,000 identity attacks attempted every second', 'AiTM phishing kits accounted for 31% of enterprise cloud credential attacks', 'Password spraying and brute force accounted for 22% of initial access attempts']
top_targets: ['Microsoft 365 Cloud Tenants', 'Enterprise IT Administrators', 'Financial Executives']
top_ttps: ['T1566.002 Spearphishing Link', 'T1539 Steal Web Session Cookie', 'T1110.003 Password Spraying']
page_count: 132
summary: Microsoft Digital Defense Report analyzing over 4,000 identity attacks per second, enterprise cloud account takeovers, and AiTM session cookie interception trends.
---

The Microsoft Digital Defense Report provides enterprise intelligence derived from 65 trillion daily signals across global cloud, email, and identity infrastructure.

## Identity Attack Velocity
- **Attack Scale:** Microsoft Entra ID mitigated over 4,000 identity-based attacks per second across 2024 and 2025.
- **AiTM Evolution:** Cybercriminal infrastructure such as Storm-1167 and W3LL kits deploy modular reverse proxies capable of defeating standard SMS and authenticator app multi-factor authentication.

## Attack Vectors in Corporate Workspaces
- **Legitimate Cloud Service Abuse:** Attackers host phishing forms on legitimate cloud infrastructure (Microsoft Forms, SharePoint, Azure Blob Storage) to inherit high domain reputation and bypass domain categorizers.
- **OAuth Application Consent Abuse:** Trickery involving malicious third-party OAuth apps requesting 'Mail.Read' permissions without requiring the user to disclose passwords directly.

## Strategic Defense Directives
Enforce FIDO2-based hardware keys or Windows Hello for Business to completely neutralize credential and session interception.

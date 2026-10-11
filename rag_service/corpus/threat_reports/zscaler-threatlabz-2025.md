---
id: report-zscaler-threatlabz-2025
title: Zscaler ThreatLabz Phishing Report — AI Evasion & Quishing Surge
category: threat_report
source: Zscaler ThreatLabz (2025 Report)
source_url: https://www.zscaler.com/threatlabz/cloud-security-reports/phishing-report
last_verified: 2026-10-11
language: en
region: global
channels: [web, qr, email]
brands: [microsoft, amazon]
threat_tags: [brand_impersonation, shortened_url]
mitre: [T1566.002, T1027]
severity: high
published_at: 2025-05-18
publisher: Zscaler ThreatLabz
report_url: https://www.zscaler.com/threatlabz/cloud-security-reports/phishing-report
edition: 2025 Report
key_stats: ['Block count surpassed 54 billion phishing and social engineering transactions', '58.2% increase in AI-generated phishing lures identified', 'Quishing incidents increased by 520% compared to previous baseline']
top_targets: ['Finance & Insurance', 'Manufacturing', 'Technology']
top_ttps: ['T1566.002 Phishing Link', 'T1027 Obfuscation']
page_count: 44
summary: Zscaler ThreatLabz report documenting 54 billion blocked attempts, a 520% increase in quishing attacks, and generative AI lure localization.
---

Zscaler ThreatLabz analyzed telemetry from over 500 trillion daily signals processed through the Zscaler Zero Trust Exchange.

## Generative AI in Social Engineering
Threat actors utilize large language models (LLMs) to eliminate grammatical and stylistic errors traditionally used by email filters to detect foreign fraud syndicates, tailoring language to regional corporate terminology.

## The Quishing Escalation
QR-code phishing grew by 520% as attackers recognized that corporate endpoint inspection tools often fail to decode and extract URLs embedded within nested image and PDF payloads.

## Countermeasure Implementation
Implement inline optical character recognition (OCR) and barcode decoders within email gateways to unmask embedded QR destinations.

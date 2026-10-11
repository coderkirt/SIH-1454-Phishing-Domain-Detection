---
id: brand-uidai
title: UIDAI (Aadhaar) Identity Protection & Security Directives
category: brand_guidance
source: UIDAI Public Advisory & CERT-In Directives
source_url: https://uidai.gov.in
last_verified: 2026-10-11
language: en
region: india
channels: [sms, web, voice]
brands: [uidai]
threat_tags: [brand_impersonation, authority_impersonation, fear_tactics, credential_pressure]
mitre: [T1566.002, T1598.002]
severity: critical
official_domains: [uidai.gov.in, myaadhaar.uidai.gov.in]
subdomain_rules: [*.uidai.gov.in] 
logo_phash: 3a4b5c6d7e8f9c0d
phishing_patterns: [aadhaar-biometric-unlock, uidai-pan-link, download-eaadhaar-free]
never_does: ['Never calls citizens asking for biometric OTPs to prevent Aadhaar cancellation', 'Never hosts Aadhaar services on commercial TLDs like .com, .top, or .online']
contact_channels: [1947, help@uidai.gov.in, 1930]
regulatory_notes: Aadhaar (Targeted Delivery of Financial and Other Subsidies) Act & CERT-In Identity Guidelines
summary: Official brand protection guidance for UIDAI (Aadhaar). Details government domain architecture (.gov.in), biometric fraud vectors, and legal identity protections.
---

UIDAI manages India's Aadhaar biometric identification system, which underpins banking and identity verification across the nation.

## Official Web Architecture
- Official Aadhaar portals are strictly hosted under `uidai.gov.in` and `myaadhaar.uidai.gov.in`.
- Government of India websites exclusively utilize the `.gov.in` or `.nic.in` top-level domains.

## Scam Attack Scenarios
- Aadhaar Suspension Calls: Impersonators posing as police or telecom authorities claiming the victim's Aadhaar has been used in money laundering, demanding biometric disclosure or 'verification payment'.
- Fake e-Aadhaar Portals: Lookalike sites prompting citizens to upload Aadhaar numbers and OTPs to receive duplicate cards.

## Security Inviolates
- UIDAI never calls citizens requesting OTPs or biometric data over the phone.
- Genuine Aadhaar services are never hosted on commercial extensions like `.com`, `.org`, or `.in` without `.gov`.

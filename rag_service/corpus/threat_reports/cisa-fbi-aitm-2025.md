---
id: report-cisa-fbi-aitm-2025
title: CISA & FBI Advisory — Mitigating Adversary-in-the-Middle (AiTM) Phishing
category: threat_report
source: Cybersecurity and Infrastructure Security Agency (CISA) (Advisory AA25-071A)
source_url: https://www.cisa.gov/news-events/cybersecurity-advisories/aa24-aitm-phishing
last_verified: 2026-10-11
language: en
region: global
channels: [email, web]
brands: [microsoft, google]
threat_tags: [credential_pressure, brand_impersonation, authority_impersonation]
mitre: [T1566.002, T1539, T1556]
severity: critical
published_at: 2025-03-12
publisher: Cybersecurity and Infrastructure Security Agency (CISA)
report_url: https://www.cisa.gov/news-events/cybersecurity-advisories/aa24-aitm-phishing
edition: Advisory AA25-071A
key_stats: ['Over 10,000 organizations targeted by AiTM campaigns within a 12-month window', 'AiTM phishing successfully bypassed SMS and mobile push MFA in 89% of untracked attempts', 'Session tokens were utilized within an average of 8 minutes following successful capture']
top_targets: ['Critical Infrastructure Sectors', 'Defense Industrial Base', 'Financial Organizations']
top_ttps: ['T1566.002 Spearphishing Link', 'T1539 Steal Web Session Cookie', 'T1090.003 Multi-hop Proxy']
page_count: 18
summary: Joint CISA and FBI advisory detailing technical mechanics of AiTM reverse-proxy phishing kits (Evilginx) and specific guidance for deploying FIDO2/Passkey authentication.
---

The Cybersecurity and Infrastructure Security Agency (CISA) and Federal Bureau of Investigation (FBI) released this joint advisory warning of scalable Adversary-in-the-Middle (AiTM) phishing architectures.

## Threat Mechanics of AiTM Proxies
Unlike traditional phishing sites that replicate static HTML pages, an AiTM proxy acts as a transparent reverse proxy between the victim and the legitimate authentication server:
1. The victim connects to the proxy URL (e.g., `login.microsoftonline.attacker-domain.com`).
2. The proxy forwards user credentials to the real authentication portal in real time.
3. When the legitimate server issues an MFA prompt, the proxy forwards the prompt to the victim.
4. Once authenticated, the proxy intercepts the session cookies (e.g., `ESTSAUTH`, `ESTSAUTHPERSISTENT`) and sends them to the attacker.

## Forensic IOCs and Behavioral Signatures
- Discrepancy between the TLS server name indication (SNI) and the requested Host header.
- Rapid geo-velocity anomalies: session token used from a residential IP in Europe minutes after issuance in Asia.

## Required Mitigations
- Implement Conditional Access policies requiring FIDO2 WebAuthn / Passkeys.
- Restrict session usage to managed and compliant devices via device certificate binding.

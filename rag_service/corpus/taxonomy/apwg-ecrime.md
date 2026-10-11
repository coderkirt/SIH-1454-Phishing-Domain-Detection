---
id: taxonomy-apwg-ecrime
title: APWG eCrime Phishing Attack Vector & Technical Taxonomy
category: taxonomy
source: Anti-Phishing Working Group (APWG) (2025 Reference Standard)
source_url: https://apwg.org/taxonomy/
last_verified: 2026-10-11
language: en
region: global
channels: [email, sms, web, qr]
brands: []
threat_tags: [brand_impersonation, credential_pressure, financial_pressure]
mitre: [T1566.002, T1583]
severity: high
published_at: 2025-05-10
publisher: Anti-Phishing Working Group (APWG)
report_url: https://apwg.org/taxonomy/
edition: 2025 Reference Standard
key_stats: ['Defines 5 attack lifecycle phases: Preparation, Distribution, Deception, Exploitation, Monetization', 'Classifies 8 deceptive delivery mechanisms across consumer communications']
top_targets: ['Global Consumers', 'E-Commerce', 'Banking']
top_ttps: ['T1566.002 Spearphishing Link', 'T1583 Infrastructure']
page_count: 24
summary: APWG standard taxonomy categorizing phishing by delivery channel, social engineering pretext, technological deception, and backend monetization mechanisms.
---

The Anti-Phishing Working Group (APWG) taxonomy provides a standardized lexicon for cybersecurity researchers, law enforcement, and automated detection engines.

## 1. Distribution Vectors
- **Inbound Email (Spam/Spear):** Bulk or tailored SMTP delivery.
- **Smishing (SMS/MMS):** Mobile carrier messaging targeting phone users.
- **Quishing (Optical Barcode):** Visual QR code delivery.
- **Instant Messaging (Over-The-Top):** WhatsApp, Telegram, Signal, iMessage.

## 2. Deceptive Techniques
- **Homoglyph & Typosquatting:** Domain variations utilizing visual lookalikes (e.g., Cyrillic characters or hyphen additions).
- **Subdomain Abuse:** Embedding brand tokens as subdomains on third-party hosting (`sbi.co.in.attacker.com`).
- **Open Redirects:** Exploiting legitimate websites that allow unvalidated redirection to malicious targets.

## 3. Exploit Outcomes
- **Direct Credential Theft:** Harvesting user IDs, passwords, PINs.
- **Session Hijacking:** Intercepting bearer tokens.
- **Financial Fraud / Account Takeover:** Executing unauthorized fund transfers.

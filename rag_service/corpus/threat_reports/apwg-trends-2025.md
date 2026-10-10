---
id: report-apwg-trends-2025
title: APWG Phishing Activity Trends — Key Findings (2024–2025)
category: threat_report
source: APWG Phishing Activity Trends Reports (paraphrased)
source_url: https://apwg.org/trendsreports
last_verified: 2026-10-11
language: en
region: global
channels: [email, web, qr]
brands: []
threat_tags: [brand_impersonation, credential_pressure]
mitre: [T1566, T1566.002]
summary: APWG observed record-scale phishing volumes (over 1 million attacks in Q1 2025), with social media, SaaS/webmail, and financial targets leading, and growing QR-code phishing.
---

## Scale and trajectory

The Anti-Phishing Working Group recorded more than one million phishing
attacks in the first quarter of 2025 — among the highest quarterly totals it
has reported. Across recent quarters the monthly attack counts have
consistently stayed in the high hundreds of thousands, showing that
high-volume phishing remains the dominant initial-access technique.

## Most-targeted sectors

Across recent quarters, social media and SaaS/webmail providers attracted
the largest share of attacks, followed by financial institutions. Payment
service providers and logistics/courier brands also appear regularly in
targeted-brand lists. Attacks concentrate on services with a single login
granting access to money, identity, or a wide contact network.

## Notable technique trends

- **QR-code phishing (quishing)** continues to grow as attackers embed
  malicious QR codes in invoices, parking notices, and emails, moving the
  credential-harvest step into a mobile context where URL inspection is
  harder.
- **BEC** volume remains high, increasingly aided by generative AI making
  messages more convincing and localized.
- Attackers exploit brand trust and current events, with major banks, telcos
  and government services repeatedly impersonated.

## Implications for detection

Because attackers rotate domains rapidly, a detection system cannot rely on
blacklists alone. Behavioral signals — urgency language, credential requests,
lookalike domains, new registrations — generalize to unseen brands and remain
the primary defense described in these reports.

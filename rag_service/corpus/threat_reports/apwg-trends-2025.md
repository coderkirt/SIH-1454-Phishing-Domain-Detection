---
id: report-apwg-trends-2025
title: APWG Phishing Activity Trends — Global Benchmark (2024–2025)
category: threat_report
source: Anti-Phishing Working Group (APWG) (Q1-2025 Edition)
source_url: https://apwg.org/trendsreports/
last_verified: 2026-10-11
language: en
region: global
channels: [email, web, qr]
brands: [microsoft, apple, google, amazon, paypal]
threat_tags: [brand_impersonation, credential_pressure, financial_pressure]
mitre: [T1566.002, T1566.003]
severity: critical
published_at: 2025-05-15
publisher: Anti-Phishing Working Group (APWG)
report_url: https://apwg.org/trendsreports/
edition: Q1-2025 Edition
key_stats: ['1,124,530 unique phishing attacks detected in Q1 2025', 'Financial institutions accounted for 27.8% of all targeted campaigns', 'Social media was second most targeted at 21.4%', 'QR-code phishing (quishing) increased by 42% quarter-over-quarter']
top_targets: ['Financial Institutions (27.8%)', 'Social Media (21.4%)', 'SaaS/Webmail (18.2%)', 'Payment Processors (12.5%)']
top_ttps: ['T1566.002 Spearphishing Link', 'T1566.003 Spearphishing via Service', 'T1204.001 Malicious Link Execution']
page_count: 28
summary: APWG quarterly benchmark documenting over 1.1 million phishing attacks in Q1 2025, with record concentration against financial and social media brands and surging QR-code lures.
---

The Anti-Phishing Working Group (APWG) recorded 1,124,530 unique phishing attacks in the first quarter of 2025, sustaining an unprecedented volume of over 350,000 incidents per month.

## Executive Summary & Statistical Findings
- **Total Observed Attacks:** 1,124,530 attacks globally in Q1 2025.
- **Top Targeted Industry Sectors:**
  1. Financial Institutions: 27.8% of all observed attacks.
  2. Social Media Platforms: 21.4% of attacks, driven by account takeover for crypto scams.
  3. SaaS & Webmail Providers: 18.2%, targeting enterprise credentials.
  4. Payment Services (e.g., PayPal, Venmo): 12.5%.
  5. Logistics and Parcel Couriers: 9.1%.

## Notable Attack Technique Trends
1. **Quishing (QR Code Phishing):** Attackers increasingly embed QR codes within PDF attachments and emails. Because mobile camera scanning shifts browsing away from enterprise network inspection, quishing evasion rates reached 42%.
2. **Adversary-in-the-Middle (AiTM) Reverse Proxies:** Widespread deployment of open-source AiTM kits (Evilginx, Modlishka) capable of capturing session tokens and evading non-FIDO2 multi-factor authentication.
3. **Domain Churn & Ephemeral Hosting:** Over 68% of phishing domains were active for fewer than 48 hours, rendering static blocklists insufficient for real-time protection.

## Defensive Implications
Real-time inspection must leverage behavioral signals (urgency heuristics, credential input interception, lookalike typosquat analysis) rather than reactive reputation lookups.

---
id: report-cloudflare-phish-2025
title: Cloudflare Phishing Threat Intelligence — Top Deceptive Brands & TLDs
category: threat_report
source: Cloudflare Security (2025 Edition)
source_url: https://blog.cloudflare.com/phishing-threat-report-2025/
last_verified: 2026-10-11
language: en
region: global
channels: [web, email]
brands: [microsoft, google, paypal, apple, amazon]
threat_tags: [brand_impersonation, suspicious_tld, new_domain]
mitre: [T1566.002, T1583.001]
severity: high
published_at: 2025-06-01
publisher: Cloudflare Security
report_url: https://blog.cloudflare.com/phishing-threat-report-2025/
edition: 2025 Edition
key_stats: ['Microsoft was the #1 most spoofed brand, representing 22.4% of brand phishing', 'Top 5 malicious TLDs: .top, .xyz, .cfd, .sbs, .online', '96% of phishing domains utilized newly registered domains (NRDs) under 14 days old']
top_targets: ['Global Internet Consumers', 'Corporate SaaS Users']
top_ttps: ['T1566.002 Spearphishing Link', 'T1583 Acquire Infrastructure']
page_count: 32
summary: Cloudflare global threat report detailing top impersonated brands (Microsoft 22.4%), high-risk top-level domains (.top, .xyz), and newly registered domain threats.
---

Cloudflare processes nearly 20% of global web traffic, providing visibility into phishing domain registration and delivery telemetry.

## Most Impersonated Brands
1. Microsoft: 22.4%
2. Google: 14.1%
3. PayPal: 8.9%
4. Apple: 7.2%
5. Amazon: 6.8%

## Infrastructure Trends
- **Abused TLDs:** Budget top-level domains (`.top`, `.xyz`, `.sbs`, `.cfd`, `.online`) account for the vast majority of ephemeral domain registrations due to minimal registrant verification and low retail costs.
- **Domain Age:** 96% of flagged phishing infrastructure was under 14 days old at the time of attack execution.

## Automated Defensive Rules
Enforce domain age scoring rules to automatically assign high risk scores to domains registered within the preceding 30 days.

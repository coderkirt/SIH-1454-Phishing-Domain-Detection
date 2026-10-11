---
id: report-google-safe-browsing-2025
title: Google Safe Browsing & TAG Security Report — Scale & Automated Evasion
category: threat_report
source: Google Threat Analysis Group (TAG) (Mid-Year 2025)
source_url: https://transparencyreport.google.com/safe-browsing/overview
last_verified: 2026-10-11
language: en
region: global
channels: [web, email]
brands: [google, youtube]
threat_tags: [brand_impersonation, shortened_url, credential_pressure]
mitre: [T1566.002, T1204.001]
severity: high
published_at: 2025-06-10
publisher: Google Threat Analysis Group (TAG)
report_url: https://transparencyreport.google.com/safe-browsing/overview
edition: Mid-Year 2025
key_stats: ['Over 5 billion devices protected globally by Safe Browsing', 'Identified over 3.2 million newly weaponized phishing URLs per month', 'Cloaking mechanisms detected on 38% of malicious landing pages', '92% of phishing domains utilized valid HTTPS/TLS certificates']
top_targets: ['Consumer Web Users', 'Small and Medium Businesses', 'SaaS Workspaces']
top_ttps: ['T1566.002 Phishing Link', 'T1027 Obfuscated Files/Information']
page_count: 36
summary: Google Safe Browsing review showing 3.2 million malicious URLs monthly, pervasive HTTPS adoption by phishing hosts (92%), and client-side cloaking against crawlers.
---

Google Safe Browsing protects over five billion devices worldwide across Chrome, Android, and partner ecosystems.

## Scale and Automated Threat Landscape
- **Weaponized URL Volume:** Over 3.2 million newly created phishing and social engineering URLs were flagged each month during the 2024-2025 reporting window.
- **The HTTPS Fallacy:** 92% of phishing websites now utilize valid TLS/HTTPS certificates via free automated certificate authorities (Let's Encrypt), invalidating browser padlock indicators as a measure of safety.

## Sophisticated Evasion Techniques
1. **Dynamic Anti-Crawler Cloaking:** Phishing pages detect IP ranges belonging to search engine bots, security crawlers, and automated scanners, serving benign 404 pages or Wikipedia redirects while serving weaponized forms only to real mobile/desktop user agents.
2. **CAPTCHA-Gated Phishing:** Attackers place Cloudflare or Turnstile style CAPTCHAs in front of phishing forms to prevent automated headless browser scrapers from reaching and analyzing the login form.

## Countermeasure Engineering
Automated scanners must simulate realistic browser profiles and evaluate behavioral cues rather than relying on SSL validity.

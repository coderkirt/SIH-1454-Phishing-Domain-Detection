---
id: report-crowdstrike-2025
title: CrowdStrike Global Threat Report — Identity Exploitation & Vishing
category: threat_report
source: CrowdStrike Intelligence (2025 Edition)
source_url: https://www.crowdstrike.com/global-threat-report/
last_verified: 2026-10-11
language: en
region: global
channels: [voice, email, web]
brands: [microsoft, google, apple]
threat_tags: [credential_pressure, authority_impersonation, brand_impersonation]
mitre: [T1566.004, T1566.002, T1078]
severity: high
published_at: 2025-02-28
publisher: CrowdStrike Intelligence
report_url: https://www.crowdstrike.com/global-threat-report/
edition: 2025 Edition
key_stats: ['75% of attacks were malware-free (hands-on-keyboard using valid credentials)', 'Vishing (voice phishing) targeting IT service desks surged by 160%', 'Breakout time dropped to a record low median of 62 minutes', 'Access brokers traded corporate credentials within 2 hours of phishing harvest']
top_targets: ['Corporate IT Service Desks', 'Identity Providers (Okta, Azure)', 'Technology & Healthcare']
top_ttps: ['T1566.004 Spearphishing Voice', 'T1078 Valid Accounts', 'T1556 Modify Authentication Process']
page_count: 84
summary: CrowdStrike Intelligence report detailing 75% malware-free attacks, targeted voice phishing (vishing) against IT helpdesks, and rapid 62-minute breakout times.
---

CrowdStrike Intelligence observed a fundamental shift from malware-centric exploitation to identity-centric abuse across 2024 and 2025.

## Identity Hijacking & Helpdesk Vishing
- **The Malware-Free Reality:** 75% of initial intrusions were completely malware-free, relying instead on legitimate credentials harvested via social engineering.
- **IT Helpdesk Impersonation:** Threat groups (such as Scattered Spider / SCATTERED SPIDER) make phone calls to internal IT helpdesks posing as employees requesting password and MFA device resets.

## Operational Velocity
- The median breakout time—the time taken by an adversary to move laterally from initial access to other systems—dropped to 62 minutes.

## Detection Requirements
Security operations must inspect out-of-band communication signals and correlate MFA reset events with network telemetry to identify impersonation attacks in progress.

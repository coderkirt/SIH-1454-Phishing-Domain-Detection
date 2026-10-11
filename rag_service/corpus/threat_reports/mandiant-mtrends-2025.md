---
id: report-mandiant-mtrends-2025
title: Mandiant M-Trends — Initial Access Vectors & Cloud Compromise
category: threat_report
source: Google Cloud Mandiant (2025 Edition)
source_url: https://www.mandiant.com/resources/reports/m-trends
last_verified: 2026-10-11
language: en
region: global
channels: [email, web]
brands: [microsoft, google]
threat_tags: [credential_pressure, brand_impersonation]
mitre: [T1566.001, T1566.002, T1190]
severity: high
published_at: 2025-04-18
publisher: Google Cloud Mandiant
report_url: https://www.mandiant.com/resources/reports/m-trends
edition: 2025 Edition
key_stats: ['Global median dwell time remained at 10 days', 'Phishing represented 17% of all investigated initial infection vectors', 'Cloud session token reuse represented 28% of post-compromise activity']
top_targets: ['Financial Services', 'High Tech & Software', 'Government']
top_ttps: ['T1566.002 Spearphishing Link', 'T1190 Exploit Public-Facing Application']
page_count: 72
summary: Mandiant M-Trends 2025 analysis of incident response investigations, initial infection vectors, cloud token theft, and dwell time dynamics.
---

Mandiant's M-Trends report compiles empirical data from thousands of frontline incident response investigations conducted worldwide.

## Initial Compromise Analysis
- **Vector Distribution:** Phishing continues to hold a position among the top three initial infection vectors alongside vulnerability exploitation.
- **Dwell Time:** The global median dwell time—the duration from initial compromise to detection—held steady at 10 days.

## Cloud Credential Abuse
Attackers frequently use stolen web session tokens to bypass IP and device health checks by utilizing VPNs located in the same geographic region as the victim.

## Defensive Posture
Endpoint detection systems must monitor browser processes spawning anomalous scripts and enforce token lifetime limits.

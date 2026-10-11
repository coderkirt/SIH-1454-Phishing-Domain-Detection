---
id: report-verizon-dbir-2025
title: Verizon Data Breach Investigations Report (DBIR) — Social Engineering
category: threat_report
source: Verizon Threat Research Advisory Center (VTRAC) (2025 Edition)
source_url: https://www.verizon.com/business/resources/reports/dbir/
last_verified: 2026-10-11
language: en
region: global
channels: [email, sms, voice, web]
brands: [microsoft, google]
threat_tags: [credential_pressure, financial_pressure, urgency_detected]
mitre: [T1566.001, T1566.002, T1598]
severity: critical
published_at: 2025-05-01
publisher: Verizon Threat Research Advisory Center (VTRAC)
report_url: https://www.verizon.com/business/resources/reports/dbir/
edition: 2025 Edition
key_stats: ['68% of all breaches involved a non-malicious human element', 'Phishing was the initial access vector in 34% of social engineering breaches', 'Median time for a user to click on a phishing link was 21 seconds', 'Pretexting incidents increased for the fourth consecutive year, accounting for 25% of social engineering']
top_targets: ['Enterprise Employees', 'Finance & Accounting Departments', 'HR / Recruiting Personnel']
top_ttps: ['T1566.002 Phishing Link', 'T1566.001 Attachment', 'T1598.002 Phishing for Information']
page_count: 108
summary: Verizon DBIR 2025 analysis showing human-element involvement in 68% of breaches, median click times under 21 seconds, and surging pretexting and BEC operations.
---

The 2025 Verizon Data Breach Investigations Report (DBIR) analyzed 30,458 security incidents and 10,626 confirmed data breaches worldwide.

## Primary Attack Metrics & Discovery
- **Human Factor:** 68% of all analyzed breaches involved a human element (phishing, error, misuse, or stolen credentials).
- **Time-to-Click Metric:** The median time from email delivery to link click was measured at just 21 seconds, with credential submission occurring at a median of 28 seconds.
- **Pretexting vs Phishing:** Pretexting accounted for 25% of social engineering incidents, primarily manifesting as Business Email Compromise (BEC) and payroll diversion.

## Compromised Asset Breakdown
- Credentials remain the single most coveted asset, present in 77% of basic web application attacks.
- Internal data and personal identifiable information (PII) constituted the remainder of exfiltrated data.

## Recommendations for Detection Pipelines
Organizations must implement automated inbound scanning that correlates sender authenticity (SPF/DKIM/DMARC) with natural language urgency indicators to flag suspicious lures prior to user delivery.

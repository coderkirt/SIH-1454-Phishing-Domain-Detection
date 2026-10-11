---
id: report-uidai-threat-advisory-2025
title: UIDAI Technical Advisory — Cloned Aadhaar Portals & Biometric Scams
category: threat_report
source: Unique Identification Authority of India (UIDAI) (2025 Security Circular)
source_url: https://uidai.gov.in/en/ecosystem/authentication-ecosystem/security-guidelines.html
last_verified: 2026-10-11
language: en
region: india
channels: [web, sms]
brands: [uidai]
threat_tags: [brand_impersonation, authority_impersonation, credential_pressure]
mitre: [T1566.002, T1598.002]
severity: high
published_at: 2025-01-20
publisher: Unique Identification Authority of India (UIDAI)
report_url: https://uidai.gov.in/en/ecosystem/authentication-ecosystem/security-guidelines.html
edition: 2025 Security Circular
key_stats: ['Blocked over 850 fraudulent domain names mimicking uidai.gov.in', 'Identified fake mobile apps advertising offline Aadhaar plastic card printing', 'Biometric locking adoption reached over 18 million citizen accounts']
top_targets: ['Aadhaar Cardholders', 'CSC Rural Center Operators']
top_ttps: ['T1566.002 Phishing Link', 'T1598.002 Phishing for Information']
page_count: 16
summary: UIDAI technical advisory documenting 850+ blocked lookalike domains, plastic card printing lures, and biometric lock security controls.
---

UIDAI issued this technical guidance detailing fraud campaigns that exploit citizen trust in the national Aadhaar identity system.

## Deceptive Lookalike Portals
- Threat actors register commercial domains like `eaadhaar-download.top` and `uidai-update.org` that mimic the myAadhaar portal.
- These sites collect citizen full names, dates of birth, 12-digit Aadhaar numbers, and OTPs under the guise of free plastic smart card delivery.

## Official Domain Architecture
All authentic Aadhaar services reside strictly under the `.gov.in` domain hierarchy (`uidai.gov.in`, `myaadhaar.uidai.gov.in`).

## Recommended Safeguards
Citizens are encouraged to use the **Biometric Lock** feature in the mAadhaar app to prevent unauthorized authentication attempts.

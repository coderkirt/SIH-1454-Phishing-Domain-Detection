---
id: report-cert-in-banking-apk-2025
title: CERT-In Advisory — Android Banking Trojans & Smishing APK Scams
category: threat_report
source: CERT-In Technical Advisory (Advisory CI-2025-0018)
source_url: https://www.cert-in.org.in/advisories/CI-2025-0018.pdf
last_verified: 2026-10-11
language: en
region: india
channels: [sms, social, app]
brands: [sbi, hdfc, icici, axis, paytm]
threat_tags: [dangerous_executable, credential_pressure, financial_pressure]
mitre: [T1476, T1418, T1437]
severity: critical
published_at: 2025-02-10
publisher: CERT-In Technical Advisory
report_url: https://www.cert-in.org.in/advisories/CI-2025-0018.pdf
edition: Advisory CI-2025-0018
key_stats: ['Over 120 unique malicious APK package variants targeting Indian banks identified', '98% of trojanized APKs abused Android Accessibility Services to read OTPs', 'Average financial loss per compromised victim was Rs 1.45 lakh']
top_targets: ['Android Mobile Banking Users in India', 'Senior Citizens']
top_ttps: ['T1476 Sideloading', 'T1418 Accessibility Abuse', 'T1437 SMS Interception']
page_count: 14
summary: CERT-In technical advisory documenting Android banking trojans disguised as KYC update tools that abuse Accessibility Services to intercept 2FA OTPs.
---

CERT-In issued this high-severity advisory documenting the proliferation of Android banking trojans targeting Indian retail banking customers.

## Attack Lifecycle
1. The victim receives an SMS alleging their bank account will be closed due to expired KYC details, with a link to download an APK (e.g., `SBI_Rewards.apk` or `HDFC_KYC.apk`).
2. Upon installation, the malware prompts the user to grant Android **Accessibility Permissions**.
3. With Accessibility enabled, the trojan monitors active apps, overlays fake login screens over legitimate banking apps, intercepts incoming SMS OTPs, and forwards credentials to an attacker-controlled Command and Control (C2) server.

## Recommended Safeguards
- Strictly forbid side-loading applications from unknown sources (`Settings -> Install unknown apps -> Don't allow`).
- Banking institutions must enforce app attestation (Google Play Protect Integrity API) before allowing netbanking logins.

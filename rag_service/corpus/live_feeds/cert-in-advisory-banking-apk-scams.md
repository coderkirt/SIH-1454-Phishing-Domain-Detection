---
id: cert-in-advisory-banking-apk-scams
title: CERT-In Advisory: Android Banking Trojan and APK Phishing Waves
category: threat_report
source: CERT-In Security Advisories
source_url: https://www.cert-in.org.in/
last_verified: 2026-10-11
language: en
region: global
channels: [sms, social, app]
brands: [sbi, incometax]
threat_tags: [fear_tactics, credential_pressure, financial_pressure, coercion]
mitre: [T1566.002, T1566]
fetched_at: 2026-10-11T08:44:22Z
source_hash: 31ffe8178ae71b0c778e58f19bb0f6d0af3609d4847722f490abacf584cb75e0
license: Government Open Data License - India (GODL)
version: 1
summary: CERT-In advisory alerting citizens to fake electricity disconnection messages distributing credential-stealing Android APKs.
---

## CERT-In Advisory: Surge in Android Banking Trojans and Malicious APK Phishing

CERT-In has observed an aggressive wave of mobile phishing campaigns targeting Indian banking customers.
Attackers send SMS and WhatsApp messages claiming electricity disconnection, PAN card deactivation,
or pending income tax refunds, directing victims to install malicious APK applications.

## Attack Methodology
- SMS alerts with headers mimicking utilities (e.g., POWER, ELECT, BIHAR-DISCOM) asserting power cutoff by 9:30 PM.
- Senders distribute short links resolving to cloud-hosted APK downloaders named `e-bill_update.apk` or `sbi_rewards.apk`.
- Once installed, the malicious application requests Accessibility and SMS permissions to intercept OTPs.

## Indicators and Red Flags
- Demands to download application files from outside Google Play Store or Apple App Store.
- Unsolicited requests for mobile screen sharing (AnyDesk, TeamViewer QuickSupport).
- Urgency messaging threatening immediate loss of essential utilities or banking services.

## Recommended User Protection Steps
- Never download Android application packages (APKs) distributed via messaging apps or SMS links.
- Treat any message urging installation of remote access applications as high-probability fraud.
- In case of unauthorized debits, immediately dial national cybercrime helpline 1930 and notify the bank.

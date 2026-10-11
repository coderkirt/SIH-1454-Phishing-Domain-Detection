---
id: report-npci-upi-fraud-2025
title: NPCI Security Advisory — UPI Payment Fraud & Collect Request Exploitation
category: threat_report
source: National Payments Corporation of India (NPCI) (2025 Advisory)
source_url: https://www.npci.org.in/what-we-do/upi/circulars
last_verified: 2026-10-11
language: en
region: india
channels: [sms, social, app]
brands: [phonepe, paytm]
threat_tags: [financial_pressure, greed_bait, urgency_detected]
mitre: [T1566.003, T1598.003]
severity: high
published_at: 2025-04-12
publisher: National Payments Corporation of India (NPCI)
report_url: https://www.npci.org.in/what-we-do/upi/circulars
edition: 2025 Advisory
key_stats: ['UPI processed over 13.5 billion transactions monthly with 99.98% system uptime', 'Collect Request scams accounted for 41% of reported consumer UPI disputes', 'Fake cashback scratch card schemes represented 28% of fraud complaints']
top_targets: ['Marketplace Sellers (OLX, Quikr)', 'Social Media Users', 'E-Commerce Buyers']
top_ttps: ['T1566.003 Service Phishing', 'T1598 Social Engineering']
page_count: 22
summary: NPCI circular clarifying that UPI PIN entry is strictly required to DEBIT money, detailing collect request fraud vectors and scratch card scams.
---

The National Payments Corporation of India (NPCI) issued this advisory to all Member Banks and UPI Third-Party Application Providers (TPAPs).

## Critical Protocol Rules
- **Core Principle:** A user **NEVER** needs to enter their UPI PIN to receive money into their account.
- **Collect Request Exploitation:** Attackers posing as prospective buyers send a collect request instead of a transfer, deceiving victims into entering their PIN under the pretense of 'authorizing receipt'.

## Mandated Safety Enhancements
1. UPI applications must clearly display a high-contrast warning whenever a user is about to pay an unlisted payee: **'You are transferring money OUT of your account'**.
2. Third-party apps must prohibit any link that attempts to auto-trigger a collect request with pre-filled amounts.

---
id: brand-paytm
title: Paytm Brand Security & Wallet Fraud Defense
category: brand_guidance
source: Paytm Security Center & RBI Directives
source_url: https://paytm.com
last_verified: 2026-10-11
language: en
region: india
channels: [sms, social, web]
brands: [paytm]
threat_tags: [brand_impersonation, financial_pressure, urgency_detected, credential_pressure]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [paytm.com, paytmbank.com]
subdomain_rules: [*.paytm.com, *.paytmbank.com] 
logo_phash: 6f7a8b9c0d1e2536
phishing_patterns: [paytm-kyc-unblock, paytm-wallet-cashback, paytm-fastag-recharge]
never_does: ['Never asks customers to install QuickSupport or AnyDesk for KYC completion', 'Never sends cashback links requiring entry of UPI PIN to receive money']
contact_channels: [1930, cybersecurity@paytm.com]
regulatory_notes: RBI Master Direction on Prepaid Payment Instruments
summary: Security guidance for Paytm users. Outlines wallet impersonation vectors, remote access scams, and official payment infrastructure.
---

Paytm is one of India's leading digital payments applications, frequently targeted by wallet freezing scams and fake cashback offers.

## Official Endpoints
- Official consumer website: `paytm.com`.
- Payments Bank infrastructure: `paytmbank.com`.

## Common Scam Vectors
- Remote Access KYC Scams: Callers pretending to be Paytm representatives asking victims to download AnyDesk or TeamViewer QuickSupport to 'complete biometric verification'.
- Fake Cashback Lures: Scratch cards and reward links hosted on `.top` or `.xyz` domains promising thousands of rupees in instant wallet credits.

## Security Rules
- Customers never need to enter a UPI PIN or password to receive funds into their Paytm wallet or linked bank account.
- Paytm employees never conduct video KYC via third-party video apps or WhatsApp calls.

---
id: brand-irctc
title: IRCTC Railway Ticketing & Brand Protection
category: brand_guidance
source: IRCTC Official Security Notice & CRIS Guidelines
source_url: https://www.irctc.co.in
last_verified: 2026-10-11
language: en
region: india
channels: [web, sms, social]
brands: [irctc]
threat_tags: [brand_impersonation, credential_pressure, financial_pressure]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [irctc.co.in, irctctourism.com]
subdomain_rules: [*.irctc.co.in] 
logo_phash: 8b9c0d1e2f3a4758
phishing_patterns: [irctc-tatkal-booking, irctc-ticket-refund, irctc-agent-portal]
never_does: ['Never distributes Tatkal booking apps via third-party APK links on WhatsApp', 'Never asks for debit card CVV or OTP to process canceled ticket refunds']
contact_channels: [1930, tickets@irctc.co.in]
regulatory_notes: Indian Railways & CERT-In E-Ticketing Security Framework
summary: Brand protection guide for IRCTC (Indian Railway Catering and Tourism Corporation). Covers Tatkal booking software scams and ticket refund phishing.
---

IRCTC is India's national railway ticketing portal, handling millions of daily reservations. Fraudsters exploit Tatkal ticket demand and refund delays.

## Official Infrastructure
- Web reservations are hosted exclusively on `irctc.co.in`.
- Tourism and hospitality services reside on `irctctourism.com`.

## High-Volume Threat Scenarios
- Malicious Android APKs: Fraudsters promote fake apps promising guaranteed Tatkal booking or automated ticket booking bots.
- Fake Refund Portals: Messages informing travelers of canceled train refunds that link to credential-harvesting forms.

## Security Rules
- IRCTC never asks for netbanking credentials or debit card PINs to issue refunds.
- Official train bookings must only be executed through `irctc.co.in` or the official IRCTC Rail Connect app.

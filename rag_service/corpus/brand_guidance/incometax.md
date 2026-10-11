---
id: brand-incometax
title: Income Tax Department of India (e-Filing) Brand Guidance
category: brand_guidance
source: Income Tax Department Public Advisory & CERT-In
source_url: https://incometax.gov.in
last_verified: 2026-10-11
language: en
region: india
channels: [email, sms, web]
brands: [incometax]
threat_tags: [brand_impersonation, authority_impersonation, financial_pressure, credential_pressure]
mitre: [T1566.002, T1598.002]
severity: critical
official_domains: [incometax.gov.in, efiling.incometax.gov.in]
subdomain_rules: [*.incometax.gov.in] 
logo_phash: 4b5c6d7e8f9a0d1e
phishing_patterns: [incometax-refund-approved, it-refund-portal, pan-card-tax-update]
never_does: ['Never sends emails promising instant tax refunds upon submitting credit card details', 'Never communicates official tax matters from non-governmental domain extensions']
contact_channels: [1930, incident@cert-in.org.in]
regulatory_notes: Central Board of Direct Taxes (CBDT) Guidelines & Information Technology Act 2000
summary: Brand security reference for the Income Tax Department of India. Outlines refund approval phishing lures, legitimate e-Filing architecture, and verification rules.
---

The Income Tax Department of India is frequently impersonated during tax filing and refund disbursement cycles.

## Official Web Infrastructure
- Official e-Filing portal: `incometax.gov.in` and `efiling.incometax.gov.in`.
- Legitimate communications carry headers like `ITDEPT` or `DITGOV`.

## Attack Signatures
- Refund Approval Lure: 'A tax refund of Rs 15,490 has been approved. Enter your bank account and debit card details here to receive immediate credit'.
- Threat of Penalty: Demands to settle tax arrears immediately via lookalike payment gateways to avoid asset seizure.

## Security Rules
- Income Tax Department refunds are credited directly into pre-validated bank accounts; taxpayers are never asked for card PINs or CVVs.
- The department never communicates from generic free email providers like Gmail or Yahoo.

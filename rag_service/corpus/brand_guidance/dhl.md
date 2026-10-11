---
id: brand-dhl
title: DHL Express Brand Security & Shipment Fraud Guidance
category: brand_guidance
source: DHL Security Center Global Guidelines
source_url: https://www.dhl.com
last_verified: 2026-10-11
language: en
region: global
channels: [email, sms, web]
brands: [dhl]
threat_tags: [brand_impersonation, financial_pressure, urgency_detected]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [dhl.com, mydhl.express.dhl, express.dhl]
subdomain_rules: [*.dhl.com, *.dhl] 
logo_phash: 6d7e8f9a0b1c2f30
phishing_patterns: [dhl-tracking-portal, dhl-customs-clearance, dhl-package-pending]
never_does: ['Never sends attachments asking recipients to enter shipment tracking passwords', 'Never requests bank account login credentials to schedule re-delivery']
contact_channels: [phishing-dpdhl@dhl.com]
regulatory_notes: Deutsche Post DHL Corporate Security Directives
summary: Authoritative brand guidance for DHL Express shipping. Explains parcel clearance fee smishing, malicious shipment attachments, and genuine tracking domains.
---

DHL Express is a leading international logistics provider whose brand is exploited to distribute malware and harvest payment card data.

## Official Infrastructure
- Global tracking resides on `dhl.com` and branded gTLD subdomains such as `mydhl.express.dhl`.

## Attack Patterns
- Malicious Shipping Documents: Emails with subject lines like 'DHL Shipping Advice - Tracking Document' containing ISO files or password-protected archives with trojans.
- Customs Clearance Smishing: Texts urging recipients to pay small customs fees on fraudulent lookalike sites.

## Security Rules
- DHL never requests payment via cryptocurrency, Western Union, or prepaid cards.
- Official tracking requires only a tracking number and never demands netbanking passwords.

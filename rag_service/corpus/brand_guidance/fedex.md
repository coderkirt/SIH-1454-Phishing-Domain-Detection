---
id: brand-fedex
title: FedEx Brand Protection & Parcel Delivery Scams
category: brand_guidance
source: FedEx Customer Protection Center
source_url: https://www.fedex.com
last_verified: 2026-10-11
language: en
region: global
channels: [sms, email, voice, web]
brands: [fedex]
threat_tags: [brand_impersonation, urgency_detected, fear_tactics, financial_pressure]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [fedex.com]
subdomain_rules: [*.fedex.com] 
logo_phash: 5c6d7e8f9a0b1e2f
phishing_patterns: [fedex-customs-fee, track-fedex-package, fedex-delivery-hold]
never_does: ['Never requires payment of package delivery fees via gift cards, UPI, or prepaid cards', 'Never threatens that police will arrest recipients unless customs clearance fee is paid via SMS link']
contact_channels: [abuse@fedex.com]
regulatory_notes: Universal Postal Union Fraud Prevention Guidelines
summary: Brand protection guide for FedEx courier logistics. Details parcel delivery smishing, narcotics parcel arrest threats, and authentic tracking endpoints.
---

FedEx is heavily targeted by both delivery fee smishing scams and high-severity 'Digital Arrest' impersonation campaigns.

## Official Infrastructure
- Tracking and logistics services are hosted on `fedex.com`.

## Threat Vectors
- Delivery Fee Smishing: Messages claiming a parcel is held at the sorting hub due to an incorrect address or unpaid fee of $1.99.
- Narcotics Parcel Coercion: Fraudsters calling victims claiming a FedEx parcel containing illegal contraband was intercepted in their name, demanding money transfers under threat of immediate arrest.

## Security Rules
- FedEx does not request personal identity documents or credit card numbers via unsolicited SMS.
- FedEx does not connect customers to 'police stations' over Skype or video calls.

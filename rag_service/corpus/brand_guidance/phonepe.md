---
id: brand-phonepe
title: PhonePe UPI & Wallet Security Protocol
category: brand_guidance
source: PhonePe Trust & Safety Advisory
source_url: https://www.phonepe.com
last_verified: 2026-10-11
language: en
region: india
channels: [sms, social, web]
brands: [phonepe]
threat_tags: [brand_impersonation, financial_pressure, urgency_detected]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [phonepe.com]
subdomain_rules: [*.phonepe.com] 
logo_phash: 7a8b9c0d1e2f3647
phishing_patterns: [phonepe-reward-scratch, phonepe-collect-bonus, phonepe-kyc-update]
never_does: ['Never requires typing UPI PIN to receive money or cashback prizes', 'Never accepts customer support requests via unverified Telegram or WhatsApp numbers']
contact_channels: [1930, support.phonepe.com]
regulatory_notes: NPCI UPI Procedural Guidelines & RBI Security Directives
summary: Brand security protocol for PhonePe. Explains UPI collect request abuse, prize baiting, and verified digital payment protocols.
---

PhonePe is a premier Indian payment app where fraudsters exploit misconceptions surrounding the UPI collect request mechanism.

## Official Domain
- Official corporate and consumer portal: `phonepe.com`.
- Transactions take place strictly inside the official PhonePe mobile app.

## Attack Patterns
- Collect Request Exploitation: Scammers on OLX or social media promise to pay for an item, but initiate a 'Collect Request' instead. They convince the victim that entering their UPI PIN is required to 'receive' money.
- Fraudulent Reward Links: Social media links displaying animated scratch cards showing prize wins that redirect to deceptive payment gateways.

## Security Rules
- UPI PIN is strictly used to DEBIT money from an account, never to CREDIT or RECEIVE money.
- PhonePe customer care operates exclusively through the help section of the official app.

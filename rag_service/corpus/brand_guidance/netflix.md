---
id: brand-netflix
title: Netflix Subscription Security & Billing Impersonation
category: brand_guidance
source: Netflix Help Center Security Advisory
source_url: https://www.netflix.com
last_verified: 2026-10-11
language: en
region: global
channels: [email, sms, web]
brands: [netflix]
threat_tags: [brand_impersonation, financial_pressure, credential_pressure, urgency_detected]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [netflix.com]
subdomain_rules: [*.netflix.com] 
logo_phash: 2f3a4b5c6d7e8b9c
phishing_patterns: [netflix-account-onhold, update-netflix-payment, netflix-free-year]
never_does: ['Never sends SMS links asking for full 16-digit credit card number and CVV to clear account hold', 'Never asks users to pay for subscriptions through third-party vendors or wire transfers']
contact_channels: [phishing@netflix.com]
regulatory_notes: Payment Card Industry Data Security Standard (PCI DSS)
summary: Authoritative brand guidance for Netflix streaming services. Outlines subscription hold smishing lures and credit card harvesting clone pages.
---

Netflix is a frequent target of high-volume payment phishing campaigns targeting subscriber payment details.

## Official Web Endpoints
- The streaming service and billing interface reside exclusively on `netflix.com`.

## Common Attack Vectors
- Payment Decline SMS: Smishing texts stating: 'Your Netflix subscription could not be renewed. Update billing within 24 hours to avoid suspension: netflix-payment.info'.
- Lookalike Account Update Pages: Pages mimicking the Netflix sign-in portal that sequentially request email, password, credit card number, expiration date, CVV, and billing address.

## Security Rules
- Netflix never requests bank account details or credit card information via text message or email.
- Subscriptions are managed directly by signing into `netflix.com`.

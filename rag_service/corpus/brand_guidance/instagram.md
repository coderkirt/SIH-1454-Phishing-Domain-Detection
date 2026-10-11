---
id: brand-instagram
title: Instagram Account Protection & Brand Impersonation
category: brand_guidance
source: Instagram Safety Center Guidelines
source_url: https://www.instagram.com
last_verified: 2026-10-11
language: en
region: global
channels: [social, web]
brands: [instagram]
threat_tags: [brand_impersonation, credential_pressure, fear_tactics]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [instagram.com]
subdomain_rules: [*.instagram.com] 
logo_phash: 0d1e2f3a4b5c697a
phishing_patterns: [instagram-copyright-infringement, ig-blue-badge-verify, instagram-appeal]
never_does: ['Never sends Direct Messages (DMs) demanding password entry to contest a copyright violation', 'Never charges fees for blue verified badge applications via third-party links']
contact_channels: [phish@instagram.com]
regulatory_notes: Meta Safety & Integrity Directives
summary: Brand protection guidelines for Instagram accounts. Outlines copyright infringement DM lures, verification badge baiting, and credential harvesting patterns.
---

Instagram accounts are targeted by phishing campaigns aimed at taking over profiles for crypto promotion and follower extortion.

## Official Domain
- The legitimate service runs strictly on `instagram.com`.

## Common Scam Vectors
- Fake Copyright Infringement Notices: Direct messages or emails claiming a post violated intellectual property rights and threatening account deletion within 24 hours.
- Verified Badge Scam: Deceptive forms offering free blue verification checkmarks in exchange for account credentials and phone numbers.

## Security Rules
- Instagram never communicates official copyright enforcement via Direct Message.
- Official emails from Instagram can always be confirmed inside the app under Settings -> Security -> Emails from Instagram.

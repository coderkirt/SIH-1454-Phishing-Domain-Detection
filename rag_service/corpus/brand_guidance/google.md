---
id: brand-google
title: Google & Gmail Authentication Security Guidance
category: brand_guidance
source: Google Safety Center & Account Security Guidelines
source_url: https://safety.google
last_verified: 2026-10-11
language: en
region: global
channels: [email, web]
brands: [google]
threat_tags: [brand_impersonation, credential_pressure, urgency_detected]
mitre: [T1566.002, T1598.002]
severity: critical
official_domains: [google.com, accounts.google.com, myaccount.google.com]
subdomain_rules: [*.google.com] 
logo_phash: 1a2b3c4d5e6f7081
phishing_patterns: [accounts-google-verify, google-storage-full, g00gle-login.com]
never_does: ['Never sends emails warning of account deletion in 2 hours unless password is typed', 'Never asks users to verify Google prompt numbers on third-party sites']
contact_channels: [report-phishing@google.com]
regulatory_notes: NIST SP 800-63 Digital Identity Guidelines
summary: Comprehensive security guidance for Google and Gmail accounts. Outlines legitimate single-sign-on (SSO) endpoints and credential harvesting patterns.
---

Google account credentials provide access to email, drive storage, and linked authentication across the web, making them a primary credential harvesting target.

## Official Authentication Endpoints
- Authentic Google authentication is exclusively served from `accounts.google.com`.
- Security settings reside on `myaccount.google.com`.

## Common Phishing Signatures
- Storage Full Alarms: Emails warning that Gmail or Google Drive has exceeded 100% capacity and will reject new emails unless upgraded via an external link.
- Security Alerts: Fake notifications alleging unauthorized sign-ins from unrecognized locations, directing targets to credential-stealing reverse proxies (AiTM).

## Security Rules
- Google never asks users to confirm passwords by replying to an email.
- Legitimate security alerts appear directly inside the user's Google account notification drawer.

---
id: brand-microsoft
title: Microsoft 365 & Office Security Architecture
category: brand_guidance
source: Microsoft Digital Defense Report & Security Guidance
source_url: https://www.microsoft.com
last_verified: 2026-10-11
language: en
region: global
channels: [email, web]
brands: [microsoft]
threat_tags: [brand_impersonation, credential_pressure, urgency_detected, authority_impersonation]
mitre: [T1566.002, T1598.002]
severity: critical
official_domains: [microsoft.com, login.microsoftonline.com, office.com, live.com]
subdomain_rules: [*.microsoft.com, *.microsoftonline.com, *.office.com] 
logo_phash: 4d5e6f7a8b9c0314
phishing_patterns: [microsoft-onedrive-document, office365-password-expiry, micros0ft-auth]
never_does: ['Never threatens permanent mailbox lockout within 1 hour to coerce credential entry', 'Never uses consumer email domains (e.g., gmail/yahoo) for enterprise security notices']
contact_channels: [phish@office365.microsoft.com]
regulatory_notes: CISA Cloud Security Directives & NIST SP 800-63
summary: Enterprise brand protection reference for Microsoft 365 and Azure AD. Details adversary-in-the-middle (AiTM) proxy tactics and credential harvesting lures.
---

Microsoft 365 and Azure AD authentication portals represent the most frequently impersonated enterprise platforms globally.

## Official Authentication Architecture
- Enterprise identity and single sign-on is centralized on `login.microsoftonline.com`.
- Portal interfaces reside on `office.com` and `microsoft.com`.

## Common Attack Techniques
- AiTM Reverse Proxies: Attackers deploy proxies (Evilginx) on lookalike domains to intercept enterprise session cookies and bypass multi-factor authentication.
- Voicemail & OneDrive Notifications: Emails alerting users to a pending voice message or secure shared document that links to a fake Microsoft login screen.

## Security Rules
- Microsoft never forces password resets through third-party forms hosted on consumer web builders.
- Microsoft cloud services mandate FIDO2 / Passkey authentication to effectively neutralize AiTM phishing.

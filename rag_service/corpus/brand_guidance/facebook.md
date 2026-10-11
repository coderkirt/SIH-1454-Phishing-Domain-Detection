---
id: brand-facebook
title: Facebook / Meta Security Guidance & Page Shield
category: brand_guidance
source: Meta Security Center & Threat Intelligence Reports
source_url: https://www.facebook.com
last_verified: 2026-10-11
language: en
region: global
channels: [email, social, web]
brands: [facebook]
threat_tags: [brand_impersonation, fear_tactics, credential_pressure]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [facebook.com, fb.com, meta.com]
subdomain_rules: [*.facebook.com, *.meta.com] 
logo_phash: 1e2f3a4b5c6d7a8b
phishing_patterns: [meta-business-suite-suspend, facebook-page-violation, fb-support-chat]
never_does: ['Never threatens page deletion within 24 hours without an official appeal option inside Meta Business Suite', 'Never asks business managers to download password-protected ZIP files to view copyright claims']
contact_channels: [phish@fb.com]
regulatory_notes: Meta Business Security Guidelines
summary: Security architecture and brand protection reference for Facebook and Meta Business Suite. Details business page takeover campaigns and fake community violation notices.
---

Facebook pages and Meta Business accounts are prime targets for infostealer malware campaigns and credential harvesting.

## Official Domains
- Consumer platform: `facebook.com` and `fb.com`.
- Corporate identity: `meta.com`.

## Attack Methodologies
- Meta Business Suspension Warnings: Phishing emails claiming a business page will be permanently unpublished due to copyright violations, directing admins to an external phishing link.
- Fake Ad Support Chats: Malicious messages posing as Meta Support providing links that execute browser infostealers.

## Security Rules
- Meta never requires admins to download software or browser extensions to maintain business page verification.
- Authentic account alerts appear within Meta Business Suite, not as random Messenger pings.

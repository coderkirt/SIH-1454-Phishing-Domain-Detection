---
id: brand-youtube
title: YouTube Creator Security & Phishing Guidance
category: brand_guidance
source: YouTube Creator Safety Center
source_url: https://www.youtube.com
last_verified: 2026-10-11
language: en
region: global
channels: [email, web]
brands: [youtube]
threat_tags: [brand_impersonation, credential_pressure, fear_tactics]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [youtube.com, studio.youtube.com, youtu.be]
subdomain_rules: [*.youtube.com] 
logo_phash: 2b3c4d5e6f7a8192
phishing_patterns: [youtube-copyright-strike, creator-monetization-review, yt-partner-verify]
never_does: ['Never sends sponsorship contract archives containing password-protected .exe or .scr payloads', 'Never asks creators to surrender session cookies or 2FA codes']
contact_channels: [support-creator@youtube.com]
regulatory_notes: Google & YouTube Community Security Guidelines
summary: Creator protection guide for YouTube. Details channel hijacking campaigns, fake copyright strikes, and fraudulent sponsorship software distribution.
---

YouTube channels are prime targets for hijacking campaigns aimed at promoting cryptocurrency giveaway scams.

## Official Endpoints
- Video hosting and viewing is located on `youtube.com`.
- Creator management functions exclusively on `studio.youtube.com`.

## Attack Mechanisms
- Bogus Sponsorship Offers: Scammers posing as game publishers or VPN providers offering thousands of dollars, attaching malware (infostealers like RedLine) inside password-protected ZIP archives.
- Copyright Claim Phishing: Notices threatening channel termination within 48 hours unless a disputed link is accessed.

## Security Rules
- YouTube never delivers official copyright notifications from non-Google email domains.
- YouTube never requests creator account credentials to review monetization status.

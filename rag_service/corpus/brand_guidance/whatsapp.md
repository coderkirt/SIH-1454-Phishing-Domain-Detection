---
id: brand-whatsapp
title: WhatsApp & Meta Messaging Anti-Phishing Rules
category: brand_guidance
source: WhatsApp Security Center & CERT-In Directives
source_url: https://www.whatsapp.com
last_verified: 2026-10-11
language: en
region: global
channels: [social, sms, web]
brands: [whatsapp]
threat_tags: [brand_impersonation, emotional_manipulation, credential_pressure]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [whatsapp.com, web.whatsapp.com]
subdomain_rules: [*.whatsapp.com] 
logo_phash: 3b9c71a4f0d82e56
phishing_patterns: [web-whatsapp-sync, wa-web-auth, whatsapp-gold-download]
never_does: ['Never sends messages asking users to share their 6-digit SMS registration code', "Never sells premium 'WhatsApp Gold' subscriptions through external links"]
contact_channels: [support@whatsapp.com]
regulatory_notes: Meta Security Center & CERT-In Messaging Scam Guidelines
summary: Brand protection rules for WhatsApp. Details account takeover scams via registration codes, malicious QR synchronization, and family emergency impersonation.
---

WhatsApp is the world's leading messaging application and a frequent medium for account takeover and contact impersonation.

## Official Web Endpoints
- Corporate information: `whatsapp.com`.
- Web messaging portal: `web.whatsapp.com`.

## Attack Vectors
- 6-Digit Registration Code Theft: Attackers attempt to register the victim's phone number on a new device, then trick the victim into sharing the incoming verification SMS code.
- Quishing (QR Code Phishing): Malicious websites displaying cloned WhatsApp Web QR codes that connect the victim's session to an attacker's device.

## Security Rules
- WhatsApp never requests registration codes or two-step verification PINs through chat messages.
- Never scan unfamiliar QR codes using the Linked Devices menu in WhatsApp.

---
id: brand-apple
title: Apple ID & iCloud Anti-Phishing Guidance
category: brand_guidance
source: Apple Security & Privacy Whitepaper
source_url: https://www.apple.com
last_verified: 2026-10-11
language: en
region: global
channels: [email, sms, web]
brands: [apple]
threat_tags: [brand_impersonation, credential_pressure, urgency_detected]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [apple.com, icloud.com, appleid.apple.com]
subdomain_rules: [*.apple.com, *.icloud.com] 
logo_phash: 5e6f7a8b9c0d1425
phishing_patterns: [findmy-iphone-alert, icloud-storage-locked, appleid-verification]
never_does: ["Never sends SMS saying 'Your lost iPhone was found; log in here to view location' to third-party domains", 'Never asks for Apple ID password or two-factor code over unsolicited calls']
contact_channels: [reportphishing@apple.com]
regulatory_notes: Apple Platform Security Guidelines
summary: Brand security reference for Apple ID and iCloud. Explains Find My device lures, storage warnings, and genuine Apple infrastructure rules.
---

Apple credentials grant attackers control over mobile devices, personal backups, and iCloud photos.

## Official Authentication Endpoints
- Web authentication: `appleid.apple.com`.
- Cloud services and web interface: `icloud.com`.

## Attack Scenarios
- Lost Device Unlocking Scams: When an iPhone is stolen, thieves send automated SMS messages to the emergency contact claiming the device was located, driving victims to a lookalike iCloud login page to unlock Activation Lock.
- Fake App Store Invoices: Receipts for expensive monthly subscriptions intended to cause panic and trigger clicks on a cancellation link.

## Security Rules
- Apple never directs customers to enter credentials on non-Apple apex domains.
- Apple support never asks for device passcodes or verification codes over phone calls.

---
id: brand-whatsapp-family-emergency
title: WhatsApp and Messaging App Impersonation
category: brand_guidance
source: Meta security guidance + consumer advisories (synthesized)
source_url: https://www.meta.com/security/
last_verified: 2026-10-11
language: en
region: global
channels: [social, sms]
brands: [whatsapp]
threat_tags: [brand_impersonation, emotional_manipulation, secrecy, financial_pressure]
mitre: [T1566.003]
severity: high
official_domains: [whatsapp.com, web.whatsapp.com]
subdomain_rules: [*.whatsapp.com]
logo_phash: 3b9c71a4f0d82e56
phishing_patterns: [web-whatsapp-login, whatsapp-qr-sync, wa-verify]
never_does: ["Never messages users requesting payment or verification codes", "Never requires scanning unknown QR codes to avoid account deletion"]
contact_channels: [support@whatsapp.com]
regulatory_notes: Meta Security Center & CERT-In Messaging Scam Guidelines
summary: Scammers pose as family or friends on WhatsApp ("new phone, new number") requesting money, OTP forwarding, or link clicks, sometimes claiming the account will be hacked.
---

## How the scam works

The victim receives a message from an unknown number displaying a familiar
name/photo: "Hi, this is my new number, my old phone was lost." The
conversation builds rapport, then requests an urgent payment, a UPI transfer,
or "help" receiving a package or refund.

A second variant impersonates WhatsApp support itself: "Your account expires
today, send this code to continue" or "verify your account via this link."
Forwarding the six-digit registration code hands the attacker control of the
victim's WhatsApp account, which is then used to attack the victim's
contacts.

## Warning signs

- A "known" contact messaging from an unlisted number, especially with
  changed display details.
- Any request to forward a WhatsApp registration/verification code.
- Pressure and secrecy: "don't call, I'm in a meeting," "it's urgent."
- Payment requests to a new UPI handle unrelated to the contact.

## Recommended guidance

Verify through a saved number or a video call before transferring money.
WhatsApp will never ask for your registration code or send you to a link to
"keep your account." Report and block the sender; warn your contacts if your
account was taken.

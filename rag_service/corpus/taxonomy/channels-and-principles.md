---
id: taxonomy-channels-principles
title: Phishing Channels and Social-Engineering Principles
category: taxonomy
source: NIST + CISA guidance (synthesized)
source_url: https://www.nist.gov/itl/smallbusinesscyber/guidance-topic/phishing
last_verified: 2026-10-11
language: en
region: global
channels: [email, sms, voice, social, qr, web]
brands: []
threat_tags: [urgency_detected, fear_tactics, authority_impersonation, greed_bait, secrecy, emotional_manipulation, credential_pressure, financial_pressure, coercion, countdown]
mitre: [T1566, T1598]
summary: A channel taxonomy (phishing/smishing/vishing/quishing/BEC/spear/whaling) mapped to the psychological principles each leverages: authority, urgency, scarcity, fear, greed, and trust.
---

## Channel taxonomy

- **Phishing (email)**: mass or targeted fraudulent email; still the largest
  channel by volume.
- **Smishing (SMS)**: short messages with links; high click-through due to
  mobile constraints.
- **Vishing (voice)**: phone-based, including OTP theft and tech-support
  pretexts; T1566.004.
- **Quishing (QR)**: QR codes deliver the hidden link, defeating URL
  preview.
- **BEC / CEO fraud**: impersonation of executives or vendors to redirect
  payments; no malware needed.
- **Spear phishing**: targeted with victim-specific details.
- **Whaling**: targeting executives and finance staff specifically.

## Psychological principles and their message signals

- **Authority** — bank, government, or boss impersonation. Signal phrases:
  "security department," "cyber cell," "income tax notice."
- **Urgency and scarcity** — deadlines force fast decisions: "act now,"
  "expires in 10 minutes," countdown timers.
- **Fear** — threats of blockage, arrest, or account loss.
- **Greed** — prizes, refunds, and guaranteed returns.
- **Trust and social proof** — familiar names, logos, group chats, and fake
  testimonials.
- **Secrecy** — instructions not to tell anyone, defeating victim-side
  verification.

## How this taxonomy is used in retrieval

Each principle and channel maps to the threat-tag vocabulary used by the
detection pipeline, so a scan whose tags include `credential_pressure` and
`urgency_detected` can be routed to playbook documents covering those
principles, and to the channel-specific guidance for the delivery method
observed.

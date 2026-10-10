---
id: taxonomy-mitre-phishing
title: MITRE ATT&CK Phishing Techniques (T1566, T1598)
category: taxonomy
source: MITRE ATT&CK (paraphrased)
source_url: https://attack.mitre.org/techniques/T1566/
last_verified: 2026-10-11
language: en
region: global
channels: [email, sms, voice, social, web]
brands: []
threat_tags: [brand_impersonation, credential_pressure]
mitre: [T1566, T1566.001, T1566.002, T1566.003, T1566.004, T1598]
summary: ATT&CK organizes phishing as initial access (T1566) with attachment, link, service, and voice sub-techniques, plus T1598 for phishing performed only to gather information.
---

## T1566 — Phishing (Initial Access)

The adversary sends a message to trick a user into executing something that
grants access or execution. Sub-techniques:

- **T1566.001 Spearphishing Attachment**: a malicious file (document, archive,
  executable) delivered via email or message.
- **T1566.002 Spearphishing Link**: a link to a credential-harvest page or
  payload download. This is the dominant web-phishing pattern and maps
  directly to URL/domain analysis.
- **T1566.003 Spearphishing via Service**: delivery through social media,
  messaging apps, or collaboration tools rather than email — the channel
  behind many WhatsApp/UPI scams.
- **T1566.004 Spearphishing Voice (vishing)**: phone-based lures, including
  OTP theft and fake support calls.

## T1598 — Phishing for Information

Used when the goal is reconnaissance rather than execution: the adversary
sends messages to harvest credentials, personal details, or security
responses. It mirrors T1566's sub-technique structure (.001–.004). In real
campaigns the same infrastructure often serves both objectives.

## Mapping to detection signals

| Sub-technique | Typical observable signals |
|---|---|
| T1566.001 | Suspicious attachments, macros, archives, executables |
| T1566.002 | Lookalike domains, login forms, urgency copy, URL shorteners |
| T1566.003 | Unknown sender on messaging platform, payment requests |
| T1566.004 | Inbound call requesting OTP/credentials, screen-share apps |

ATT&CK content updates bi-annually; cite technique IDs and the ATT&CK
version used when generating explanations.

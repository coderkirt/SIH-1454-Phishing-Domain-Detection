---
id: cisa-advisory-aitm-phishing
title: CISA Advisory: Adversary-in-the-Middle (AiTM) Phishing Campaigns
category: threat_report
source: CISA Cybersecurity Advisories
source_url: https://www.cisa.gov/news-events/cybersecurity-advisories
last_verified: 2026-10-11
language: en
region: global
channels: [email, web]
brands: [microsoft, google]
threat_tags: [credential_pressure, urgency_detected, brand_impersonation]
mitre: [T1566.002, T1566]
fetched_at: 2026-10-11T08:44:22Z
source_hash: 97302531d68d3c608867828bfc4e7e92091ee718446bdcd99f810271c27d225d
license: U.S. Public Domain (17 U.S.C. § 105)
version: 1
summary: CISA advisory detailing modern AiTM phishing tactics designed to intercept session cookies, bypass MFA, and impersonate authentication services.
---

## CISA Advisory: Threat Actors Exploiting Phishing and Session Hijacking

Cyber actors continue to rely heavily on spearphishing emails and lookalike landing pages
as their primary method of initial compromise. Recent campaigns observe attackers deploying
adversary-in-the-middle (AiTM) phishing kits to intercept session cookies and bypass multi-factor
authentication mechanisms.

## Primary Threat Indicators
- Emails with urgent themes relating to IT password expiration, tax obligations, or invoices.
- Hyperlinks directing targets to reverse-proxy servers hosting spoofed corporate authentication pages.
- Requests for session verification codes and OTP tokens directly within the spoofed web interface.

## Technical Mitigation Recommendations
- Enforce FIDO2 / WebAuthn-based phishing-resistant MFA rather than SMS or push-based OTPs.
- Inspect outbound traffic for abnormal proxy connections and newly registered apex domains.
- Implement automated domain blocklists targeting newly observed malicious hosting infrastructure.
- Provide continuous user awareness training emphasizing verification through typed official addresses.

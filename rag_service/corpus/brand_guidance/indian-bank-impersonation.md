---
id: brand-bank-impersonation-india
title: Indian Bank Brand Impersonation (SBI/HDFC/ICICI/Axis)
category: brand_guidance
source: Bank public fraud advisories + RBI guidance (synthesized)
source_url: https://www.rbi.org.in/
last_verified: 2026-10-11
language: en
region: india
channels: [sms, email, web, social]
brands: [sbi, hdfc, icici, axis]
threat_tags: [brand_impersonation, authority_impersonation, credential_pressure, fear_tactics]
mitre: [T1566.002]
severity: high
official_domains: [onlinesbi.sbi, sbi.co.in, hdfcbank.com, icicibank.com, axisbank.com]
subdomain_rules: [*.sbi, *.hdfcbank.com, *.icicibank.com, *.axisbank.com]
logo_phash: a3f0c1b4892c5d1e
phishing_patterns: [onlinesbi-kyc, hdfc-netbanking-verify, icici-rewards, axis-card-update]
never_does: ["Never asks for netbanking password or ATM PIN over SMS", "Never requests remote desktop applications like AnyDesk or TeamViewer"]
contact_channels: [1930, report.phishing@sbi.co.in]
regulatory_notes: RBI Master Direction on Digital Payment Security Controls
summary: Phishing mimicking Indian banks via KYC-update lures, fake reward points, blocked-card warnings, and lookalike domains such as onlinesbi-login.example.
---

## Recurring lures

- "Your KYC is incomplete; account will be blocked" with a link to a fake
  net-banking login.
- "Reward points expire today — redeem now" leading to a card-details form.
- "Your card is blocked due to suspicious transaction; unblock here."
- Fake SMS sender IDs spoofing the bank's official header, paired with
  shortened links.

## Domain tells

Real net-banking hosts include `onlinesbi.sbi`, `sbi.co.in`, `hdfcbank.com`,
`icicibank.com`, `axisbank.com`. Phishing hosts prepend service words
(`secure`, `login`, `verify`, `netbanking`) to the brand, swap characters
(`hdfcbonus.example`), or hide the brand in a subdomain of an unrelated
domain. Any shortener hiding the final host is a warning sign.

## Behavioral rules for users

- Banks never ask for OTP, PIN, or full card number over SMS, email, or
  phone.
- Official apps and bookmarks should be used instead of message links.
- SMS sender IDs can be spoofed; the link target is the reliable signal.

## Analyst mapping

Bank-impersonation pages typically combine brand tokens with credential
forms and urgency copy. When a scan shows bank-brand tokens plus a
newly-registered domain or a suspicious TLD, treat credential harvesting as
the likely intent even before page content is fetched.

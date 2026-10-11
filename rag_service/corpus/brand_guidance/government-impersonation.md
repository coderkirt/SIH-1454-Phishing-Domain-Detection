---
id: brand-government-impersonation
title: Government Brand Misuse (Income Tax, UIDAI/Aadhaar, EPFO)
category: brand_guidance
source: CERT-In + departmental public advisories (synthesized)
source_url: https://cert-in.org.in/
last_verified: 2026-10-11
language: en
region: india
channels: [email, sms, social]
brands: [uidai, incometax]
threat_tags: [brand_impersonation, authority_impersonation, fear_tactics, financial_pressure]
mitre: [T1566.002, T1598.004]
severity: critical
official_domains: [uidai.gov.in, incometax.gov.in, epfindia.gov.in]
subdomain_rules: [*.gov.in]
logo_phash: 9f8e7d6c5b4a3120
phishing_patterns: [incometax-refund-claim, aadhaar-kyc-verify, epfo-claim-status]
never_does: ["Never sends refund approval links demanding bank card numbers", "Never threatens immediate police detention via SMS or WhatsApp"]
contact_channels: [1930, helpdesk@uidai.gov.in]
regulatory_notes: CERT-In Advisory on Government Department Impersonation Scams
summary: Fraudsters pose as the Income Tax Department, UIDAI, or EPFO claiming pending refunds, Aadhaar suspension, or KYC failure, driving victims to fake portals or paid "activation."
---

## Recurring lures

- "Income Tax Department: refund of ₹ pending — update bank details within
  48 hours" with a fake portal asking for PAN, bank, and card data.
- "Your Aadhaar is suspended/blocked due to misuse; verify at the linked
  portal" — often with a PDF crafted to look official.
- "EPFO claim rejected — confirm UAN and OTP here."
- Phone calls demanding Aadhaar biometric re-verification or payment to
  "reactivate" benefits.

## Ground rules for users and analysts

- UIDAI has repeatedly stated it never asks for Aadhaar details over phone,
  SMS, or email, and Aadhaar is never "suspended" for non-use.
- The Income Tax e-filing portal is a single official domain; refunds are
  credited without upfront payment, and the department does not demand
  payment via gift cards, UPI to individuals, or crypto.
- Government notices cite reference numbers you can verify on the official
  portal, not links sent by the notifier.

## Domain tells

`.gov.in` and `gov.in` domains are restricted; phishing uses `.com`, `.in`
lookalikes, or free hosting with official logos embedded. Presence of a
national emblem in an email does not verify the sender.

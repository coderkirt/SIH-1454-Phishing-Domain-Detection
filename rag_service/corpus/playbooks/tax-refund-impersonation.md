---
id: playbook-tax-refund-impersonation
title: Government Tax Refund and Rebate Phishing
category: playbook
source: Income Tax Department + IRS Consumer Alerts (synthesized)
source_url: https://incometax.gov.in/
last_verified: 2026-10-11
language: en
region: global
channels: [sms, email, web]
brands: [incometax]
threat_tags: [authority_impersonation, financial_pressure, credential_pressure, greed_bait]
mitre: [T1566.002]
severity: high
tactics: [tax_rebate_bait, credential_harvest, card_details_form, pan_kyc_theft]
iocs: [approved_refund_amount, submit_card_details, non_gov_tld, fake_refund_portal]
first_seen: 2024-03-01
summary: Phishing campaigns claiming an approved tax refund or rebate is waiting, directing victims to fake revenue portals that harvest credit card numbers, net-banking logins, and PAN credentials.
---

## How the scam works

During tax season or assessment periods, attackers distribute emails and SMS alerts claiming a substantial
tax refund (e.g. Rs 15,490 or $480.00) has been calculated and approved for the recipient's bank account.
However, the message asserts that the refund could not be deposited due to incorrect or missing banking details.

The message directs the victim to click a link to a fraudulent lookalike portal copying the national revenue
service (e.g., `incometax-refund-update.com` or `irs-gov-portal.net`). To "verify eligibility and process payment",
the victim is prompted to enter their full banking username, password, debit card number, CVV, and OTP.

## Common message patterns

- "Income Tax Refund of Rs 15,490 has been approved. Please verify your bank account number ending in XXXX.
   If this is incorrect, click here to update your details immediately."
- "Notice: Your annual tax rebate is awaiting release. Claim within 48 hours to avoid forfeiture."

The lure combines legitimate government authority, greed (unexpected windfall), and urgency to prompt quick action.

## Warning signs for analysts

- Links pointing to commercial TLDs (`.top`, `.xyz`, `.com`, `.info`) rather than official government domains (`.gov.in`, `.gov`).
- The portal asks for sensitive card verification numbers (CVV) or ATM PINs, which tax authorities never require for refund credits.
- Generic greeting without the taxpayer's masked PAN or full name.
- Short deadlines threatening that the refund will lapse if not claimed within hours.

## Recommended user guidance

Tax refunds are processed automatically by government revenue portals directly into validated bank accounts
without requiring taxpayers to click email links or provide card CVVs. Access the official tax portal directly
by typing the known government URL (`incometax.gov.in`) into your browser and check the refund status tab.

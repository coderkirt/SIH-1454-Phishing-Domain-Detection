---
id: brand-paypal-impersonation
title: PayPal Impersonation Patterns
category: brand_guidance
source: PayPal official security guidance (synthesized)
source_url: https://www.paypal.com/in/security
last_verified: 2026-10-11
language: en
region: global
channels: [email, web]
brands: [paypal]
threat_tags: [brand_impersonation, urgency_detected, financial_pressure, credential_pressure]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [paypal.com, paypal.me]
subdomain_rules: [*.paypal.com]
logo_phash: e4b2d1c9a7f30841
phishing_patterns: [paypal-security-check, paypal-account-verify, paypa1.com]
never_does: ["Never asks for full debit/credit card CVV via email link", "Never asks users to confirm SMS OTP via third-party form"]
contact_channels: [phishing@paypal.com]
regulatory_notes: FTC Consumer Sentinel Network Fraud Directives
summary: How phishing pages imitate PayPal: lookalike domains, "unusual activity" account alerts, fake invoice/payment notifications, and fake dispute-resolution forms.
---

## Common impersonation patterns

- **Account alert lures**: emails claiming an account is limited, frozen, or
  has unusual activity, with a "Confirm your identity" button leading to a
  fake login and then a fake identity-verification form requesting card
  number, CVV, and bank details.
- **Fake invoice / payment received**: notices that PayPal has received a
  payment you "didn't authorize," with a cancellation link that opens a
  credential-harvest page.
- **Item dispute threats**: messages that a buyer filed a dispute and demand
  you "verify shipment" via a link.

## Domain tells

Phishing hosts use patterns like `paypal-secure-verify.example`,
`paypal.com.account-verify.example`, punycode lookalikes, and numeric
substitutions (`paypa1`). The real domain is `paypal.com`; its login path
never requires credentials on a third-party host.

## What PayPal will never do

- Ask for full card number, CVV, or bank credentials by email link.
- Ask you to confirm an OTP received by SMS.
- Threaten immediate account closure with a countdown to force a click.

## Recommended guidance

Check account status by typing paypal.com directly. Enable the account
security key/2FA. Report the email through PayPal's official phishing
report channel and forward the message; do not reply.

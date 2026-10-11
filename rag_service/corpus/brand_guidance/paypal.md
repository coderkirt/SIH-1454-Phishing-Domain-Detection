---
id: brand-paypal
title: PayPal Official Brand Security Guidance
category: brand_guidance
source: PayPal Security Center Guidance
source_url: https://www.paypal.com
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
never_does: ['Never asks for full debit/credit card CVV via email link', 'Never asks users to confirm SMS OTP via third-party form']
contact_channels: [phishing@paypal.com]
regulatory_notes: FTC Consumer Sentinel Network Fraud Directives
summary: Authoritative brand guidance for PayPal. Details authentic domain signatures, fake invoice notifications, and dispute resolution lures.
---

PayPal is one of the most widely spoofed global payment brands. Attackers frequently send fraudulent billing notices and account limitation alerts.

## Official Infrastructure
- All legitimate PayPal transaction flows occur strictly on `paypal.com`.
- Short payment links originate from `paypal.me`.

## Attack Patterns
- Fake Invoice Notifications: Emails alleging an unauthorized transaction (e.g., $650 for Geek Squad or Bitcoin) containing a fraudulent customer support number.
- Account Limitation Lures: Warning messages claiming the account has been restricted due to suspicious logins, driving users to clone forms.

## Security Rules
- PayPal never asks users to confirm their identity by emailing photos of credit cards with CVV visible.
- PayPal never prompts customers to send funds via cryptocurrency or gift cards to cancel an invoice.

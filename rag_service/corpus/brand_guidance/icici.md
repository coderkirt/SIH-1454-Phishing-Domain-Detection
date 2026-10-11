---
id: brand-icici
title: ICICI Bank Brand Security Protocol
category: brand_guidance
source: ICICI Safe Banking & CERT-In Guidance
source_url: https://www.icicibank.com
last_verified: 2026-10-11
language: en
region: india
channels: [sms, email, web]
brands: [icici]
threat_tags: [brand_impersonation, credential_pressure, urgency_detected]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [icicibank.com, infinity.icicibank.com]
subdomain_rules: [*.icicibank.com] 
logo_phash: c3d4e5f60718293a
phishing_patterns: [icicibank-login-verify, icici-rewards-redeem, icici-card-protect]
never_does: ['Never asks for grid values printed on the reverse of the debit card', 'Never asks for iMobile MPIN or login OTP on external portals']
contact_channels: [1930, antiphishing@icicibank.com]
regulatory_notes: RBI Master Direction on Digital Payment Security Controls
summary: Authoritative brand guidance for ICICI Bank detailing official domains, debit card grid card harvesting techniques, and safe banking practices.
---

ICICI Bank customers are frequently targeted by social engineering attacks attempting to harvest netbanking passwords and debit card Grid Authentication values.

## Official Web Infrastructure
- Legitimate consumer banking is hosted on `icicibank.com` and secure subdomains such as `infinity.icicibank.com`.
- Mobile banking operates exclusively through the certified iMobile Pay application downloaded from official app stores.

## Threat Campaign Tells
- Scammers deploy cloned portals requesting both login credentials and values from the debit card grid (letters A through P on the back of the card).
- Lures mimic PAN update requests or false alerts regarding unauthorized international credit card charges.

## What ICICI Will Never Do
- ICICI Bank will never ask a customer to enter their complete debit card Grid letters to 'confirm account status'.
- Employees never request passwords, ATM PINs, or CVV numbers over the phone or email.

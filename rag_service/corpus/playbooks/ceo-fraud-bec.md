---
id: playbook-ceo-fraud-bec
title: Business Email Compromise (BEC) and Executive Impersonation
category: playbook
source: FBI IC3 + CISA Business Email Compromise Guidance (synthesized)
source_url: https://www.cisa.gov/news-events/cybersecurity-advisories
last_verified: 2026-10-11
language: en
region: global
channels: [email, web]
brands: []
threat_tags: [authority_impersonation, urgency_detected, secrecy, financial_pressure]
mitre: [T1566.002, T1598]
severity: critical
tactics: [executive_impersonation, wire_fraud, urgency, confidential_mandate]
iocs: [lookalike_domain, display_name_spoof, reply_to_mismatch, urgent_wire]
first_seen: 2024-01-15
summary: Attackers pose as CEOs, CFOs, or company executives demanding urgent, confidential wire transfers or vendor account updates.
---

## How the scam works

The attacker sends an email mimicking a senior executive — the CEO, Managing Director,
or CFO — directed to finance, accounts, or HR personnel. The email typically asserts
that an urgent, confidential acquisition, vendor payment, or legal settlement requires
immediate funds transfer before normal business approval cycles.

Attackers often register lookalike domains (e.g. `company-corp.com` instead of `company.com`)
or compromise legitimate corporate mailboxes to bypass email filters. Once trust is established,
the attacker instructs the employee to wire funds to an offshore or mule bank account.

## Common message patterns

- "Are you at your desk? I need an urgent, confidential wire transfer processed today for an acquisition."
- "Please process the attached invoice immediately. Do not discuss this with the team until finalized."
- "Our supplier changed their banking details; please route all future vendor disbursements to this new account."

These lures exploit executive authority, artificial confidentiality mandates, and fear of insubordination.

## Warning signs for analysts

- Display name matches the CEO, but the actual envelope sender or `Reply-To` points to an external webmail service.
- The sender demands strict secrecy or asks the recipient not to contact them via phone.
- Sudden change in supplier bank account details without out-of-band verification.
- Domain age of the sender domain is under 30 days or carries character substitutions.

## Recommended user guidance

Never execute financial transfers or alter bank routing numbers based solely on an email request.
Always verify wire transfer instructions through a trusted, pre-established phone number or in-person
confirmation with the executive. Establish multi-person authorization controls for all disbursements.

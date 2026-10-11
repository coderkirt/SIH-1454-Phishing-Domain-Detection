---
id: playbook-account-suspension-lure
title: Account Suspension and "Verify Your Account" Lures
category: playbook
source: FTC Consumer Guidance (synthesized)
source_url: https://consumer.ftc.gov/articles/how-recognize-avoid-phishing-scams
last_verified: 2026-10-11
language: en
region: global
channels: [email, sms, web]
brands: []
threat_tags: [urgency_detected, fear_tactics, credential_pressure, coercion, countdown]
mitre: [T1566.002]
severity: high
tactics: [credential_harvest, account_takeover, fake_login, urgency_pressure]
iocs: [verify_login_subdomain, account_closure_deadline, lookalike_auth_page]
first_seen: 2024-01-01
summary: Scammers claim your account will be suspended or closed unless you "verify" it through a link that leads to a fake login page harvesting your credentials.
---

## How the scam works

The attacker sends a message claiming to be from a service you use — a bank,
an email provider, a shopping site, or a government portal. The message says
your account has been suspended, will be closed, or has shown suspicious
activity, and that you must "verify" or "reactivate" it immediately by clicking
a link.

The link leads to a page that visually copies the real service. Any username,
password, OTP, or card details entered there are captured by the attacker. The
page may then redirect to the real site so the victim notices nothing.

## Common message patterns

- "Your account has been suspended due to unusual activity. Verify now to
  avoid permanent closure."
- "Failure to verify within 24 hours will result in account deactivation."
- "We detected an unauthorized login. Secure your account immediately."

These messages deliberately combine urgency (act now), fear (account loss),
and authority (the "security department") to short-circuit careful thinking.

## Warning signs for analysts

- Threats of deletion or suspension with a short deadline.
- A login form reached from an email or SMS link rather than the app or a
  typed address.
- The destination domain is newly registered, uses a lookalike spelling, or
  carries unusual subdomains such as `secure-login.service-support.example`.
- The page asks for more than a username and password — OTP, PIN, CVV, or
  full card number.

## Recommended user guidance

Do not use the link. Open the app or type the official address yourself and
check the account from there. Real services do not suspend accounts for
failing to click a link. Report the message and change the password from a
known-good device if you already entered it.

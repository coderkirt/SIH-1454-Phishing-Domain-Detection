---
id: playbook-otp-kyc-theft
title: OTP and KYC Theft (Bank/Aadhaar Impersonation)
category: playbook
source: RBI/CERT-In public advisories + bank fraud advisories (synthesized)
source_url: https://cert-in.org.in/
last_verified: 2026-10-11
language: en
region: india
channels: [sms, voice, email, social]
brands: [sbi, hdfc, icici, axis, uidai]
threat_tags: [credential_pressure, authority_impersonation, urgency_detected, coercion]
mitre: [T1566.004, T1598.004]
severity: critical
tactics: [otp_harvest, kyc_deactivation_threat, vishing, credential_interception]
iocs: [pan_aadhaar_form, urgent_account_hold, otp_input_box, reverse_caller_id]
first_seen: 2024-01-01
summary: A caller or message posing as a bank or "KYC department" persuades the victim to read out an OTP, UPI PIN, or Aadhaar details to complete a fake KYC update.
---

## How the scam works

The victim receives an SMS or phone call from someone claiming to be from
their bank's KYC department, or from UIDAI/Aadhaar services. The scammer says
the victim's KYC (Know Your Customer) record is incomplete or expired and the
account will be blocked unless verification is done "right now."

The victim is then asked to install a remote-screen-sharing app, or to read
out an OTP that was just sent to their phone, or to confirm a UPI mandate.
With screen sharing the scammer can see the OTP in real time; with the OTP
alone they can authorize transactions or bind a new device to the victim's
payment app.

## Why it succeeds

- The caller already knows real details (name, partial account number) often
  obtained from earlier data leaks, which builds false trust.
- The threat of account blocking triggers fear and urgency.
- Victims believe the OTP is "needed to complete verification" — no legitimate
  bank or UIDAI ever asks for an OTP over phone or SMS.

## Warning signs for analysts

- Any request for OTP, UPI PIN, or full Aadhaar number over a call or chat.
- Instructions to install screen-sharing or "verification" apps.
- Caller ID showing a personal mobile number rather than an official bank line.
- Pressure that prevents the victim from calling the bank back independently.

## Recommended user guidance

Hang up and call the bank using the number on the back of your card or the
official website. Never share an OTP with anyone, including someone claiming
to be bank staff. Report cyber-fraud immediately on the national helpline so
the transaction window can be frozen.

---
id: playbook-sim-swap-telecom-verification
title: SIM Swap and eSIM 5G Upgrade Phishing
category: playbook
source: Telecom Regulatory Authority Guidance + CISA SIM Swapping Warnings (synthesized)
source_url: https://www.cisa.gov/news-events/cybersecurity-advisories
last_verified: 2026-10-11
language: en
region: global
channels: [sms, voice, web]
brands: []
threat_tags: [urgency_detected, credential_pressure, fear_tactics, authority_impersonation]
mitre: [T1566.002]
severity: critical
tactics: [esim_qr_capture, sim_swap_port, otp_interception, telecom_spoof]
iocs: [esim_activation_qr, urgent_5g_migration, forward_sms_code, telco_header_spoof]
first_seen: 2024-03-10
summary: Telecom impersonation lures tricking victims into requesting a SIM swap or scanning a malicious eSIM QR code, enabling attackers to take over phone numbers and intercept 2FA banking codes.
---

## How the scam works

The victim receives an SMS or phone call claiming to be from their mobile network operator (Jio, Airtel, Vi, AT&T,
Verizon). The communication warns that their current physical SIM card will be deactivated within 24 hours unless
they upgrade to a 5G eSIM immediately, or claims their KYC documents are expired.

The attacker directs the victim to send a specific carrier porting SMS (e.g. `SIM <new-sim-number>` to 121) or
scan an "eSIM configuration QR code" sent via email. Once scanned or sent, the victim's phone number is transferred
to the attacker's physical device. The victim's phone loses cellular signal, while the attacker immediately initiates
password resets across the victim's banking, crypto, and email accounts using intercepted SMS OTPs.

## Common message patterns

- "URGENT: Your SIM card will be blocked within 24 hours. To upgrade to 5G network free of cost, scan the eSIM QR code."
- "Dear customer, your mobile KYC is suspended. Send SMS `PORT <number>` or call telecom verification at 98765-XXXXX."

Attackers exploit the fear of losing phone connectivity to push targets into quick compliance.

## Warning signs for analysts

- Urgent messages demanding SIM upgrades or porting codes to avoid service disconnection.
- Telecom emails containing attached QR codes for eSIM profile installation without an in-store request.
- Instructions asking users to forward carrier confirmation codes or reply with carrier command keywords.
- Calls instructing the subscriber not to restart their phone or ignore temporary network drops.

## Recommended user guidance

Mobile operators never initiate unsolicited calls or SMS messages demanding that customers generate eSIM codes
or forward porting confirmation SMSs. If your phone unexpectedly loses cellular connectivity ("No Service"),
immediately contact your mobile operator from another device and alert your banks to freeze online transactions.

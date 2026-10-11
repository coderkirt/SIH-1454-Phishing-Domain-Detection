---
id: playbook-electricity-utility-disconnection
title: Electricity and Essential Utility Disconnection Lures
category: playbook
source: CERT-In Advisory + Power Discom Warnings (synthesized)
source_url: https://cert-in.org.in/
last_verified: 2026-10-11
language: en
region: india
channels: [sms, social, app]
brands: []
threat_tags: [fear_tactics, urgency_detected, countdown, financial_pressure, coercion]
mitre: [T1566.002]
severity: high
tactics: [utility_blackmail, immediate_cutoff, fake_helpline, apk_dropper]
iocs: [power_cut_time, personal_mobile_helpline, discom_header_spoof, screen_share_lure]
first_seen: 2024-02-15
summary: SMS and WhatsApp messages claiming electricity power will be disconnected tonight due to unpaid bills, prompting victims to call fake officers or download malicious APKs.
---

## How the scam works

The victim receives an urgent SMS or WhatsApp message appearing to come from an electricity board or power utility
(e.g., BSES, Mahavitaran, UPPCL, TNEB). The message warns that power supply will be cut off tonight at 9:30 PM
because last month's bill payment was not updated in the government billing software.

The notification provides a personal 10-digit mobile number for an "Electricity Officer" or prompts the user
to click a link to install an "e-bill verification APK". When the victim calls, the fraudster instructs them to make
a token payment of Rs 10 via a phishing page or download a remote-access app (QuickSupport, AnyDesk), through
which the fraudster captures banking credentials and drains accounts.

## Common message patterns

- "Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM from electricity office.
   Because your previous month bill was not updated. Please immediately contact our electricity officer at 98765-XXXXX."
- "URGENT: Power supply disconnection order issued for meter #49201. Call billing officer to prevent outage."

The threat of darkness, spoiled food, or household disruption prompts immediate compliance without checking utility accounts.

## Warning signs for analysts

- Official utilities send notifications from verified alphanumeric sender IDs, not individual personal 10-digit mobile numbers.
- Messages demand contact with a single mobile number rather than listing official customer care helplines or website URLs.
- Demands to install third-party screen sharing applications or download APK files to resolve billing status.
- Strict same-day deadlines (e.g. "tonight at 9:30 PM") designed to prevent consultation with utility offices.

## Recommended user guidance

Never call mobile numbers provided in unverified SMS messages. Open your official power utility mobile application
or visit the verified consumer portal to check billing status. Utilities never ask consumers to download remote-access
applications or APK files to update a payment.

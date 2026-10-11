---
id: playbook-quishing-qr
title: QR Code Phishing (Quishing)
category: playbook
source: APWG Trends Report + vendor security guidance (synthesized)
source_url: https://apwg.org/trendsreports
last_verified: 2026-10-11
language: en
region: global
channels: [qr, email, web, print]
brands: []
threat_tags: [credential_pressure, financial_pressure, urgency_detected]
mitre: [T1566.002]
severity: high
tactics: [qr_obfuscation, mobile_credential_harvest, physical_sticker_overlay, fake_meter]
iocs: [untrusted_qr_image, parking_meter_sticker, short_link_in_qr]
first_seen: 2024-01-01
summary: Attackers place or send QR codes that open phishing pages or payment endpoints; the code hides the true URL from the victim and from many scanners.
---

## How the scam works

Quishing (QR phishing) uses a QR code as the delivery vehicle. Stickers with
fake QR codes are placed over real codes on parking meters, restaurant
menus, or delivery notices; or codes are emailed as "invoices," "delivery
notices," or "wifi login" sheets.

Scanning opens a URL the victim cannot preview, typically a phishing login
or a UPI/payment page. Because the link is hidden behind the image, casual
inspection of the message text reveals nothing suspicious, and many email
gateways do not scan inside images.

## Warning signs for analysts

- QR codes on stickers applied over existing codes in public places.
- Codes promising refunds, parking "payments," or menu access.
- Destination domains that are shorteners, freshly registered, or unrelated
  to the venue brand.
- Emails asking you to scan a code to "unlock," "verify," or "receive" money.

## Recommended user guidance

Inspect the surface: a sticker placed over a printed code is suspicious. Use
the official app for parking or payments instead of scanning. Before
entering credentials on a scanned page, check the URL carefully and type the
official address yourself if unsure.

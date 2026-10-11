---
id: playbook-delivery-parcel-scam
title: Delivery, Parcel, and "Customs Fee" Scams
category: playbook
source: Postal/courier fraud advisories (synthesized)
source_url: https://www.cisa.gov/secure-our-world/recognize-and-report-phishing
last_verified: 2026-10-11
language: en
region: global
channels: [sms, email, social]
brands: [fedex, dhl, amazon]
threat_tags: [financial_pressure, urgency_detected, credential_pressure]
mitre: [T1566.002]
severity: medium
tactics: [redelivery_fee_bait, card_theft, address_update_harvest, courier_spoof]
iocs: [unpaid_shipping_fee, package_tracking_shortener, fake_fedex_portal]
first_seen: 2024-01-01
summary: Fake delivery notices claim a parcel is held pending a small fee or address confirmation; the link leads to a payment page that steals card details.
---

## How the scam works

The victim receives an SMS, WhatsApp message, or email claiming a parcel is
held by customs, the courier, or the postal service pending a small fee,
re-addressing charge, or identity verification. A shortened or lookalike
link opens a convincing courier-branded page asking for card details or a
small "refundable" payment.

Variants also claim a failed delivery attempt and ask the victim to install
a tracking app or share an OTP to "reschedule." Amazon/Flipkart order scams
follow the same shape with order-confirmation lures.

## Warning signs for analysts

- Delivery notices for parcels the victim never ordered.
- Fees demanded via links instead of at the counter or official app.
- Shortened URLs and domains that resemble but do not match the courier's
  real domain.
- Requests for card number, CVV, or OTP to release a parcel.

## Recommended user guidance

Check tracking in the courier's official app or website by typing the
address. Delivery companies do not collect small fees via SMS links. Never
enter card details on a page reached from a message link.

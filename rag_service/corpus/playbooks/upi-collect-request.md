---
id: playbook-upi-collect-request
title: UPI Collect/Payment Request Scams
category: playbook
source: NPCI + bank public advisories (synthesized)
source_url: https://www.npci.org.in/
last_verified: 2026-10-11
language: en
region: india
channels: [sms, social, app]
brands: [paytm, phonepe, google]
threat_tags: [financial_pressure, greed_bait, urgency_detected, credential_pressure]
mitre: [T1566.002]
severity: critical
tactics: [upi_collect_fraud, pin_theft, refund_disguise, reverse_payment_trap]
iocs: [upi_collect_notification, pin_to_receive_claim, fake_cashback_banner]
first_seen: 2024-01-01
summary: Scammers send UPI collect requests or payment links disguised as refunds, prize winnings, or "pending payments" — approving them debits money instead of crediting it.
---

## How the scam works

In the UPI collect-request pattern, the attacker sends a payment request that
appears in the victim's payment app. The request screen shows a large amount
(the "refund" or "prize") but the action the victim is asked to approve is a
debit — the request is structured so that tapping "Approve"/"Pay" sends money
to the scammer, not receives it.

Variants include SMS links claiming an unclaimed refund, cashback, or
compensation, and messages asking the victim to "confirm a small payment" to
receive a larger amount. Some messages use a legitimate-looking QR code that
is actually a payment QR.

## Why it succeeds

- The UI of a payment request is confusing under time pressure.
- Victims are conditioned to tap "Approve" for refunds.
- The promise of easy money (cashback, lottery winnings) lowers suspicion.

## Warning signs for analysts

- Payment requests from unknown VPA handles.
- Messages framing a debit as a refund or prize.
- QR codes received via SMS or social media that promise money in return.
- Requests to share a screenshot of a payment or OTP "for confirmation."

## Recommended user guidance

Never approve a UPI request from an unknown sender, even a small amount —
the displayed amount can be misleading. Refunds from legitimate services are
credited automatically and never require you to first pay or approve
anything. Verify cashback claims only inside the official app.

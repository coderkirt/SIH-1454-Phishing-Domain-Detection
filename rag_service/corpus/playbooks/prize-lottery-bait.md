---
id: playbook-prize-lottery-bait
title: Prize, Lottery, and "You Have Won" Bait
category: playbook
source: FTC Consumer Guidance (synthesized)
source_url: https://consumer.ftc.gov/articles/how-recognize-avoid-phishing-scams
last_verified: 2026-10-11
language: en
region: global
channels: [email, sms, social]
brands: []
threat_tags: [greed_bait, urgency_detected, financial_pressure, secrecy]
mitre: [T1566.002]
severity: medium
tactics: [advance_fee_fraud, lottery_bait, claim_charge, lucky_draw_spoof]
iocs: [unsolicited_winnings, upfront_processing_charge, kbc_lottery_letter]
first_seen: 2024-01-01
summary: Victims are told they have won a lottery, lucky draw, or cashback and must pay a fee, share payment details, or install an app to "claim" the prize.
---

## How the scam works

The message announces that the recipient has won a prize, lottery, lucky
draw, or festival cashback from a well-known brand or telecom operator. To
claim it, the victim must act quickly: pay a small "processing" or "customs"
fee, share bank/UPI details for the "transfer," or install an app to receive
the reward.

Each requested step is the actual attack: the fee is stolen, the shared
payment details enable fraud, or the app is malware/remote-access software.
There is no prize. Escalation continues ("your prize is about to be
cancelled") until the victim stops paying.

## Why it succeeds

- Greed combined with a countdown ("claim within 30 minutes").
- Fake "official" branding and congratulatory formatting.
- Small initial fee makes the ask feel harmless.

## Warning signs for analysts

- Prize claims for a contest the victim never entered.
- Any upfront fee to receive winnings — real prizes are free.
- Requests for bank, card, or UPI credentials to "transfer the prize."
- Pressure to keep the win secret ("do not tell anyone until processed").

## Recommended user guidance

Treat any unsolicited winning notice as fake. Real lotteries deduct taxes
where applicable and never require a fee to release winnings. Do not click,
pay, or share details; delete and report the message.

---
id: playbook-sextortion-blackmail-threat
title: Sextortion and Credential-Leak Blackmail Threats
category: playbook
source: FBI IC3 Alerts + Europol Cybercrime Centre Guidance (synthesized)
source_url: https://www.fbi.gov/how-we-can-help-you/safety-resources/scams-and-safety
last_verified: 2026-10-11
language: en
region: global
channels: [email]
brands: []
threat_tags: [fear_tactics, credential_pressure, secrecy, countdown, coercion]
mitre: [T1566]
severity: high
tactics: [credential_dump_bluff, webcam_recording_claim, shame_coercion, crypto_ransom]
iocs: [old_compromised_password, countdown_timer, bitcoin_wallet_address, pegasus_spyware_claim]
first_seen: 2024-01-05
summary: Attackers cite real historical breached passwords to claim they infected the victim's device with spyware, demanding cryptocurrency ransom under threat of leaking private recordings.
---

## How the scam works

The victim receives an email containing an old, real password previously exposed in an unrelated third-party
data breach. The attacker claims this password proves they compromised the recipient's computer using sophisticated
malware (often falsely naming "Pegasus" or a zero-day remote trojan).

The attacker asserts they recorded split-screen footage of the victim visiting adult websites while capturing
their webcam video. They threaten to blast the embarrassing video to all friends, colleagues, and family contacts
unless a ransom payment (typically $500–$2,000 in Bitcoin or Monero) is transferred within a strict 48-hour countdown.

## Common message patterns

- "I know your password is `Winter2021!`. I installed a trojan on your computer and recorded you on adult sites."
- "You have 48 hours to transfer $1,200 in Bitcoin to my wallet address, or this video goes to all your contacts."
- "Do not try to reply or contact police; I have tracking pixels and notice every move you make."

The scam relies entirely on psychological shock, shame, fear of exposure, and fabricated proof of compromise.

## Warning signs for analysts

- Emails sent in bulk from compromised SMTP relays or spoofed sender headers.
- The password cited matches historical credential dumps from public data breaches.
- Inclusion of static Bitcoin or Monero wallet addresses with identical text blasted to millions of inboxes.
- Zero technical evidence or file hashes provided to substantiate the presence of active malware.

## Recommended user guidance

Do not pay the ransom. Attackers have no recordings; the password was obtained from historical corporate breaches.
Mark the email as spam, delete it, and change the compromised password on any accounts where it was reused.
Enable multi-factor authentication across all critical personal and work accounts.

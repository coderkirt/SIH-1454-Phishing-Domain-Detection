---
id: playbook-job-task-investment-scam
title: Job Offer and "Task-Based" Investment Scams
category: playbook
source: CERT-In + enforcement-directorate public advisories (synthesized)
source_url: https://cert-in.org.in/
last_verified: 2026-10-11
language: en
region: india
channels: [social, app]
brands: [naukri, linkedin]
threat_tags: [financial_pressure, greed_bait, urgency_detected, secrecy]
mitre: [T1566.002, T1598.002]
severity: high
tactics: [task_scam, telegram_prepaid_task, ponzi_deposit, fake_recruitment]
iocs: [youtube_like_task, telegram_vip_salary, crypto_merchant_deposit]
first_seen: 2024-01-01
summary: Victims are recruited via messaging apps for easy "online tasks" or investment plans; early small payouts build trust before larger deposits are stolen.
---

## How the scam works

The victim is contacted on LinkedIn, Naukri, or WhatsApp with a low-effort
part-time job: complete "tasks" (rating apps, boosting listings) or invest in
a trading plan with guaranteed returns. The first tasks pay small real
amounts, building confidence.

The victim is then moved to an attacker-controlled app or website showing
fake growing profits. To "withdraw," they must complete a block of tasks or
pay a "release fee," "tax," or "upgrade charge." Each payment unlocks a new
mandatory payment; the displayed balance is fictional. Total losses are
typically very large.

## Why it succeeds

- Gradual trust building with genuine-looking small payouts.
- Fake profit dashboards create sunk-cost escalation.
- Social proof from group chats containing other (fake) earners.

## Warning signs for analysts

- Job offers arriving via personal messaging with upfront "registration"
  or "task" deposits.
- Investment platforms with guaranteed returns and withdrawal fees.
- Apps distributed via direct links rather than official stores.
- Pressure to keep the scheme confidential "to protect the offer."

## Recommended user guidance

Legitimate employers never charge candidates to work. Treat guaranteed
returns as fraud. Do not install apps or pay "release fees" — the money will
not come back. Report the account and preserve chat/payment evidence.

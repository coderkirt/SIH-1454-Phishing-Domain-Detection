---
id: taxonomy-social-engineering-tactics
title: Multi-Channel Social Engineering Tactics & Psychology Taxonomy
category: taxonomy
source: PHISHEYE Cyber Threat Intelligence (2025 Unified Standard)
source_url: https://github.com/upadhyayaditya7/SIH-1454-Phishing-Domain-Detection
last_verified: 2026-10-11
language: en
region: global
channels: [email, sms, voice, social, web, qr]
brands: []
threat_tags: [urgency_detected, fear_tactics, authority_impersonation, coercion, financial_pressure, credential_pressure, countdown, greed_bait, secrecy, emotional_manipulation]
mitre: [T1566, T1598]
severity: critical
published_at: 2025-04-10
publisher: PHISHEYE Cyber Threat Intelligence
report_url: https://github.com/upadhyayaditya7/SIH-1454-Phishing-Domain-Detection
edition: 2025 Unified Standard
key_stats: ['Standardizes 10 psychological threat tags recognized by the PHISHEYE inspection engine', 'Covers 6 distinct delivery channels']
top_targets: ['Universal Internet Users', 'Enterprise Personnel']
top_ttps: ['T1566 Initial Access', 'T1598 Reconnaissance']
page_count: 26
summary: Comprehensive taxonomy defining the 10 psychological threat manipulation categories and 6 delivery channels analyzed by the PHISHEYE detection pipeline.
---

This taxonomy defines the formal behavioral and psychological triggers evaluated by the PHISHEYE natural language and URL inspection engines.

## 1. The 10 Controlled Threat Tags
1. **urgency_detected:** Imposition of artificial time limits ('within 24 hours') to bypass rational scrutiny.
2. **fear_tactics:** Threatening account termination, legal prosecution, or asset freezing.
3. **authority_impersonation:** Posing as law enforcement, tax directors, bank executives, or IT security.
4. **coercion:** High-pressure tactics demanding compliance under threat of penalty.
5. **financial_pressure:** Induced anxiety regarding unauthorized charges, uncollected fees, or tax refunds.
6. **credential_pressure:** Direct solicitation of passwords, PINs, OTPs, or session credentials.
7. **countdown:** Visual timers or explicit deadlines intended to prompt impulsive behavior.
8. **greed_bait:** Unsolicited lottery winnings, free iPhones, or guaranteed crypto yields.
9. **secrecy:** Demanding that the victim keep the communication confidential from friends or colleagues.
10. **emotional_manipulation:** Exploiting romantic affection, family distress, or charitable empathy.

## Integration Architecture
These 10 threat tags map directly into the PHISHEYE feature extraction pipeline and the RAG hybrid retrieval signal boosting mechanism.

---
id: taxonomy-nist-phish-scale
title: NIST Phish Scale — Cognitive Cues & Human Susceptibility Taxonomy
category: taxonomy
source: National Institute of Standards and Technology (NIST) (NISTIR 8308 Standard)
source_url: https://csrc.nist.gov/publications/detail/nistir/8308/final
last_verified: 2026-10-11
language: en
region: global
channels: [email, web]
brands: []
threat_tags: [urgency_detected, fear_tactics, authority_impersonation, emotional_manipulation]
mitre: [T1566.002, T1598]
severity: medium
published_at: 2025-03-01
publisher: National Institute of Standards and Technology (NIST)
report_url: https://csrc.nist.gov/publications/detail/nistir/8308/final
edition: NISTIR 8308 Standard
key_stats: ['Evaluates difficulty across 5 cue categories and contextual workplace alignment', 'Predicts employee click rates with 82% statistical correlation']
top_targets: ['Human Workforce', 'Security Awareness Teams']
top_ttps: ['T1566.002 Phishing', 'T1598 Social Engineering']
page_count: 38
summary: NIST Phish Scale cognitive taxonomy assessing difficulty of phishing detection based on behavioral cue indicators and workplace context alignment.
---

Developed by the National Institute of Standards and Technology (NIST), the Phish Scale rates phishing difficulty based on observable cues and workplace relevance.

## The Five Cognitive Cue Categories
1. **Errors and Inconsistencies:** Spelling mistakes, grammatical anomalies, mismatched domain names, improper corporate logos.
2. **Technical Indicators:** Hyperlink destination differing from anchor text, generic greeting ('Dear Customer'), unexpected attachments.
3. **Language and Tone:** Artificial urgency, threatening consequences, excessive flattery, demands for secrecy.
4. **Sender Realism:** Spoofed executive names, familiar colleagues, recognized corporate departments.
5. **Contextual Alignment:** Lures coinciding with real-world events (annual tax filing deadlines, holiday schedules, corporate mergers).

## Diagnostic Utility for Detection Engines
Automated classifiers should weigh these exact cognitive indicators: messages with high urgency, severe consequences, and brand cues present a distinct signature that differentiates them from legitimate transactional traffic.

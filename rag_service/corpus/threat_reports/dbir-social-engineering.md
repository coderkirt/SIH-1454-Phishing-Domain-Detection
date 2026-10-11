---
id: report-verizon-dbir-social-engineering
title: Verizon DBIR — Phishing and Social Engineering Findings
category: threat_report
source: Verizon Data Breach Investigations Report (paraphrased)
source_url: https://www.verizon.com/business/resources/reports/dbir/
last_verified: 2026-10-11
language: en
region: global
channels: [email, voice, web]
brands: []
threat_tags: [credential_pressure, urgency_detected]
mitre: [T1566, T1566.004]
summary: Verizon's DBIR consistently finds phishing is a top breach entry point, victims click fast, few report, and median time to fall for a phishing page is under 60 seconds.
---

## Key findings across recent DBIR editions

- **Human element**: a large majority of breaches involve a non-malicious
  human element — a mistake, credential abuse, or being tricked. Phishing
  remains one of the top initial access vectors alongside stolen
  credentials.
- **Speed of failure**: in simulated phishing, the median time for a user to
  fall for a message is under one minute, and the median time to click a
  malicious link is well under a minute — faster than a typical SOC can
  block a freshly registered domain.
- **Reporting rates**: only a small share of simulated phishing messages are
  reported by employees, though organizations with regular training see
  better reporting and lower click rates.
- **Pretexting and BEC**: pretexting (including business email compromise)
  represents a substantial share of the social-engineering breaches, driven
  by gift-card and wire-transfer fraud.

## Interpretation

Phishing success depends on human factors more than technical
sophistication; the fastest lever is reducing victim interaction time —
blocking the page or explaining the risk before credentials are typed.
Explainability at the moment of clicking therefore has measurable risk
reduction value, not just UX value.

Figures cited are paraphrased from published DBIR editions; consult the
report for exact statistics and methodology.

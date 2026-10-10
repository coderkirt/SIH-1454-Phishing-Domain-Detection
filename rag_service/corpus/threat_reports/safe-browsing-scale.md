---
id: report-google-safe-browsing-scale
title: Google Safe Browsing — Phishing at Internet Scale
category: threat_report
source: Google Safe Browsing documentation and research (paraphrased)
source_url: https://developers.google.com/safe-browsing
last_verified: 2026-10-11
language: en
region: global
channels: [web, email]
brands: [google]
threat_tags: [phishing, brand_impersonation]
mitre: [T1566.002]
summary: Google Safe Browsing protects billions of devices against unsafe sites including phishing, using machine-learning classifiers plus URL analysis, and publishes how sites are classified.
---

## What Safe Browsing does

Google Safe Browsing maintains continuously updated lists of URLs that host
phishing, malware, unwanted software, or social-engineering content. Its
protection is built into Chrome, Android, and other services, covering
billions of devices.

## How phishing is identified

- **Machine-learning classifiers** score pages using page content, DOM
  structure, and visual/brand signals to detect pages imitating known
  services.
- **URL and domain signals** — registration freshness, redirects, and
  lookalike patterns — feed the same pipeline.
- Newly observed URLs are reviewed quickly; classification can be appealed
  by site owners through a review process.

## Practical lessons for a detection system

- A clean Safe Browsing result is not proof of safety: many phishing domains
  live for only hours, before they are listed.
- Brand-impersonation detection at scale relies on page-level evidence
  (logos, login forms, brand name in title/body) combined with domain
  signals — the same combination PHISHEYE uses.
- The API is intended for non-commercial use; commercial deployments are
  directed to Google's Web Risk service.

Figures and mechanisms are paraphrased from Google's public documentation;
see the Safe Browsing developer site for current details and terms.

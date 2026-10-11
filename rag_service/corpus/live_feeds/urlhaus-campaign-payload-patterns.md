---
id: urlhaus-campaign-payload-patterns
title: URLhaus Threat Report: Malicious Distribution & Staging Patterns
category: threat_report
source: abuse.ch URLhaus Campaign Intelligence
source_url: https://urlhaus.abuse.ch/
last_verified: 2026-10-11
language: en
region: global
channels: [email, web, social]
brands: []
threat_tags: [shortened_url, credential_pressure, financial_pressure]
mitre: [T1566.002, T1566]
fetched_at: 2026-10-11T08:44:22Z
source_hash: 84928e14d98793f61426ab9029d73b74f88e0f7900bceff2a45e3ae9c01a6ddb
license: Creative Commons CC0 1.0 Universal
version: 1
summary: abuse.ch URLhaus analysis of malicious link redirection chains, cloud CDN abuse, and fast-flux domain rotation.
---

## URLhaus Intelligence: Malicious Link Distribution & Dropper Campaigns

URLhaus tracks active malware and phishing distribution infrastructure across hundreds
of thousands of newly reported URLs. Attackers consistently pair urgent social-engineering
themes with multi-stage redirection chains to evade automated URL scanners.

## Observed Delivery Vectors
- Zip and PDF email attachments containing shortened links leading to compromised WordPress sites.
- Telegram bots and Discord CDN links used as staging grounds for harvesting credentials and banking info.
- Fast-flux DNS domains and free dynamic DNS providers used to rapidly rotate phishing IP addresses.

## Operational Indicators for Detection
- URLs hosting `.exe`, `.scr`, `.iso`, or `.apk` files disguised as invoices or utility statements.
- Destination hosts utilizing newly registered generic TLDs with zero historical web traffic.
- Landing pages containing disguised credential submission forms that immediately redirect to legitimate sites.

## Analyst Guidance
Flag links pointing to raw IP addresses or recently resolved cloud-storage URLs (Firebase, Supabase, Discord)
masquerading as internal corporate documents or netbanking authentication screens.

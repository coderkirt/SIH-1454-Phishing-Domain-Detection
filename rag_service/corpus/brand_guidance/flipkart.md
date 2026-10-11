---
id: brand-flipkart
title: Flipkart E-Commerce Brand Security Guidance
category: brand_guidance
source: Flipkart Trust & Safety Advisory
source_url: https://www.flipkart.com
last_verified: 2026-10-11
language: en
region: india
channels: [web, social, sms]
brands: [flipkart]
threat_tags: [brand_impersonation, financial_pressure, urgency_detected]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [flipkart.com]
subdomain_rules: [*.flipkart.com] 
logo_phash: 9c0d1e2f3a4b5869
phishing_patterns: [flipkart-bigbillion-sale, flipkart-lucky-draw, flipkart-spin-wheel]
never_does: ['Never hosts lucky draw contests requiring shipping fee payment before claiming free electronics', 'Never operates flash sales on unverified domains outside flipkart.com']
contact_channels: [1930, security@flipkart.com]
regulatory_notes: Consumer Protection (E-Commerce) Rules & CERT-In Guidelines
summary: Brand security guidance for Flipkart e-commerce. Details festival sale scams, lucky draw spin-the-wheel lures, and cloned storefronts.
---

Flipkart is a major Indian e-commerce marketplace targeted during high-traffic shopping festivals like the Big Billion Days.

## Official Web Infrastructure
- Official marketplace operations take place strictly on `flipkart.com`.

## Common Attack Techniques
- Spin-the-Wheel / Lucky Draw Bait: Viral WhatsApp messages advertising free laptops or iPhones, requiring users to forward the message to 10 contacts and pay a 'processing fee'.
- Cloned Storefronts: Domains like `flipkart-super-deals.online` offering electronics at 90% discounts to steal card numbers.

## Security Rules
- Flipkart never requires upfront processing fees to claim legitimate promotional contest prizes.
- All genuine promotional campaigns are hosted directly inside the Flipkart application or on `flipkart.com`.

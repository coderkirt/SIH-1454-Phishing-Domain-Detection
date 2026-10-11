---
id: brand-amazon
title: Amazon Brand Protection & Phishing Indicators
category: brand_guidance
source: Amazon Security & Customer Protection Reports
source_url: https://www.amazon.com
last_verified: 2026-10-11
language: en
region: global
channels: [email, sms, web, voice]
brands: [amazon]
threat_tags: [brand_impersonation, urgency_detected, financial_pressure]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [amazon.com, amazon.in, amazon.co.uk]
subdomain_rules: [*.amazon.com, *.amazon.in] 
logo_phash: f5a6b7c8d9e01234
phishing_patterns: [amazon-order-cancelled, amazon-security-alert, amzn-security.top]
never_does: ['Never calls customers demanding remote access to cancel an accidental order', 'Never asks for payment via gift cards or crypto transfers']
contact_channels: [stop-spoofing@amazon.com]
regulatory_notes: FTC E-Commerce Consumer Protection Guidance
summary: Brand security reference for Amazon. Details high-frequency order cancellation lures, phone refund scams, and legitimate e-commerce domain architectures.
---

Amazon impersonation scams target buyers through bogus order confirmations, account lockouts, and fraudulent customer care phone numbers.

## Official Infrastructure
- Official marketplaces operate under regional apex domains: `amazon.com`, `amazon.in`, `amazon.co.uk`.
- Automated order updates are logged synchronously in the customer's Message Center on the real website.

## Attack Methodologies
- 'Order Confirmation' Phishing: Sending receipts for high-value electronics (iPhone, MacBook) the victim never ordered, with a link or phone number to 'cancel'.
- Account Lock Scam: Claims that billing information must be re-entered immediately to prevent order cancellation.

## Security Rules
- Amazon never demands payment outside of its secure checkout system.
- Amazon customer support never asks customers to install screen-sharing tools to reverse a charge.

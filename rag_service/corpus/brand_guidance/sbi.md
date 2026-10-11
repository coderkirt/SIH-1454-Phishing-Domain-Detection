---
id: brand-sbi
title: State Bank of India (SBI) Brand Security Guidance
category: brand_guidance
source: SBI Fraud Prevention & RBI Security Directives
source_url: https://onlinesbi.sbi
last_verified: 2026-10-11
language: en
region: india
channels: [sms, email, web, voice]
brands: [sbi]
threat_tags: [brand_impersonation, urgency_detected, credential_pressure, fear_tactics]
mitre: [T1566.002, T1598.002]
severity: critical
official_domains: [onlinesbi.sbi, sbi.co.in, bank.sbi]
subdomain_rules: [*.onlinesbi.sbi, *.sbi.co.in, *.sbi] 
logo_phash: a3f0c1b4892c5d1e
phishing_patterns: [onlinesbi-kyc, sbi-rewards, sbi-card-blocked, sbi-pan-update]
never_does: ['Never sends SMS or email with links to update KYC details', 'Never asks for netbanking password or ATM PIN', 'Never threatens permanent account freeze within 24 hours to compel clicking links']
contact_channels: [1930, report.phishing@sbi.co.in]
regulatory_notes: RBI Master Direction on Digital Payment Security Controls & CERT-In Banking Advisories
summary: Comprehensive security guidance for State Bank of India (SBI). Documents official domain architectures, common lookalike phishing signatures, and non-negotiable security rules.
---

State Bank of India (SBI) is India's largest public sector bank and the highest-volume target for brand impersonation scams. Fraud campaigns predominantly leverage smishing (fake SMS) and lookalike netbanking landing pages.

## Official Web & Authentication Architecture
- Legitimate consumer netbanking resides exclusively on `onlinesbi.sbi` and `sbi.co.in`.
- SBI enforces EV-SSL certificates and dedicated top-level banking infrastructure under the `.sbi` gTLD.
- Legitimate OTP communications originate strictly from authorized telecom headers (e.g., `SBIINB`, `SBISMS`).

## Common Impersonation & Typosquat Patterns
- Attackers register domains combining keywords like `onlinesbi-pan.top`, `sbi-kyc-update.com`, or `secure-sbi-portal.in`.
- Messages employ artificial urgency: 'Dear SBI User, your NetBanking is blocked due to incomplete PAN. Click to update immediately.'
- Phishing pages closely mirror the SBI login page, harvesting username, password, profile password, and intercepted 2FA OTPs.

## Security Inviolates (What SBI Will Never Do)
1. SBI never asks customers to disclose their PIN, OTP, CVV, or passwords over phone, SMS, or email.
2. SBI never demands installation of third-party remote access software (AnyDesk, TeamViewer) to verify identity.
3. SBI never sends SMS links directing customers to third-party file hosting servers or APK downloads.

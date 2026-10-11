---
id: brand-linkedin
title: LinkedIn Career Network Brand Security Protocol
category: brand_guidance
source: LinkedIn Safety & Security Guidance
source_url: https://www.linkedin.com
last_verified: 2026-10-11
language: en
region: global
channels: [email, web, social]
brands: [linkedin]
threat_tags: [brand_impersonation, credential_pressure, emotional_manipulation]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [linkedin.com]
subdomain_rules: [*.linkedin.com] 
logo_phash: 7e8f9a0b1c2d3041
phishing_patterns: [linkedin-message-alert, linkedin-job-offer, lnkedin-verify.com]
never_does: ['Never sends recruitment messages demanding upfront onboarding fees or software license purchases', 'Never asks users to enter LinkedIn passwords on external recruiter questionnaire links']
contact_channels: [phish@linkedin.com]
regulatory_notes: Professional Network Identity Integrity Directives
summary: Brand security protocol for LinkedIn professional network. Details corporate recruiting lures, credential-stealing InMail notices, and session hijacking risks.
---

LinkedIn accounts are valuable assets for corporate espionage, social engineering, and recruitment fraud.

## Official Web Architecture
- Professional profiles and networking are hosted exclusively on `linkedin.com`.

## Attack Scenarios
- Fake InMail Notifications: Emails claiming an executive or recruiter sent an urgent private message, linking to a lookalike sign-in portal.
- Fraudulent Job Offers: Scammers posing as recruiters from prestigious tech firms offering high salaries, asking applicants to install proprietary testing software that contains infostealers.

## Security Rules
- Official LinkedIn notifications originate from `@linkedin.com`.
- Legitimate recruiters never charge job application fees or demand credit card numbers during interviews.

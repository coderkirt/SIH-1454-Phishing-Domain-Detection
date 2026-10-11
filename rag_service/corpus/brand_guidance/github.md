---
id: brand-github
title: GitHub Developer Security & Token Protection
category: brand_guidance
source: GitHub Security Advisory Database & Docs
source_url: https://github.com
last_verified: 2026-10-11
language: en
region: global
channels: [email, web]
brands: [github]
threat_tags: [brand_impersonation, credential_pressure, urgency_detected]
mitre: [T1566.002, T1598.002]
severity: high
official_domains: [github.com, github.blog, api.github.com]
subdomain_rules: [*.github.com] 
logo_phash: 3c4d5e6f7a8b9203
phishing_patterns: [github-security-audit, git-token-expired, github-repo-verify]
never_does: ['Never asks developers to enter Personal Access Tokens (PATs) on external web forms', 'Never sends urgent PR notifications with third-party OAuth consent requests']
contact_channels: [support@github.com]
regulatory_notes: OpenSSF Supply Chain Integrity Principles
summary: Developer security guidance for GitHub. Details repository hijacking, fake CI/CD security audits, and developer token harvesting campaigns.
---

GitHub attacks target developers to compromise open-source software supply chains and corporate codebases.

## Official Endpoints
- Web interface and repository hosting: `github.com`.
- API endpoints: `api.github.com`.

## Attack Vectors
- Fake Security Alerts: Emails claiming a high-severity CVE was discovered in the developer's repository, urging them to authenticate on a lookalike domain.
- Job / Project Collaboration Lures: Invitations to collaborate on a private repository requiring execution of malicious npm packages or token disclosure.

## Security Rules
- GitHub never sends messages requesting Personal Access Tokens (PATs) or SSH keys.
- Official GitHub automated notifications always originate from `@github.com` addresses with valid SPF and DKIM signatures.

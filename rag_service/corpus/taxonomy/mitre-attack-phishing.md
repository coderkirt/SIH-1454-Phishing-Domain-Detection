---
id: taxonomy-mitre-attack-phishing
title: MITRE ATT&CK Enterprise Matrix — Phishing Techniques & Sub-Techniques
category: taxonomy
source: MITRE Corporation (v15 Enterprise Matrix)
source_url: https://attack.mitre.org/techniques/T1566/
last_verified: 2026-10-11
language: en
region: global
channels: [email, sms, voice, social, web]
brands: []
threat_tags: [brand_impersonation, credential_pressure, dangerous_executable]
mitre: [T1566, T1566.001, T1566.002, T1566.003, T1566.004, T1598, T1539]
severity: critical
published_at: 2025-04-15
publisher: MITRE Corporation
report_url: https://attack.mitre.org/techniques/T1566/
edition: v15 Enterprise Matrix
key_stats: ['Covers 4 sub-techniques under T1566 (Initial Access: Phishing)', 'Maps 3 sub-techniques under T1598 (Reconnaissance: Phishing for Information)', 'Correlates with 87 distinct threat groups tracked in ATT&CK']
top_targets: ['Enterprise Users', 'Identity Infrastructure']
top_ttps: ['T1566.001 Attachment', 'T1566.002 Link', 'T1566.003 Service', 'T1566.004 Voice', 'T1539 Cookie Theft']
page_count: 32
summary: MITRE ATT&CK formal taxonomy mapping all sub-techniques of T1566 (Phishing) and T1598 (Phishing for Information) with technical mitigation mappings.
---

The MITRE ATT&CK Enterprise Matrix classifies phishing under the **Initial Access** tactic (TA0001) and **Reconnaissance** tactic (TA0043).

## T1566: Phishing Sub-Technique Taxonomy
- **T1566.001 - Spearphishing Attachment:** Delivering weaponized files (macro-enabled documents, ISO files, script archives, LNK shortcuts) directly via email or messaging channels.
- **T1566.002 - Spearphishing Link:** Embedding hyperlinks that redirect victims to credential-harvesting pages, exploit kits, or drive-by download sites.
- **T1566.003 - Spearphishing via Service:** Utilizing legitimate third-party services (LinkedIn messages, WhatsApp, Slack, GitHub PRs, cloud document comments) to deliver lures.
- **T1566.004 - Spearphishing Voice (Vishing):** Utilizing voice telephony to impersonate IT support or authority figures to elicit credentials or MFA authorization.

## Related ATT&CK Techniques
- **T1539 - Steal Web Session Cookie:** Adversary-in-the-Middle tools capturing active session cookies to bypass MFA.
- **T1598 - Phishing for Information:** Probing targets to collect organizational charts, employee contact details, or technical environment specifications.

## Defensive Mitigations
M1031 (Network Intrusion Prevention), M1049 (Antivirus/EDR), M1021 (Restrict Web-Based Content), M1027 (Password Policies / FIDO2 Authentication).

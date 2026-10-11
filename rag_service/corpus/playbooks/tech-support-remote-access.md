---
id: playbook-tech-support-remote-access
title: Tech Support Scams and Remote Access Trojans
category: playbook
source: CISA + Microsoft public guidance (synthesized)
source_url: https://www.cisa.gov/secure-our-world/recognize-and-report-phishing
last_verified: 2026-10-11
language: en
region: global
channels: [web, voice, email]
brands: [microsoft, apple]
threat_tags: [authority_impersonation, fear_tactics, urgency_detected, credential_pressure]
mitre: [T1566.001, T1566.004]
severity: high
tactics: [remote_access_trojan, fake_virus_alert, phone_helpline_lure, screen_share_access]
iocs: [browser_lock_popup, toll_free_support_number, anydesk_teamviewer_lure, zeus_trojan_popup]
first_seen: 2024-01-01
summary: Pop-ups or calls claim the victim's computer is infected; the "technician" requests remote access, then steals credentials or installs malware.
---

## How the scam works

A browser pop-up or search-ad page mimics an official vendor support screen
(Microsoft, Apple, or an antivirus brand) and claims the device is infected.
A phone number is displayed; calling connects the victim to a scammer posing
as a certified technician.

The scammer persuades the victim to grant remote desktop access. Once
connected, they may "show" fake infections, install remote-access software or
a RAT, capture passwords typed during a fake scan, or take payment for
unnecessary "support contracts."

## Warning signs for analysts

- Pop-ups that lock the browser and demand an immediate call.
- Phone contact initiated by "Microsoft/Applied support" — vendors never
  cold-call about infections.
- Requests to install remote-access tools (AnyDesk, TeamViewer) or run
  command-line "diagnostics."
- Payment for support via gift cards, cryptocurrency, or wire transfer.

## Recommended user guidance

Close the page or force-quit the browser. Real vendors never show pop-ups
with phone numbers about infections. If you granted access, disconnect the
network, run a reputable scan, and change passwords from a different device.

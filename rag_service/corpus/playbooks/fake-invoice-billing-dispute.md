---
id: playbook-fake-invoice-billing-dispute
title: Fake Invoice and Billing Dispute Phishing
category: playbook
source: FTC Consumer Advice + APWG Billing Scam Reports (synthesized)
source_url: https://consumer.ftc.gov/articles/how-recognize-avoid-phishing-scams
last_verified: 2026-10-11
language: en
region: global
channels: [email, web]
brands: [paypal, amazon, apple, google]
threat_tags: [financial_pressure, fear_tactics, urgency_detected]
mitre: [T1566.001, T1566.002]
severity: high
tactics: [fake_invoice, dispute_bait, call_back_scam, payment_gateway_spoof]
iocs: [unrecognized_charge, pdf_invoice, support_phone_lure, spoofed_receipt]
first_seen: 2024-02-01
summary: Fraudulent receipts or subscription renewal invoices designed to provoke fear of unauthorized charges, luring victims into fake dispute portals or call centers.
---

## How the scam works

Attackers distribute emails containing fabricated invoices or renewal receipts for high-value purchases
(e.g., $499 for Norton Antivirus, Geek Squad, or a high-end smartphone on PayPal or Amazon). The message asserts
that the user's credit card or bank account has already been debited, or will be charged within 24 hours.

To dispute the false charge or request an immediate refund, the message prompts the recipient to click a link
or call a toll-free customer support number. The link leads to a lookalike dispute portal that captures card
numbers and online banking credentials, while telephone variants trick victims into installing remote desktop software.

## Common message patterns

- "Your subscription has automatically renewed for $599.99. If you did not authorize this charge, click here to cancel."
- "Invoice #INV-84920 attached. Payment received via PayPal. Call support immediately to dispute."
- "Your order for Apple iPhone 15 Pro Max is confirmed. Total charged: $1,199. Dispute transaction on portal."

The lure triggers immediate financial alarm, prompting victims to act before verifying their actual bank statements.

## Warning signs for analysts

- Invoices arriving from generic domains (`gmail.com`, `outlook.com`) claiming to represent major billing departments.
- The invoice PDF contains embedded hyperlinks pointing to newly registered redirectors or URL shorteners.
- The recipient has no active account or past purchase history with the purported merchant.
- Urgency demanding cancellation within a 24-hour window to avoid permanent debiting.

## Recommended user guidance

Do not click any dispute link or call the phone number listed on the suspicious email. Check your actual
bank, credit card, or payment provider account directly through their official app or verified website.
If no charge appears on your statement, the notification is fraudulent and should be marked as spam.

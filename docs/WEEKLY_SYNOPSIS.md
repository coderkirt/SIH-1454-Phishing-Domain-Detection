# PHISHEYE — Weekly project synopsis

**SIH 2026 · Problem Statement 1454 · Week of 6–12 October 2026**  
Theme: Blockchain and Cybersecurity · Category: Software  
Idea title: PhishShield AI  
Team ID: ______________ · Team name: ______________

## Problem

Attackers copy a real bank, wallet, or government service with a new domain, a shortened link, or a rushed message. Blacklists catch known sites and miss new lookalikes.

## Objective

Score a link or a pasted message before the user trusts it, and show both a plain warning and the evidence behind the score.

## Method

One FastAPI pipeline serves the React dashboard and the Chrome extension.

The system accepts a URL, a pasted email, WhatsApp, or SMS message, a page the extension can already see, or a QR image. It normalizes the address, unwraps short links, and refuses fetches to localhost, private addresses, and cloud metadata.

It queries OpenPhish, URLhaus, PhishTank, Phishing Army, and Google Safe Browsing when a key is set. A miss or a timeout is not treated as safe. A confirmed hit sets a score floor that later heuristics cannot lower.

It also scores lookalike names, domain age, TLS facts, and urgency language in English and Hinglish. Language alone cannot mark a result critical. Community reports and this-browser open counts are supporting signals, not proof.

The result is a score from 0 to 100, labelled Low, Medium, High, or Critical, returned as a Simple view and a Technical view.

A separate retrieval service explains the result from a curated threat corpus. It uses facts already collected and does not fetch the destination page.

## In use now

The dashboard, the extension, and the API are deployed. Accounts, scan history, and statistics use SQLite. Users can mark a result, export a report, and delete an analysis.

## This week

Decision fusion now keeps a confirmed threat-feed hit from being averaged away. The scanner can send on-page signals and this-browser activity with the URL. The technical panel shows that evidence. A retrieval evaluation harness checks that explanations stay tied to the corpus.

## Limits

There is no trained image or classical model in this build, so no accuracy figure is claimed. The live store is SQLite. The system does not read an inbox or phone messages unless the user pastes them or the extension sees links already on screen.

## Next

Package screenshot text recognition with the install, keep scan history tied to the logged-in user, and train a model only after a labelled set exists.

# Paste this into Gamma.app → Create new → Paste in text
# Theme: Dark / Midnight / black + red. 16:9. Keep screenshots you upload.

PHISHEYE — Scan before you trust
Lenovo LEAP jury presentation
A working phishing and lookalike-domain detector for Indian users. Dashboard + Chrome extension share one FastAPI engine.

---

The problem: a padlock does not mean it is SBI
SMS: “Your SBI account will be blocked. Complete KYC in 10 minutes. Share OTP.”
The page looks real. It has HTTPS. The victim types the OTP. Money leaves.
Blacklists are late. Short links and QR codes hide the host. Parents need plain English.
Lookalikes we must catch: paypa1.com · sbi-login.xyz · amaz0n-secure.tk · hdfc-login.vercel.app

---

The idea: one brain, two surfaces
Dashboard: paste URL, message, email, WhatsApp/SMS text, screenshot, or QR.
Chrome extension: holds the tab, scores first. LOW opens. MEDIUM asks. HIGH and CRITICAL stay closed.
Pipeline: Normalize → Analyze + fuse → Explain + act
SSRF guard on short links. Confirmed intel cannot be talked down.

---

Product landing (upload 01_landing.png)
Working UI. Not a mockup. Analyze URL · Upload screenshot · Get browser protection.

---

Security console (upload 02_dashboard.png and 05_scan.png)
Signed-in operator console. FastAPI + SQLite.
Multi-channel scan: URL, Message, Email, WhatsApp/SMS, Screenshot, QR.

---

What you can scan
URL — check-url
Message — pasted scam text
Email — visible links only. No inbox OAuth.
WhatsApp/SMS — paste the text. We do not read the phone.
Screenshot — page or poster image
QR — OpenCV reads the code. We do not visit the destination.

---

Real checks, stored (upload 07_history.png and 10_reports.png)
History is SQLite. Nothing invented.
Community reports are one signal, not proof that a site is malicious.

---

Live console metrics (upload 08_statistics.png and 09_pie.png)
From this prototype’s SQLite — not a published accuracy paper.
Do not claim 99% or F1.

---

The main product: extension (upload 13_extension.png)
Scan before the other site opens. Same engine as the dashboard.
Load unpacked, not Chrome Web Store.
Demo: github.com gates then opens if LOW. sbi-login.xyz stays closed. Do not open a live phishing kit.

---

Novelty — what is actually new
Not “the first phishing detector.” The combination is the product.
1. Scan-first gate — HIGH/CRITICAL never load the kit
2. Intel floors — confirmed feed hit cannot be vetoed; a miss is not SAFE
3. One engine — dashboard and extension share FastAPI
4. India language — Hinglish, UPI/OTP/KYC, bank lookalikes
5. Explainable Simple View + Technical View
6. Honest privacy — no passwords, OTP, SMS inbox, or Gmail OAuth

---

How it actually runs
Input → normalize → intel + heuristics → fuse → explain → act
Frontend: React 19, Vite, Tailwind
API: FastAPI + Uvicorn. Not Flask.
Data: SQLite. Not live Postgres.
Detect: heuristics + public feeds + weighted fusion. No trained CNN in this repo.
QR: OpenCV. Does not visit the URL.
Intel: OpenPhish, URLhaus, PhishTank, Phishing Army, optional Google Safe Browsing
Levels: LOW 0–29 · MED 30–49 · HIGH 50–69 · CRITICAL 70–100

---

Demo, limits, ask
Wake API: https://phisheye-api.onrender.com/health
Web: https://phisheye-web-fhn5.onrender.com
Extension: https://phisheye-web-fhn5.onrender.com/extension
We do not claim: Flask, live PostgreSQL, trained CNN, 99% accuracy, reading WhatsApp/SMS/Gmail, Chrome Web Store, blockchain, padlock = genuine bank.
Next: labelled reports → supervised model. Persistent DB. The gate stays.

Copy ALL text below into Gamma.app → Create new → Paste in text.
Then set: 16:9 · 12 slides only · theme = premium navy / ice-blue (NOT black-red, NOT the PHISHEYE app UI) · add images when asked.

Do not summarize this prompt away. Every number, API path, weight, floor, and limitation below is verified from the PHISHEYE repository. If a fact is not here, do not invent it.

================================================================================
ROLE
================================================================================

You are a hackathon presentation designer for an industry jury (Lenovo).

Build a PREMIUM executive technology deck: navy and ice-blue, like a board briefing, not a SOC dashboard.

Do NOT copy the PHISHEYE product UI (that app is black with bright red buttons). This deck must look independent: calm, expensive, blue.

Not a college assignment, not a generic SaaS template, not a red “cyber hacker” theme.

Product: PHISHEYE
Event: Lenovo Hackathon
Category: Software + Cybersecurity
Status: working software prototype (local + Render). Not a finished enterprise product.

One-line position (keep this meaning):
Scan the link before the fake page loads.

================================================================================
ABSOLUTE RULES (BREAKING ANY ONE MAKES THE DECK FALSE)
================================================================================

USE ONLY THIS PROMPT. Do not browse. Do not add “typical phishing stats” (billions lost, 90% of attacks, etc.) unless they appear below. They do not.

DO NOT INVENT:
team name, team members, college, Team ID, logo of Lenovo as if we are Lenovo,
accuracy, precision, recall, F1, ROC, dataset size, user count, MAU,
latency, throughput, money saved, 99%, “AI-powered CNN”, “deep learning model”,
Flask, Django, Node API, live PostgreSQL, Redis, Kafka, Kubernetes, Docker as the live path,
ESP32, ESP8266, NodeMCU, Raspberry Pi, IoT, sensors, cameras, hardware nodes,
blockchain, smart contracts,
Chrome Web Store listing,
Gmail OAuth, WhatsApp Business API, native SMS reader,
BERT, GPT-as-classifier, TensorFlow, PyTorch, sklearn .pkl, trained CNN.

DO NOT RANK COMPETITORS. Do not say “better than VirusTotal / Google Safe Browsing / Microsoft Defender.” You may say: VirusTotal-style research is usually after the click; PHISHEYE can gate the tab first. That is a design difference, not a benchmark.

TEAM / COLLEGE: not in the source. Title slide has NO people names. If you need a team line, write: “PHISHEYE team” and nothing else.

HARDWARE: none. Never draw a device, Pi, ESP, or sensor.

DATABASE: live is SQLite file backend/threats.db via python sqlite3.
SQLAlchemy model files exist in the repo but ARE NOT the live path.
PostgreSQL = FUTURE only. Label it FUTURE if shown.

AI/ML TRUTH:
There is no trained model file.
Intelligence = heuristic URL scoring + public threat feeds + phrase-matching psychology + documented fusion / intel floors.
Fusion key "ml" COPIES the lexical URL risk score so a low “ML” number cannot be used as proof of safety.
NumPy is used to reshape image bytes for OpenCV QR, not for neural nets.
model_confidence = min(95, 35 + 10 × count(signals ≥ 20)). This is signal AGREEMENT, not accuracy.

DASHBOARD COUNTS (958 scans, 117 threats, 87.8% safety rate) came from ONE local SQLite demo. safety_rate = (url_checks − HIGH/CRITICAL) / total. Do NOT put these numbers on slides as product KPIs or accuracy.

COMMUNITY REPORTS: one signal, not legal proof, not a verdict.

INTEL: miss = no_match ≠ SAFE. timeout = unavailable ≠ SAFE.
HTTPS / padlock ≠ genuine SBI / PayPal / bank.

CHANNELS:
Email / WhatsApp / SMS = user PASTES the text into the dashboard. Chrome cannot read the phone. No inbox OAuth.
QR: OpenCV reads the code. PHISHEYE does NOT HTTP-fetch the QR destination just to decode it.
Screenshot OCR: PARTIAL. Works only if Tesseract is installed. Not in Python requirements.txt. QR in screenshots is implemented without Tesseract.

EXTENSION: Manifest V3 1.8.0. Load unpacked. Not Web Store.
Does not read passwords, OTPs, cookies, or phone SMS.
Does not rewrite page hrefs.

PSYCHOLOGY GUARD: if psychological score is high but url/domain/threat_intel/brand/community are all weak, fused score is capped at 35 (MEDIUM). Psychology cannot solo HIGH/CRITICAL.

Keep slides visually BRIEF (short bullets). Put extra truth in speaker notes, not as walls of body text.

This is a Lenovo deck. Do not brand it Smart India Hackathon / NTRO unless a tiny “origin problem: lookalike domains” note is needed. Do not make SIH the title.

================================================================================
DESIGN SYSTEM — PREMIUM BLUE (MANDATORY)
================================================================================

THIS IS THE MOST IMPORTANT VISUAL RULE.
Do not use PHISHEYE product red (#E10600, #FF0000, scarlet, crimson).
Do not use a black-and-red “threat console” look.
Do not put a red left rail, red top bar, or red CTA blocks as the theme.

Gamma theme to pick if a picker exists: Navy, Midnight, Ice, Cobalt, Executive Blue, or similar.
If you generate custom colors, lock to this palette only:

Background (deep navy, not pure black):  #0B1F3A
Surface / cards:                         #122A4A
Card hairline:                           #1E3F6B
Primary text:                            #F4F8FF
Secondary text:                          #A9C2E0
Accent (ice / royal blue):               #4C9BFF
Accent 2 (pale ice):                     #B7D4FF
Accent 3 (deep cobalt for filled boxes): #1A4F9C
Muted footer:                            #7A97B8
Warning only (CRITICAL / DANGER labels): #E8B84A amber — never red
Success / LOW (if needed):               #7DCEB8  (soft teal, not traffic-light green)

Title slide: full-bleed navy, large white wordmark, a single thin ice-blue underline. Lots of empty space.
Cards: navy panels with a 3px ice-blue left edge (not red).
Arrows and kicker labels: ice blue #4C9BFF.
The last box in a flow may be filled cobalt #1A4F9C with white text — not a red “LOSS” brick.
Diagrams: same blue language throughout. One visual system, 12 slides.

Typography: large confident sans for titles (editorial, not techno-glitch). Clean sans for body. Monospace only for APIs, weights, hostnames, URLs.
Layout: one idea per slide. Wide margins. Thin ice-blue hairline at the very top. Footer: PHISHEYE · LENOVO HACKATHON · SOFTWARE · 01/12 in muted blue-gray.

Forbidden visuals: red theme, product screenshot colors as the slide chrome, neon magenta, hacker green-on-black, orange “alert” backgrounds, 3D glassmorphism, hoodie stock photos, random hex grids.

Screenshots of the real black/red app MAY appear as photos on slides 8 and 11. Frame them in a navy bezel. Do not let that red leak into titles, footers, or diagram boxes.

Canvas: 16:9 (13.333 × 7.5 in).
Diagrams: left-to-right or top-to-bottom boxes with short labels. Ice-blue arrows. Real names from this prompt (FastAPI, sqlite3, decision_engine, risk_engine.fuse).
Screenshots: if the user uploads them, use real UI. Never fake a UI screenshot.

Screenshot files the presenter can upload (local repo):
docs/_leap_media/01_landing.png
docs/_leap_media/02_dashboard.png
docs/_leap_media/05_scan.png
docs/_leap_media/07_history.png
docs/_leap_media/10_reports.png
docs/_leap_media/11_privacy.png
docs/_leap_media/12_advisor.png
docs/_leap_media/13_extension.png  (install page: Browser protection / Download PHISHEYE extension)

================================================================================
PRODUCT — FULL VERIFIED FACT SHEET
================================================================================

NAME ON UI, API, AND EXTENSION: PHISHEYE
Older names in docs only (do not put on slides): PhishShield AI, CyberGuard.

WHAT IT IS
A software prototype that:
1) accepts a URL, pasted scam text, QR image, screenshot, or a browser navigation,
2) scores phishing / lookalike / social-engineering evidence,
3) returns Simple View (plain English) + Technical View (tags, reasons, intel),
4) stores the check in SQLite,
5) if the Chrome extension is installed, can keep HIGH/CRITICAL sites closed until the user is warned.

WHY IT EXISTS (problem, not a statistic)
People receive SMS/WhatsApp/email: fake KYC, blocked account, share OTP, UPI.
The fake page can have HTTPS. Non-technical users do not parse certificate warnings.
Lookalike examples the product is designed to catch (illustrative hostnames, not a live hit list on the slide unless demoed):
paypa1.com · sbi-login.xyz · amaz0n-secure.tk · hdfc-login.vercel.app

WHO IT IS FOR
- Recipients of OTP/UPI/KYC lures who need “do not enter OTP” not “SSL mismatch”
- An operator using the signed-in React console (history, stats, reports)

TWO CLIENTS, ONE ENGINE
React dashboard localhost:5173 (Vite) talks to FastAPI localhost:8000
Chrome MV3 extension talks to the same FastAPI (local or Render)
API title: PHISHEYE API version 2.0.0

FRONTEND PAGES (IMPLEMENTED ROUTES)
Public: /  landing, /login, /signup, /extension install
Auth console: /dashboard, /scanner, /history, /reports, /statistics, /privacy, /settings, /advisor
Also: /scan-result
Landing CTAs include Analyze URL, Upload screenshot, Get browser protection.

BACKEND ROUTERS
threat_detection, user, stats, analyze, reports, scans
Health: GET /health → {"status":"ok"}
GET / lists endpoints.

IMPLEMENTED APIS (you may show a subset on architecture, not all on one slide)
POST /api/v1/threat/check-url
POST /api/v1/threat/check-message
POST /api/v1/analyze/content
POST /api/v1/analyze/url
POST /api/v1/analyze/email
POST /api/v1/analyze/qr
POST /api/v1/analyze/screenshot
POST /api/v1/report
POST /api/v1/feedback
GET  /api/v1/reputation/domain/{domain}
GET  /api/v1/scans
GET  /api/v1/threat/intel-status
GET  /api/v1/stats/overview
GET  /api/v1/stats/sources
GET  /api/v1/stats/timeline
Signup / login / profile under /api/v1/user/*

PIPELINE (ALWAYS THIS ORDER)
INPUT → NORMALIZE → (SSRF-safe short-link unwrap if needed) → THREAT INTEL + HEURISTICS + PSYCHOLOGY + BRAND + TLS + AGE → DECIDE (floors or fuse) → SIMPLE + TECHNICAL VIEW → SQLITE → EXTENSION GATE (if extension)

URL PATH (single address)
url_checker.analyze then decision_engine.calculate_final_risk
ml_score on this path is the lexical/heuristic URL score, exposed so a low value cannot be read as “the model says safe.”

INTEL FLOORS (confirmed_malicious)
exact_url 85
normalized_url 80
hostname 72
registered_domain 55
Score = max(heuristic, floor). Heuristics cannot veto a confirmed feed hit.
Unverified “reported” intel floors around 58 and is classified SUSPICIOUS, not treated as clean.
If intel is unavailable: that is said in the explanation. Unavailable ≠ clean.

CONTENT PATH (pasted message / several links / QR text)
Extract links, score each URL, take strongest, then risk_engine.fuse(signals, weights).
DEFAULT_WEIGHTS (sum 1.0) — you MAY print these on the risk slide:
url 0.22
domain 0.16
ml 0.10          ← copy of URL risk, not a neural net
nlp 0.10         ← psychology score
psychological 0.10
threat_intel 0.10
brand 0.08
redirect 0.04
sender 0.05
community 0.05
False-positive guard: if psychological ≥ 20 and none of url/domain/threat_intel/brand/community ≥ 40, score = min(score, 35).

RISK LEVELS
LOW 0–29
MEDIUM 30–49
HIGH 50–69
CRITICAL 70–100

SIMPLE VIEW VERDICTS (from warnings.py)
DANGER (HIGH/CRITICAL or confirmed intel / missing domain as designed)
BE CAREFUL (MEDIUM)
NO MALICIOUS INDICATORS (LOW) — and the LOW text explicitly says this is NOT a guarantee of safety; absence from feeds does not mean legitimate; still check the address bar.

Example Simple View lines you MAY quote (they exist in code):
- “This website looks like {brand}, but it is not the real {brand}. Do not enter your password, OTP, or bank details.”
- “Threat-intelligence feeds confirmed this address as malicious.”
- “This domain does not exist.”
- “A padlock alone does not mean the site is genuine.”
- LOW URL: “No malicious indicators were detected. That is not a guarantee of safety.”

Brand short names in Simple View include SBI, HDFC Bank, ICICI Bank, IRCTC, PayPal, Amazon, Google, Paytm, PhonePe, Flipkart, WhatsApp, etc. (mapping in warnings.py). Do not claim we legally represent those brands.

PSYCHOLOGY 2.0 — CATEGORIES AND POINTS (psychology.py)
urgency_detected 12 — urgent, act now, immediately, last chance, abhi click, jaldi karo, turant
fear_tactics 12 — account blocked, will be blocked, suspended, legal action, band ho jayega
authority_impersonation 12 — bank security, government notice, RBI, cyber cell, kyc department
coercion 10 — failure to verify, mandatory kyc, or your account
financial_pressure 10 — payment required, refund pending, transfer now
credential_pressure 14 — enter otp, share otp, confirm password, aadhaar otp, complete kyc
countdown 8 — expires in, within 10 minutes, within 5 minutes
greed_bait 10 — you won, lottery, prize, claim now, inaam
secrecy 8 — do not tell, keep this confidential
emotional_manipulation 10 — help me urgently, hospital bill, please beta
Matching is lowercase substring, English + Hinglish. NOT BERT. NOT sentiment-NN.
On URL-only checker, psych score is scaled (about ×0.4, cap 40).

THREAT INTEL PROVIDERS IN CODE
OpenPhish, URLhaus, PhishTank, Phishing Army, optional Google Safe Browsing (needs GOOGLE_SAFE_BROWSING_API_KEY).
Feeds warmup on API startup unless PHISHEYE_SKIP_FEED_WARMUP is set.

OTHER URL CHECKS (IMPLEMENTED)
Normalize URL (https if missing, registered domain, www handling)
Shortener unwrap AFTER SSRF block: localhost, private IPs, link-local, cloud metadata 169.254.169.254
If short link cannot unwrap: extra risk (hidden destination)
Domain DNS exists; if not: +35, tag domain_not_found
RDAP/WHOIS-style age: <30 days +20 tag new_domain; <90 days +10
TLS/SSL inspect (hostname mismatch, expired, untrusted tags exist)
Brand / lookalike / leetspeak / free-host + login patterns
Trusted real destinations (Google, GitHub, etc.) skip noisy heuristics; confirmed intel still wins
Ads / clutter signals exist in url_checker
Sender analysis when From / Reply-To is provided on content scans

EXTENSION BEHAVIOR (IMPLEMENTED)
Permissions: tabs, storage, webNavigation; host permissions for http/https
Service worker intercepts navigation, calls check-url
Badge: OK / MED / HIGH / CRIT / …
canOpenAfterScan: safe (LOW) → true; medium → only if user continues; else false
HIGH/CRITICAL stay closed
Optional settings: pre-navigate gate, scan all pages
Install: chrome://extensions → Developer mode → Load unpacked → folder with manifest.json
Zip on dashboard: /phisheye-extension.zip with live API baked at Render build

AUTH / PRIVACY (IMPLEMENTED)
bcrypt password hash + JWT
Stored: username, email, password hash, scanned URLs + scores (SQLite)
JWT in browser localStorage
Privacy page states what is stored vs local
Extension does not scrape password fields

SECURITY (IMPLEMENTED)
SSRF guard, hop-by-hop redirect checks, outbound timeouts, parameterized SQL, 5 MB upload limit, JWT on report/feedback/delete, report rate limits
CORS: FRONTEND_ORIGINS, often * on prototype (credentials off when *). Do not call this production lock-down.

DATABASE TABLES (LIVE SQLITE)
users, url_checks, threats, content_scans, extracted_links, plus reports / scan_feedback
Free Render: SQLite resets on deploy unless a persistent disk is added.

DEPLOY
render.yaml: Python API phisheye-api + static phisheye-web
LIVE (do not change):
https://phisheye-web-fhn5.onrender.com
https://phisheye-web-fhn5.onrender.com/extension
https://phisheye-api.onrender.com/health
https://phisheye-api.onrender.com/docs
Free API sleeps ~15 minutes. Jury must hit /health first.

LOCAL START
Backend: uvicorn app.main:app --host 0.0.0.0 --port 8000
Frontend: npm run dev on 127.0.0.1:5173

TESTS
pytest under backend/tests/ (api, psychology, threat intel, qr, ssl, golden detection, url normalize, multichannel). These test behaviour, NOT published F1.

SCRIPTS THAT ARE NOT PRODUCT METRICS
backend/scripts/accuracy_simulation.py
backend/scripts/phishtank_live_eval.py
Do not quote numbers from these as official product accuracy.

FUTURE / NEXT PHASE ONLY (must label FUTURE)
Supervised model after curated human reports
PostgreSQL at scale
Android SMS companion
Official Gmail/Outlook OAuth if granted
Campaign clustering
Calibrated fraud probability
Deep attachment sandbox
Automatic retention deletion

================================================================================
MAKE EXACTLY 12 SLIDES — DETAILED BLUEPRINT
================================================================================

SLIDE 1 TITLE
Kicker (mono, ice blue #4C9BFF): LENOVO HACKATHON · SOFTWARE · CYBERSECURITY
Huge: PHISHEYE
Sub: Scan the link before the fake page loads.
Two lines: Explainable phishing and lookalike-domain detection. One FastAPI engine. React console. Chrome scan-before-open gate.
Footer meta: Working prototype · No hardware · No trained CNN · SQLite live
No people names. No fake Lenovo partnership badge.

SLIDE 2 PROBLEM
Headline: A padlock does not mean it is your bank.
Diagram 5 boxes: ATTACKER → TRUST (fear/OTP) → FAKE HTTPS LINK → VICTIM → LOSS
LOSS box: filled cobalt blue, not red.
Left panel: example SMS (illustration): “Your SBI account will be blocked. Complete KYC in 10 minutes. Share OTP.”
Right panel: victim cannot use certificate jargon; Simple View is for them.
Do not add “billions lost in India” or any uncited number.

SLIDE 3 GAP
Headline: Feeds are late. Certificates are not brands. Panic is a signal.
Four equal panels:
1 Technical: lookalike, new domain, TLS, SSRF-safe unwrap
2 Social engineering: English + Hinglish phrase rules
3 Threat intel: confirmed hit floors the score; miss ≠ SAFE
4 Act: scan-before-open + “do not enter OTP”
Honesty strip: we do not rank VirusTotal; we gate the tab first.

SLIDE 4 INTRODUCING PHISHEYE
Headline: Score the lure. Explain it. Optionally block the tab.
Flow: INPUT → ANALYZE → FUSE/FLOOR → RESULT (LOW–CRITICAL) → ACT
Three columns:
Protects: KYC/OTP recipients + console operators
Analyzes (implemented only): URL, pasted SMS/WA/email, QR (no visit), screenshot (QR; OCR if Tesseract), extension navigation
Produces: 0–100 + level, Simple View, Technical View, SQLite row, allow/hold/block

SLIDE 5 ARCHITECTURE
Headline: Clients → FastAPI → analyzers → decide → SQLite → explain.
Rows (real names):
USER | Paste or navigate | Two clients, one brain
API | FastAPI + Uvicorn :8000 | Not Flask. GET /health
SERVICES | URL, brand, TLS, SSRF, QR | Intel feeds + psychology rules
DECIDE | decision_engine floors (URL) | risk_engine.fuse (content)
STORE | sqlite3 threats.db | Simple + Technical View
Must show Not Flask / Not live Postgres / Not a CNN as small labels, not as the only headline.

SLIDE 6 INTELLIGENCE
Headline: Explainable scoring. No trained model file in this repository.
Pipeline: RAW → PREPROCESS (normalize, SSRF unwrap) → FEATURES (TLD, lookalike, age, keywords) → SIGNALS (intel, psych, brand, community) → DECISION (floors + fuse)
Must-state: channel “ml” copies URL score
Must-state: no sklearn / TensorFlow / CNN / published F1
Confidence formula in notes or small type: min(95, 35+10×count(signals≥20))

SLIDE 7 PSYCHOLOGY
Headline: Rules that read panic. Not a neural language model.
Example box: “Your account will be blocked. Verify immediately.”
Hits: fear_tactics + urgency_detected + credential_pressure
Hinglish from code: abhi click · jaldi karo · band ho jayega · complete kyc
Guardrail box: cannot solo HIGH/CRITICAL; fuse cap 35
Ten small tags with a real phrase each (from the category list above). Show points only if space; do not invent new categories.

SLIDE 8 EXTENSION + CHANNELS
Headline: Scan first. Then maybe open.
Left: URL · pasted text · QR (OpenCV, no visit) · screenshot · extension
Center flow: navigate → service worker holds tab → POST check-url → LOW open / MEDIUM ask / HIGH-CRIT closed
Right: upload 13_extension.png if provided. Caption: install page, Load unpacked, API baked to Render.
MV3 1.8.0. Does not read passwords or SMS. Not Web Store.

SLIDE 9 RISK + EXPLAINABILITY
Headline: Two views. One score. Documented combination.
Left SIMPLE VIEW: quote “Do not enter your password, OTP, or card number.” Verdicts: NO MALICIOUS INDICATORS · BE CAREFUL · DANGER. LOW is not a guarantee.
Right TECHNICAL VIEW: domain tags, TLS, RDAP age, intel provider + match type, heuristic reasons, psych findings, model_confidence = agreement
Bottom left: URL floors (85/80/72/55)
Bottom right: content weights (print the 10 weights)
Levels: LOW 0–29 · MED 30–49 · HIGH 50–69 · CRIT 70–100

SLIDE 10 STACK
Headline: What we actually run.
8 groups, one-line jobs, only listed tech:
FRONTEND: React 19, Vite 8, Tailwind 4, Axios, Recharts
BACKEND: FastAPI, Uvicorn, Pydantic, bcrypt, JWT
DATA: sqlite3 threats.db (Postgres = FUTURE)
INTELLIGENCE: heuristics + fusion + feeds (not a trained net)
SECURITY: SSRF, parameterized SQL, 5 MB uploads
EXTENSION: Chrome MV3 1.8.0, same API, Load unpacked
EXTERNAL: OpenPhish, URLhaus, PhishTank, Phishing Army, optional GSB
DEPLOY: Render API + static web; wake /health; free sleep ~15 min
No logo salad. No Docker/K8s unless you mark unverified — they are not the documented live path. Skip them.

SLIDE 11 WORKING PRODUCT
Headline: Running UI. Not a mockup.
Collage of uploaded real screenshots: landing, scanner (URL/Message/Email/WhatsApp/Screenshot/QR tabs), history, dashboard.
Caption: SQLite-backed console. Do not print 87.8% as accuracy.
If no images uploaded, use labeled wireframe captions of those screens — still do not fake pixels.

SLIDE 12 IMPACT + FUTURE + CLOSE
Headline: Protect people who cannot read a certificate warning.
NOW: scan-before-open · OTP-language Simple View · paste analysis · community as signal
FUTURE (must say FUTURE): labelled supervised model · PostgreSQL · Android SMS companion · official inbox APIs
Live demo URLs in small mono:
https://phisheye-web-fhn5.onrender.com
https://phisheye-api.onrender.com/health
Close (large):
Phishing + social engineering + threat intelligence + explainable scoring + browser protection = PHISHEYE

Do not generate slide 13. Do not add Q&A as a slide. Do not add a fake ROI slide. Do not add hardware. Stop.

================================================================================
SPEAKER NOTES (ATTACH TO EACH SLIDE IF GAMMA SUPPORTS NOTES)
================================================================================

1: Name PHISHEYE once. Dashboard + extension, same FastAPI. No Flask, no CNN, no hardware.
2: Tell OTP/UPI story. HTTPS is cheap. Point at LOSS.
3: Difference vs after-click scanners: we can hold the tab.
4: WhatsApp means paste. QR means OpenCV, no visit.
5: sqlite3 is live. Postgres planned. SQLAlchemy models unused.
6: If they ask for CNN accuracy: there is none. ml copies URL score.
7: Read the example, then the cap 35, then Hinglish.
8: Demo github.com if LOW; lookalike stays closed; never open a live phishing kit.
9: Confidence is agreement. LOW Simple View still says not a guarantee.
10: If they say AI, point at fusion + intel. If they say DB, say SQLite.
11: Screenshots are the running app. Do not quote demo SQLite ratios as F1.
12: Say the word FUTURE. Close on the last line. Wake /health before demo.

================================================================================
FINAL QA YOU MUST RUN ON YOUR OWN OUTPUT
================================================================================

Search your generated slides for: Flask, PostgreSQL (unless FUTURE), CNN, 99%, F1, ESP32, Raspberry, IoT, Web Store, BERT, TensorFlow, “reads WhatsApp”, “reads SMS”, blockchain, team member names, 87.8%, 958 scans.
Also reject the deck if the chrome/theme is black-red, scarlet, or matches the PHISHEYE app. Theme must stay navy + ice blue.
If found as a CURRENT CLAIM (not a “we do not” / FUTURE line), DELETE IT.

Every architecture box must match the pipeline in this prompt.
Every channel must be implemented as paste/QR/extension, not native inbox.

Then stop.

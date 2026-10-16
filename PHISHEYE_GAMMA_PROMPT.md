# PHISHEYE_GAMMA_PROMPT.md

**9-slide jury story (not 15).**  
Copy **everything from `===== PASTE INTO GAMMA START =====` to `===== PASTE INTO GAMMA END =====`** into [gamma.app](https://gamma.app).

Then:
1. Sign in → **Create new** → **Paste in text**
2. Type: **Presentation** · **16:9** · **exactly 9 cards**
3. Theme: premium navy / ice blue (or upload your template)
4. Prefer **Generate from notes or an outline**
5. Upload screenshots from `docs/_leap_media/` when asked (landing, dashboard, scan, history, extension)

Do **not** paste the other `PHISHEYE_*.md` files into Gamma.

---

===== PASTE INTO GAMMA START =====

ROLE
You are a senior hackathon presentation designer for an industry jury (Lenovo).
Build a PREMIUM 9-slide executive cybersecurity deck for PHISHEYE.
Use the visual template the user uploaded. If none is uploaded, use midnight navy + ice cyan only.

This deck must feel like a board briefing, not a college assignment and not a SOC dashboard.

STORY (do not reorder, do not add slides):
PROBLEM → SOLUTION → AI/ML → PSYCHOLOGY → WORKFLOW → ARCHITECTURE → EXPLAINABILITY → FEASIBILITY → PROOF + IMPACT

Product: PHISHEYE
Event: Lenovo Hackathon
Category: Software + Cybersecurity
Status: working software prototype (local + Render). Not a finished enterprise product.
Hardware: none. Team names / college: omit unless the user typed them.

One-line value proposition (use this wording):
Scan the link before the fake page loads.

PALETTE (keep even if the template is used for layout):
Background #0B1F3A · Surface #122A4A · Hairline #1E3F6B · Text #F4F8FF · Secondary #A9C2E0 · Accent #4C9BFF · Pale ice #B7D4FF · Cobalt fill #1A4F9C · Amber warning #E8B84A · Soft teal #7DCEB8 · Footer #7A97B8

NEVER use product red, scarlet, hoodie stock, neon hacker green, glassmorphism everywhere, circuit boards, or “AI brain” clipart.
Footer every slide: PHISHEYE · LENOVO HACKATHON · SOFTWARE · 01/09 (increment)
On-slide text BRIEF. Extra truth in speaker notes.

================================================================================
ABSOLUTE RULES — A FALSE CLAIM FAILS THE DECK
================================================================================

USE ONLY THIS PROMPT. Do not browse. Do not add phishing statistics (billions lost, 90% of attacks). They are not sourced here.

DO NOT INVENT: accuracy, precision, recall, F1, dataset size, user counts, money saved, 99%, latency benchmarks, team names, college, Lenovo partnership.

DO NOT CLAIM AS CURRENT: Flask, live PostgreSQL, Redis, Kafka, Kubernetes, Docker as the live path, trained CNN / Random Forest / XGBoost / BERT / TensorFlow / sklearn .pkl, Chrome Web Store, Gmail OAuth, native WhatsApp/SMS inbox, blockchain, ESP32 / Raspberry Pi / IoT.

DO NOT RANK COMPETITORS. Never say better / best / superior.
Allowed difference: “Many conventional tools emphasize technical URL indicators. PhishEye also scores human-facing social-engineering phrases and explains the result in OTP language.”
Allowed design difference (not a benchmark): after-click scanners research a URL after the visit; PHISHEYE can hold the Chrome tab first.

LIVE DATABASE: sqlite3 file backend/threats.db.
PostgreSQL = FUTURE / proposed production only. If the architecture sketch shows Postgres, it MUST be labeled FUTURE. The live box is sqlite3.

AI / ML TRUTH (required on slide 3):
There is no trained model file in this repository.
Intelligence = heuristic URL scoring + public threat feeds + phrase-matching psychology + documented fusion / intel floors.
Fusion key "ml" COPIES the lexical URL risk score so a low “ML” number cannot be used as proof of safety.
NumPy reshapes OpenCV QR images — not neural nets.
model_confidence = min(95, 35 + 10 × count(signals ≥ 20)) = signal AGREEMENT, not accuracy.

Dashboard demo ratios (958 scans, 87.8%) are NOT product KPIs. Never print them.

Psychology is RULE-BASED lowercase substring match (English + Hinglish), not BERT.
If psych is high but url/domain/intel/brand/community are weak, fused score is capped at 35. Psychology cannot solo HIGH/CRITICAL.

Email/WhatsApp/SMS = user PASTES text. We do not read inboxes.
QR = OpenCV decode. We do not HTTP-fetch the QR destination just to decode it.
OCR = PARTIAL (Tesseract optional, not in requirements). Screenshot QR works without Tesseract.

Extension MV3 1.8.0, Load unpacked, not Web Store.
LOW opens · MEDIUM asks · HIGH/CRITICAL stay closed · API unavailable stays closed.
Does not read passwords, OTPs, cookies, or phone SMS.

Intel miss ≠ SAFE. Timeout ≠ SAFE. HTTPS padlock ≠ real bank.
Community report = one signal, not proof.

MAKE EXACTLY 9 SLIDES. No title-only extra slide. No slide 10. No fake ROI slide. No Q&A slide.

================================================================================
VERIFIED FACTS (ONLY THESE)
================================================================================

WHAT PHISHEYE IS
A software prototype that scores phishing / lookalike URLs and pasted scam content, explains the result in Simple View + Technical View, stores the check in SQLite, and can hold a Chrome tab until the scan finishes.

TWO CLIENTS, ONE ENGINE
React 19 + Vite 8 dashboard (:5173) and Chrome MV3 talk to FastAPI + Uvicorn (:8000), PHISHEYE API 2.0.0.

INPUTS IMPLEMENTED
URL · pasted SMS/WA/email · QR image · screenshot (QR; OCR if Tesseract) · extension navigation

PIPELINE
INPUT → NORMALIZE → SSRF-safe short-link unwrap → URL/DOMAIN/TLS/BRAND HEURISTICS + THREAT INTEL + PSYCHOLOGY RULES → DECIDE (intel floors OR static fuse) → SIMPLE + TECHNICAL VIEW → SQLITE → USER ACTION / EXTENSION GATE

URL PATH
url_checker → decision_engine.calculate_final_risk
Score = max(heuristic, intel_floor)
Floors (confirmed_malicious): exact_url 85 · normalized_url 80 · hostname 72 · registered_domain 55
ml_score = copy of lexical URL score

CONTENT PATH
Extract links, strongest URL, then risk_engine.fuse
STATIC WEIGHTS (sum 1.0): url 0.22 · domain 0.16 · ml 0.10 (copy) · nlp 0.10 (psych) · psychological 0.10 · threat_intel 0.10 · brand 0.08 · redirect 0.04 · sender 0.05 · community 0.05
Weights are defaults, not learned.

LEVELS: LOW 0–29 · MEDIUM 30–49 · HIGH 50–69 · CRITICAL 70–100

SIMPLE VIEW quotes you MAY use:
“Do not enter your password, OTP, or bank details.”
“A padlock alone does not mean the site is genuine.”
LOW: “No malicious indicators were detected. That is not a guarantee of safety.”

PSYCHOLOGY CATEGORIES (psychology.py) with static points:
urgency 12 (act now, immediately, jaldi karo, abhi click)
fear 12 (account blocked, band ho jayega)
authority / impersonation 12 (bank security, RBI, cyber cell, kyc department)
coercion / pressure 10 (mandatory kyc, failure to verify)
credential / OTP request 14 (enter otp, share otp, complete kyc)
countdown 8 (expires in, within 10 minutes)
greed 10 · secrecy 8 · emotional 10

INTEL: OpenPhish, URLhaus, PhishTank, Phishing Army, optional Google Safe Browsing.
OTHER: DNS exists, RDAP age (<30 days +20), TLS inspect, lookalike/leetspeak, SSRF block of private IPs and 169.254.169.254.

SECURITY IMPLEMENTED: bcrypt+JWT, parameterized SQL, SSRF, 5 MB uploads, JWT on report/delete, QR in memory.
PROTOTYPE LIMITS: CORS often *, SQLite on free Render, token in localStorage, no auto-retention. Not SOC2.

DEPLOY NOW: Render API + static web
https://phisheye-web-fhn5.onrender.com
https://phisheye-api.onrender.com/health
Free API sleeps ~15 min. Hit /health first.

TESTS: pytest behaviour tests. NOT published F1.

FUTURE: supervised model after curated reports · PostgreSQL · Android SMS companion · inbox APIs if granted · Chrome Web Store · cache/replicas

================================================================================
EXACTLY 9 SLIDES
================================================================================

SLIDE 1 — PROBLEM STATEMENT
Kicker (mono ice): LENOVO HACKATHON · PHISHEYE
Headline: A padlock does not mean it is your bank.
One line: Users still fall for phishing because the attack targets trust, not just the URL.
Diagram (last node cobalt, never red):
ATTACKER → DECEPTIVE MESSAGE / LINK → HUMAN TRUST (fear, urgency, authority) → CLICK → FAKE HTTPS SITE → OTP / UPI / PASSWORD LOSS
Left: illustration SMS — “Your SBI account will be blocked. Complete KYC in 10 minutes. Share OTP.”
Right three chips:
• Social engineering (panic, impersonation)
• Human error (OTP shared before the address is checked)
• Technical warnings fail people who will not parse certificates
No statistics.

SLIDE 2 — PROPOSED SOLUTION: PHISHEYE
Headline: PHISHEYE
Value proposition (large): Scan the link before the fake page loads.
What it is (one sentence): A working software prototype that scores a URL or pasted lure, explains the risk in OTP language, and can hold a Chrome tab closed when risk is HIGH, CRITICAL, or the API is unavailable.
What makes it different (not “better”):
• Conventional detectors often stop at URL / blacklist signals
• PhishEye also scores social-engineering phrases and returns Simple View + Technical View
• Same FastAPI engine for the React console and the Chrome scan-before-open gate
• Intel miss ≠ SAFE
Three columns: INPUT (URL / paste / QR / navigation) → ANALYZE (heuristics + feeds + rules) → ACT (explain + optional gate)
Do not draw a trained neural net.

SLIDE 3 — AI / ML APPROACH
Headline: Explainable scoring. No trained model file in this repository.
This is the honesty slide. Do not hide it.
Six short blocks:
1 Data / features — this request’s URL or text + public feeds. No labelled product dataset shipped.
2 URL / domain analysis — lexical URL, lookalike/leetspeak, DNS exists, RDAP age, TLS, shortener unwrap after SSRF, brand patterns.
3 “ML” — code key ml COPIES the URL heuristic score. Not RF / XGB / CNN / BERT. No .pkl.
4 NLP / psych — rule-based phrase match, not a neural language model.
5 Inference — each scan is a live function call. No separate model server.
6 Combination — URL path: max(heuristic, intel floors 85/80/72/55). Content path: static weighted fuse. Confidence = agreement, not accuracy.
Pipeline strip: RAW → PREPROCESS → FEATURES → SIGNALS → FLOORS / FUSE → SCORE
Future chip (tiny, labeled FUTURE): curated reports → supervised model.

SLIDE 4 — PSYCHOLOGICAL THREAT DETECTION  ★ STAND OUT
Headline: Phishing is a social-engineering problem. Detection is rule-based, not a neural net.
How it works (must show HOW, not just that it exists):
TEXT → lowercase → substring / phrase match (English + Hinglish) → category points → psych score → fuse (weight 0.10) → cap 35 if psych-only
Six detection cards with a real phrase from code:
• URGENCY — “act now” / “immediately” / “jaldi karo”
• FEAR — “your account will be blocked” / “band ho jayega”
• ACCOUNT-BLOCKING — blocked / suspended / legal action
• ACT-NOW PRESSURE — “verify now” / “within 10 minutes” / “expires in”
• IMPERSONATION — bank security, RBI, cyber cell, KYC department
• CREDENTIAL / OTP REQUEST — “enter OTP” / “share OTP” / “complete KYC”
Guardrail box: psychology cannot solo HIGH/CRITICAL (fuse cap 35).
Do not claim BERT, sentiment-NN, or hybrid-learned NLP.

SLIDE 5 — END-TO-END WORKFLOW  ★ MOST IMPORTANT JURY SLIDE
Headline: From lure to decision.
Use this exact implemented chain (adapt labels, do not add a trained-model box):
INPUT → FEATURE EXTRACTION / PREPROCESS → URL / DOMAIN ANALYSIS → HEURISTIC SCORE (ml = copy) → PSYCHOLOGICAL ANALYSIS (rules) → THREAT INTEL → RISK ENGINE (floors OR fuse) → EXPLANATION (Simple + Technical) → USER ACTION (open / ask / hold)
Annotate each box with one tech word:
Input: React or MV3
Preprocess: normalize + SSRF unwrap
URL/domain: url_checker, TLS, age, lookalike
Heuristic: lexical score
Psych: psychology.py
Intel: OpenPhish / URLhaus / PhishTank / Phishing Army
Risk: decision_engine or risk_engine.fuse
Explain: warnings.py
Action: dashboard + extension gate
Store under the chain: sqlite3 threats.db
Tiny note: content scans fuse; single URL uses intel floors.

SLIDE 6 — TECHNICAL ARCHITECTURE
Headline: What actually runs. Why these technologies.
Live diagram (MUST match code):

USER
 ├ WEB APP (React 19 / Vite)
 └ CHROME EXTENSION (MV3 1.8.0)
        │ HTTPS JSON
     FASTAPI + UVICORN
        ├ Detection engine (url_checker, brand, TLS, SSRF, QR/OpenCV)
        ├ Psychology rules + threat intel
        ├ Risk engine (floors / fuse)
        └ sqlite3 threats.db   ← LIVE
PostgreSQL = FUTURE production (ghost box, dashed, labeled FUTURE)

Why chips (one line, no logo salad):
• Python — detectors, tests, feed clients
• FastAPI — typed JSON APIs, OpenAPI /docs, demoable
• React — operator console
• Chrome MV3 — only supported way to intercept navigation
• sqlite3 — zero-ops prototype persistence
• bcrypt + JWT — accounts without cookies
Not Flask. Not a CNN server. Not live Postgres.

SLIDE 7 — RISK SCORE + EXPLAINABILITY
Headline: Many signals. One decision. Two views.
Risk analysis stack (only implemented):
• Technical / URL indicators
• Domain indicators (age, DNS, lookalike)
• “ML” result = copy of URL score
• Psychological signals (rule-based)
• Threat intelligence (match floors the score; miss ≠ SAFE)
Then two large cards:

SIMPLE VIEW
“This website appears suspicious. Do not enter your password, OTP, or card number.”
LOW is not a guarantee of safety.

TECHNICAL VIEW
Tags · TLS · RDAP age · intel provider + match type · heuristic reasons · psych findings · agreement confidence

Bottom: levels LOW 0–29 · MED 30–49 · HIGH 50–69 · CRIT 70–100
Small print: content weights are static defaults; URL path uses floors 85/80/72/55.

SLIDE 8 — FEASIBILITY, SCALABILITY & SECURITY
Headline: This is a working prototype. Scale is a plan.
Four columns, each with NOW vs PROPOSED:

TECHNICAL — NOW: FastAPI loop, heuristics, feeds, psych rules, pytest. PROPOSED: same APIs, more workers.
DEPLOYMENT — NOW: Render API + static web, Load unpacked extension. PROPOSED: replicas, managed Postgres disk, store/MDM.
SCALE — NOW: one SQLite, intel HTTP, 30s timeout, free sleep ~15 min. PROPOSED: stateless API, cache, indexing (not built).
SECURITY / PRIVACY — NOW: bcrypt+JWT, parameterized SQL, SSRF, no OTP collection, QR in memory, HTTPS on Render URLs. LIMIT: CORS often *, localStorage token, not SOC2.

False positives: psych cap 35, trusted-host quieter heuristics, intel still wins.
False negatives: unknown kits possible; miss ≠ SAFE; we do not claim we catch all zero-days.
No invented costs or QPS.

SLIDE 9 — IMPLEMENTATION, IMPACT & FUTURE
Headline: Built enough to demo. Honest about what is next.
Left — IMPLEMENTED: URL/message/QR/screenshot-QR · Simple+Technical · fusion+floors · MV3 gate · auth · reports · Render
PARTIAL: GSB key · Tesseract OCR
FUTURE: trained model · PostgreSQL · native SMS · Web Store
Center — screenshots if uploaded (landing, scanner, history, extension) in navy bezels. If none, labeled frames, never fake pixels.
Caption: pytest tests behaviour. No published F1. Do not print 87.8%.
Right — who: OTP/UPI/KYC recipients; first-time digital banking; console operators. Not measured user counts.
Use cases: fake KYC SMS (paste) · lookalike bank URL (gate) · QR poster (OpenCV, no visit)
Close (large):
PhishEye aims to make phishing detection understandable enough to act on — not a black-box score with a fake F1.
Live URLs in mono:
https://phisheye-web-fhn5.onrender.com
https://phisheye-api.onrender.com/health

================================================================================
DIAGRAM RULES
================================================================================

Arrows ice-blue. Last flow node may be cobalt fill, never red.
Do not add Redis, Kafka, GPU, hardware, or a neural-net glyph.
Do not show PostgreSQL as the live cylinder.
ml box must say “copy of URL score” if it appears.
Psychology box must say “rules”.

================================================================================
SPEAKER NOTES
================================================================================

1 HTTPS is cheap. The victim shares OTP because of fear, not because they failed SSL. No fake stats.
2 Value is the gate + OTP-language explanation. WhatsApp = paste. Same engine for site and extension.
3 If they ask for CNN/F1: there is none. ml copies URL score. That honesty is the point.
4 Read the example SMS, then HOW (substring + points), then cap 35. Attackers can avoid phrases — limitation.
5 Content fuses; URL uses floors. sqlite3 under the chain.
6 Live is FastAPI + sqlite3 + MV3. Postgres is the production proposal.
7 Quote Simple View. Confidence is agreement. LOW still says not a guarantee.
8 Separate NOW vs PROPOSED out loud. Wake /health before demo. Unavailable is not safe.
9 Screenshots are the running app. Say FUTURE. Close on understandable enough to act on.

================================================================================
FINAL QA
================================================================================

Search the 9 slides for: Flask, live PostgreSQL, CNN, F1, 99%, BERT, TensorFlow, ESP32, IoT, Web Store, “reads WhatsApp”, blockchain, 87.8%, Random Forest, “best detector”.
If found as a CURRENT claim, delete it.
Theme must stay navy + ice blue (or the uploaded template’s navy family), not product-red.
Psychology must be labeled rule-based.
ml must be labeled as a URL-score copy.
Exactly 9 slides. Then stop.

===== PASTE INTO GAMMA END =====

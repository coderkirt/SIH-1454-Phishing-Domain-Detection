# PHISHEYE — COMPLETE SOURCE DOCUMENT FOR CHATGPT / CLAUDE

**This file is long on purpose.** The short version was not enough for an LLM to understand SIH1454, the product, the website, the extension, the detection engine, or how to win the college internal round. Read **every section** before writing a script. Do not skip. Do not invent files, models, or accuracy numbers.

**How students use this**

1. Copy this **entire** markdown file.
2. Paste into ChatGPT (GPT-4o / 5) or Claude (Sonnet / Opus). Prefer Claude or a long-context ChatGPT if the model truncates.
3. If the model says the message is too long, attach the file instead of pasting, or split: paste **Sections 0–18 first**, then **Sections 19–end** in a second message saying “continue using the first paste.”
4. After pasting, send only this: `Follow Section 0. Do not invent anything.`

**Product names in this repo**

| Name | Meaning |
|---|---|
| **PHISHEYE** | Current product name on the UI, API title, and Chrome extension |
| PhishShield AI | SIH slide / idea title used in some docs |
| CyberGuard | Older code name in comments |

Always say **PHISHEYE** to the jury. If a slide still says PhishShield, say: “PhishShield is the SIH idea title. The running product is PHISHEYE.”

**Team ID / Team Name:** not in the repository. Fill from the SIH portal. Never invent them.

---

## 0. MASTER PROMPT FOR THE LLM

```
You are a Smart India Hackathon internal-round coach and technical writer.

You have received a COMPLETE source document about PHISHEYE, a working SIH1454 prototype (NTRO, Blockchain & Cybersecurity, Software).

YOUR JOB — produce ALL of the following in one reply, in this order:

A) A 60-second elevator pitch (spoken English).
B) A 12-minute jury script, timed every 30–60 seconds, written as spoken lines a student can read aloud. Include who speaks (Lead / Backend / Frontend / Extension) and exact demo click-by-click lines.
C) A 3-minute emergency script if Wi-Fi or the demo laptop fails.
D) Slide-by-slide speaker notes for the official 6 SIH slides (title, idea, technical approach, feasibility, impact, research).
E) Mermaid diagrams: (1) system architecture (2) website page map (3) URL scan sequence (4) message/QR pipeline (5) extension gate sequence (6) decision engine vs fusion.
F) 40 viva questions with 20–45 second spoken answers, using ONLY this document. Include “if they push back” follow-ups.
G) A one-page cheat sheet the team can print (stack, ports, demo URLs, honesty lines, closing sentence).
H) Internal-round winning tactics specific to Indian college faculty panels (HOD, CSE, maybe one industry person): marking scheme, body language, time control, how to look original vs GitHub clones.

HARD RULES
- Product: PHISHEYE.
- Backend: FastAPI + Uvicorn. NEVER Flask.
- Database live today: SQLite file backend/threats.db. NEVER say live PostgreSQL. Postgres is planned only.
- There is NO trained CNN, sklearn, TensorFlow, BERT, or LLM classifier in the repo.
- The fusion channel named "ml" is a COPY of the lexical/heuristic URL score so a low ML number cannot be used as proof of safety.
- Psychology is keyword/phrase rules (English + Hinglish), not neural NLP.
- QR uses OpenCV and does NOT visit the QR destination URL.
- Chrome cannot read phone SMS or native WhatsApp.
- Gmail/Outlook: paste or visible links only. No inbox OAuth.
- Do not claim 99% accuracy, published F1, production users, or blockchain.
- Theme is "Blockchain & Cybersecurity" but this problem is cybersecurity. We did NOT build a blockchain.
- HTTPS / padlock does NOT mean the site is genuine.
- Threat-intel MISS is not SAFE. Timeout is UNAVAILABLE, not SAFE.
- Community reports are a SIGNAL, not legal proof.
- model_confidence = how many signals agreed, NOT detection accuracy.
- If a fact is missing from this document, write “not specified in the brief” instead of inventing it.
- Write simply enough that a non-CS HOD understands, and technically enough that a CSE professor cannot trap the team.
- Include India-specific examples (SBI, UPI, KYC, OTP, IRCTC) because NTRO / SIH cares about Indian users.
```

---

## 1. THE OFFICIAL PROBLEM (SIH1454) — EXPLAIN IT FULLY

| Field | Official value |
|---|---|
| Problem Statement ID | **SIH1454** |
| Title | Create an intelligent system using AI/ML to detect phishing domains which imitate look and feel of genuine domains |
| Theme | Blockchain & Cybersecurity |
| Category | Software |
| Organisation / ministry-style body | **National Technical Research Organisation (NTRO)** |
| Typical SIH year on slides | SIH 2026 template in this repo |

### 1.1 What the sentence actually asks

Break the title into four requirements:

1. **Intelligent system** — not a static blacklist website where a human types a URL into VirusTotal by hand. The system must combine several signals and decide.
2. **Using AI/ML** — SIH wording. In this prototype, “intelligence” is **multi-signal fusion + threat intelligence + lookalike heuristics**. There is **no trained neural network in the repo**. The honest jury line is: *“We implement an explainable intelligence pipeline now. A supervised model is phase 2 after we have curated labelled reports.”*
3. **Detect phishing domains** — catch fake websites used to steal passwords, OTPs, UPI pins, card data.
4. **Which imitate look and feel of genuine domains** — **typosquatting and brand impersonation**, not only “malware .exe downloads.” Examples:
   - `paypa1.com` (digit 1 instead of L)
   - `sbi-login.xyz` (real brand + extra word + cheap TLD)
   - `amaz0n-secure.tk`
   - `www.google.com.evil.xyz` (deceptive subdomain)
   - Unicode lookalikes (Cyrillic “а” that looks like Latin “a”)
   - Free-host fakes: `hdfc-login.vercel.app`

### 1.2 Why NTRO / India cares (story for faculty)

India’s digital public infrastructure grew very fast: UPI, net banking, IRCTC, DigiLocker, Aadhaar KYC. Attackers send SMS and WhatsApp:

> “Your SBI account will be blocked. Complete KYC in 10 minutes. Click here. Share OTP.”

The page looks like the bank. It has a padlock (HTTPS). The victim types the OTP. Money leaves.

Blacklists are late: a new domain can steal for hours before OpenPhish lists it. Users cannot read “SSL certificate mismatch.” Elderly parents and first-time UPI users need **plain English: do not enter OTP.**

### 1.3 Why URL-only is hard

- HTTPS is cheap. Padlock ≠ official brand.
- Short links (`bit.ly`) hide the real host.
- QR codes in posters and WhatsApp images hide the URL until scanned.
- Homoglyphs and leetspeak fool the human eye.
- A feed can list one YouTube `/watch?v=scam` video; that must **not** mark all of YouTube as phishing.
- Absence from a feed is **not** proof of safety (zero-day phishing).

### 1.4 What a winning SIH prototype must show

Faculty / SIH internals typically want:

- A **running** demo, not only slides.
- Mapping to **lookalike domains** (the PS core).
- Something a **non-technical user** can understand.
- Honest engineering, not fake 99% CNN claims.
- A path to scale (feeds, SQLite now, Postgres later, optional trained model later).

PHISHEYE maps to that as: dashboard + Chrome gate + one FastAPI brain + Simple View + Technical View.

---

## 2. WHAT PHISHEYE IS (PRODUCT, NOT SLOGAN)

**One sentence**

PHISHEYE is a working multi-channel scam intelligence prototype: one FastAPI engine scores URLs, pasted messages, QR codes, screenshots, and the browser tab; it explains the result in Simple English and Technical evidence; a Chrome Manifest V3 extension scans **before** the destination site is used, auto-opens clear sites, and keeps fishy or dangerous sites closed.

**Five verbs (use on slides)**

1. **Detect** — URL heuristics, brand distance, feeds, psychology, sender, community.
2. **Understand** — normalize URL, unwrap short links (with SSRF guard), extract many links from one message.
3. **Explain** — Simple View for victims; Technical View for analysts.
4. **Protect** — extension gate: scan first, then open or refuse.
5. **Learn** — logged-in users can Mark Scam / Risky / Safe (rate-limited; signal not proof).

**What it is not**

- Not an antivirus that scans disk.
- Not a police tool that arrests gangs.
- Not a Gmail/WhatsApp spyware.
- Not a blockchain ledger.
- Not a production SOC platform with 10 million users.
- Not a calibrated “87.3% probability of fraud” model.

---

## 3. WHO USES IT (PERSONAS)

| Persona | How they use PHISHEYE | What they see |
|---|---|---|
| Parent / first-time UPI user | Pastes SMS or opens a link; extension blocks | Simple View: “Do not enter OTP” |
| Student | Dashboard Scan tab, QR of a poster | Score, reasons, decoded QR text |
| Campus SOC / CSE student analyst | Technical View, history, statistics, intel providers | Evidence JSON, match type, registered domain |
| Team demo to jury | Prepared URLs + gate | Google LOW auto-open; paypa1 stays closed |

---

## 4. COMPLETE TECH STACK (WHY EACH PIECE)

### 4.1 Frontend (folder `frontend/`)

| Technology | Version / notes | Why |
|---|---|---|
| React | 19 | UI components, pages |
| Vite | 8 | Dev server, fast HMR |
| React Router | 7 | Routes: landing, login, dashboard, scanner… |
| Tailwind CSS | 4 via `@tailwindcss/vite` | Styling |
| Axios | HTTP client | REST calls; JWT interceptor |
| Recharts | Charts | Statistics / dashboard |
| Lucide | Icons | UI |
| Dev port | `http://127.0.0.1:5173` | Browser UI |
| Env | `VITE_API_URL` optional; default API `http://127.0.0.1:8000` | |

**Not used:** Next.js, Angular, Vue, Redux.

### 4.2 Backend (folder `backend/`)

| Technology | Notes | Why |
|---|---|---|
| Python 3 | venv | |
| **FastAPI** | `app/main.py`, title PHISHEYE API v2.0.0 | REST + OpenAPI `/docs` |
| Uvicorn | `uvicorn app.main:app --host 0.0.0.0 --port 8000` | ASGI server |
| Pydantic | Request bodies | Validation |
| python-multipart | QR / screenshot uploads | |
| requests | Feed download, GSB, RDAP | |
| python-dotenv | `.env` for optional GSB key | |
| passlib + bcrypt 4.0.1 | Password hashes | |
| python-jose | JWT HS256 | |
| OpenCV headless + NumPy + Pillow | QR decode | |
| pytest + httpx | Tests | |
| SQLAlchemy | **In requirements but unused for live queries** | Do not say “we run on SQLAlchemy ORM today.” Live path is `sqlite3`. |

**NOT Flask.** If an old nested `app.js` / Express file existed, it is leftover / removed — the live API is FastAPI.

### 4.3 Database

| Live today | Planned |
|---|---|
| SQLite file `backend/threats.db` | PostgreSQL for multi-user production |

Tables (from `backend/app/database/connection.py`):

- `users` — id, username, email, password_hash, created_at
- `url_checks` — id, user_id, url, risk_level, risk_score, ml_confidence, timestamp
- `threats` — id, threat_type, threat_data, severity, last_updated (HIGH/CRITICAL URL checks)
- `content_scans` — multi-channel scans
- `extracted_links` — per-link rows for a content scan
- `user_reports` — community flags
- `domain_reputation` — scam/risky/safe counts per domain
- `scan_feedback` — helpful yes/no

Indexes on url, user_id, timestamp, reports, scans.

**SQL is parameterized** (`?` placeholders) to reduce injection.

### 4.4 Detection / intel

| Piece | Implementation |
|---|---|
| URL normalize | `url_normalize.py` — path kept, fragment dropped, default ports dropped, query stored separately, registered domain |
| Threat intel | OpenPhish feed, URLhaus online list, PhishTank public dump (verified-only without API key), Phishing Army domain list, optional Google Safe Browsing v4 |
| Feed cache | `backend/data/feeds/` TTL 30 minutes; `PHISHEYE_SKIP_FEED_WARMUP` for tests |
| Decision | `decision_engine.py` — intel floors; miss ≠ safe |
| Fusion | `risk_engine.py` — weighted sum |
| Psychology | `psychology.py` substring rules |
| Brand | `url_checker._detect_brand` + `brand_detector.py` |
| TLS | `ssl_certs.py` inspect when reachable |
| Domain age | RDAP/WHOIS-style via `external_intel.py` |
| Redirects | `redirects.py` + `ssrf.py` |
| Ads/clutter | `ad_signals.py` (skipped if intel already confirmed, to avoid fetching phish pages) |
| QR | `qr_analyzer.py` — OpenCV, scale/CLAHE, PIL fallback; **no HTTP GET of destination** |
| Community | `reputation.py` |
| Warnings | `warnings.py` Simple + Technical |

Optional env (never print secrets in a script):

- `GOOGLE_SAFE_BROWSING_API_KEY`
- `PHISHTANK_API_KEY`
- `URLHAUS_AUTH_KEY`
- `ENABLE_ONLINE_CHECKS` (default true)
- `PHISHEYE_SKIP_FEED_WARMUP`

Without GSB key, public feeds still run.

### 4.5 Chrome extension (folder `extension/`)

- Manifest **V3**, name PHISHEYE, version **1.8.0**
- Service worker module: `background/service-worker.js`
- Permissions: `tabs`, `storage`, `webNavigation`
- Host permissions: localhost + all http/https (needed to intercept navigation)
- Content scripts at `document_start`: `gate-clicks.js` + `gate-hold.css`
- Content script at `document_idle`: `content.js` (toasts, outline visible links)
- Gate UI: `panel/panel.html` + `panel.js`
- Popup, settings (includes **Scan every page** toggle, default **off**), welcome
- Same FastAPI `POST /api/v1/threat/check-url` as the dashboard
- Does **not** read passwords, OTPs, cookies, or phone SMS

### 4.6 Tests

pytest under `backend/tests/`. Live feeds are mocked / skipped via warmup skip so CI does not depend on the internet.

---

## 5. SYSTEM ARCHITECTURE (NARRATIVE)

Think of **one brain, many mouths**.

```
[ React dashboard :5173 ]
[ Chrome extension gate / popup ]
        |  HTTP JSON
        v
[ FastAPI :8000 ]
        |
        +-- URLChecker (single URL)
        +-- analyze_content (message / email / WA / QR / screenshot)
        |       ContentNormalizer
        |       URLChecker per link
        |       Psychology, Brand, Sender, Community
        |       fuse() weights
        +-- threat_intel (feeds, never fetches the attacker page to decide intel)
        +-- SQLite threats.db
        v
[ Simple View + Technical View JSON ]
```

Modular monolith: not microservices. One Python process.

Pipeline slogan for slides:

**INPUT → NORMALIZE → ANALYZE → FUSE → EXPLAIN → ACT**

| Stage | Meaning |
|---|---|
| INPUT | URL, pasted text, QR image, screenshot, extension tab URL |
| NORMALIZE | Scheme, host, path, query, extract URLs from text |
| ANALYZE | Intel, DNS/age/TLS, heuristics, psychology, brand, sender |
| FUSE | Weighted score 0–100 + decision-engine floors |
| EXPLAIN | Simple English + technical evidence |
| ACT | Save history; extension open / keep closed; optional community report |

---

## 6. WEBSITE MAP AND CONTROL FLOW (EVERY PAGE)

Auth: JWT in `localStorage` key `cg_token`. Axios attaches `Authorization: Bearer`. Signup/login via FastAPI. Anonymous `check-url` is still allowed (history user_id may be empty).

Theme: light/dark via `ThemeContext`.

### 6.1 Public routes (`PublicLayout`)

| Path | Page | User journey |
|---|---|---|
| `/` | `Landing.jsx` | Brand PHISHEYE, “Web threat analysis system,” capability cards, pipeline chips (URL → Screenshot → Threat intelligence → Analysis → Risk). Can scan URL or screenshot **without** login via widgets. CTA to login/signup. |
| `/login` | `Login.jsx` | Username/password → JWT → `/dashboard` |
| `/signup` | `Signup.jsx` | Create user, bcrypt stored in SQLite |
| `/home` | redirect | Goes to `/` |

### 6.2 Adaptive

| `/scan-result` | Last scan from `sessionStorage`. Logged-in users get `AppLayout` chrome; guests get public layout. |

### 6.3 Protected (`ProtectedRoute` + `AppLayout`)

Left nav (01–09):

| Path | Nav label | What happens |
|---|---|---|
| `/dashboard` | Dashboard | Cards/charts from real `url_checks` / content scans / stats APIs — not fake numbers |
| `/scanner` | Scan | Tabs: URL, Message, Email, WhatsApp/SMS, Screenshot, QR |
| `/scan-result` | Last Result | Score, badge, Simple/Technical, intel providers, QR payload fields, flag actions |
| `/history` | History | Past scans; delete one or all |
| `/reports` | Reports | Community flags the user submitted |
| `/statistics` | Statistics | Recharts: risk distribution, timeline, sources, threat types |
| `/privacy` | Privacy | Honest privacy copy |
| `/advisor` | Advisor | **Rule-based FAQ**, not a chatbot/LLM |
| `/settings` | Settings | Account / preferences |

404: `NotFound.jsx`.

### 6.4 Scanner tabs in detail

**URL tab** — `UrlScanner` → `POST /api/v1/threat/check-url` `{ url, view: "both" }` → `saveLastScan` → navigate `/scan-result`.

**Message tab** — paste full SMS/chat including links → `POST /api/v1/analyze/content` `{ source_type: "text", text }`.

**Email tab** — same plus optional Display name, From, Reply-To → `source_type: "email"` + `sender` object. Sender analysis only works if the user **types** those fields (we do not read Gmail).

**WhatsApp / SMS tab** — paste visible text. UI explicitly says Chrome cannot read phone SMS. `source_type: "whatsapp"`.

**Screenshot tab** — upload image + optional hint URL → `POST /api/v1/analyze/screenshot` multipart. QR decoded always; OCR only if Tesseract is installed on that PC.

**QR tab** — upload PNG/JPG max 5 MB → `POST /api/v1/analyze/qr`. Result includes `qr_payloads`, `qr_urls`, `decoded_text`. Destination is **not** fetched.

Safe Open: if a link is HIGH/CRITICAL, dashboard warns before `window.open`.

### 6.5 Frontend API module (`frontend/src/services/api.js`)

Functions: healthCheck, signup, login, getProfile, checkUrl, checkMessage, analyzeContent, analyzeImage, reportUrl, sendFeedback, getReputation, getThreatStats, getRecentUrls, getOverview, getThreatTypes, getRiskDistribution, getDailySummary, getSources, getTimeline, getReportsSummary, getContentScans, deleteScan, deleteScanHistory, getMyReports.

Timeout 30s. User-friendly errors if backend is down.

---

## 7. ALL BACKEND ROUTES

App: `backend/app/main.py`

CORS: `allow_origins=["*"]` — **dev-weak**. Say “prototype, not production hardening.”

Lifespan: background thread warms threat feeds unless `PHISHEYE_SKIP_FEED_WARMUP`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Status + endpoint list |
| GET | `/health` | `{ status: ok }` |
| POST | `/api/v1/threat/check-url` | Main URL scan; optional `page_signals` |
| POST | `/api/v1/threat/check-message` | Message + optional URL |
| GET | `/api/v1/threat/intel-status` | Are feeds loaded? |
| GET | `/api/v1/threat/stats` | Threat stats |
| GET | `/api/v1/threat/recent-urls` | Recent URL checks |
| POST | `/api/v1/analyze/content` | Unified multi-channel |
| POST | `/api/v1/analyze/url` | Wrapper |
| POST | `/api/v1/analyze/email` | Wrapper |
| POST | `/api/v1/analyze/qr` | Multipart image |
| POST | `/api/v1/analyze/screenshot` | Multipart + hint |
| POST | `/api/v1/user/signup` | Register |
| POST | `/api/v1/user/login` | JWT |
| GET | `/api/v1/user/profile` | Auth required |
| POST | `/api/v1/report` | Mark scam/risky/safe |
| POST | `/api/v1/feedback` | Helpful? |
| GET | `/api/v1/reputation/domain/{domain}` | Community counts |
| GET | `/api/v1/scans` | Content scan history |
| DELETE | `/api/v1/scans/{id}` | Delete one |
| DELETE | `/api/v1/scans` | Delete all for user |
| GET | `/api/v1/reports/mine` | My reports |
| GET | `/api/v1/stats/overview` | Dashboard |
| GET | `/api/v1/stats/threat-types` | |
| GET | `/api/v1/stats/risk-distribution` | |
| GET | `/api/v1/stats/daily-summary` | |
| GET | `/api/v1/stats/sources` | |
| GET | `/api/v1/stats/timeline` | |
| GET | `/api/v1/stats/reports-summary` | |

If URL has no scheme, check-url prepends `https://`.

HIGH/CRITICAL URL checks also insert into `threats` with a classified type (phishing / malware / fake_login / credential_theft) from tags — heuristic classification, not a separate ML model.

---

## 8. URL SCAN PIPELINE (DEEP)

Function: `URLChecker.analyze(url)` in `url_checker.py`.

### Step A — Normalize

`normalize_url`:

- Parse host, path, query, scheme
- Drop `#fragment`
- Drop default ports 80/443
- Compute hostname and **registered / registrable domain** (`www.google.com` → `google.com`)
- Keep path (important: `/login` vs `/`)
- Store query separately (important: do not treat `google.com/?shortlink=evil` as the Google homepage)

### Step B — Threat intelligence (`lookup_threat_intelligence`)

This module **never fetches the submitted phishing page** to decide intel (avoids driving traffic to kits and some SSRF).

Providers (independent):

1. **OpenPhish** — URL list feed  
2. **URLhaus** — malware/phish URLs  
3. **PhishTank** — public dump; without API key only **verified** entries are used  
4. **Phishing Army** — domain-style blocklist  
5. **Google Safe Browsing** — if API key present  

Each provider returns a structured result:

- `confirmed_malicious` — treat as hit  
- `reported_malicious` — unverified report  
- `no_match` — queried, nothing found (**not SAFE**)  
- `unavailable` — timeout/error (**not no_match, not SAFE**)  
- overall can be `partial` if some feeds failed  

Match types (strictness):

- exact raw URL  
- normalized URL  
- path-related (parent/child paths)  
- hostname / registered_domain (Phishing Army) — **skipped for official trusted destinations** so one dump row cannot burn Google  

**Trusted-domain special rules:** If the site is Google/YouTube/GitHub/etc.:

- A feed row for `/watch?v=abc` does not match every other `/watch` video  
- Query must overlap on generic paths (`/search`, `/watch`, `/`) when needed  
- `google.com/?phishing=1` is **not** treated as the clean homepage  

**User-content hosts still fully scanned:** `sites.google.com`, `docs.google.com`, `forms.google.com`, `github.io`, gists, etc. Official `github.com` is trusted; `username.github.io` is not a free pass.

### Step C — Network / age / TLS (when useful)

- Domain exists? (DNS)  
- Domain age days (young domains are riskier)  
- TLS inspect if reachable  
- Short-link expand with **SSRF block**: no localhost, private RFC1918, `169.254.169.254` cloud metadata  

If intel already **confirmed** malicious, aggressive page-ad fetching is **skipped** so we do not load the phishing HTML.

### Step D — Heuristics (if not a trusted official destination, or still run some checks)

Examples of score additions (capped at 100 before decision engine):

| Signal | Typical points | Example |
|---|---|---|
| Known phishing fragment | +40 | paypa1, amaz0n, go0gle, bank-login |
| Piracy streaming names | +35 | 123movies, tamilrockers, fmovies |
| Aggressive ads / clutter | +20 / extra | malware-style popups |
| Brand impersonation (Levenshtein, leet, homoglyph) | +40 | sbi-login.xyz vs sbi.co.in |
| Free host + login/bank/otp tokens | extra | `*-login.vercel.app` |
| Suspicious TLD | +15 | xyz, tk, top, click, zip, icu… |
| Keywords in URL | +5 | verify, urgent, password |
| IP as host | +30 | `http://192.0.2.10/login` |
| Too many subdomains | +10 | |
| No HTTPS | extra | padlock missing — still not “safe if HTTPS” |
| Psychology on URL string | extra | urgency words in the address |

**Trusted official destinations:** skip noisy heuristics that would false-positive Google/YouTube; still allow **confirmed intel** to win.

### Step E — Decision engine (`calculate_final_risk`)

This is **not** a simple average that can wash away a feed hit.

| Situation | Effect |
|---|---|
| Confirmed intel, match exact_url | floor score **85** |
| Confirmed, normalized_url | floor **80** |
| Confirmed, hostname | floor **72** |
| Confirmed, registered_domain | floor **55** |
| Reported (unverified) | floor **58**, classification SUSPICIOUS |
| Heuristic ≥ 50 | SUSPICIOUS even if no feed hit |
| Intel unavailable + weak heuristics | NO_MALICIOUS_EVIDENCE, **not** a clean bill of health |
| Feed miss + weak heuristics | same honesty: absence ≠ safety |

`ml_score` = lexical/heuristic URL score copy. Label in evidence: *“Lexical / heuristic URL score (no trained classifier in this build)”*.

`safe` is true only if not blocking AND level LOW AND domain exists.

Confidence here is a small heuristic (higher if confirmed), still **not published accuracy**.

### Step F — Explain

- `build_simple_view` — verdict DANGER / BE CAREFUL / NO MALICIOUS INDICATORS; “Do not enter password, OTP, or card.”
- `build_technical_view` — scores, tags, domain, intel providers
- `debug` / `evidence` — for Technical panel and extension

### Step G — Persist

Insert `url_checks`. If HIGH/CRITICAL, insert `threats`.

---

## 9. MESSAGE / QR / SCREENSHOT PIPELINE (DEEP)

`analyze_content()` in `content_analyzer.py`.

1. `normalize_content` — source_type, extract URLs from text (and HTML hrefs if present), language hint, sender object.
2. `analyze_message` psychology on **full text** (not only URL).
3. For each extracted URL, `URLChecker.analyze`.
4. Domain-risk helper: missing domain, young age, suspicious TLD, brand.
5. Intel signal for fusion: ~90 if confirmed malicious tags, else top URL score.
6. Redirect signal: 40 if any shortener.
7. `detect_impersonation(text, urls, extra)` — brand **mentioned** AND domain **not official** AND extra scam signal (urgency/fear/credential/suspicious domain). Mention of “SBI” alone in a news article is not enough.
8. `analyze_sender` if From / Reply-To provided (display name “SBI” vs email `@gmail.com` mismatch).
9. `get_reputation(domain)` community counts → a 0–100-ish signal, **not proof**.
10. `fuse(signals)` with weights below.
11. If any link is confirmed malicious, fused score cannot fall below that URL’s decision score.
12. Save `content_scans` + `extracted_links` if user_id present.
13. `build_explanation`, simple/technical views, optional export report (no secrets).

Psychology categories (points accumulate, cap internally): urgency, fear, authority, coercion, financial pressure, credential/OTP, countdown, greed/lottery, secrecy, plus Hinglish (`abhi click`, `band ho jayega`, `jaldi karo`, `enter otp`, `aadhaar otp`, …).

**False-positive guard:** if psychology is high but URL/domain/intel/brand/community are all weak, fused score is **capped at 35** (LOW/MEDIUM). Marketing “act now” cannot solo-CRITICAL.

---

## 10. FUSION WEIGHTS (CONTENT PIPELINE)

`risk_engine.DEFAULT_WEIGHTS` (sum = 1.0) — **starting defaults, not proven-optimal**:

| Signal key | Weight | What it is |
|---|---|---|
| url | 0.22 | Worst link’s URLChecker score |
| domain | 0.16 | Age, existence, TLD, brand-ish domain risk |
| ml | 0.10 | **Copy of url score** — placeholder for a future model |
| nlp | 0.10 | Same psychology score (named nlp; still rules) |
| psychological | 0.10 | Psychology 2.0 |
| threat_intel | 0.10 | Feed confirmation mapped to ~90 or url risk |
| brand | 0.08 | Impersonation detector |
| sender | 0.05 | From / Reply-To |
| community | 0.05 | User reports |
| redirect | 0.04 | Shortener present |

Risk levels:

- LOW 0–29  
- MEDIUM 30–49  
- HIGH 50–69  
- CRITICAL 70–100  

`scam_risk` = same integer score, **not** a calibrated probability.  
`model_confidence` = 35 + 10 × (how many signals ≥ 20), capped 95 — **agreement, not accuracy**.

---

## 11. BROWSER EXTENSION CONTROL FLOW (DEEP)

Problem we solved: if Chrome loads the phishing page first, the victim may already type a password. PHISHEYE **gates** navigation.

### 11.1 Link click (best case)

1. `gate-clicks.js` at `document_start` listens to clicks on `http(s)` anchors.
2. `preventDefault` / stop navigation (except local dashboard `:5173` / API `:8000`, and same-site after allow).
3. Message `GATE_NAVIGATE` to service worker.
4. Tab shows `panel/panel.html?target=...` (PHISHEYE gate page), **not** the phishing HTML.
5. Panel calls SCAN_URL → FastAPI check-url.
6. Decision:
   - **LOW / clear:** `OPEN_AFTER_SCAN` automatically (no extra click).
   - **MEDIUM:** user must choose **Open anyway** or Keep closed.
   - **HIGH / CRITICAL / failed / unavailable:** stay closed.
7. Session allow-list by **registered domain**. Later pages on `google.com` are **not** re-gated unless settings **Scan every page** (`cg_scan_all_pages`) is ON (default OFF).
8. Destination finally loads.

### 11.2 Address bar / omnibox

Chrome MV3 cannot always fully cancel typed URLs. Honest limit: a **brief blank flash** of the destination can happen; then gate takes over. **Do not claim we always prevent the first byte.** Claim: *“Link clicks are blocked before load; typed URLs are intercepted as far as Chrome allows.”*

`gate-hold.css` hides the destination at document_start when a hold is required.

### 11.3 After a site is allowed

Default: do not scan every SPA route / every YouTube video. Optional toggle for paranoid mode.

### 11.4 Other extension features

- Toolbar popup: scan current tab, status.
- `content.js`: HIGH/CRITICAL overlay (Go back / Continue anyway) on pages that did load; outline up to ~15 visible links (Gmail Web / WhatsApp Web **visible DOM only**).
- Cache ~90 seconds for repeat scans.
- Backend down → **UNAVAILABLE**, never treated as SAFE.

### 11.5 Privacy sentence for jury

“The extension does not read passwords, OTPs, cookies, or SMS. It sends the **URL** (and optional visible link URLs) to the local FastAPI engine.”

---

## 12. SECURITY AND PRIVACY (SAY THIS)

Implemented:

- bcrypt password hashing  
- JWT auth  
- Parameterized SQL  
- SSRF guard on outbound fetch of attacker-controlled URLs  
- Upload size cap 5 MB  
- Report rate limits: **1 URL per 24h per user, 20 reports per day** (community abuse control)  
- Images processed in memory, **not stored**  
- Export report strips raw message secrets  
- User can delete scan history  

Weak / prototype:

- CORS `*`  
- No global API rate-limit middleware  
- JWT secret from config — treat as campus prototype  
- SQLite single-file, not multi-AZ production  

Not implemented: ZKP, federated learning, E2E encrypted analysis.

---

## 13. HOW TO RUN THE DEMO (OPERATIONS)

Two terminals, **before** entering the jury room.

**Backend**

```powershell
cd "$env:USERPROFILE\cybersecurity-platform\backend"
.\venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://127.0.0.1:8000/docs` to prove FastAPI (Swagger).  
Open `http://127.0.0.1:8000/health` → `{"status":"ok"}`.  
Open `http://127.0.0.1:8000/api/v1/threat/intel-status` to show feeds.

**Frontend**

```powershell
cd "$env:USERPROFILE\cybersecurity-platform\frontend"
npm run dev
```

Open `http://127.0.0.1:5173`.

**Extension**

Chrome → Extensions → Developer mode → Load unpacked → select `extension/` folder. Reload after code changes. Pin PHISHEYE.

**Never** open a live phishing kit in the jury browser. Use lookalike domains that heuristics catch (`paypa1.com`, `sbi-login.xyz`) and Google/GitHub for LOW.

---

## 14. PREPARED DEMO SCRIPT (CLICK-BY-CLICK)

Do this in order. Zoom browser 125%. Hide WhatsApp/Discord.

1. **Landing** — “This is PHISHEYE. Same engine as the Chrome extension.”
2. Login (account already created).
3. **Scan → URL** → `https://www.google.com` → Last Result: LOW, Simple View not alarming, Technical: trusted / no_match intel. Line: *“No feed match is not a 100% guarantee, but heuristics are clean and this is an official domain.”*
4. Scan `https://paypa1.com` or `https://sbi-login.xyz` → HIGH/CRITICAL, brand impersonation, Simple View: do not enter OTP. Point at score.
5. **WhatsApp/SMS tab** paste:

   ```
   Urgent: Your SBI account will be blocked. Complete KYC immediately.
   Enter OTP here: https://sbi-login.xyz/verify
   ```

   Show psychology tags + link HIGH.
6. **QR tab** — pre-saved PNG of a lookalike URL. Show `decoded_text` and score. *“We decode the QR. We do not visit the site.”*
7. **Extension** — type `github.com` → gate → auto open. Then try lookalike or a known heuristic URL → stays closed. Settings: *“Scan every page is off so we don’t re-scan every GitHub click.”*
8. **Statistics** — “Charts come from real scan rows in SQLite.”
9. **Advisor** — “This is FAQ, not ChatGPT inside the app.”

Backup screenshots on the desktop if Wi-Fi dies: ScanResult CRITICAL, gate closed, Swagger `/docs`.

---

## 15. FULL 12-MINUTE SPOKEN SCRIPT (STUDENTS CAN MEMORIZE THIS; LLM SHOULD POLISH NOT CONTRADICT)

**0:00–0:45 Lead**  
Good morning. Problem SIH1454 from NTRO: detect phishing domains that imitate genuine domains. Theme is Blockchain and Cybersecurity; our work is **cybersecurity**, not a blockchain. In India, a fake SBI or UPI link on WhatsApp is enough to steal an OTP even when the padlock is green. HTTPS does not mean the brand is real.

**0:45–2:00 Lead**  
Our product is PHISHEYE. It is a working prototype, not a slide. Five verbs: Detect, Understand, Explain, Protect, Learn. Users get a website and a Chrome extension. Both call **one FastAPI engine**.

**2:00–3:30 Backend**  
Stack: React 19 and Vite on port 5173. FastAPI and Uvicorn on port 8000. SQLite file `threats.db` — PostgreSQL is planned, not live. Auth is bcrypt and JWT. QR is OpenCV. Intel is OpenPhish, URLhaus, PhishTank dump, Phishing Army, optional Google Safe Browsing. Tests are pytest.

Pipeline: INPUT, NORMALIZE, ANALYZE, FUSE, EXPLAIN, ACT.

**3:30–5:30 Backend**  
Intelligence today is explainable. We normalize the URL so `www` and query strings cannot trick us. We query public threat feeds. A miss is `no_match`, not SAFE. A timeout is `unavailable`, not SAFE. If a feed confirms a URL, heuristics cannot override it — confirmed intel floors the score around 80 to 85.

Separately we catch lookalikes: paypa1, amaz0n, Levenshtein distance to SBI and PayPal, free hosts like vercel.app with login in the name. Psychology is English and Hinglish phrases — rules, not BERT. Psychology alone cannot go CRITICAL; we cap it at 35 so a marketing SMS is not a phishing alert.

There is **no trained CNN** in this repository. The channel named ML is a copy of the lexical URL score so nobody can say “ML said 10 therefore it is safe.” A supervised model is phase two after curated labels.

Famous sites: Google, YouTube, GitHub are trusted so one dump row for a `/watch` video does not burn all of YouTube. `sites.google.com` and `github.io` stay fully scanned because anyone can host a page there.

**5:30–6:30 Frontend**  
The site: land, sign up, dashboard, scanner with six tabs, last result with Simple and Technical views, history, community reports, statistics, privacy, advisor FAQ, settings. Simple View is for parents: do not enter OTP. Technical View is for us: providers, registered domain, tags.

**6:30–9:30 Extension + live demo**  
(Run section 14. Narrate every click. Do not debug silently.)

Extension: we scan **before** the other site is used. Clear sites auto-open. MEDIUM asks Open anyway. HIGH and CRITICAL stay closed. Chrome may flash a blank page on a typed URL; link clicks do not load the phish first.

**9:30–11:00 Honesty**  
We do not read Gmail or WhatsApp inboxes. We do not read phone SMS. We do not store uploaded images. Community Mark Scam is a signal, not a court proof. Model confidence is signal agreement, not accuracy. CORS is open for the prototype. We will not claim 99 percent.

**11:00–12:00 Close**  
Impact: fewer OTP thefts for students and families; a local engine campuses can run; a path to a trained model when NTRO-scale data exists. Closing sentence:

> PHISHEYE is a working SIH1454 prototype: one FastAPI threat engine, Simple and Technical views, public threat feeds plus lookalike heuristics, and a Chrome gate that opens clear sites and keeps the rest closed — without claiming a trained CNN, live Postgres, or inbox access we do not have.

Thank you. We are ready for questions.

---

## 16. 3-MINUTE BACKUP (DEMO DEAD)

Lead: SIH1454, PHISHEYE, FastAPI not Flask, SQLite not Postgres, no CNN.  
Show screenshot of CRITICAL Simple View. Show screenshot of gate. Show phone photo of Swagger `/docs`.  
One lookalike example spoken: paypa1 vs paypal.com.  
Honesty four lines. Closing sentence. Sit down.

---

## 17. SIX SIH SLIDES — WHAT TO SAY

**Slide 1 Title:** SMART INDIA HACKATHON 2026, SIH1454 full title, theme, software, NTRO, Team ID, Team Name.

**Slide 2 Idea:** PHISHEYE / PhishShield AI — Analyze before you trust. Multi-channel → one engine → Simple+Technical. Innovation = Detect Understand Explain Protect Learn. Honesty footer: no inbox OAuth, OCR partial, CNN planned, confidence ≠ accuracy.

**Slide 3 Technical:** React/Vite/Tailwind/Axios/Recharts · FastAPI/Pydantic · SQLite · URLChecker + Psychology 2.0 + decision engine + fusion + OpenCV · MV3 · bcrypt/JWT/SSRF. Architecture line. Not Flask, not live Postgres, not TF CNN.

**Slide 4 Feasibility:** Technical (Python campus laptops). Operational (local feeds cache 30 min). Security (SSRF, bcrypt, report caps). Challenge→mitigation: psych false positives capped; famous-site dump noise handled; intel miss not safe.

**Slide 5 Impact:** Users = citizens + students + analysts. Before: padlock + panic SMS. After: scan-first + plain English. KPIs are **proposed** (time-to-warn, false-open rate), **not claimed production results**.

**Slide 6 Research:** SIH1454/NTRO, Google Safe Browsing docs, OpenPhish, URLhaus, PhishTank, RDAP, OWASP phishing/SSRF, FastAPI, React, Chrome MV3, SQLite, OpenCV. No fake IEEE papers.

---

## 18. VIVA BANK (LLM MUST EXPAND TO 40 USING THESE FACTS)

Use these answers. Short spoken form.

**What is PHISHEYE?** Multi-channel phishing/scam intelligence: website + extension + one FastAPI brain.

**What is SIH1454?** Detect lookalike phishing domains with an intelligent system, NTRO, software, cybersecurity theme.

**Where is the AI?** Explainable fusion + intel + lookalike heuristics. No neural net in repo. ML key is lexical copy.

**Flask?** No. FastAPI.

**Postgres?** Planned. Live is SQLite `threats.db`.

**How do you detect paypa1?** Fragment list + leet table 1→l + Levenshtein to paypal.

**Homoglyphs?** Limited Cyrillic→Latin map in url_checker.

**Why not blacklist only?** New domains; feeds lag; we add heuristics and psychology.

**Why not ML only?** No labelled production dataset yet; black-box fails viva; explainability required for users.

**Is no_match safe?** No.

**Unavailable?** Feeds timed out; not safe, not no_match.

**Can psychology mark CRITICAL alone?** No. Cap 35.

**Community proof?** No. Signal only. Rate limited.

**HTTPS safe?** No. Padlock is encryption, not identity of SBI.

**Do you visit the phishing page?** Not for intel decision. Ads/clutter fetch skipped if already confirmed. QR does not visit. Shortener unwrap uses SSRF guard.

**SSRF?** Block localhost, private IPs, cloud metadata.

**Extension read WhatsApp?** Only visible links on WhatsApp Web after the page rendered. No native app, no SMS.

**Gmail?** Paste or visible links. No OAuth inbox.

**QR malware?** We decode payload; we don’t execute. Then we score extracted URLs.

**OCR?** Optional Tesseract. If missing, paste text or use QR.

**Trusted Google false positive?** Path/query-aware matching; hostname blocklist skipped on official domains; UGC hosts excluded from trust.

**Weights optimal?** Documented starting weights, not proven-optimal.

**SQL injection?** Parameterized queries.

**Passwords?** bcrypt. JWT after login.

**CORS?** Allow all — prototype limitation.

**Blockchain?** Theme includes cybersecurity. We did not implement a ledger. Phishing intelligence does not require blockchain for MVP.

**Accuracy?** No official product F1. Closed-world or feed evals must be labelled as simulations if mentioned at all. Prefer not to quote a percentage unless the team has the exact script and caveats.

**Who is the user?** Non-technical victim (Simple View) and student/analyst (Technical View).

**Future work?** Postgres, trained model on curated reports, Android SMS companion, inbox OAuth if legally allowed, global rate limit, CORS lockdown.

**Why FastAPI?** Async, Pydantic validation, automatic `/docs` for jury.

**Why SQLite?** Zero-ops MVP, one file, campus demo. Scale later.

**Why Manifest V3?** Chrome requirement; service worker; no blocking webRequest as in MV2 — hence gate page pattern.

**Advisor chatbot?** No. Static FAQ.

**Do you store images?** No.

**Do you store URLs?** Yes, in url_checks / content_scans for history and charts. Be honest.

**How does Learn work?** Logged-in Mark Scam/Risky/Safe → domain_reputation counters → small fusion weight.

**Decision engine vs fusion?** URL path uses decision_engine so intel cannot be averaged away. Message path uses weighted fuse, then raises floor if a child URL was confirmed malicious.

**Free host phishing?** login/otp/bank tokens on vercel.app / lovable.app / pages.dev etc.

**Piracy sites?** Separate list; malvertising tags; still not “we scan every torrent.”

**NTRO fit?** National-scale phishing harm; explainable prototype they can audit; feeds + lookalikes match the PS.

If asked something not in this file: “That is not in our current build. Today we do X. It is on the roadmap.” **Never invent a filename.**

---

## 19. INTERNAL ROUND — HOW INDIAN COLLEGE PANELS ACTUALLY MARK

Typical internal / institute finale (not national SIH yet): 8–12 minutes + 3–5 questions. Panel: HOD, two CSE faculty, sometimes MBA/ECE, rarely a real NTRO person.

They usually score some mix of:

1. Problem understanding (did you read SIH1454?)  
2. Originality (not a copied GitHub phishing-ml notebook with a fake 99%)  
3. Technical depth (can you explain fusion vs intel?)  
4. Feasibility (does it run on this laptop?)  
5. Presentation and teamwork  
6. Q&A honesty  

**To get shortlisted / into the institute finale**

1. Demo must work in the first minutes of the demo block. Boot servers in the corridor.  
2. One story. If Lead says FastAPI and a teammate says Flask, you fail.  
3. Map every feature back to **imitate genuine domains**. Extension is the “protect” extra; don’t let it steal the PS.  
4. Dual audience: HOD hears Simple View and OTP; CSE hears decision floors and SSRF.  
5. Admit limits in the same sentence as the mitigation. Faculty hate bluff more than missing CNN.  
6. Title card with Team ID / Name / PS ID. Internals are bureaucratic.  
7. Two URLs only for live: hero Google, villain paypa1 / sbi-login.xyz.  
8. Timer: **never cut the demo** to save architecture. Cut architecture instead.  
9. If they ask blockchain: one sentence, stop. Don’t lecture on Ethereum.  
10. Don’t say “ChatGPT built this.” You may say tools helped; **you** must own design and honesty.  
11. Laptop: dark UI, 125% zoom, airplane mode after feeds are cached if Wi-Fi is toxic — feeds have 30 min TTL on disk.  
12. Print a one-page handout. Internal panels remember paper.  
13. Practice Q&A with a friend whose job is to say “show me the CNN.” Your answer must be calm.  
14. GitHub is a plus; don’t claim production users.  
15. After questions, repeat the closing sentence if they look unconvinced.

**Roles**

| Person | Talks | Silent when |
|---|---|---|
| Lead | Open, close, time | Demo clicks |
| Backend | Engine, intel, SQLite | Frontend CSS |
| Frontend | Pages, Simple/Technical | Extension internals |
| Extension | Gate, privacy, MV3 limit | Fusion weights |
| Floater | Restarts uvicorn, holds printed Q&A | Never argues |

**Red flags:** arguing with HOD; opening a live phish kit; two people answering; staring at Cursor; “99% ResNet”; “we use blockchain for URLs”; empty dashboard because DB file wasn’t created (init_db runs on API start — start the API).

**Green flags:** “Unavailable is not safe.” “Psychology cannot solo-CRITICAL.” “Same engine as Chrome.” “We can open `/docs`.” pytest exists. Trusted-domain explanation when they type youtube.com.

**Body language:** stand beside the screen; cursor on the score; repeat the question in five words; pause two seconds after the closing line.

**Dress:** simple formal. One laptop, one HDMI adapter.

**Night before:** cold start both servers; load extension; run Google + paypa1; print cheat sheet; sleep.

---

## 20. FORBIDDEN CLAIMS (BLOCKLIST)

Never write or say:

- Flask  
- Live / production PostgreSQL  
- Trained CNN, ResNet, YOLO, BERT, TensorFlow SavedModel, sklearn pickle in this repo  
- We intercept native WhatsApp or phone SMS  
- We OAuth-read Gmail/Outlook  
- 98–99% accuracy as product guarantee  
- Padlock / HTTPS means genuine SBI  
- Community report is legal proof  
- Model confidence is accuracy  
- We store nothing (we store scan metadata)  
- Zero-knowledge / federated learning implemented  
- Blockchain / smart contracts implemented  
- We always block the first byte of a typed URL (MV3 limit)  
- We visit every phishing page to screenshot it  
- Official NTRO deployment  

---

## 21. GLOSSARY FOR THE LLM AND THE TEAM

| Term | Meaning in PHISHEYE |
|---|---|
| Simple View | Plain English warning |
| Technical View | Scores, tags, intel, domain facts |
| Registered domain | eTLD+1, e.g. google.com |
| no_match | Feed queried, nothing found |
| unavailable | Feed failed |
| confirmed_malicious | Treat as hit; floor score |
| Fusion | Weighted sum of signals |
| Decision engine | Intel-first finalization for URLChecker |
| Gate | Extension interstitial page |
| Scan every page | Optional re-scan of every navigation |
| Scam risk | Same 0–100 score, uncalibrated |
| Lookalike / typosquat | Domain imitating a brand |

---

## 22. REPOSITORY MAP (FOR “SHOW ME THE FILE”)

```
cybersecurity-platform/
  README.md
  docs/INTERNAL_ROUND_LLM_BRIEF.md          ← this file
  docs/IMPLEMENTATION_STATUS.md
  docs/SIH_PRESENTATION_CONTENT.md
  docs/SIH_PRESENTATION_REALITY_CHECK.md
  backend/app/main.py
  backend/app/routes/threat_detection.py
  backend/app/routes/analyze.py
  backend/app/routes/user.py
  backend/app/routes/stats.py
  backend/app/routes/reports.py
  backend/app/routes/scans.py
  backend/app/database/connection.py
  backend/app/services/url_checker.py
  backend/app/services/url_normalize.py
  backend/app/services/threat_intel.py
  backend/app/services/feed_cache.py
  backend/app/services/decision_engine.py
  backend/app/services/risk_engine.py
  backend/app/services/trusted.py
  backend/app/services/psychology.py
  backend/app/services/brand_detector.py
  backend/app/services/content_analyzer.py
  backend/app/services/content_normalizer.py
  backend/app/services/qr_analyzer.py
  backend/app/services/ssrf.py
  backend/app/services/warnings.py
  backend/app/services/explanation.py
  backend/app/services/auth.py
  backend/requirements.txt
  frontend/src/App.jsx
  frontend/src/pages/*.jsx
  frontend/src/services/api.js
  frontend/package.json
  extension/manifest.json
  extension/background/service-worker.js
  extension/panel/
  extension/content/gate-clicks.js
  extension/content/gate-hold.css
  extension/content/content.js
```

---

## 23. CHEAT SHEET (PRINT)

- PS: SIH1454 · NTRO · Software · Cybersecurity (not blockchain implemented)  
- Name: PHISHEYE  
- UI 5173 · API 8000 · Swagger `/docs` · DB `backend/threats.db`  
- FastAPI · React · SQLite · MV3 1.8.0 · OpenCV QR  
- Demo: google.com LOW · paypa1 / sbi-login.xyz HIGH · paste SMS · QR · gate auto-open  
- Intel miss ≠ safe · psych cap 35 · no CNN · no inbox · no 99%  
- Close: working prototype, explainable engine, scan-before-open  

---

## 24. AFTER THE LLM GENERATES OUTPUT — TEAM CHECK

- [ ] Says FastAPI and SQLite  
- [ ] Does not say Flask, Postgres-live, CNN-trained, 99%, blockchain-built  
- [ ] Demo order matches Section 14  
- [ ] Extension: scan first; LOW auto-open; HIGH closed; scan-every-page default off  
- [ ] Dual views explained  
- [ ] Team ID blank or real, never fake  
- [ ] 12:00 timing  
- [ ] Blockchain answer is one sentence  
- [ ] MV3 blank-flash honesty  
- [ ] Closing sentence present  

---

*End of complete source document. LLM: execute Section 0. Students: this is the whole problem and the whole project as it exists in the repository.*

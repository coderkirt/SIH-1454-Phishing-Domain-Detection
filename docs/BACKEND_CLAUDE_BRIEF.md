# PHISHEYE BACKEND — COMPLETE SOURCE DOCUMENT FOR CLAUDE

**Upload this entire file to Claude.** It describes only the **backend** of PHISHEYE (SIH1454). Do not invent Flask, live PostgreSQL, a trained CNN, sklearn, TensorFlow, BERT, inbox OAuth, or native SMS reading.

After uploading, send:

```
Follow Section 0. Use only this backend brief. Do not invent files, models, or accuracy numbers.
```

Product name on the API: **PHISHEYE API v2.0.0**  
Older names in comments/docs: PhishShield, CyberGuard — same codebase.  
Folder: `backend/` in repo `cybersecurity-platform`.  
Live stack: **Python 3 + FastAPI + Uvicorn + sqlite3 + Pydantic**. **Not Flask.**

---

## 0. MASTER PROMPT FOR CLAUDE

```
You are helping a student explain and present the PHISHEYE backend for Smart India Hackathon SIH1454 (NTRO, detect phishing domains that imitate genuine domains).

Using ONLY this document, produce:

1. A plain-English explanation of the whole backend (as if teaching a CSE HOD).
2. A technical walkthrough of every route, every important service, and the SQLite schema.
3. Sequence diagrams (mermaid) for: app startup, URL check, content/QR analysis, auth, threat-intel lookup, community report.
4. A 4-minute spoken “backend only” jury script.
5. 30 viva Q&A about this backend (20–40 second answers).
6. A file-by-file map: what each Python file does.
7. Honest limitations and the exact “do not say” list.

HARD RULES
- FastAPI + Uvicorn. NEVER Flask.
- Live DB is SQLite file backend/threats.db via sqlite3. SQLAlchemy model files exist but are UNUSED for live queries. Postgres is planned only (DATABASE_URL in config is unused by connection.py).
- There is NO trained ML model. backend/app/ml/__init__.py is empty. Fusion key "ml" copies the lexical/heuristic URL score.
- Psychology is substring rules, not neural NLP.
- QR decode does NOT HTTP-fetch the destination.
- Threat intel never fetches the submitted phishing page to decide a feed hit.
- Intel miss = no_match, not SAFE. Timeout = unavailable, not SAFE.
- Community reports are a signal, not proof.
- model_confidence is signal agreement, not accuracy.
- CORS is allow_origins=["*"] — prototype weakness.
- Mobile SMS companion is PLANNED (mobile_source.py).
- If something is missing, say “not specified,” do not invent it.
```

---

## 1. WHY THIS BACKEND EXISTS (SIH1454)

Problem: **Create an intelligent system using AI/ML to detect phishing domains which imitate look and feel of genuine domains** (NTRO, Software, theme Blockchain & Cybersecurity).

The backend is the **single brain**. The React dashboard (`:5173`) and the Chrome extension both send HTTP JSON to this API (`:8000`). There are no microservices.

“Intelligence” in this build means:

- URL normalization
- Public threat-intel feeds
- Lookalike / typosquat / free-host heuristics
- Psychology phrase matching (EN + Hinglish)
- Brand + sender signals
- Weighted fusion + an intel-first decision engine
- Plain-English Simple View + Technical View

It does **not** mean a trained neural network sitting in `backend/app/ml/`.

---

## 2. HOW TO RUN

```powershell
cd "$env:USERPROFILE\cybersecurity-platform\backend"
.\venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Health: `GET /health` → `{"status":"ok"}`
- Root: `GET /` lists endpoints
- Intel: `GET /api/v1/threat/intel-status`

On startup, `init_db()` creates/opens `backend/threats.db`. A daemon thread warms public feeds unless `PHISHEYE_SKIP_FEED_WARMUP=1`.

Tests:

```powershell
cd backend
$env:PHISHEYE_SKIP_FEED_WARMUP="1"
python -m pytest -q
```

`tests/conftest.py` blocks live feed downloads.

---

## 3. DEPENDENCIES (`backend/requirements.txt`)

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
sqlalchemy>=2.0.30          # listed; ORM models unused at runtime
requests>=2.31.0
python-dotenv>=1.0.0
pytest>=8.0.0
pydantic>=2.7.0
pydantic-settings>=2.2.0
passlib[bcrypt]>=1.7.4
bcrypt==4.0.1
python-jose[cryptography]>=3.3.0
httpx>=0.27.0
python-multipart>=0.0.9
pillow>=10.0.0
numpy>=1.26.0
opencv-python-headless>=4.8.0
```

**Not in requirements:** tensorflow, torch, sklearn, transformers, flask, psycopg2, tesseract (OCR is optional system install via pytesseract if present).

---

## 4. CONFIG AND ENV

`backend/app/config.py` — Pydantic Settings:

- `app_name` default string still says "CyberGuard" (legacy)
- `host` 0.0.0.0, `port` 8000
- `secret_key` from env, default `dev-secret-key` (prototype)
- `algorithm` HS256
- `database_url` default `sqlite:///./threats.db` — **the live connection module ignores this and uses a file path**

`backend/.env.example` (never commit real `.env`):

```
HOST=0.0.0.0
PORT=8000
SECRET_KEY=change-this
DATABASE_URL=sqlite:///./threats.db
ENVIRONMENT=development
ENABLE_ONLINE_CHECKS=true
GOOGLE_SAFE_BROWSING_API_KEY=
PHISHTANK_API_KEY=
URLHAUS_AUTH_KEY=
```

Auth actually reads `SECRET_KEY` in `auth.py` with fallback `your-secret-key-change-in-production` (slightly different default than config.py — campus prototype).

Optional intel keys: without them, public OpenPhish / URLhaus / Phishing Army still run; PhishTank dump is **verified-only**; GSB is skipped.

Other env:

- `ENABLE_ONLINE_CHECKS` default true; tests set false
- `PHISHEYE_SKIP_FEED_WARMUP` skip OpenPhish etc. on boot

**Never print API keys in a presentation.**

---

## 5. APP ENTRY (`backend/app/main.py`)

```
lifespan:
  unless PHISHEYE_SKIP_FEED_WARMUP:
    thread → threat_intel.warmup_feeds()
init_db()
FastAPI(title="PHISHEYE API", version="2.0.0")
CORSMiddleware allow_origins=["*"] allow_credentials=True allow_methods=* allow_headers=*
routers:
  threat_detection, user, stats, analyze, reports, scans
GET / and GET /health
```

Modular **monolith**. One Uvicorn process.

---

## 6. FOLDER MAP (EVERY BACKEND FILE)

```
backend/
  requirements.txt
  .env.example
  threats.db                      # created at runtime; do not commit secrets/dumps
  data/feeds/                     # cached OpenPhish/URLhaus/PhishTank/Phishing Army; gitignored
  app/main.py
  app/config.py
  app/database/connection.py      # LIVE sqlite3
  app/routes/
    threat_detection.py           # check-url, check-message, intel-status, stats, recent-urls
    analyze.py                    # content, url, email, qr, screenshot
    user.py                       # signup, login, profile
    stats.py                      # dashboard aggregations
    reports.py                    # report, feedback, reputation, reports/mine
    scans.py                      # list/get/delete content scans
  app/services/                   # detection brain (see Section 8)
  app/models/                     # SQLAlchemy classes — UNUSED at runtime
    user.py, url_check.py, threat.py
  app/ml/__init__.py              # EMPTY — no model
  app/utils/__init__.py
  tests/                          # pytest
  scripts/
    accuracy_simulation.py        # closed-world fixture sim; NOT product F1
    phishtank_live_eval.py        # eval vs catalog URLs; does not open phish pages
```

---

## 7. DATABASE (LIVE SCHEMA)

File: `backend/threats.db`  
Code: `get_db_connection()` → `sqlite3.connect`, `row_factory = sqlite3.Row`, `PRAGMA foreign_keys = ON`.

Path is always inside the backend folder, regardless of cwd.

### users
`id INTEGER PK AUTOINCREMENT`, `username UNIQUE`, `email UNIQUE`, `password_hash`, `created_at`

### url_checks
`id`, `user_id` FK users (nullable — anonymous checks), `url`, `risk_level`, `risk_score`, `ml_confidence DEFAULT 0`, `timestamp`  
Indexes: url, user_id, timestamp  
Used by `POST /threat/check-url`.

### threats
`id`, `threat_type`, `threat_data` (the URL string), `severity`, `last_updated`  
Inserted when URL check is HIGH or CRITICAL. Types from tag heuristics: phishing / malware / fake_login / credential_theft.

### content_scans
`id`, `user_id`, `source_type`, `url`, `risk_level`, `risk_score`, `scam_risk`, `confidence`, `created_at`  
Raw message text is **not** stored.

### extracted_links
`id`, `scan_id` FK content_scans, `url`, `domain`, `risk_score`, `classification`

### user_reports
`id`, `user_id`, `url`, `domain`, `user_label` (scam|risky|safe), `reason`, `created_at`

### domain_reputation
`domain PK`, `scam_reports`, `risky_reports`, `safe_reports`, `last_reported`

### scan_feedback
`id`, `scan_id`, `helpful` 0/1, `created_at`

SQL uses `?` placeholders (parameterized).

**Honesty:** `safety_rate` in stats is `(total_url_checks - HIGH/CRITICAL) / total` — a dashboard ratio, **not** detection accuracy.

---

## 8. SERVICES — WHAT EACH FILE DOES

| File | Role |
|---|---|
| `url_normalize.py` | Parse URL; drop fragment & default ports; keep path; store query separately; registrable domain (`sbi.co.in` kept; `www.google.com` → `google.com`); IDNA host. **Never fetches.** |
| `trusted.py` | `TRUSTED_DOMAINS` (Google, YouTube, GitHub, banks, Indian gov, etc.). `USER_CONTENT_HOSTS` still scanned (`sites.google.com`, `forms.google.com`, `github.io`, gists). Confirmed intel still wins on trusted sites. |
| `threat_intel.py` | Lookup OpenPhish, URLhaus, PhishTank, Phishing Army, optional GSB. Structured statuses. Path/query-aware matching so one YouTube `/watch` dump row does not burn all YouTube. **Never fetches the submitted page.** |
| `feed_cache.py` | Download/cache feeds under `data/feeds/`, TTL 30 minutes, User-Agent PHISHEYE academic. Stale cache reused if refresh fails. Failed download → unavailable. |
| `decision_engine.py` | Intel floors vs heuristics. `ml_score` = lexical copy. Classifications: CONFIRMED_MALICIOUS, SUSPICIOUS, NO_MALICIOUS_EVIDENCE. |
| `url_checker.py` | Main URL analyzer: shorteners, DNS, age, TLS, intel, trusted short-circuit, heuristics (fragments, piracy, ads, brand Levenshtein/leet/homoglyph, free-host, TLD, keywords, IP host, subdomains, HTTPS, psychology on URL string), then decision_engine + simple/technical views. |
| `external_intel.py` | Domain exists (DNS), domain age (RDAP/WHOIS-style). |
| `ssl_certs.py` | TLS inspect when host reachable. |
| `redirects.py` | Unwrap bit.ly-style shorteners. |
| `ssrf.py` | Block fetch of localhost, `.local`, private IPs, multicast, `169.254.169.254`, GCP metadata hosts. |
| `ad_signals.py` | Aggressive ads / page clutter. **Skipped if intel already confirmed** (do not load phish HTML). |
| `psychology.py` | Phrase lists: urgency, fear, authority, coercion, financial, OTP/credential, countdown, greed, secrecy + Hinglish. |
| `brand_detector.py` | Brand mentioned + unofficial domain + extra scam signal. Mention alone is not enough. |
| `sender_analyzer.py` | Only if caller sent From / Reply-To. Display-name brand vs gmail mismatch. |
| `content_normalizer.py` | Unify source_type: url, text, email, whatsapp, sms, webpage, screenshot, qr. Extract URLs. Language hint hi / en-hi / en. |
| `url_extractor.py` | Pull URLs from pasted text / hrefs. |
| `content_analyzer.py` | Multi-channel: normalize → psych → URLChecker each link → brand → sender → community → `fuse()` → persist content_scans. |
| `risk_engine.py` | Weighted fusion. Psych-only cap score 35. Confidence = agreement. |
| `warnings.py` | Simple View (DANGER / BE CAREFUL / NO MALICIOUS INDICATORS) + Technical View. |
| `explanation.py` | `{headline, what, why, what_to_do, confidence_note}` — **object, not a string**. Frontend must use `.what`. |
| `qr_analyzer.py` | OpenCV decode with scale/CLAHE/threshold variants + PIL fallback. Extract URLs from payload. No visit. |
| `reputation.py` | add_report rate limits: 1 URL / 24h / user, 20 / day. Reputation score from counts. |
| `report_service.py` | Export JSON without secrets / raw message. |
| `attachments.py` | Filename/extension only. Deep scan PLANNED. Never executes files. |
| `mobile_source.py` | `implemented = False`. Android SMS companion contract only. |
| `auth.py` | bcrypt hash/verify, JWT HS256, default expiry helper 15 min but login/signup pass **7 days**. |

---

## 9. AUTH FLOW

Signup `POST /api/v1/user/signup`  
Body: `{username, email, password}`  
Rules: username ≥ 3, password ≥ 6, unique username/email.  
Stores bcrypt `password_hash`. Returns JWT `access_token`, `token_type: bearer`. Claim `sub` = username.

Login `POST /api/v1/user/login`  
Same JWT 7 days.

Profile `GET /api/v1/user/profile`  
`Authorization: Bearer <jwt>` via HTTPBearer.

**Anonymous URL check is allowed.** `check-url` does not require a token. Analyze routes take **optional** bearer to attach `user_id` on content_scans. Report/feedback/delete require login.

Frontend stores token as `cg_token` (that is frontend; backend only issues JWT).

---

## 10. COMPLETE API CATALOG

Base: `http://127.0.0.1:8000`

### 10.1 Root
- `GET /` — product name, version, endpoint list
- `GET /health` — `{status: ok}`

### 10.2 Threat (`/api/v1/threat`)

**POST `/check-url`**  
Request:

```json
{ "url": "https://paypa1.com", "view": "both", "page_signals": { "buttons": 0, "iframes": 0, "popups": 0, "overlays": 0, "links": 0 } }
```

`view`: `simple` | `technical` | `both` (default both). Empty URL → 400. Missing scheme → prepend `https://`.

Response includes: `url`, `risk_score`, `risk_level`, `reasons`, `safe`, `classification`, `explanation` (string from decision engine on this path), `threat_tags`, `brand_impersonated`, redirect fields, `debug`, `evidence`, plus `simple_view` and/or `technical_view`.

Side effect: INSERT url_checks; if HIGH/CRITICAL also INSERT threats.

**POST `/check-message`**  
`{ "message": "...", "url": "optional" }` → runs `analyze_content(source_type=text)`.

**GET `/intel-status`**  
Feed load state + booleans whether GSB/PhishTank/URLhaus **keys exist** (not the key values).

**GET `/stats`** — counts from url_checks + safety_rate string + last 10 URLs.

**GET `/recent-urls?limit=`** — recent url_checks.

### 10.3 Analyze (`/api/v1/analyze`)

**POST `/content`**  
```json
{
  "source_type": "text",
  "text": "Urgent KYC https://sbi-login.xyz",
  "urls": [],
  "language": null,
  "sender": { "email": "", "display_name": "", "reply_to": "" }
}
```
source_type: url | text | email | whatsapp | sms | webpage | screenshot | qr.

Need text or urls else 400.

**POST `/url`** — wrapper, text or urls[0] as URL.

**POST `/email`** — content with source email.

**POST `/qr`** — multipart `file`, max 5 MB. Decode QR. If no payload → 400 with human message. Then `analyze_content("qr", ...)`. Extra fields: `qr_payloads`, `qr_urls`, `decoded_text`. Images **not stored**.

**POST `/screenshot`** — multipart `file` + form `hint`. QR always; OCR via pytesseract+PIL **if installed**, else empty OCR. Need some text or URLs else 400.

Optional JWT attaches user_id for history.

### 10.4 User (`/api/v1/user`)
signup, login, profile (see §9).

### 10.5 Reports (`/api/v1`)
- `POST /report` `{url, domain?, label: scam|risky|safe, reason?}` auth required. Message: “Report saved. It is one signal, not proof.”
- `GET /reputation/domain/{domain}`
- `POST /feedback` `{scan_id?, helpful: bool}`
- `GET /reports/mine`

### 10.6 Scans (`/api/v1`)
- `GET /scans?limit=` list content_scans (currently not filtered by user in list endpoint — prototype)
- `GET /scans/{id}` + extracted links; privacy note raw text not stored
- `DELETE /scans/{id}` owner or null user_id
- `DELETE /scans` delete all for user

### 10.7 Stats (`/api/v1/stats`)
overview, threat-types, risk-distribution, daily-summary, sources, timeline, reports-summary — all SQL aggregations over real rows, not fake seed numbers (empty DB → zeros).

---

## 11. URL CHECK PIPELINE (STEP BY STEP)

`URLChecker.analyze(url, page_signals=None, intel_providers=None)`

1. **Normalize** candidate URL.
2. **Shortener?** If yes, `expand_url` with SSRF guard. +12 if unwrapped, +20 if hidden dest, +10 if hops > 2. Continue on **final URL**.
3. Parse host; re-normalize; registrable domain + label + TLD.
4. **`lookup_threat_intelligence(url)`** — providers independent.
5. **DNS exists?** Invalid/missing host or NXDOMAIN → +35, tag `domain_not_found`.
6. **Age** if exists: <30 days +20, <90 +10.
7. **TLS** inspect if exists.
8. **Trusted destination** and domain exists and intel not confirmed → skip noisy heuristics; cap heuristic score at 20; still run decision_engine (confirmed intel would not take this branch).
9. Else heuristics:
   - phishing fragments (paypa1, amaz0n, go0gle, bank-login, …) +40
   - piracy names +35
   - ads/clutter unless intel confirmed
   - `_detect_brand` Levenshtein ≤2 after leet/homoglyph normalize, skip if domain already official +40
   - free-host + login/otp/bank tokens (vercel.app, lovable.app, pages.dev, github.io, …)
   - suspicious TLD set (xyz, tk, top, click, zip, icu, …) +15
   - keywords in URL +5
   - IP host +30
   - many dots in host +10
   - missing https extra points
   - psychology on URL string
10. Cap heuristic 0–100.
11. **`calculate_final_risk`**
12. simple_view + technical_view + debug/evidence
13. Route layer persists url_checks / threats

### Decision engine floors

| Intel | Floor | Class |
|---|---|---|
| confirmed exact_url | 85 | CONFIRMED_MALICIOUS |
| confirmed normalized_url | 80 | CONFIRMED_MALICIOUS |
| confirmed hostname | 72 | CONFIRMED_MALICIOUS |
| confirmed registered_domain | 55 | CONFIRMED_MALICIOUS |
| reported_malicious unverified | max(heuristic, 58) | SUSPICIOUS |
| heuristic ≥ 50 | heuristic | SUSPICIOUS |
| unavailable + weak | heuristic | NO_MALICIOUS_EVIDENCE + honesty text |
| no_match + weak | heuristic | NO_MALICIOUS_EVIDENCE + “absence does not guarantee safety” |

`safe` true only if not blocking AND LOW AND no `domain_not_found`.

Intel explanation says heuristics/ML **cannot override** a confirmed feed hit.

---

## 12. THREAT INTEL MATCHING RULES

Statuses per provider: `confirmed_malicious` | `reported_malicious` | `no_match` | `unavailable`

Match attempts:

- exact raw URL
- normalized full URL
- path-related (child/parent paths; stricter on trusted generic paths)
- hostname / domain blocklist — **not applied to official trusted destinations** (stops Phishing Army from burning google.com)
- query overlap required on trusted roots / `/watch` / `/search` so dump noise does not match every Google/YouTube URL
- `google.com/?evil=` is not the Google homepage

PhishTank without API key: **verified listings only**.  
GSB: POST to Google API only if key set; missing key ≠ invented matches.  
`ENABLE_ONLINE_CHECKS=false` → lookups unavailable/no network.

Lookup cache ~15 min hits; feeds TTL 30 min.

---

## 13. MULTI-CHANNEL `analyze_content`

1. `normalize_content` → raw_text, urls[], domains, language, sender
2. `analyze_message` psychology on full text
3. Each URL → `URLChecker.analyze` → `links[]`
4. Domain-risk helper from age / NXDOMAIN / TLD / brand
5. threat_intel fusion input ≈ 90 if confirmed tags else top URL score
6. redirect 40 if any shortener
7. `detect_impersonation`
8. `analyze_sender`
9. `get_reputation(domain)`
10. `fuse({url, domain, ml: url_risk, nlp: psych, psychological, threat_intel, brand, redirect, sender, community})`
11. If confirmed malicious link, fused score ≥ that link’s score
12. explanation object + simple_view + technical_view + privacy flags + export
13. `_store_scan` content_scans + extracted_links (raw text not stored)

### Fusion weights (sum 1.0) — starting defaults, not proven-optimal

| key | weight |
|---|---|
| url | 0.22 |
| domain | 0.16 |
| ml | 0.10 (copy of url) |
| nlp | 0.10 |
| psychological | 0.10 |
| threat_intel | 0.10 |
| brand | 0.08 |
| sender | 0.05 |
| community | 0.05 |
| redirect | 0.04 |

Psych-only (psych ≥ 20 and url/domain/intel/brand/community all < 40) → score **min(score, 35)**.

Levels: LOW 0–29, MEDIUM 30–49, HIGH 50–69, CRITICAL 70–100.

`scam_risk` = same integer.  
`model_probability` = same integer (not a calibrated probability).  
`model_confidence` = min(95, 35 + 10 * count(signals ≥ 20)).

---

## 14. BRAND / PSYCHOLOGY / SENDER DETAILS

**URLChecker brands map** (label vs real domain): paypal, amazon, google, youtube, github, microsoft, apple, facebook, instagram, whatsapp, netflix, flipkart, paytm, phonepe, sbi, hdfc, icici, axisbank, irctc.

Leet: 0→o, 1→l, 3→e, 4→a, 5→s, 7→t, 8→b, @→a, $→s.  
Homoglyphs: limited Cyrillic lookalikes.

**brand_detector** extra brands: uidai/aadhaar, incometax, fedex, dhl, linkedin, naukri. Requires extra_signals (credential/urgency/fear/suspicious_domain).

**Psychology patterns** include: act now, account blocked, enter otp, aadhaar otp, abhi click, jaldi karo, band ho jayega, KYC, lottery, share otp, …

**Sender:** Reply-To domain ≠ From domain +25; brand in display name but email not on REAL_DOMAINS +40.

---

## 15. QR DECODE INTERNALS

`extract_qr_urls(bytes)`:

- Reject oversized in route (5 MB)
- Decode with OpenCV QRCodeDetector on variants: color, gray, invert, blur, CLAHE, Otsu, morph close, adaptive threshold; may scale up small images
- PIL fallback if OpenCV finds nothing
- Normalize payloads to http(s) URLs
- Cap 15 URLs
- Returns payloads, urls, error string if none

Does not `requests.get` the QR destination.

---

## 16. SECURITY CONTROLS (REAL)

Implemented:

- bcrypt passwords
- JWT HS256
- parameterized SQL
- SSRF `assert_public_http_url` before fetching attacker URLs
- 5 MB upload cap
- report 24h/URL and 20/day
- images in memory only
- export strips secrets
- user can delete scans
- intel path does not fetch phish page
- ads fetch skipped on confirmed intel

Weak / prototype:

- CORS `*`
- default SECRET_KEY
- no global HTTP rate-limit middleware
- GET `/scans` not strictly per-user
- SQLite single writer
- JWT 7-day access tokens (long for production)

Not implemented: Postgres live, CNN, federated learning, ZKP, attachment deep scan, Android SMS.

---

## 17. TESTS

| File | Covers |
|---|---|
| `test_url_normalize.py` | path/query/www |
| `test_threat_intel.py` | match vs no_match vs trusted YouTube/Google |
| `test_golden_detection.py` | lookalikes vs famous sites |
| `test_threat_detection.py` | check-url API |
| `test_multichannel.py` | analyze_content |
| `test_psychology.py` | phrases |
| `test_qr_analyzer.py` | decode helpers |
| `test_ssl_certs.py` | TLS helper |
| `test_api.py` | HTTP smoke |

Feeds mocked. Do not claim tests equal published academic F1.

---

## 18. EVAL SCRIPTS (DO NOT QUOTE AS PRODUCT ACCURACY)

`scripts/accuracy_simulation.py` — closed-world cases, stubbed DNS/intel fixtures, does not fetch live phish pages. If a number exists from a past run, it is a **simulation**.

`scripts/phishtank_live_eval.py` — uses catalog URL strings, does not open phishing pages. Verified vs unverified behave differently by design.

Jury line: “We can run offline simulations. We do not claim a certified 99% model.”

---

## 19. EXAMPLE RESPONSES (SHAPE, NOT GUARANTEED SCORES)

**Low / trusted** `https://www.google.com` typically:

- risk_level LOW
- classification NO_MALICIOUS_EVIDENCE
- intel overall no_match or similar
- simple_view verdict not DANGER
- safe true if domain exists

**Lookalike** `https://paypa1.com` or `https://sbi-login.xyz` typically:

- HIGH or CRITICAL
- tags include brand_impersonation and/or phishing
- simple_view tells user not to enter OTP

**Confirmed feed URL** (if listed in OpenPhish etc.):

- classification CONFIRMED_MALICIOUS
- score floored ~80–85+
- explanation says intel cannot be overridden

Actual numbers depend on live feeds and DNS. Do not hardcode 99.

---

## 20. BACKEND 4-MINUTE JURY SCRIPT (SPOKEN)

The website and the Chrome extension are only clients. The brain is FastAPI on port 8000. Swagger is at `/docs`.

A URL POST hits `check-url`. We normalize it so www and query strings cannot trick matching. We ask public feeds: OpenPhish, URLhaus, PhishTank verified dump, Phishing Army, optional Google Safe Browsing. A miss is not safe. A timeout is unavailable, not safe. If a feed confirms the URL, heuristics cannot talk it down.

Then we catch lookalikes: paypa1, Levenshtein to SBI and PayPal, free hosts like vercel.app with login in the name. Psychology is English and Hinglish phrases, capped so marketing cannot go CRITICAL alone.

SQLite file `threats.db` stores scans and users with bcrypt. PostgreSQL is planned. There is no TensorFlow model. The ml channel is a copy of the URL heuristic score.

QR: OpenCV reads the code, we score the extracted URL, we do not visit it. SSRF blocks localhost and cloud metadata if we unwrap a short link.

That is an explainable SIH1454 backend a jury can audit.

---

## 21. BACKEND VIVA (SHORT ANSWERS)

**Flask?** No. FastAPI.

**Where is the model pickle?** There isn’t one. `app/ml` is empty.

**Why FastAPI?** Pydantic validation, `/docs` for jury, async Uvicorn.

**Why SQLite?** Zero-ops campus demo. `connection.py` is sqlite3.

**Why SQLAlchemy in requirements?** Leftover models in `app/models/` unused.

**How JWT?** python-jose HS256, `sub`=username, login issues 7-day token.

**Passwords?** passlib bcrypt.

**SQL injection?** `?` binds.

**SSRF?** `ssrf.py` before outbound fetch.

**Do you fetch the phish site for intel?** No.

**no_match vs unavailable?** Queried empty vs error/timeout.

**Trusted Google?** Skip noisy heuristics; still honor confirmed intel; UGC hosts excluded.

**Psychology NLP?** Substring rules.

**Fusion vs decision engine?** Messages use weighted fuse; single URL uses intel floors; content path also floors if a child URL was confirmed.

**OCR?** Screenshot route tries pytesseract; not a pip requirement.

**Rate limit API?** Not global. Reports are limited.

**CORS?** Allow all — say prototype.

**Mobile SMS?** `mobile_source.implemented = False`.

**Who calls this API?** React Axios and Chrome extension, same JSON.

**Blockchain?** Not in backend. Theme is cybersecurity.

**Postgres URL in config?** Unused by live connection.

**safety_rate?** Dashboard ratio, not F1.

**OpenCV in a URL API?** Only QR/screenshot decode.

**Thread on startup?** Feed warmup daemon.

**Tests hit internet?** conftest blocks downloads.

---

## 22. FORBIDDEN CLAIMS

- Flask, Django, Express as the live API
- Live PostgreSQL / production RDS
- Trained CNN / sklearn / TF / BERT
- 99% accuracy as product metric
- We read Gmail/WhatsApp/SMS on the server
- We store uploaded images
- We store raw message bodies
- Community report is proof
- Padlock checked = genuine brand (we inspect TLS when reachable; HTTPS ≠ identity)
- Intel miss = SAFE
- Blockchain smart contracts
- NTRO production deployment

---

## 23. CHEAT SHEET

- FastAPI `app.main:app` :8000
- sqlite3 `backend/threats.db`
- Routers: threat, analyze, user, stats, reports, scans
- Brain: url_checker + threat_intel + decision_engine + content_analyzer + risk_engine
- Feeds: OpenPhish, URLhaus, PhishTank verified dump, Phishing Army, optional GSB
- QR: OpenCV, no fetch
- Auth: bcrypt + JWT
- No trained ML file

---

*End of backend brief. Claude: execute Section 0.*

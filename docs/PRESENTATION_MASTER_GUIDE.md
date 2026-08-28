# PhishShield AI — Presentation Master Guide

**Problem:** SIH 1454 — Intelligent system using AI/ML to detect phishing domains imitating genuine domains.  
**Code name in repo:** CyberGuard  
**Current engine:** FastAPI rule-based multi-signal detector + live intel. **Not** Flask. **Not** PostgreSQL. **Not** a CNN.

If a jury says “show me the CNN,” answer: *“CNN is planned. Today we combine heuristics, brand impersonation, psychological language, and Google Safe Browsing / OpenPhish. Metrics for a trained model are not yet available.”*

---

# 1. Project from zero

## 1.1 What problem are we solving?

**Beginner:** People click fake bank / PayPal links in SMS, WhatsApp, and email. The site looks real. They type a password. Money or accounts are stolen.

**Technical:** SIH 1454 asks for detection of **domains that imitate genuine brands** (typosquatting, homoglyphs, deceptive subdomains) using intelligent methods. Our MVP scores a URL with many signals and explains the result in plain English.

## 1.2 Why phishing detection is difficult

Attackers use HTTPS, real-looking logos, new domains, and shortened links. A site can be “valid HTTPS” and still be fake. Blacklists lag. Users are rushed (OTP, “account blocked”).

## 1.3 Why URL-only detection is insufficient (honest)

**Beginner:** The address bar is the first clue, but a clever fake page can still trick you.

**Technical:** Our MVP **mostly analyzes the URL** (plus optional HTML sample for aggressive ads, plus message text on a separate API). We do **not** fully render JavaScript, do **not** verify certificate chains, and do **not** run a CNN on the page screenshot. That is a limitation. Psychological checks on **message text** exist in `POST /api/v1/threat/check-message` but the dashboard does not call it yet.

## 1.4 Domain impersonation

Using a name close to a real brand: `paypa1.com`, `sbi-login.xyz`, `amaz0n-secure.tk`. Implemented in `_detect_brand()` with leetspeak, limited homoglyphs, and Levenshtein distance.

## 1.5 Psychological manipulation

Urgency, fear, greed (English + Hinglish phrases). Implemented as substring rules in `psychology.py`, not as a neural NLP model.

## 1.6 End-to-end: URL to result

1. User pastes URL in React (`UrlScanner.jsx`) or opens a tab (extension).
2. Client `POST /api/v1/threat/check-url` with `{ url, view: "both" }`.
3. FastAPI strips/adds `https://` if missing.
4. `URLChecker.analyze()` runs DNS, Safe Browsing/OpenPhish, RDAP age, phishing fragments, piracy list, ads, brand, TLD, keywords, IP host, HTTPS, psychology on the URL string.
5. Score capped at 100 → LOW/MEDIUM/HIGH/CRITICAL.
6. `build_simple_view` / `build_technical_view`.
7. Row inserted into `url_checks`; HIGH/CRITICAL also into `threats`.
8. JSON returned. React saves last scan in `sessionStorage` and shows `ScanResult.jsx`. Extension shows toast/overlay.

## 1.7 How the extension works

Service worker watches tab load → skips `chrome://` → same check-url API → badge OK/MED/HIGH/CRIT → content script toast. HIGH/CRITICAL full-page warning. Cache ~90 seconds. Backend down → **UNAVAILABLE**, never SAFE.

## 1.8 React does **not** talk to Flask

React/Axios talks to **FastAPI** at `http://127.0.0.1:8000`. CORS is currently `allow_origins=["*"]`.

## 1.9 Backend does **not** talk to PostgreSQL

Routes use `sqlite3.connect` on `backend/threats.db`. SQLAlchemy model files exist but are unused.

## 1.10 How the ML model participates

**It does not, in this version.** `ml_confidence` stays `0.0`. Landing page says “AI-powered” meaning intelligent automation + intel, not a trained network. Advisor page states there is no LLM.

## 1.11 How risk is calculated

Additive integer points (see study guide / url_checker). Thresholds: ≥70 CRITICAL, ≥50 HIGH, ≥30 MEDIUM, else LOW. Trusted allowlist (google.com, sbi.co.in, …) returns score 0 if DNS exists.

## 1.12 How explanation is generated

`warnings.py` maps tags + brand + level to English sentences. Not an LLM.

## 1.13 Simple vs Technical View

Simple: verdict LOOKS SAFE / BE CAREFUL / DANGER + warning text.  
Technical: domain, exists, https, TLD, brand, age, Safe Browsing label, aggressive ads.

## 1.14 Privacy

Sends the scanned URL (and login fields on signup). Does not collect passwords from web pages. Privacy Center lists planned ZK/federated items as **Planned**.

---

# 2. Architecture (actual arrows)

```
Extension popup/SW/content     React (Vite :5173)
              \                    /
               \ REST JSON HTTP   /
                v                v
           FastAPI CORS *  (:8000)
                      |
         Detection pipeline (Python services)
                      |
         sqlite3  ←→  threats.db
```

| Arrow | Data | Tech | Why | Failure | Handling | Security issue |
|---|---|---|---|---|---|---|
| Extension → FastAPI | `{url, view}` + optional Bearer | `fetch` in service worker | One engine | Network / 500 | Toast UNAVAILABLE | Host permissions broad; URL leaves the browser |
| React → FastAPI | same JSON + JWT on profile | Axios | Dashboard | Timeout 30s | `getErrorMessage` | Token in localStorage (XSS risk) |
| FastAPI → URLChecker | URL string | in-process | No extra hop | Parse error | score 20 + reason | Malicious URL string — handled as data |
| URLChecker → DNS/RDAP/GSB/OpenPhish | hostname / URL | socket, requests | Live intel | Timeout/fail | skip or OpenPhish; never fake SAFE from silence | Outbound API key in `.env` |
| URLChecker → ad fetch | GET HTML sample | requests, 4s, 150KB, no private IPs | Malvertising | Fail-soft | no extra points | SSRF mitigated; still fetches user URL |
| FastAPI → SQLite | INSERT url_checks/threats | sqlite3 `?` params | History/stats | File lock | 500 to client | No per-user isolation yet |
| FastAPI → client | score, views | JSON | UI | — | — | CORS `*` too open for prod |

---

# 3. Backend APIs (there is no `/api/analyze`)

Use **`POST /api/v1/threat/check-url`** in viva, not a fictional Flask route.

### GET `/`  
Health + endpoint list. File: `main.py`. No DB.

### GET `/health`  
`{"status":"ok"}`.

### POST `/api/v1/threat/check-url`  
**Request:** `{ "url": "https://example.com", "view": "both" }`  
**Response:** url, risk_score, risk_level, reasons, safe, threat_tags, simple_view, technical_view  
**DB:** INSERT url_checks; maybe threats  
**Errors:** 400 empty URL; 500 analysis exception  
**Security:** unauthenticated; anyone can fill the DB

Pipeline (line-by-line story):

1. Pydantic validates JSON.  
2. Strip URL; prefix https if needed.  
3. `url_checker.analyze(url)`.  
4. INSERT `(url, risk_level, risk_score)` — `user_id` and `ml_confidence` not set (defaults).  
5. If HIGH/CRITICAL, INSERT threats with `classify_threat_type`.  
6. `_pick_view` attaches simple and/or technical objects.

### POST `/api/v1/threat/check-message`  
Message required; optional URL. Combines psychology score + URL score. **No dashboard UI.**

### GET `/api/v1/threat/stats` and `/recent-urls`  
Counts and last N scans.

### POST `/api/v1/user/signup` | `login` | GET `profile`  
Signup/login return JWT. Profile needs `Authorization: Bearer`. Username ≥3, password ≥6.

### GET `/api/v1/stats/overview|threat-types|risk-distribution|daily-summary`  
Aggregates. **Do not** defend `average_response_time_ms: 245` as telemetry.

---

# 4. Database (SQLite, not PostgreSQL)

**Why SQLite now:** zero ops, one file, enough for SIH demo.  
**Why PostgreSQL later:** concurrency, backups, multi-server.  
**SQLAlchemy:** models exist; **live code is sqlite3**.  
**Migrations:** none; `init_db()` CREATE IF NOT EXISTS.

### Table `users`
id PK, username unique, email unique, password_hash, created_at.

### Table `url_checks`
id PK, user_id FK (nullable, **not filled**), url, risk_level, risk_score, ml_confidence default 0, timestamp. Indexes on url, user_id, timestamp.

### Table `threats`
id PK, threat_type, threat_data (the URL), severity, last_updated. Inserted only for HIGH/CRITICAL.

**SQL injection:** queries use `?` placeholders.  
**Two users at once:** SQLite serializes writes; OK for demo, weak for production.  
**DB down:** API 500; extension UNAVAILABLE.

Sample SQL:

```sql
SELECT url, risk_level, risk_score FROM url_checks ORDER BY id DESC LIMIT 20;
SELECT threat_type, COUNT(*) FROM threats GROUP BY threat_type;
```

---

# 5. “Machine learning” section (truth)

**Dataset / train/test / CNN / accuracy: METRIC NOT YET AVAILABLE.**

What exists instead are **features scored by rules**:

| Feature | Why it can indicate phishing | Code |
|---|---|---|
| Domain missing in DNS | Disposable fake names | +35 |
| Listed in GSB/OpenPhish | Known campaign | +40 |
| Domain age <30 / <90 days | Fresh phishing domains | +20 / +10 |
| Phishing fragments | paypa1, amaz0n | +40 |
| Piracy names | hdhub4u, 123movies | +35 |
| Brand impersonation | fake SBI/PayPal | +40 |
| Suspicious TLD | .xyz .tk .click | +15 |
| Keywords login/verify | credential lure | +5 (noisy) |
| IP URL | hides brand | +30 |
| Many subdomains | extra.login.bank.evil.xyz | +10 |
| URL length >100 | obfuscation | +8 |
| No https | easier tamper | +5 |
| Email as host | odd | +20 |
| Urgency/fear/greed in URL | social engineering | +15/+15/+12 |
| Aggressive ads | malvertising | +20 |

**Why accuracy alone is dangerous:** if 99% of sites are safe, a dummy “always SAFE” model is 99% accurate and still useless. **Recall** (catching phishing) matters more. We have **no** confusion matrix yet.

---

# 6. Psychological Threat Detection (novelty — be precise)

Implemented: **urgency, fear, greed** via phrase lists (including Hinglish: *jaldi karo*, *band ho jayega*).

**Not implemented as separate detectors:** coercion, fake countdown timers, credential-form OCR, authority logos, repeated CTA counting on the rendered page.

**Countdown ≠ phishing:** a real airline sale can say “expires today.” We add points; we do **not** auto-set CRITICAL from one phrase. Multi-signal: brand fake + urgency + new domain is stronger.

**False positives:** a real bank URL containing `login` (+5) or a marketing path with `urgent`. Trusted allowlist reduces this for google.com etc.

---

# 7. Cybersecurity map vs our system

| Topic | Detected here? |
|---|---|
| Typosquatting / brand fake | Yes |
| Homograph (limited Cyrillic) | Partial |
| Punycode xn-- | No dedicated check |
| HTTPS present | Yes (scheme only) |
| Certificate mismatch | No |
| DNS spoofing of victim | No (we resolve from server) |
| Smishing/vishing audio | Message API for text only; no UI |
| Google Safe Browsing overlap | Yes, optional |
| Spear phishing content | Only if text/URL submitted |
| Pharming | No |

---

# 8. Security of PhishShield itself

| Attack | Risk | Prevention | Status |
|---|---|---|---|
| SSRF | Backend fetches user URL for ads | Block localhost/private IPs, timeout, size cap | IMPLEMENTED in ad fetch |
| SQL injection | Malicious URL in SQL | Parameterized queries | IMPLEMENTED |
| XSS | Overlay HTML | React text; extension `escapeHtml` | PARTIAL |
| CSRF | Cross-site POST | JWT not cookies | PARTIAL / not classic CSRF tokens |
| CORS abuse | Any origin | `allow_origins=["*"]` | **Weak for production** |
| Open redirect | N/A as scanner | We don’t redirect users to scanned URL | OK |
| Rate limit | Scan flooding | — | NOT IMPLEMENTED |
| Auth on scans | Privacy of URLs | Scans public | NOT IMPLEMENTED |
| Secrets | GSB key, JWT secret | `.env`, gitignore `.env` | IMPLEMENTED pattern |
| Logging passwords | — | Login doesn’t log password | OK |
| Extension steals OTP | — | Content script doesn’t read forms | By design |

---

# 9. Frontend components (actual)

| Component | Purpose | API |
|---|---|---|
| `AuthContext` | token, login/signup | login, signup, profile |
| `ProtectedRoute` | redirect to login | — |
| `UrlScanner` | submit URL | `checkUrl` |
| `ScanResult` | last result | sessionStorage |
| `Dashboard` / `Statistics` | charts | overview, daily, risk, types, recent |
| `History` | table | recent-urls limit 100 |
| `Settings` | profile + local prefs | profile |
| `Privacy` | honest data list | none |
| `Advisor` | static FAQ | none |
| `Landing` | marketing + scan | checkUrl |

Hooks used: `useState`, `useEffect`, `useMemo`, `useNavigate`, `useContext`.

---

# 10. Dual view (product innovation)

**Simple View** for parents, first-time UPI users: “This looks like SBI but is not. Do not enter OTP.”  
**Technical View** for SOC-style demo: score, tags, DNS, age, intel label.

Antivirus often shows a red shield with little evidence. We show **why** in two layers. We still must not claim we are “better than Google” — we **use** Google when the key is present, plus extra brand/psychology rules.

---

# 11. Presentation slides (what to say)

**SLIDE 1 Title**  
PhishShield AI | SIH 1454 | CyberGuard implementation  
Say: problem + who we help (digital banking users).  
Jury: Is this ML? *Rules + intel today; ML planned.*

**SLIDE 2 Problem**  
Phishing imitating SBI/PayPal; SMS/WhatsApp.  
Diagram: fake vs real domain.

**SLIDE 3 Gap**  
Blacklists lag; HTTPS ≠ safe; tools are English/jargon.  
Do not trash Google Safe Browsing; say we complement it.

**SLIDE 4 Solution**  
URL in → FastAPI engine → score + Simple/Technical → dashboard + extension.

**SLIDE 5 Innovation**  
(1) Brand impersonation + Hinglish psychology  
(2) Dual explanation  
(3) Same API for web and extension  
Not: “our CNN is 99%.”

**SLIDE 6 Architecture**  
Use the honest diagram (FastAPI + SQLite).  
If asked PostgreSQL: *SQLite for MVP, Postgres planned.*

**SLIDE 7 Pipeline**  
DNS → intel → heuristics → ads → psychology → score → persist.

**SLIDE 8 AI/ML**  
Title it “Intelligent detection (current + planned).”  
Current: rules. Planned: supervised model on these features.  
METRIC NOT YET AVAILABLE.

**SLIDE 9 Psychological**  
Urgency/fear/greed lists. Multi-signal. Countdown/urgency alone ≠ verdict.

**SLIDE 10 Simple View**  
Screenshot of warning English.

**SLIDE 11 Technical View**  
Score, tags, Safe Browsing, ads.

**SLIDE 12 Extension**  
MV3, auto-scan, toast, CRITICAL overlay, never-SAFE-if-offline.

**SLIDE 13 Data**  
SQLite tables. Admit user_id unused.

**SLIDE 14 Security**  
Parameterized SQL, bcrypt, JWT, SSRF on ad fetch. Admit CORS * and no rate limit.

**SLIDE 15 Testing**  
pytest: google LOW, paypa1 HIGH/CRITICAL, Hinglish message tags.

**SLIDE 16 Stack**  
React, Vite, Tailwind, FastAPI, SQLite, Manifest V3, requests.

**SLIDE 17 Novelty**  
Hinglish + dual view + unified extension/web scoring.

**SLIDE 18 Limitations**  
URL-centric; no CNN; no cert pinning; SQLite; global history; no rate limit.

**SLIDE 19 Future**  
PostgreSQL, trained model, per-user history, message UI, tighter CORS, punycode.

**SLIDE 20 Conclusion**  
Demo: scan google vs paypa1 vs sbi-login.xyz. Same result in extension.

---

# 12. 2-minute pitch (spoken)

“Sir, phishing sites copy banks and UPI apps. Victims are often non-technical and get a WhatsApp link that looks almost right. Blacklists are late, and HTTPS does not mean the site is genuine.

PhishShield AI, implemented in our CyberGuard repo, lets a user paste a URL or browse with our Chrome extension. Both call the same FastAPI engine. We check whether the domain exists, whether Google Safe Browsing or OpenPhish already flags it, whether the name is a fake PayPal or SBI, whether the ending is suspicious, whether the URL uses fear or Hinglish urgency language, and whether the page uses aggressive popup ads.

We add those signals into a 0 to 100 score: LOW to CRITICAL. Non-technical users get a Simple View in plain English: do not enter OTP. Technical users see the evidence.

We are honest: this version is a multi-signal rule engine plus live intel, not a trained CNN, and we store scans in SQLite. A machine-learning classifier and PostgreSQL are the next step. The value today is consistent scoring, explainability, and real-time browser warnings without inventing results.”

---

# 13. 5-minute technical talk

1. Problem SIH 1454, impersonation.  
2. Architecture: React :5173, FastAPI :8000, sqlite3, extension MV3.  
3. Endpoint POST `/api/v1/threat/check-url`.  
4. Walk `URLChecker.analyze` buckets and thresholds.  
5. Psychology module: tags urgency_detected, fear_tactics, greed_bait.  
6. Persistence: url_checks + threats. Stats charts from SQL.  
7. Auth JWT for dashboard; scans currently anonymous.  
8. Extension cache, badge, overlay, unavailable ≠ safe.  
9. Security: parameterized SQL, bcrypt, SSRF guards; gaps CORS and rate limit.  
10. Tests. Limitations. Roadmap ML + Postgres.

---

# 14. If you don’t know

Templates:

- “That is **planned / not in this repo**. Today we handle it by …”  
- “We do not have that metric yet. I will not invent one.”  
- “The code path is in `url_checker.py`, I can open it.”  
- “Flask/Postgres/CNN were design options; the running system is FastAPI/SQLite/rules.”

**Never:** fake 99% accuracy, “we use TensorFlow,” “we never send URLs,” “we block all ads.”

---

# 15. One-page cheat sheet

**Name:** PhishShield AI / CyberGuard  
**Problem:** Detect phishing domains imitating genuine brands  
**Solution:** FastAPI multi-signal URL engine + React dashboard + MV3 extension  
**Novelty:** Brand impersonation + Hinglish psychology + Simple/Technical views + same API everywhere  
**Stack:** React, Vite, Tailwind, Axios, Recharts, FastAPI, Uvicorn, SQLite, JWT, Manifest V3  
**DB:** users, url_checks, threats  
**ML:** NOT TRAINED — rules; ml_confidence unused  
**Risk:** points → LOW/MED/HIGH/CRITICAL  
**Simple View:** English warning  
**Technical View:** DNS, HTTPS, intel, ads  
**Security:** bcrypt, JWT, parameterized SQL, SSRF on ads  
**Limits:** no CNN, SQLite, no rate limit, CORS *, URL-heavy  
**Future:** PostgreSQL, supervised ML, per-user history, punycode, message UI  

**10 answers:**  
1. Not Flask — FastAPI.  
2. Not Postgres yet — SQLite.  
3. Not CNN — rules + intel.  
4. Same check-url for web and extension.  
5. HTTPS ≠ safe.  
6. Urgency alone ≠ phishing.  
7. Offline ≠ SAFE.  
8. No password collection from pages.  
9. METRIC NOT YET AVAILABLE.  
10. Biggest limit: no trained model + URL-centric analysis.

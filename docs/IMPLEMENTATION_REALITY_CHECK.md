# Implementation Reality Check

**SIH name used in this handbook:** PhishShield AI (Problem SIH 1454)  
**Name in the current repository:** CyberGuard  

In viva, say both: *“Our SIH problem is Intelligent Phishing Domain Detection (SIH 1454). The current codebase is branded CyberGuard. Same product.”*

Do not claim Flask, PostgreSQL, CNN, TensorFlow, or published ML accuracy. Those are **not** in this repository.

---

## How to read this table

| Status | Meaning |
|---|---|
| IMPLEMENTED | Present in code and used at runtime |
| PARTIALLY IMPLEMENTED | File or column exists but is unused, incomplete, or UI-only |
| PLANNED / NOT YET IMPLEMENTED | Discussed in docs/UI as future, or absent from code |

---

## Feature inventory

| Feature | Status | Evidence / file | What to say in viva |
|---|---|---|---|
| FastAPI REST backend | IMPLEMENTED | `backend/app/main.py` | “The API is FastAPI + Uvicorn, not Flask.” |
| Flask | PLANNED / NOT YET IMPLEMENTED | No Flask import anywhere | “We used FastAPI because it is async-ready and has native OpenAPI. Flask was not chosen.” |
| React 19 + Vite 8 dashboard | IMPLEMENTED | `frontend/package.json`, `frontend/src/` | “Dashboard is React + Vite + Tailwind.” |
| Tailwind CSS 4 | IMPLEMENTED | `@tailwindcss/vite` in `package.json` | “Utility CSS for the dark security UI.” |
| Axios | IMPLEMENTED | `frontend/src/services/api.js` | “Frontend HTTP client. Base URL from `VITE_API_URL`.” |
| Recharts | IMPLEMENTED | `Dashboard.jsx`, `Statistics.jsx` | “Charts read live SQLite counts, not dummy data.” |
| React Router | IMPLEMENTED | `frontend/src/App.jsx` | “Login, dashboard, scanner, history, stats, privacy, settings.” |
| JWT signup/login/profile | IMPLEMENTED | `backend/app/routes/user.py`, `services/auth.py` | “Passwords hashed with bcrypt. JWT HS256.” |
| URL threat scan API | IMPLEMENTED | `POST /api/v1/threat/check-url` | “This is the single source of truth for web app and extension.” |
| Message psychology API | IMPLEMENTED (API only) | `POST /api/v1/threat/check-message` | “Backend can scan SMS/email text. The React dashboard does not call it yet.” |
| Rule-based URL engine | IMPLEMENTED | `backend/app/services/url_checker.py` | “Heuristic scoring, not a trained neural net.” |
| Brand impersonation / typosquat | IMPLEMENTED | `_detect_brand()`, Levenshtein, leetspeak, homoglyphs | “paypa1 → PayPal, sbi-login.xyz → SBI.” |
| Psychological language (urgency/fear/greed) | IMPLEMENTED | `backend/app/services/psychology.py` | “Keyword/phrase rules in English + Hinglish. Not an LLM.” |
| Simple View + Technical View | IMPLEMENTED | `backend/app/services/warnings.py` | “Plain English warning vs domain/HTTPS/Safe Browsing details.” |
| Google Safe Browsing | IMPLEMENTED (optional key) | `external_intel.py`, `GOOGLE_SAFE_BROWSING_API_KEY` | “Used if the key is set. Otherwise OpenPhish feed.” |
| OpenPhish fallback | IMPLEMENTED | `external_intel.py` | “Public phishing URL feed when Google key is empty.” |
| DNS existence + RDAP domain age | IMPLEMENTED | `check_domain_exists`, `get_domain_age_days` | “Fails softly if the network is down.” |
| Aggressive ad / malvertising check | IMPLEMENTED | `backend/app/services/ad_signals.py` | “Flags popup ad networks, not normal Google Ads. SSRF-safe fetch.” |
| SQLite persistence | IMPLEMENTED | `backend/app/database/connection.py`, `threats.db` | “Three tables: users, url_checks, threats.” |
| PostgreSQL | PLANNED / NOT YET IMPLEMENTED | Not in requirements or connection code | “Current MVP is SQLite. PostgreSQL is a scale-up plan.” |
| SQLAlchemy ORM models | PARTIALLY IMPLEMENTED | `backend/app/models/*.py` | “Model classes exist, but routes use raw sqlite3. ORM is not the live path.” |
| Alembic / Flask-Migrate | PLANNED / NOT YET IMPLEMENTED | No migrations folder | “Schema is created with CREATE TABLE IF NOT EXISTS.” |
| scikit-learn / Random Forest | PLANNED / NOT YET IMPLEMENTED | Not in `requirements.txt` | “No trained classical ML model in this repo.” |
| TensorFlow / Keras / CNN | PLANNED / NOT YET IMPLEMENTED | No matches in repo | “No CNN. Do not quote CNN architecture as implemented.” |
| NumPy / Pandas / Joblib | PLANNED / NOT YET IMPLEMENTED | Not installed | “No dataset pipeline files.” |
| `ml_confidence` column | PARTIALLY IMPLEMENTED | `url_checks.ml_confidence` default `0.0` | “Column reserved for a future model. Current scans do not fill a real ML score.” |
| Published accuracy / F1 | PLANNED / NOT YET IMPLEMENTED | No metrics file | Say: “METRIC NOT YET AVAILABLE.” |
| Browser extension Manifest V3 | IMPLEMENTED | `extension/` | “Same `check-url` API. Auto-scan, badge, page toast, HIGH/CRITICAL overlay.” |
| Extension login | IMPLEMENTED | `extension/settings/`, service worker LOGIN | “Uses existing `/api/v1/user/login`.” |
| Frontend message scanner UI | PLANNED / NOT YET IMPLEMENTED | `checkMessage` exported but unused | “API ready, page not built.” |
| Rate limiting | PLANNED / NOT YET IMPLEMENTED | No limiter middleware | Admit this gap. |
| CSRF tokens | PLANNED / NOT YET IMPLEMENTED | Bearer JWT, not cookies | “Less CSRF surface than cookie sessions, but not a CSRF implementation.” |
| XSS sanitization library | PARTIALLY IMPLEMENTED | Extension overlay escapes HTML | “React escapes text. Extension warning uses `escapeHtml`.” |
| Localization (full i18n) | PARTIALLY IMPLEMENTED | Hinglish patterns in psychology; UI is English | “Hinglish scam phrases detected. UI language switch is not implemented.” |
| LLM / chatbot advisor | PLANNED / NOT YET IMPLEMENTED | `Advisor.jsx` static FAQ | “Advisor page is rule-based copy. No LLM.” |
| Per-user scan history (`user_id`) | PARTIALLY IMPLEMENTED | Column exists; INSERT does not set `user_id` | “History is global SQLite rows, not filtered by logged-in user.” |
| `average_response_time_ms` | PARTIALLY IMPLEMENTED | Hardcoded `245` in `stats.py` | Do not present 245 ms as a measured SLA. |
| Privacy Center honesty | IMPLEMENTED | `frontend/src/pages/Privacy.jsx` | “We label planned crypto features as Planned.” |
| Pytest API + unit tests | IMPLEMENTED | `backend/tests/` | “Health, phishing URL, psychology, auth, stats.” |
| Git history | NOT AVAILABLE | `master` has no commits in this workspace | Do not invent a commit story. |
| Zero-knowledge / federated learning | PLANNED / NOT YET IMPLEMENTED | Privacy page lists them as Planned | Never claim they run today. |

---

## Actual runtime architecture (honest)

```
Browser extension  ──┐
                     │  POST /api/v1/threat/check-url
React dashboard    ──┤          { url, view: "both" }
                     │
                     v
              FastAPI (Uvicorn :8000)
                     │
         URLChecker + psychology + intel + ads
                     │
                     v
              SQLite threats.db
                     │
                     v
         JSON: score, level, reasons,
               simple_view, technical_view
```

There is **no** Flask process and **no** PostgreSQL server in the running MVP.

---

## Jury-safe one-liners

1. “This version is a multi-signal **rule engine** plus live threat lists, not a trained CNN.”
2. “Web app and extension call the **same** FastAPI endpoint, so scores match.”
3. “Simple View is for non-technical users; Technical View shows the evidence.”
4. “SQLite is the current database; PostgreSQL is future production scale.”
5. “If the backend is down, the extension says unavailable — it never says SAFE.”

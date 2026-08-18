# Tech Stack Study Guide

PhishShield AI (repository product name: **CyberGuard**)

Study only what is in the repo unless a row is marked planned.

Difficulty: 1 = easy viva, 5 = easy to get trapped if you bluff.

---

## Frontend

| Technology | Version (repo) | Where | Why | What to know for viva | Diff | Likely jury questions |
|---|---|---|---|---|---|---|
| React | ^19.2.8 | `frontend/src` | Component UI | JSX, state, hooks, SPA | 3 | Why React? What is a hook? |
| React DOM | ^19.2.8 | `main.jsx` | Mounts the app | `createRoot` | 2 | How does the app start? |
| Vite | ^8.2.0 | `vite.config.js` | Dev server + bundle | HMR, `import.meta.env` | 2 | Why Vite not CRA? |
| Tailwind CSS | ^4.3.3 | `index.css`, `@tailwindcss/vite` | Dark security theme | Utility classes | 2 | How do you style without CSS files per component? |
| Axios | ^1.19.0 | `services/api.js` | HTTP to FastAPI | Interceptor adds JWT | 3 | Axios vs fetch? How is the token sent? |
| React Router DOM | ^7.18.2 | `App.jsx` | Pages | Protected routes | 3 | How do you hide dashboard if not logged in? |
| Recharts | ^3.10.1 | Dashboard, Statistics | Live charts | Pie/bar from API JSON | 2 | Are chart numbers fake? **No — SQLite.** |
| Lucide React | ^1.31.0 | Layouts, pages | Icons | Accessibility labels | 1 | Why icons? |
| Oxlint | ^1.75.0 | `npm run lint` | Lint JS/JSX | Not ESLint | 1 | How do you lint? |

## Backend

| Technology | Version | Where | Why | What to know | Diff | Jury |
|---|---|---|---|---|---|---|
| Python 3 | project venv | `backend/` | Language | Services vs routes | 2 | Why Python? |
| FastAPI | >=0.115 | `app/main.py` | REST API | Pydantic models, OpenAPI | 4 | **Why FastAPI not Flask?** (Flask is not used.) |
| Uvicorn | >=0.30 | run command | ASGI server | `--host 0.0.0.0 --port 8000` | 2 | What is ASGI? |
| Pydantic / pydantic-settings | >=2 | routes, `config.py` | Validation | Request body must match schema | 3 | How do you reject bad JSON? |
| python-dotenv | >=1.0 | intel, auth | Load `.env` | Secrets not in code | 2 | Where is the Safe Browsing key? |
| requests | >=2.31 | `external_intel.py`, `ad_signals.py` | Outbound HTTP | Timeouts, fail-soft | 3 | What if Google is down? |
| passlib + bcrypt 4.0.1 | listed | `auth.py` | Password hash | Never store plaintext | 4 | Can you reverse bcrypt? No. |
| python-jose | >=3.3 | JWT | Access tokens | HS256, `SECRET_KEY` | 4 | What is in the JWT? `sub` = username. |
| httpx | >=0.27 | tests/client stack | Test HTTP | Used by TestClient | 2 | How do you test APIs? |

## Database (actual)

| Technology | Version | Where | Why | What to know | Diff | Jury |
|---|---|---|---|---|---|---|
| SQLite | stdlib `sqlite3` | `threats.db` | Local MVP DB | File-based, one writer-friendly | 3 | Why SQLite not PostgreSQL **today**? |
| SQL | DDL/DML in `connection.py` and routes | Persistence | Parameterized `?` queries | 4 | How do you stop SQL injection? |
| Indexes | `idx_url`, `idx_user_id`, `idx_timestamp` | Speed lookups | Why index URL/time | 3 | Why indexes? |
| SQLAlchemy (library) | >=2.0.30 | `app/models/*.py` only | Planned ORM | **Not used by live routes** | 4 | Do not say “we query via ORM” unless you add it. |
| PostgreSQL | — | — | Planned production | Relational scale-up | 3 | Answer: future, not running. |
| Alembic | — | — | Planned | No migration files | 2 | Schema via `init_db()`. |

## Detection / “AI” (honest)

| Technology | Version | Where | Why | What to know | Diff | Jury |
|---|---|---|---|---|---|---|
| Rule engine | custom | `url_checker.py` | Score 0–100 | Additive points, cap 100 | 4 | Is this AI or rules? **Rules + intel.** |
| Edit distance | Levenshtein | `_levenshtein` | Typosquat | paypa1 / brand distance | 4 | How do you catch lookalike domains? |
| Pattern NLP | string match | `psychology.py` | Urgency/fear/greed | Not BERT/LLM | 3 | Is this machine learning? **No.** |
| Google Safe Browsing v4 | API | `external_intel.py` | Known bad URLs | Optional API key | 3 | Difference vs your engine? |
| OpenPhish feed | HTTP | fallback intel | Free phishing URLs | Cache ~30 min | 3 | What if feed fails? |
| DNS / RDAP | socket + HTTP | domain exists/age | New-domain risk | Fail-soft `None` | 3 | What is RDAP? |
| Ad HTML sample | requests GET | `ad_signals.py` | Malvertising | SSRF blocks private IPs | 4 | Do you flag Google Ads? **No.** |
| scikit-learn / TF / CNN | — | — | Planned | No model files | 5 | If asked CNN: **not implemented.** |

## Extension

| Technology | Version | Where | Why | What to know | Diff | Jury |
|---|---|---|---|---|---|---|
| Manifest V3 | 3 | `extension/manifest.json` | Chrome/Edge/Brave | Service worker, not MV2 background page | 4 | MV2 vs MV3? |
| Service worker | ES module | `background/service-worker.js` | Auto-scan, badge, cache | Can sleep; cache in `chrome.storage` | 4 | How does auto-scan work? |
| Content script | JS | `content/content.js` | On-page toast + warning | Shadow DOM overlay | 4 | Do you steal passwords? **No. URL only.** |
| Popup | HTML/CSS/JS | `popup/` | Manual status | Messages to worker | 2 | Why not put the whole dashboard in the popup? |
| chrome.storage | MV3 | settings, token, cache | Persist config | Token in `local`, cache session | 3 | Where is the password stored? **Nowhere.** |
| Host permissions | http(s)://*/* | call API + inject | Needed for page overlay | Privacy tradeoff | 4 | Why all sites? To warn on any tab. |

## Testing and tools

| Technology | Where | Why | Viva | Diff |
|---|---|---|---|---|
| Pytest | `backend/tests/` | Unit + API | Name 3 tests you ran | 3 |
| FastAPI TestClient | `test_api.py` | In-process HTTP | No live server required | 3 |
| npm | frontend | install/dev | `npm run dev` | 1 |
| pip + venv | backend | isolate deps | how to activate on Windows | 1 |
| Git | repo exists, **no commits yet** in this workspace | version control | Do not invent history | 1 |
| GitHub | not evidenced here | planned remote | Don’t claim a URL unless you have one | 1 |

## Cybersecurity concepts used in code

| Concept | Implemented? | File | Viva note |
|---|---|---|---|
| HTTPS check | Yes (protocol prefix only) | `url_checker.py` +5 if not https | Not full TLS cert validation |
| SSL/TLS certificates | No deep check | — | “We check https://, not cert chain.” |
| Typosquatting | Yes | brand + Levenshtein | |
| Homograph (limited) | Yes | few Cyrillic glyphs | Not full IDN/punycode decoder |
| Punycode / xn-- | Not dedicated | — | Admit gap |
| Threat intel IOC URLs | Yes | GSB / OpenPhish | |
| SSRF protection | Yes on ad fetch | `ad_signals.py` `_is_private_host` | |
| Input validation | Yes | Pydantic + empty URL 400 | |
| CORS | Yes, `allow_origins=["*"]` | `main.py` | Too open for production |
| Auth on scan | No | check-url is public | Anyone can scan; history is global |

---

## Beginner: what “the stack” means

The **frontend** is the website you see.  
The **backend** is the Python brain.  
The **database** is a file that remembers scans.  
The **extension** is a small Chrome program that asks the same brain.

## Technical: why this stack for SIH

FastAPI + SQLite + React is enough to demo end-to-end detection. PostgreSQL, CNN, and Flask are **not** required to tell the truth. If the jury wants a “real ML” roadmap, describe a future Random Forest / CNN on URL features **as planned**, and point at `ml_confidence` as a reserved column.

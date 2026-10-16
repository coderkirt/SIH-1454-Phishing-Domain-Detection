# PHISHEYE technical architecture

Software only. Live path is **FastAPI + sqlite3**, not Flask, not live PostgreSQL.

## Clients

| Client | Role | Tech |
|---|---|---|
| Web app | Operator console + landing + `/extension` | React 19, Vite 8, Tailwind 4, Axios, Recharts |
| Chrome extension | Scan-before-open gate | MV3 1.8.0, service worker, `webNavigation` |

Both call the same HTTP API. Extension default API `http://127.0.0.1:8000` (Settings override; Render zip can bake the live URL). Cache TTL **90s**. Request timeout **30s**.

## API

Uvicorn serves `backend/app/main.py` (PHISHEYE API 2.0.0).

Routers: `threat_detection`, `user`, `stats`, `analyze`, `reports`, `scans`.

Primary scan:

1. `POST /api/v1/threat/check-url` — single URL (`url_checker` → `decision_engine`)
2. `POST /api/v1/threat/check-message` — pasted text
3. `POST /api/v1/analyze/content` (and `/url` `/email` `/qr` `/screenshot`) — multi-signal `content_analyzer` → `risk_engine.fuse`

Auth: bcrypt + JWT on mutating routes (report, feedback, delete). CORS from `FRONTEND_ORIGINS` (`*` disables credentials).

## Data flow (implemented)

```
USER
  ├─ React (paste URL / message / QR / screenshot)
  └─ Chrome MV3 (navigation / visible links)
        │  HTTPS JSON
        ▼
   FastAPI (Uvicorn :8000)
        │
        ├─ normalize_url
        ├─ SSRF + short-link unwrap (redirects.py)
        ├─ threat_intel (OpenPhish, URLhaus, PhishTank, Phishing Army, optional GSB)
        ├─ url_checker (lexical, DNS, RDAP age, TLS, brand, ads)
        ├─ psychology (substring rules)
        ├─ brand_detector, sender_analyzer, reputation
        ├─ qr_analyzer (OpenCV; does not fetch destination)
        │
        ├─ URL path: decision_engine.calculate_final_risk  (intel FLOORS)
        └─ content path: risk_engine.fuse  (STATIC weights)
        │
        ▼
   sqlite3 threats.db
        │
        ▼
   JSON: risk_score, risk_level, simple_view, technical fields
        │
        ├─ Dashboard Scan Result
        └─ Extension: LOW open / MEDIUM ask / HIGH-CRIT or UNAVAILABLE stay closed
```

## Why each live technology

| Tech | Why (honest) |
|---|---|
| Python | Existing detector, tests, feed clients |
| FastAPI | Typed JSON APIs, OpenAPI `/docs`, async-capable ASGI |
| Uvicorn | ASGI server for FastAPI |
| Pydantic | Request validation |
| sqlite3 | Zero-ops local/prototype persistence; **current live DB** |
| bcrypt + JWT | Account auth without cookies |
| React/Vite | Operator UI |
| Chrome MV3 | Only supported way to intercept navigation in Chrome |
| OpenCV headless | QR decode from image bytes |
| requests/httpx | Outbound intel with timeouts |
| NumPy | Image array reshape for OpenCV — **not** neural nets |

PostgreSQL, Redis, Kafka, Docker/K8s as **live** path: **not demonstrated**. PostgreSQL is **Future Scope**.

## Database (live)

File: `backend/threats.db` (`DATABASE_PATH` env override).
Tables include `users`, `url_checks`, `threats`, `content_scans`, `extracted_links`, reports, `scan_feedback`.
PRAGMA foreign_keys ON. Parameterized SQL.
SQLAlchemy models in `app/models/` are **not** the live connection.

Free Render: SQLite **resets on deploy** unless a disk is added.

## Extension failure handling

If API 5xx, timeout (30s), or network error → status `unavailable`.
Unknown is **not** treated as safe. HIGH/CRIT/**unavailable** keep the destination closed (`panel.js`).

## Proposed production architecture (label PROPOSED)

Frontend CDN/static host → FastAPI replicas (stateless) → managed Postgres → optional redis cache of intel/scan → object storage not required for current QR-in-memory design → extension via store **or** enterprise policy.

This is **not** what runs today except: static frontend + one FastAPI + SQLite on Render.

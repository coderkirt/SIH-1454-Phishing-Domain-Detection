# PHISHEYE content audit

**Source of truth:** repository code, not README marketing.
**Hardware:** none. No ESP32, Raspberry Pi, IoT, sensors.
**Team name / members / college:** **Needs verification** — not in the repo. Do not invent on slides.

Status key: **IMPLEMENTED** | **PARTIAL** | **PROTOTYPE** | **PLANNED** | **UNVERIFIED**

---

## What PhishEye currently is

A **software prototype** that scores phishing / lookalike URLs and pasted scam content, explains the result in Simple View + Technical View, stores checks in SQLite, and can **hold a Chrome tab until the scan finishes** (LOW opens, MEDIUM asks, HIGH/CRITICAL stay closed). Dashboard and extension share one **FastAPI** engine.

---

## CLAIM | SOURCE | STATUS | SAFE TO PRESENT?

| Claim | Source | Status | Safe to present? |
|---|---|---|---|
| Product name PHISHEYE | `backend/app/main.py`, `extension/manifest.json` | IMPLEMENTED | Yes |
| FastAPI + Uvicorn API v2.0.0 | `main.py`, `requirements.txt` | IMPLEMENTED | Yes |
| React 19 + Vite 8 dashboard | `frontend/package.json` | IMPLEMENTED | Yes |
| Chrome MV3 extension 1.8.0 | `extension/manifest.json` | IMPLEMENTED | Yes |
| Scan-before-open: LOW open, MEDIUM confirm, HIGH/CRIT closed | `extension/utils/api.js` `canOpenAfterScan` | IMPLEMENTED | Yes — not “antivirus”, not Web Store |
| Backend down ≠ SAFE; tab stays closed | `extension/panel/panel.js`, `api.js` timeout/5xx | IMPLEMENTED | Yes |
| URL check `POST /api/v1/threat/check-url` | `routes/threat_detection.py` | IMPLEMENTED | Yes |
| Message check `POST /api/v1/threat/check-message` | same | IMPLEMENTED | Yes |
| Unified `POST /api/v1/analyze/content` | `routes/analyze.py` | IMPLEMENTED | Yes |
| Email/WhatsApp/SMS as **pasted text** | `Scanner.jsx`, analyze routes | IMPLEMENTED | Yes — never “we read WhatsApp” |
| Native SMS / WhatsApp / Gmail OAuth | `IMPLEMENTATION_STATUS.md` | PLANNED | Future only |
| QR decode OpenCV, no visit of destination | `qr_analyzer.py` | IMPLEMENTED | Yes |
| Screenshot QR | `analyze.py` `/screenshot` | IMPLEMENTED | Yes |
| Screenshot OCR (Tesseract) | optional import; **not** in `requirements.txt` | PARTIAL | “If Tesseract is installed” |
| Simple View + Technical View | `warnings.py`, frontend result pages | IMPLEMENTED | Yes |
| Psychology phrase rules EN+Hinglish | `psychology.py` | IMPLEMENTED | Yes — **rule-based**, not BERT |
| Psych cannot solo HIGH/CRITICAL (cap 35) | `risk_engine.py` | IMPLEMENTED | Yes |
| Weighted fusion for **content** scans | `risk_engine.py` DEFAULT_WEIGHTS | IMPLEMENTED | Yes — weights are **static defaults**, not learned |
| URL path uses intel **floors** | `decision_engine.py` | IMPLEMENTED | Yes |
| Fusion key `ml` copies URL lexical score | `decision_engine.py` docstring, `content_analyzer.py` | IMPLEMENTED | Must say this if you say “ML” |
| Trained sklearn/TF/CNN/BERT | absent from `requirements.txt` | NOT PRESENT | **No** |
| Published accuracy / F1 / dataset | no metrics file | NOT PRESENT | **No** |
| `model_confidence` | `35 + 10×count(signals≥20)`, cap 95 | IMPLEMENTED | Yes as **agreement**, not accuracy |
| Dashboard `safety_rate` | `(url_checks − HIGH/CRIT)/total` `stats.py` | IMPLEMENTED | Dashboard ratio only, **not** F1 |
| OpenPhish, URLhaus, PhishTank, Phishing Army | `threat_intel.py` | IMPLEMENTED | Yes |
| Google Safe Browsing | key optional | PARTIAL | “If API key configured” |
| Intel miss ≠ SAFE; timeout ≠ SAFE | `decision_engine.py` | IMPLEMENTED | Yes |
| URL normalize, SSRF, short-link unwrap | `url_normalize.py`, `ssrf.py`, `redirects.py` | IMPLEMENTED | Yes |
| Domain exists + RDAP age (+20 if <30 days) | `url_checker.py` | IMPLEMENTED | Yes |
| TLS inspect | `ssl_certs.py` | IMPLEMENTED | Yes |
| Brand / lookalike | `brand_detector.py` | IMPLEMENTED | Yes |
| Live DB SQLite `threats.db` via sqlite3 | `database/connection.py` | IMPLEMENTED | Yes |
| PostgreSQL live | not connected | PLANNED | Future only |
| SQLAlchemy models | `backend/app/models/` | UNUSED | “Files exist, not live path” |
| Auth bcrypt + JWT | `auth.py`, `user.py` | IMPLEMENTED | Yes |
| Community reports signal not proof | `report_service.py` | IMPLEMENTED | Yes |
| Render deploy API + static web | `render.yaml`, `docs/RENDER.md` | IMPLEMENTED | Yes — free API sleeps ~15 min |
| Live URLs | `phisheye-web-fhn5.onrender.com`, `phisheye-api.onrender.com` | IMPLEMENTED | Yes |
| Chrome Web Store | not listed | NOT PRESENT | **No** |
| Blockchain | not built | NOT PRESENT | **No** |
| Hardware / IoT | not in repo | NOT PRESENT | **No** |
| Flask | not used | NOT PRESENT | **No** |
| pytest behaviour tests | `backend/tests/` | IMPLEMENTED | Yes — not ML quality metrics |
| CORS `*` on prototype | `main.py` | IMPLEMENTED | Say prototype, not enterprise lockdown |
| Auto retention delete | roadmap | PLANNED | Future |
| Calibrated fraud probability | roadmap | PLANNED | Future |

---

## Must not claim on any slide

Flask · live Postgres · trained CNN · 99%/F1 · user counts · reading WhatsApp/SMS inboxes · padlock = real bank · community report = proof · Chrome Web Store · blockchain · hardware · `ml` channel is a neural net · `safety_rate` is detection accuracy.

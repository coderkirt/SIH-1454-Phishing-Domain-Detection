# SIH Presentation Reality Check

Every claim on the 6-slide deck vs the repository.

| Slide | Claim | Evidence / file | Status |
|---|---|---|---|
| 1 | PS ID SIH1454 | Official SIH list (NTRO); user brief | Official PS |
| 1 | Title: detect phishing domains imitating genuine domains | SIH1454 wording | Official PS |
| 1 | Theme Blockchain & Cybersecurity | Official SIH 2024/25 PS list | Official PS |
| 1 | PS Category Software | Official list + user brief | Official PS |
| 1 | Team ID / Team Name | Not in repo | PLACEHOLDER — fill from portal |
| 2 | Unified `POST /api/v1/analyze/content` | `backend/app/routes/analyze.py` | IMPLEMENTED |
| 2 | URL / domain analysis | `url_checker.py` | IMPLEMENTED |
| 2 | Psychological threat (EN + Hinglish) | `psychology.py` | IMPLEMENTED |
| 2 | Brand + sender signals | `brand_detector.py`, `sender_analyzer.py` | IMPLEMENTED (sender needs caller-supplied From) |
| 2 | GSB / OpenPhish | `external_intel.py` | IMPLEMENTED (GSB needs key) |
| 2 | Community reports as signal not proof | `reputation.py`, `routes/reports.py` | IMPLEMENTED |
| 2 | Risk fusion 0–100 | `risk_engine.py` | IMPLEMENTED |
| 2 | Simple + Technical views | `warnings.py`, `explanation.py` | IMPLEMENTED |
| 2 | Browser overlay HIGH/CRITICAL | `extension/content/content.js` | IMPLEMENTED |
| 2 | Pasted email/WA/SMS (not inbox) | `Scanner.jsx` tabs + analyze API | IMPLEMENTED as paste |
| 2 | QR image | `qr_analyzer.py`, OpenCV in requirements | IMPLEMENTED |
| 2 | Gmail/WhatsApp inbox auto-read | no OAuth | NOT IMPLEMENTED — not claimed as live |
| 2 | Native phone SMS | `mobile_source.py` PLANNED=True | PLANNED — labelled on slide |
| 2 | Screenshot OCR | `analyze.py` pytesseract optional | PARTIAL — labelled |
| 2 | Trained CNN / sklearn model | `"ml": url_risk` copy in `content_analyzer.py`; no TF/sklearn in requirements | PLANNED — labelled; fusion is not a CNN |
| 2 | model_confidence = accuracy | `risk_engine.py` says agreement not accuracy | NOT claimed |
| 3 | FastAPI not Flask | `requirements.txt`, `main.py` | IMPLEMENTED |
| 3 | SQLite live, Postgres planned | `database/connection.py` sqlite3 | ACCURATE |
| 3 | Manifest V3 | `extension/manifest.json` | IMPLEMENTED |
| 3 | Short-link unwrap | `redirects.py` / url checker details | IMPLEMENTED |
| 4 | bcrypt, JWT, parameterized SQL | `auth.py`, routes | IMPLEMENTED |
| 4 | SSRF private IP / metadata block | `ssrf.py`, `ad_signals.py` | IMPLEMENTED |
| 4 | Report 24h / 20 per day | `reputation.add_report` | IMPLEMENTED |
| 4 | CORS allow-all | `main.py` | WEAK / dev — labelled PARTIAL |
| 4 | Global API rate limit | not in middleware | PLANNED — labelled |
| 4 | Psych cannot solo-CRITICAL | `risk_engine.py` psych_only cap 35 | IMPLEMENTED |
| 5 | No published F1 | no metrics file | ACCURATE — KPIs labelled proposed |
| 6 | References | public docs actually used | No fake citations |

## Six-slide compliance

- [x] Exactly 6 slides (template instruction slide removed)
- [x] Slide 1 keeps SMART INDIA HACKATHON 2026 + official field labels
- [x] Official headings preserved on slides 2–6
- [x] No 100% accuracy / inbox monitoring claims
- [x] Team ID not invented

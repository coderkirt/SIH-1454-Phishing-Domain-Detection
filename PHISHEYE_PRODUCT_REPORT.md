# PhishEye product report

Detailed description of the live product: web console, Chrome extension, detection, and what happens after a threat is found. Use this with `PHISHEYE_RAG_ML_BRIEF.md` if the question is about adding RAG or a trained model.

PhishEye does **not** delete a phishing site from the internet, sinkhole DNS, or clean malware off a PC. "Neutralizing" here means stopping the user before they trust the page, explaining why, and recording the case.

There is no trained classifier in this working copy. Detection here is rules plus public threat feeds.

## Fetched remote (11 Oct 2026)

`git fetch` against `https://github.com/coderkirt/SIH-1454-Phishing-Domain-Detection.git`.

| Item | Value |
|---|---|
| Current checkout | branch `phisheye-update`, commit `4a7e055`, one commit ahead of `origin/phisheye-update` |
| Latest `origin/main` | `b82c3e1` (merge of PR #18) |
| Also updated on the remote | `origin/frontend07` moved to `7ac6b42`; new branches `docs/full-readme-update`, `docs/team-phisheye-section`, `docs/update-phisheye-readme` |

This folder has **not** been merged with `origin/main`. The pages above describe the code that is checked out and running. The RAG service below exists only on the fetched `main` branch.

### What `origin/main` added

A standalone service in `rag_service/` (FastAPI, port **8001**). It does not replace the 0–100 score. After a scan, the backend calls it to write a cited explanation. If port 8001 is down, the old rule-written explanation is used (`rag_grounded: false`).

Flow on `main`:

1. The scanner still scores the URL with heuristics and threat feeds.
2. `backend/app/services/explanation.py` calls `fetch_rag_explanation_sync`.
3. That posts to `http://127.0.0.1:8001/api/explain-scan` (`RAG_SERVICE_URL`, timeout from settings, `RAG_ENABLED` defaults to true).
4. The RAG service checks an in-memory cache (512 entries, TTL 1 hour), then retrieves chunks and returns a summary, playbook, brand note, actions, and citations.
5. `frontend/src/pages/ScanResult.jsx` shows those cards only when `explanation.rag_grounded` is true.

Retrieval on that branch:

- Corpus markdown under `rag_service/corpus/`: brand guidance (SBI, Paytm, UIDAI, and others), 16 scam playbooks (OTP/KYC, UPI collect, parcel, job scam, quishing, and others), live-feed notes (CERT-In, CISA, URLhaus), and taxonomy notes (APWG, MITRE, NIST).
- Chunks stored in ChromaDB collection `phishing_knowledge`, embeddings `all-MiniLM-L6-v2`, data dir `rag_service/data/chroma`.
- Hybrid search: dense weight 0.6, BM25 sparse weight 0.4, fused with reciprocal rank fusion (`RRF_K` 60). Default `top_k` is 4. Brand names and threat tags boost matching chunks.
- Optional live wording via `GEMINI_API_KEY` and model `gemini-1.5-flash`. Without a key, synthesis stays on the retrieved chunks.
- Other routes: `GET /api/health`, `GET /api/cache/stats`, `POST /api/cache/clear`.

The numeric decision (levels, feed floors, extension block) is unchanged on that branch. RAG only fills the explanation.

## 1. Product pieces

| Piece | Role |
|---|---|
| React web console | Scan, read the report, history, charts, community flags, advisor |
| FastAPI service | One scoring engine for the console and the extension |
| SQLite (`backend/threats.db`) | Accounts, scans, reports, feed snapshot |
| Chrome extension 1.8.0 (Manifest V3) | Holds a new page closed until the same API scores it |

Anyone can scan a URL from the landing page. History, reports, statistics, privacy, settings, and the advisor require a signed-in account. There is no separate admin role. Every signed-in user has the same API rights.

The extension does not read passwords, OTP fields, cookies, or phone SMS. QR and screenshot bytes are decoded in memory and are not saved as files.

## 2. Web console

Routes in `frontend/src/App.jsx`.

| Route | Who | What it does |
|---|---|---|
| `/` | Public | Landing scan: paste a URL or upload a screenshot. Links to the extension and the dashboard |
| `/login`, `/signup` | Public | Account. Token stored in this browser as `cg_token` |
| `/scan-result` | Public | Last scan: score, level, Simple View, Technical View, evidence, feed providers |
| `/extension` | Public | How to load the unpacked extension in Chrome |
| `/dashboard` | Signed in | Counts, risk pie, threat-type bars, daily summary, recent URLs, quick scan |
| `/scanner` | Signed in | Tabs: URL, Message, Email, WhatsApp/SMS, Screenshot, QR |
| `/history` | Signed in | Stored scans. Search, filter, delete one or all |
| `/reports` | Signed in | The user's scam / risky / safe flags |
| `/statistics` | Signed in | Risk distribution, sources, timeline, report summary |
| `/privacy` | Signed in | What is stored in the browser vs the database |
| `/settings` | Signed in | Profile from the API, theme, local notify/strict toggles, logout |
| `/advisor` | Signed in | Fixed Q&A (not a chatbot): what HIGH/CRITICAL means, what to do if a password was already typed |

Scanner inputs:

- **URL** — address only.
- **Message / WhatsApp / SMS** — pasted text. Links inside the text are extracted and scored. The phone inbox is never read.
- **Email** — pasted body plus optional sender email, display name, and reply-to. No Gmail or Outlook login.
- **Screenshot** — image up to 5 MB. QR is always decoded. Visible text is read only if Tesseract is installed on the server (it is not in `requirements.txt`). An optional hint URL can be added.
- **QR** — image up to 5 MB. Decoded URLs go through the same URL engine as a typed link.

A HIGH or CRITICAL link inside a message is not opened from the scanner. The UI asks first. LOW and MEDIUM can open in a new tab.

The result page shows:

- Score out of 100 and level badge
- Classification: confirmed malicious, suspicious, or no malicious indicators
- Simple View: a short warning in plain language
- Recommendation tied to the level
- Evidence tiles: URL analysis, domain, TLS, threat feeds, brand match, manipulation and redirects
- Technical rows: domain, HTTPS, certificate, TLD, brand, age, feed status, normalized URL
- Per-feed match / no match / unavailable
- Flag actions: mark scam, risky, or safe
- Debug block (normalized URL, each feed, heuristic score, final score)

Dashboard charts use real rows from the database. Empty history stays empty. Numbers are not invented.

## 3. Chrome extension

Loaded with Chrome's "Load unpacked". It is not published on the Chrome Web Store. Default API is `http://127.0.0.1:8000`. Default console is `http://127.0.0.1:5173`. Both can be changed in the extension settings page.

Permissions: `tabs`, `storage`, `webNavigation`, and host access to http/https pages. It does not have permission to read page passwords or cookies.

### Files

| File | Job |
|---|---|
| `background/service-worker.js` | Intercept navigation, call the API, badge, open or refuse the tab |
| `content/gate-clicks.js` | Stop a clicked link from loading before the scan. Same-site clicks on an already allowed host are left alone |
| `content/content.js` | Toast on the page: SCANNING, NO THREAT, FISHY, or THREAT DETECTED |
| `panel/panel.html` | Full-page gate the tab is sent to while the real site stays closed |
| `popup/popup.js` | Toolbar popup: status of the current tab, scan again, open dashboard |
| `settings/settings.js` | API URL, dashboard URL, toggles below |
| `welcome/` | First-run page |

### Settings (extension)

| Toggle | Default | Effect |
|---|---|---|
| Auto scan | On | Scan http(s) pages |
| Scan every page | Off | If off, a host already allowed in this session is not scanned again on every click |
| Scan before open | On | New navigation is replaced by the gate until the scan finishes |
| Page popup | On | Show the in-page toast |

Scan results are cached for 90 seconds. The API call times out after 30 seconds.

Browser-internal pages (`chrome:`, `edge:`, `about:`, `file:`, the extension's own pages) are not scanned. `http://127.0.0.1:5173`, `http://localhost:5173`, and the same hosts on port 8000 are the PhishEye app itself and are not gated or badged as a threat.

### Gate (this is the block)

1. User types a URL or clicks a link.
2. `onBeforeNavigate` / `onCommitted` sees a top-frame http(s) navigation.
3. If scan-before-open is on, and this URL was not already allowed, the tab is sent to the extension gate page. The destination does not render.
4. The gate calls `POST /api/v1/threat/check-url`.
5. Result:

| API result | What the user sees | Tab |
|---|---|---|
| LOW (status `safe`) | "No threat". Page opens | Destination loads |
| MEDIUM (status `medium`) | FISHY. User must choose to continue | Stays closed until they confirm |
| HIGH or CRITICAL | Threat detected. No continue that skips the block | Stays closed |
| Timeout, API down, or scan error | Unavailable. Unknown is not safe | Stays closed |

`canOpenAfterScan`: only `safe` opens by itself. `medium` opens only if the user explicitly continues. Everything else stays blocked.

After a LOW open, or a MEDIUM continue, that URL is remembered for the session so the gate does not loop. The toolbar badge shows OK, MED, HIGH, CRIT, or `!` when the service is down.

The in-page toast is a warning on a page that is already open (for example scan-every-page, or a page that loaded before the gate). It does not replace the gate. The gate is what keeps a dangerous URL closed.

## 4. Detection process

Same engine for a typed URL, a link inside a paste, a QR payload, and the extension.

1. **Normalize.** Scheme, host, registered domain. A short link is expanded only if the hop is not localhost, a private range, link-local, or the cloud metadata address `169.254.169.254`.
2. **URL and domain heuristics.** Lookalike or leetspeak brand (paypa1, amaz0n), suspicious words in the path (verify, login, password, OTP), raw IP (not 127.0.0.1 / localhost), very long URL, many subdomains, suspicious ending (`.xyz`, `.tk`, and similar), domain does not resolve, domain younger than 30 days (strong) or 90 days (weaker), no HTTPS, bad or mismatched certificate, brand name parked on a free host (vercel.app, github.io, and similar).
3. **Threat feeds.** OpenPhish, URLhaus, PhishTank, Phishing Army. Google Safe Browsing only when an API key is configured. Each provider returns match, no match, or unavailable. Feeds are cached on disk (feed list about 30 minutes, a hit about 15 minutes). Startup downloads the public lists unless `PHISHEYE_SKIP_FEED_WARMUP=1`.
4. **Message psychology.** Phrase rules, English and Hinglish, fixed points: urgency 12, fear 12, authority impersonation 12, coercion 10, financial pressure 10, credential/OTP 14, countdown 8, greed bait 10, secrecy 8, emotional manipulation 10.
5. **Extras.** Community scam/risky/safe counts for that domain, optional sender fields on an email paste, popup-style page clutter. Local and private hosts skip the live ad-page fetch.
6. **Decide.**

Single URL: `score = max(heuristic score, feed floor)`.

| Feed match | Minimum score |
|---|---|
| Exact URL | 85 |
| Normalized URL | 80 |
| Hostname | 72 |
| Registered domain | 55 |
| Unverified report | 58 |

A confirmed feed hit cannot be cancelled by a low heuristic score.

Message with several links: weighted sum (weights total 1.0): URL 0.22, domain 0.16, lexical URL score 0.10, message language 0.10, psychology 0.10, threat intel 0.10, brand 0.08, sender 0.05, community 0.05, redirects 0.04. If the only strong signal is psychology, the score is capped at 35 so urgent wording alone cannot become HIGH or CRITICAL.

| Level | Score | Extension |
|---|---|---|
| LOW | 0–29 | Opens |
| MEDIUM | 30–49 | Asks |
| HIGH | 50–69 | Blocked |
| CRITICAL | 70–100 | Blocked |

The lexical slot named `ml` is the same heuristic URL score. It is not a model probability. Confidence on a fused scan counts how many signals fired. It is not accuracy.

`localhost` and `127.0.0.1` score LOW and are labelled as this computer. Other IP addresses still take the IP penalty.

Explanations are built in code (`warnings.py`) from the same decision: Simple View for the user, Technical View for the operator. Nothing is retrieved from a document index.

## 5. What happens after a threat is found

This is the full response path. It is prevention and record-keeping, not a takedown.

1. **Stop the visit.** The extension gate never loads HIGH, CRITICAL, or an unscored URL. MEDIUM needs an explicit continue. The scanner refuses to open a HIGH or CRITICAL link from a pasted message until the user is warned.
2. **Say why.** Simple View states the action in plain language (do not enter a password, the domain does not exist, it looks like a named brand, a feed matched). Technical View lists the signals and each feed. The toast and the toolbar badge repeat the level.
3. **Tell them what to do next.** The advisor page (static text, not an LLM) says: do not sign in, do not download files, tell the sender, and if a password was already typed, change it on the real site opened from a bookmark, not from the suspicious link.
4. **Store the scan.** Signed-in scans go to `content_scans` and `extracted_links`. URL checks from the threat route go to `url_checks`. HIGH and CRITICAL URL checks also insert a row in `threats`. History can be reviewed or deleted by that user.
5. **Let the user flag it.** Signed-in user marks the URL scam, risky, or safe, with an optional reason. That updates `user_reports` and the domain counters (`scam_reports`, `risky_reports`, `safe_reports`). The API response says the flag is one signal, not proof. It does not by itself rewrite the score of the scan just completed. Later scans can use the community weight (0.05).
6. **Optional feedback.** "Was this helpful?" is stored on `scan_feedback` for later false-positive review. It does not change the live score.
7. **Fail closed.** If the API cannot be reached, the extension does not guess. The page stays blocked.

What this path does **not** do:

- It does not contact the phishing host to shut it down.
- It does not email a registrar or a bank.
- It does not remove the message from WhatsApp, SMS, or Gmail.
- It does not change the user's password for them.
- It does not quarantine a downloaded file.
- A community flag is not a legal finding and is not treated as a confirmed feed hit.

## 6. Accounts and stored data

Signup: username, email, password. Password is stored as a bcrypt hash. Login returns a JWT. Mutating routes (report, feedback, delete scans, profile) require that token.

| Table | Contents |
|---|---|
| `users` | username, email, password hash |
| `url_checks` | url, level, score, ml_confidence, time |
| `content_scans` | source type, url, level, score, confidence |
| `extracted_links` | links taken from a message or image |
| `user_reports` | scam / risky / safe plus reason |
| `domain_reputation` | counts per domain |
| `scan_feedback` | helpful yes/no |
| `threats` | snapshot rows from high-risk checks and feeds |

Browser `localStorage` holds the token, username, theme, and two console toggles. The extension's own storage holds the API URL, cache, and gate-allow list.

## 7. API surface

| Prefix | Main calls |
|---|---|
| `POST /api/v1/threat/check-url` | Extension and URL box. Score plus both views |
| `POST /api/v1/threat/check-message` | Pasted text |
| `GET /api/v1/threat/stats`, `intel-status`, `recent-urls` | Console status |
| `POST /api/v1/analyze/content`, `/url`, `/email`, `/qr`, `/screenshot` | Scanner tabs |
| `POST /api/v1/report`, `GET /reputation/domain/{domain}`, `POST /feedback`, `GET /reports/mine` | Flags |
| `GET /api/v1/scans`, `GET /scans/{id}`, `DELETE` one or all | History |
| `GET /api/v1/stats/overview`, `threat-types`, `risk-distribution`, `daily-summary`, `sources`, `timeline`, `reports-summary` | Charts |
| `POST /api/v1/user/signup`, `/login`, `GET /profile` | Account |
| `GET /health` | Process is up |

## 8. Stack

- Python 3.12, FastAPI, Uvicorn, Pydantic, SQLite
- bcrypt, JWT (`python-jose`)
- requests / httpx for feeds
- OpenCV, Pillow, NumPy for QR
- React 19, Vite 8, Tailwind 4, React Router, Axios, Recharts
- Chrome extension Manifest V3
- pytest for API, psychology rules, feed status, QR, TLS, and URL normalization

## 9. Not in this working copy

- No trained model, no dataset file, no precision/recall/F1
- No chatbot on the advisor page (the page itself says a later phase)
- No RAG process in this checkout. Explanations are templates filled from the decision. The fetched `origin/main` branch does add `rag_service/` (see the section at the top). It is not running with the local site on port 5173 until that branch is checked out
- No inbox OAuth, no Firefox build, no Chrome Web Store listing
- No admin console
- Screenshot OCR only if Tesseract happens to be installed on the machine

# Team Study Plans

Everyone must be able to draw the honest architecture: **Extension/React → FastAPI → URLChecker → SQLite**.

Repository roles below map to files. Adjust names to your team.

---

## Shared (all members)

- Product name: PhishShield AI (SIH 1454) / CyberGuard in code  
- Endpoint: `POST /api/v1/threat/check-url`  
- Score thresholds 30/50/70  
- Simple vs Technical View  
- “Is this ML?” honest answer  
- Demo: google.com vs paypa1.com vs sbi-login.xyz  

**1-day (all):** read `docs/IMPLEMENTATION_REALITY_CHECK.md` + cheat sheet.  
**3-day (all):** own module + 20 questions from the bank.  
**Final checklist:** run backend+frontend, scan 3 URLs, open extension, say limitations out loud.

---

## Member 1 — Backend + Integration

**Tech:** Python, FastAPI, Pydantic, Uvicorn, JWT, pytest  
**Files:** `backend/app/main.py`, `routes/*.py`, `services/auth.py`, `tests/test_api.py`  
**Concepts:** REST, JSON, CORS, 400/401/500, TestClient  
**Likely Q:** Why FastAPI not Flask? Walk check-url. How does React call you?  
**Hard Q:** What if two scans at once? Why is check-url unauthenticated?  
**1-day:** Trace check-url from route to sqlite INSERT.  
**3-day:** Memorize every route table; run pytest.  
**Checklist:** Can start uvicorn; can show OpenAPI `/docs`.

---

## Member 2 — Cybersecurity + Threat Intelligence

**Tech:** phishing types, GSB, OpenPhish, HTTPS vs TLS, SSRF  
**Files:** `external_intel.py`, `ad_signals.py`, `url_checker.py` lists  
**Concepts:** typosquat, homograph, IOC, fail-soft intel  
**Likely Q:** HTTPS phishing? Difference vs Safe Browsing?  
**Hard Q:** Punycode? Certificate mismatch? (admit gaps)  
**1-day:** List every +points rule.  
**3-day:** Security table in master guide.  
**Checklist:** Never say we validate full SSL chain.

---

## Member 3 — ML + NLP (honest owner of the gap)

**Tech:** what a classifier would need; current rule features; psychology strings  
**Files:** `psychology.py`, `url_checker.py`, `ml_confidence` column  
**Concepts:** accuracy vs recall, false pos/neg, data leakage (theoretical)  
**Likely Q:** Where is the CNN? Dataset? F1?  
**Must answer:** METRIC NOT YET AVAILABLE; planned model would use these features.  
**Hard Q:** “This isn’t AI.” Reply: intelligent automation + intel; SIH ML phase is next.  
**1-day:** Psychology tests.  
**3-day:** Explain why rules can still be “intelligent systems.”  
**Checklist:** Do not quote fake accuracy.

---

## Member 4 — Frontend

**Tech:** React 19, hooks, Router, Axios, Tailwind, Recharts  
**Files:** `frontend/src/**` especially `api.js`, `AuthContext`, Dashboard, ScanResult  
**Likely Q:** How is the token attached? Are charts fake?  
**Hard Q:** Why last scan in sessionStorage not DB fetch by id?  
**1-day:** Click every route logged-in.  
**3-day:** Explain ProtectedRoute + error messages.  
**Checklist:** Know `VITE_API_URL`.

---

## Member 5 — UI/UX + Localization

**Tech:** Simple View copy, Advisor FAQ, Privacy Center, dark theme  
**Files:** `warnings.py`, `Advisor.jsx`, `Privacy.jsx`, `Landing.jsx`  
**Likely Q:** Why two views? Why not Hindi UI?  
**Answer:** Hinglish **detection** exists; **UI i18n** not implemented.  
**Hard Q:** Accessibility? Contrast, text not color-only (RiskBadge + words).  
**1-day:** Read every Simple View branch.  
**3-day:** Privacy planned vs implemented.  
**Checklist:** Never claim ZK proofs.

---

## Member 6 — Database + Browser Extension

**Tech:** SQLite schema, indexes, MV3, service worker, content script  
**Files:** `database/connection.py`, `extension/**`  
**Likely Q:** Why SQLite? How does auto-scan work?  
**Hard Q:** user_id unused; SW sleep; host_permissions privacy  
**1-day:** Load unpacked extension; show toast.  
**3-day:** Badge states; cache TTL; CONTINUE ANYWAY.  
**Checklist:** Offline must not show SAFE.

---

## 3-day schedule (team)

### Day 1 — Project + fundamentals
- Morning: SIH 1454, phishing vs impersonation, demo dry run  
- Afternoon: architecture + API list  
- Evening: Simple/Technical views + privacy  
- Night: cheat sheet twice  

### Day 2 — Own module + depth
- Morning: own files line-by-line  
- Afternoon: pair with adjacent member (backend↔frontend, intel↔extension)  
- Evening: pytest + three live scans  
- Night: 15 questions in your section  

### Day 3 — Jury + cross questions
- Morning: 30 hard questions out loud  
- Afternoon: mock viva (one member is hostile jury)  
- Evening: limitations + future scope only  
- Night: 2-min pitch + 5-min technical; sleep  

**Priority if time is short:** reality check → check-url pipeline → “not CNN/not Postgres” → demo → limitations.

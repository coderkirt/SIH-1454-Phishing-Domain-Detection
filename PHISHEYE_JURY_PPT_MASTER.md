# PHISHEYE jury PPT master (15 slides)

Use this with `PHISHEYE_GAMMA_PROMPT.md` and a **premium navy / ice-blue** Gamma template (not product red).

**Team name / members / institution:** Needs verification — not in repo. Leave blank or fill from your portal only.

**Hackathon:** Lenovo (adjust name if the organizer wrote it differently).

Every on-slide line is safe to present unless marked Future / Proposed.

---

## SLIDE 1 — TITLE

**A. Title:** PHISHEYE  
**B. Objective:** Name the product and the promise.  
**C. On-slide:**
- PHISHEYE
- Scan the link before the fake page loads.
- Lenovo Hackathon · Software · Cybersecurity
- Working prototype · FastAPI + React + Chrome MV3
- No team names unless verified  

**D. Visual:** Full-bleed navy, ice-blue underline, empty space. No architecture.  
**E. Technical:** Tagline is operational (gate + explain), not “CNN accuracy.”  
**F. Jury should understand:** This is a real software prototype, not hardware, not a paper.  
**G. Notes:** Say PHISHEYE once. Dashboard and extension share FastAPI.  
**H. Q:** Is this an app or an extension?  
**I. A:** Both; one engine.

**Remember:** The name and the gate.

---

## SLIDE 2 — THE PROBLEM

**A. Title:** A padlock does not mean it is your bank.  
**B. Objective:** Human-centric phishing, no fake statistics.  
**C. On-slide:**
- Attack flow: ATTACKER → DECEPTIVE MESSAGE/LINK → TRUST → CLICK → FAKE HTTPS SITE → LOSS (OTP / UPI / password)
- Illustration (not a measured stat): “Your SBI account will be blocked. Complete KYC in 10 minutes. Share OTP.”
- Technical browser warnings fail people who will not parse certificates.  

**D. Diagram:** 6-node attack chain, last node cobalt (not red).  
**E. Why warnings fail:** `warnings.py` exists because jargon does not stop OTP entry.  
**F. Understand:** Impersonation + panic, not “user forgot HTTPS.”  
**G. Notes:** Do not cite “billions lost.” External source required if you add a number.  
**H. Q:** Why not just teach URL-bar reading?  
**I. A:** Victims are often first-time UPI users; Simple View is OTP language.

**Remember:** HTTPS is not identity.

---

## SLIDE 3 — THE GAP

**A. Title:** Technical indicators are not the whole attack.  
**B. Objective:** Defensible difference, no competitor ranking.  
**C. On-slide (table):**

| Dimension | Conventional emphasis | PhishEye (this repo) |
|---|---|---|
| URL / domain | Often primary | Heuristics + age + TLS + lookalike |
| Lists / intel | Blacklist match | Match **floors** score; **miss ≠ SAFE** |
| Social engineering | Often absent | **Rule-based** psych signals |
| Output | Score / blockpage jargon | Simple View + Technical View |
| Browser | After-the-fact or none | **Scan-before-open gate** |
| Feedback | Rare | Community report = **signal, not proof** |

Wording: “Many conventional tools emphasize technical indicators. PhishEye also scores human-facing social-engineering phrases and explains the result in OTP language.”  

**D. Visual:** Two-column comparison, ice-blue headers.  
**E. Not “better than VirusTotal.”** VT-style research is usually after click.  
**F. Understand:** Gap = explain + gate + psych rules + intel floors.  
**G. Notes:** Never say “best.”  
**H. Q:** How are you different from Safe Browsing?  
**I. A:** GSB is optional input; we still run heuristics/psych; miss ≠ SAFE; we explain.

**Remember:** Miss ≠ safe. Panic is a signal. Gate is before load.

---

## SLIDE 4 — INTRODUCING PHISHEYE

**A. Title:** One engine. Score, explain, optionally hold the tab.  
**B. Objective:** Product in one journey.  
**C. On-slide journey (implemented):**
1. User pastes a URL/message/QR **or** Chrome navigates  
2. Client POSTs to FastAPI  
3. Normalize + SSRF-safe unwrap  
4. Intel + URL/domain/TLS/brand heuristics  
5. Psychology phrase rules (not a neural net)  
6. `ml` channel **copies URL score** (not a trained model)  
7. Floors (URL) or static weighted fuse (content)  
8. Simple View + Technical View  
9. SQLite row; extension LOW open / MEDIUM ask / HIGH-CRIT closed  
10. Optional community report (signal)

**D. Diagram:** INPUT → ANALYSIS → SIGNALS → RISK ENGINE → EXPLANATION → ACTION  
**E. AI/ML box must not imply a trained CNN.**  
**F. Understand:** What happens on a suspicious link, exactly.  
**G. Notes:** WhatsApp = paste. QR = OpenCV, no visit.  
**H. Q:** Do you read my WhatsApp?  
**I. A:** No.

**Remember:** Same brain for site and extension.

---

## SLIDE 5 — END-TO-END WORKFLOW

**A. Title:** From click to decision.  
**B. Objective:** Map boxes to code.  
**C. On-slide (adapt — all IMPLEMENTED):**

USER / BROWSER → INPUT → PREPROCESS (normalize, SSRF) → URL/DOMAIN/TLS → THREAT INTEL → HEURISTIC SCORE → PSYCHOLOGY RULES → DECISION (`decision_engine` **or** `fuse`) → EXPLAIN (`warnings.py`) → SQLITE → UI / GATE

Label **`ml` = copy of URL heuristic** under the heuristic box, not a separate trained model box.  
Do **not** draw PostgreSQL. Draw **sqlite3**.  

**D. Visual:** Vertical pipeline, ice-blue arrows.  
**E. Per block:** input JSON/URL; processing named files; output score+views.  
**F. Understand:** Two decide paths: floors vs fuse.  
**G. Notes:** Content scans fuse; single URL floors.  
**H. Q:** Where is the ML service?  
**I. A:** There isn’t a separate one. `ml` is a field copy.

**Remember:** sqlite3 in the diagram.

---

## SLIDE 6 — AI / ML ENGINE (HONEST)

**A. Title:** Explainable scoring — no trained model file in this repository.  
**B. Objective:** Survive an ML professor.  
**C. On-slide:**
- Data source: the URL or pasted text **this request**, plus public feeds  
- Dataset / training / validation / F1: **not in product**  
- Features: lexical URL, lookalike, age, TLS, intel match, psych tags (see `url_checker` / `psychology`)  
- “Model”: **not** RF/XGB/NN. Code key `ml` **= URL risk copy**  
- Integration: fusion weight 0.10 on content path; floors on URL path  
- NumPy: OpenCV images, not nets  
- Future: curated reports → supervised model  

**D. Diagram:** RAW → PREPROCESS → FEATURES → SIGNALS → FLOORS/FUSE → SCORE  
**E. Why this is appropriate for a prototype:** explainable, demoable, no fake accuracy.  
**F. Understand:** Do not ask for CNN weights.  
**G. Notes:** Offer `PHISHEYE_AI_ML_EXPLANATION.md`.  
**H. Q:** Show accuracy.  
**I. A:** Metric not available. pytest tests behaviour.

**Remember:** `ml` copies URL score.

---

## SLIDE 7 — PSYCHOLOGICAL THREAT DETECTION

**A. Title:** Phishing is also social engineering.  
**B. Objective:** Differentiator without NLP theater.  
**C. On-slide:**
- Type: **RULE-BASED** (not ML/NLP neural, not hybrid-learned)  
- Example: “Your account will be blocked. Verify immediately.” → fear + urgency + credential/OTP  
- Hinglish in code: abhi click, jaldi karo, band ho jayega  
- Countdown phrases: within 10 minutes, expires in  
- Interaction: content fuse uses psych weight 0.10; **cap 35** if psych-only  
- URL path: psych scaled down (cap 40)  

**D. Diagram:** TEXT → lowercase → phrase match → category points → psych score → fuse/cap  
**E. Points table optional in notes, not 10 paragraphs on slide.  
**F. Understand:** Panic is scored; it cannot solo CRITICAL.  
**G. Notes:** Attackers can avoid phrases — limitation.  
**H. Q:** Is this BERT?  
**I. A:** Substring rules.

**Remember:** Rule-based + cap 35.

---

## SLIDE 8 — RISK + EXPLAINABILITY

**A. Title:** Many signals. One decision. Two views.  
**B. Objective:** Show the real combination.  
**C. On-slide:**

Content (static weights):  
Technical/url 0.22 + domain 0.16 + ml 0.10 + nlp 0.10 + psych 0.10 + intel 0.10 + brand 0.08 + redirect 0.04 + sender 0.05 + community 0.05  

URL path: `max(heuristic, intel_floor)` — floors 85 / 80 / 72 / 55  

Levels: LOW 0–29 · MED 30–49 · HIGH 50–69 · CRIT 70–100  
Confidence: agreement, not accuracy  

**SIMPLE VIEW:** “Do not enter your password, OTP, or card number.” LOW is **not** a guarantee.  
**TECHNICAL VIEW:** tags, TLS, age, intel provider, reasons, psych findings  

Weights = **static defaults, not learned.**  

**D. Diagram:** stacked bars or weight row + two view cards.  
**E. Formula is in `risk_engine.py` / `decision_engine.py`.  
**F. Understand:** Explainability is the product.  
**G. Notes:** Quote LOW guarantee sentence if challenged.  
**H. Q:** Who tuned weights?  
**I. A:** Documented starting defaults, not proven-optimal.

**Remember:** Static weights + intel floors.

---

## SLIDE 9 — BROWSER EXTENSION + CHANNELS

**A. Title:** Scan first. Then maybe open.  
**B. Objective:** Protection that is real but scoped.  
**C. On-slide:**
- Channels **implemented:** URL, pasted SMS/WA/email, QR (no visit), screenshot (QR; OCR if Tesseract), extension navigation  
- Flow: visit → MV3 holds tab → `POST check-url` → risk → LOW open / MEDIUM ask / HIGH-CRIT **closed**  
- API down / timeout: **UNAVAILABLE**, stays closed (unknown ≠ safe)  
- Cache 90s · timeout 30s · Load unpacked · not Web Store  
- No password/OTP/cookie/SMS read  

**D. Diagram:** Browser → extension → FastAPI → result → warning/gate  
**E. This **is** blocking of navigation for HIGH/CRIT, not “complete internet protection.”  
**F. Understand:** Main demo surface.  
**G. Notes:** github.com LOW; lookalike stays closed; no live kits.  
**H. Q:** Chrome Web Store?  
**I. A:** No.

**Remember:** Unavailable is not safe.

---

## SLIDE 10 — TECHNICAL ARCHITECTURE

**A. Title:** What actually runs.  
**B. Objective:** Replace the Postgres cartoon.  
**C. On-slide diagram:**

```
USER
 ├ WEB APP (React :5173)
 └ EXTENSION (MV3)
        │ HTTPS JSON
     FASTAPI + UVICORN :8000
        ├ scanner / analyze
        ├ risk: floors OR fuse
        ├ auth JWT
        ├ intel + psychology + QR
        └ sqlite3 threats.db
```

**Why:** FastAPI = demoable JSON+docs; sqlite3 = prototype persistence; MV3 = only Chrome intercept.  
Postgres = **Future**. ML box = **heuristic copy**, not a model server.  

**D. Visual:** navy architecture, ice arrows.  
**E. See `PHISHEYE_TECHNICAL_ARCHITECTURE.md`.  
**F. Understand:** No Flask, no live Postgres.  
**G. Notes:** SQLAlchemy unused.  
**H. Q:** Where is Docker?  
**I. A:** Not the documented live path; Render blueprint is.

**Remember:** FastAPI + sqlite3 + MV3.

---

## SLIDE 11 — SECURITY, PRIVACY, TRUST

**A. Title:** What we collect — and what we refuse to.  
**B. Objective:** Trust without “enterprise-grade” theater.  
**C. On-slide:**

**Implemented:** bcrypt+JWT; parameterized SQL; SSRF guard; 5 MB uploads; JWT on report/delete; QR in memory not saved; no passwords/OTPs collected; extension does not read password fields; Render public URLs are HTTPS.  

**Prototype limits:** CORS often `*`; SQLite on free Render; token in localStorage; no auto retention job.  

**Privacy:** store account + URL/scores + report you submit; not raw secrets (`PRIVACY_MODEL.md`).  

**D. Visual:** two columns IMPLEMENTED vs HARDENING (future).  
**E. Do not claim SOC2.  
**F. Understand:** Honest privacy story is a feature.  
**G. Notes:** Delete analysis exists.  
**H. Q:** Do you store the WhatsApp dump?  
**I. A:** Paste analysis; metadata + extracted URLs, not a full inbox.

**Remember:** SSRF + no OTP collection.

---

## SLIDE 12 — FEASIBILITY + SCALE

**A. Title:** Feasible as a prototype. Scale is a plan.  
**B. Objective:** Separate now vs proposed.  
**C. On-slide:**

| | Now | Proposed |
|---|---|---|
| Technical | FastAPI loop works | Same APIs, more workers |
| Operational | Paste + Load unpacked | Store / MDM (future) |
| Economic | Public feeds + Render | Quota + managed DB (no fake prices) |
| Deploy | Render API + static | Replicas + Postgres disk |
| Scale | One SQLite | Stateless API + cache (not built) |

Bottlenecks now: intel HTTP, SQLite locks, 30s timeout, free sleep.  

**D. Visual:** now/next table, not a fake AWS bill.  
**E. `PHISHEYE_FEASIBILITY.md`  
**F. Understand:** Jury can trust the demo; they should not hear “millions of QPS.”  
**G. Notes:** Wake /health.  
**H. Q:** Millions of URLs?  
**I. A:** Not this deployment. Here’s the proposed shape.

**Remember:** Now vs proposed.

---

## SLIDE 13 — IMPLEMENTATION + VALIDATION

**A. Title:** Built. Tested for behaviour. Not a published F1.  
**B. Objective:** Proof without fake metrics.  
**C. On-slide:**

**IMPLEMENTED:** URL/message/QR/screenshot-QR, Simple/Technical, fusion+floors, MV3 gate, auth, stats, reports, Render.  
**PARTIAL:** GSB key, Tesseract OCR.  
**FUTURE:** trained model, Postgres, native SMS, Web Store.  

Screenshots: landing, scanner tabs, history, extension page (`docs/_leap_media/`).  

**Validation:** `backend/tests/` pytest (api, psychology, intel, qr, ssl, golden, normalize).  
**Not:** official accuracy. Dashboard safety_rate is **not** F1.  

**D. Visual:** screenshot collage + three status chips.  
**E. Golden tests ≠ production dataset.  
**F. Understand:** Working demo + honest tests.  
**G. Notes:** Do not flash 87.8%.  
**H. Q:** False positive rate?  
**I. A:** Not published. We have guards (psych cap, trusted hosts) and tests.

**Remember:** Screenshots + pytest, no F1.

---

## SLIDE 14 — IMPACT + USE CASES

**A. Title:** Make the warning understandable enough to act on.  
**B. Objective:** Human impact, no invented user counts.  
**C. On-slide scenarios (channels we actually take):**
- Fake KYC / account blocked SMS → **paste** or screenshot/QR → Simple View  
- Lookalike bank URL → dashboard or **extension gate**  
- QR poster → OpenCV, no destination fetch  
- Community mark scam → **signal**, not proof  

Users: students, elderly, first-time digital banking — **relevant**, not measured adoption.  

**D. Visual:** one KYC scenario strip.  
**E. No “saved ₹X crore.”  
**F. Understand:** Meaningful because OTP victims cannot read certs.  
**G. Notes:** Don’t claim org-wide SOC.  
**H. Q:** Impact metric?  
**I. A:** Not measured. The impact is the warning + gate in the demo.

**Remember:** Understandable enough to act, not a fake ROI.

---

## SLIDE 15 — FUTURE + CLOSE

**A. Title:** Current → enhanced → scale  
**B. Objective:** Roadmap clearly labelled FUTURE.  
**C. On-slide:**

**NOW:** explainable scoring, intel floors, psych rules, scan-before-open, SQLite, Render.  
**FUTURE:** curated supervised model, Postgres, Android SMS companion, inbox APIs if granted, campaign clustering, store listing, retention jobs.  

Close: “PhishEye aims to make phishing detection understandable enough to act on — not a black-box score with a fake F1.”  

**D. Visual:** three-stage roadmap, ice-blue.  
**E. Do not list OCR/QR as future if already implemented (QR is now; OCR partial).  
**F. Understand:** Team knows the prototype boundary.  
**G. Notes:** Say FUTURE out loud.  
**H. Q:** Blockchain?  
**I. A:** Not built.

**Remember:** Understandable enough to act on.

---

## Competitive framing (not a slide of “we win”)

Use Available / Different focus / Not demonstrated only:

| Capability | PhishEye (this repo) |
|---|---|
| URL/domain heuristics | Available |
| Threat intel floors | Available |
| Trained ML classifier | Not demonstrated |
| Neural NLP | Not demonstrated (rules Available) |
| Simple + Technical View | Available |
| Scan-before-open extension | Available (Load unpacked) |
| Native inbox | Not demonstrated |

Do not name-rank vendors.

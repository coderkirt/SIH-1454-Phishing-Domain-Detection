# SIH 2026 Presentation — Content (6 slides)

Official template: `SIH2026-IDEA-Presentation-Format.pptx`  
Output: `PhishShield_SIH_2026_Final_Presentation.pptx`  
Slide size: 13.333" × 7.5" (16:9). Slide 7 (instructions) deleted per template note.

Team ID / registered team name were **not** in the repository → placeholders on the title slide.

---

## Slide 1 — TITLE PAGE (official structure kept)

SMART INDIA HACKATHON 2026

- Problem Statement ID – SIH1454
- Problem Statement Title – Create an intelligent system using AI/ML to detect phishing domains which imitate look and feel of genuine domains
- Theme – Blockchain & Cybersecurity
- PS Category – Software
- Team ID – [TEAM ID]
- Team Name (Registered on portal) – [TEAM NAME]

Fill Team ID and Team Name from the SIH portal before upload.

---

## Slide 2 — IDEA TITLE / Proposed Solution

**Idea title:** PhishShield AI — Analyze before you trust

**Implemented flow:** URL | pasted email/WA/SMS | webpage (extension) | QR image → `POST /api/v1/analyze/content` → URL/domain, psychology, brand/sender, GSB/OpenPhish, community signal → risk fusion → Simple + Technical view.

**Addresses SIH1454:** lookalike-domain detection plus a warning a non-technical user can act on.

**Innovation (implemented only):** Detect, Understand, Explain, Protect, Learn (community as signal not proof).

**Honesty line on slide:** no inbox OAuth; OCR partial; native SMS planned; trained CNN planned; confidence ≠ accuracy.

---

## Slide 3 — TECHNICAL APPROACH

Stack: React/Vite/Tailwind/Axios/Recharts · FastAPI/Pydantic · SQLite live · URLChecker + Psychology 2.0 + fusion + OpenCV QR · MV3 extension · bcrypt/JWT/SSRF.

Architecture: INPUT → NORMALIZE → ANALYZE → FUSE → EXPLAIN → ACT.

Not listed as implemented: Flask, live PostgreSQL, TensorFlow CNN, sklearn model file.

---

## Slide 4 — FEASIBILITY AND VIABILITY

Three columns: Technical / Operational / Security (only real controls).

Challenge→mitigation matrix including psych false-positive guard and report rate limits.

---

## Slide 5 — IMPACT AND BENEFITS

Target users · Before vs With PhishShield · Proposed KPIs explicitly **not** claimed results.

---

## Slide 6 — RESEARCH AND REFERENCES

SIH1454/NTRO, Google Safe Browsing, OpenPhish, RDAP, OWASP SSRF/phishing, FastAPI, React, Chrome MV3, SQLite, OpenCV. No fake papers.

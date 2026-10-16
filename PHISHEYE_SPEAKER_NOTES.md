# PHISHEYE speaker notes — Lenovo Hackathon

Slides expand what is on screen. Do not read the bullets verbatim. **No hardware. No Flask. No live Postgres. No trained CNN. No 99%.**

Team name / college are **not in the repo**. If the portal has them, say them on slide 1. Do not invent.

---

## Slide 1 — Title

**Say:** We built PHISHEYE: a working software prototype that scores a link or a pasted scam message, explains it in plain English, and can stop the browser **before** the fake page loads.

**Judges may ask:** Is this an app or an extension?  
**Answer:** Both share one FastAPI engine. The dashboard is the console. The extension is the protection.

---

## Slide 2 — The problem

**Say:** Open with an SBI/UPI OTP SMS. The site has a padlock. The victim still loses money. The problem is impersonation plus panic, not “the user forgot HTTPS.”

**Q:** Why not just teach people to read the URL bar?  
**A:** Non-technical users are the victims we designed Simple View for (`warnings.py`).

---

## Slide 3 — The gap

**Say:** A feed miss is not safe. A certificate is not a brand. A scary message without a bad domain is not automatically CRITICAL — we cap psychology so marketing language cannot nuke a site.

**Q:** How are you different from VirusTotal?  
**A:** VT is research after the click. We gate navigation and speak in OTP language.

---

## Slide 4 — Introducing PHISHEYE

**Say:** Inputs we actually take: URL, pasted message/email/WhatsApp/SMS text, QR image, screenshot (QR always; OCR only if Tesseract is installed). Output: LOW/MEDIUM/HIGH/CRITICAL, Simple View, Technical View.

**Q:** Do you read my WhatsApp?  
**A:** No. Paste the text. Chrome cannot read the phone.

---

## Slide 5 — How it works

**Say:** User → React or MV3 → FastAPI → analyzers → decision engine (URL) or weighted fuse (content) → SQLite → result. Walk the boxes. Name FastAPI, not Flask. Name SQLite, not Postgres.

**Q:** Where is PostgreSQL?  
**A:** Planned. Live file is `backend/threats.db`.

---

## Slide 6 — AI / ML

**Say:** Intelligence today is **explainable scoring**, not a trained network. Features are URL/domain heuristics. The fusion channel named `ml` **copies the URL score** so a low ML number cannot be used as a clean bill of health. Weights are in `risk_engine.py`. No F1 in this repo.

**Q:** Show the CNN.  
**A:** There isn’t one. Phase 2 after curated reports. NumPy is for OpenCV images.

---

## Slide 7 — Psychological threat detection

**Say:** Read the example: “Your account will be blocked. Verify immediately.” That hits fear + urgency + credential pressure in `psychology.py` (English and Hinglish). Psychology **cannot** take a site to CRITICAL alone — fuse cap 35 without a strong technical signal.

**Q:** Is this BERT?  
**A:** Substring rules. Honest and demoable.

---

## Slide 8 — Multi-channel + extension

**Say:** Demo path: Load unpacked → github.com should gate then open if LOW. A lookalike stays closed. Do **not** open a live phishing kit.

**Q:** Chrome Web Store?  
**A:** Not listed. Zip from `/extension`. Same API as the dashboard.

---

## Slide 9 — Risk + explainability

**Say:** Simple View: do not enter OTP. Technical View: tags, intel, TLS, age. URL scans use intel **floors** (confirmed hit cannot be averaged down). Content scans use documented weights. Confidence is how many signals fired, not accuracy.

---

## Slide 10 — Stack

**Say:** Point at groups. If they hear “AI” — point at fusion + intel, not TensorFlow. Deployment: Render API + static web. Extension is local.

---

## Slide 11 — Product proof

**Say:** These are screenshots of the running UI, not Figma. Stats on the dashboard are **that SQLite file’s counts**, not a published detection rate. Do not quote 87.8% as accuracy.

**Q:** How many users?  
**A:** Not claimed. Prototype.

---

## Slide 12 — Impact + future

**Say:** Impact today: understandable warnings + scan-first browser. Future (say the word **future**): labelled ML, Postgres, Android SMS companion. Close on the line on the slide.

**Q:** Blockchain? Theme may mention it. We did not build a chain.

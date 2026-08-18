# PHISHEYE

An AI-powered **multi-channel scam intelligence** system. It analyzes links, messages, sender signals, psychological manipulation and community reports in one threat engine.

This is not “just another phishing URL checker.”

## What you can scan today
- Direct URLs
- Pasted messages (SMS, WhatsApp, email text)
- Email sender fields if you type them
- QR codes from images
- Screenshots (QR always; OCR if Tesseract is installed)
- Visible page links from the Chrome extension

## What this app cannot do
- Read native phone SMS from Chrome (**planned:** Android companion)
- Read private Gmail/WhatsApp without you pasting content or using visible-page links
- Claim a calibrated “true probability of fraud”
- Treat community reports as proof

## Folders
- `backend/` — FastAPI + SQLite
- `frontend/` — React + Vite dashboard
- `extension/` — Manifest V3
- `docs/` — architecture and honest status

## Start

### Backend (http://localhost:8000)

```powershell
cd "$env:USERPROFILE\cybersecurity-platform\backend"
.\venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend (http://localhost:5173)

```powershell
cd "$env:USERPROFILE\cybersecurity-platform\frontend"
npm run dev
```

Sign up, open **Scan**, paste a message with several links, then open Dashboard / Reports / History.

## Risk numbers (read this)
- **Risk score** 0–100: fused evidence
- **Scam risk**: same score shown as an estimate, not a calibrated fraud probability
- **Model confidence**: how many signals agreed — **not accuracy**

## Docs
- `docs/IMPLEMENTATION_STATUS.md`
- `docs/MULTI_CHANNEL_ARCHITECTURE.md`
- `docs/CONTENT_ANALYSIS.md`
- `docs/COMMUNITY_REPUTATION.md`
- `docs/PSYCHOLOGICAL_THREAT_DETECTION.md`
- `docs/BROWSER_EXTENSION.md`
- `docs/PRIVACY_MODEL.md`
- `docs/SECURITY_MODEL.md`
- `docs/FEATURE_ROADMAP.md`

## SIH 2026 idea submission (exactly 6 slides)

Uses the official SIH template structure. Fill `[TEAM ID]` and `[TEAM NAME]` from the portal before upload.

- `PhishShield_SIH_2026_Final_Presentation.pptx`
- `PhishShield_SIH_2026_Final_Presentation.pdf`
- `docs/SIH_PRESENTATION_CONTENT.md`
- `docs/SIH_PRESENTATION_REALITY_CHECK.md`

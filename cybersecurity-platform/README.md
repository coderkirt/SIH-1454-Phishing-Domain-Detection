# CyberGuard

AI-powered phishing and threat detection platform.

## What is in this folder

- `backend/` — FastAPI + SQLite threat detection API
- `frontend/` — React + Vite + Tailwind dashboard
- `extension/` — Manifest V3 popup that can scan the current tab URL

## How to start

### 1. Backend (http://localhost:8000)

```powershell
cd "$env:USERPROFILE\cybersecurity-platform\backend"
.\venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend (http://localhost:5173)

Open a second PowerShell window:

```powershell
cd "$env:USERPROFILE\cybersecurity-platform\frontend"
npm run dev
```

Then open http://localhost:5173

Sign up, log in, scan a URL, and open Dashboard / History / Statistics.

## Environment

Frontend reads `frontend/.env`:

```
VITE_API_URL=http://localhost:8000
```

Copy `frontend/.env.example` if you need a new env file. Do not put secrets in git.

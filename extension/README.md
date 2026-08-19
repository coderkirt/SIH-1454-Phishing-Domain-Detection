# PHISHEYE browser extension

PHISHEYE is the real-time browser protection layer for this project.

It does **not** detect phishing by itself.

It sends the current website URL to the same FastAPI backend used by the React dashboard:

`POST /api/v1/threat/check-url`

Same URL → same backend → same risk score, risk level, and reasons.

## What it does

- Intercepts link clicks and other navigations so the destination does not open first
- Shows the PHISHEYE gate and scans the URL with the FastAPI backend
- Opens LOW / clear sites automatically. MEDIUM needs Open anyway. HIGH and CRITICAL stay closed
- Skips browser pages such as `chrome://` and `edge://`
- Shows the real result in the popup and on the gate
- Updates the toolbar badge: OK, MED, HIGH, CRIT
- Saves scans through the backend, so they appear in dashboard history
- Lets you log in with the existing PHISHEYE account

## Folder

```
extension/
  manifest.json
  popup/
  background/service-worker.js
  content/content.js
  settings/
  welcome/
  assets/
  utils/config.js
  utils/api.js
```

## Configure the backend URL

Default development URL:

`http://127.0.0.1:8000`

Change it in either place:

1. Extension Settings page → Backend URL
2. `extension/utils/config.js` → `DEFAULT_API_BASE_URL`

The dashboard URL default is `http://127.0.0.1:5173`.

## Start the backend

```powershell
cd "$env:USERPROFILE\cybersecurity-platform\backend"
.\venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Start the frontend / dashboard

```powershell
cd "$env:USERPROFILE\cybersecurity-platform\frontend"
npm run dev
```

Then open http://127.0.0.1:5173

## Install in Chrome, Edge, or Brave

1. Open Chrome
2. Go to `chrome://extensions`
3. Turn on **Developer mode**
4. Click **Load unpacked**
5. Select this `extension` folder
6. Pin PHISHEYE
7. Make sure the backend is running
8. Reload the unpacked extension after code changes (this build is **1.7.0**)
9. Type a website or click a link — you should see the PHISHEYE gate, not the live site
10. A clear site opens by itself. A fishy or dangerous site stays on the gate

For Edge use `edge://extensions`. For Brave use `brave://extensions`.

## How to test

Use the same URL in the web scanner and in the extension. The score and level must match.

Try:

- `https://www.google.com` — usually LOW / SAFE
- `https://paypa1.com` — phishing-style name
- `https://sbi-login.xyz` — fake brand style
- `http://192.168.1.1/login` — IP-based URL
- A very long suspicious URL
- `chrome://extensions` — should say unsupported, not SAFE
- Stop the backend — popup must say **Protection service unavailable**, never SAFE

## Package it

In `chrome://extensions`, click **Pack extension** and choose this folder.

Or zip the `extension` folder and keep `manifest.json` at the zip root.

## Privacy

This version sends the URL needed for threat analysis to your PHISHEYE backend.

It does not collect passwords, OTPs, or card numbers.

Planned, not implemented: zero-knowledge proofs, encrypted local database, federated learning.

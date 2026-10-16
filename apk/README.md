# apk

Android wrapper for the PhishEye dashboard. This folder is the APK project, next to `frontend/` and `backend/`.

The Python API is **not** inside the APK. The phone opens the packaged site and calls the FastAPI server on your PC.

```text
phone  →  PhishEye.apk (the React pages)
               ↓  http://<your-pc-ip>:8000
PC     →  backend (FastAPI)
```

## What you get

After a successful build this folder contains `PhishEye.apk`. Copy that file to the phone and install it (allow install from this source).

## Build

On the PC, from this folder:

```powershell
.\build.ps1
```

That script:

1. Finds this PC’s Wi-Fi address
2. Builds `frontend/` so scans call `http://<that-address>:8000`
3. Copies the site into `www/`
4. Syncs Capacitor
5. Writes `PhishEye.apk`

If the address is wrong, set it yourself:

```powershell
$env:PHISHEYE_API_URL = "http://192.168.1.10:8000"
.\build.ps1
```

First build needs Node.js, Java 21 (or 17), and the Android SDK (Android Studio is the usual install).

## Run the API for the phone

The phone cannot use `127.0.0.1`. From this folder:

```powershell
.\run-backend.ps1
```

That starts the existing backend on `0.0.0.0:8000`. Keep the PC awake and on the same Wi-Fi as the phone.

In the app, **Settings → API on this PC** can change the address without rebuilding if the PC gets a new IP.

## Checking a link without pasting

1. Open PhishEye → **Set PhishEye as default browser**.
2. Open PhishEye → **Turn on Chrome / in-app link guard** → enable PhishEye.
3. Keep `run-backend.ps1` running on the PC.

Taps in WhatsApp, SMS, and mail open the PhishEye browser, which scans first. The guard watches Chrome’s address bar and stops a dangerous page.

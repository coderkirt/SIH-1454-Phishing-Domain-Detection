# Deploy PHISHEYE on Render

| Piece | How it is hosted |
|---|---|
| FastAPI | Render **web service** `phisheye-api` |
| React dashboard | Render **static site** `phisheye-web` |
| Chrome extension | **Zip on the dashboard** (`/extension` and `/phisheye-extension.zip`). Chrome cannot run MV3 from a website. The zip already points at the live API. |

Free web services **sleep after ~15 minutes**. Wake `/health` before the jury sits. SQLite on free Render **resets on deploy** unless you add a paid disk.

## After deploy

1. Open `https://<web>/health` is wrong — health is on the **API**: `https://<api>/health` and `/docs`.
2. Open the static site → **Extension** (or `/extension`) → **Download PHISHEYE extension**.
3. Unzip → Chrome `chrome://extensions` → Developer mode → **Load unpacked**.
4. Visit `github.com` (gate, then auto-open if LOW). Do not open a live phishing kit.

## Blueprint

1. `render.yaml` must be on GitHub branch `phisheye-update`.
2. [dashboard.render.com](https://dashboard.render.com) → **New +** → **Blueprint** → this repo → Apply.
3. Wait for **phisheye-api** Live, then **phisheye-web** (it bakes `VITE_API_URL` into the dashboard **and** the extension zip).

## Manual

**API:** root `backend`, Python 3.12, `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`, health `/health`. Env: `SECRET_KEY`, `ENABLE_ONLINE_CHECKS=true`, `FRONTEND_ORIGINS=*`.

**Web:** root `frontend`, `npm ci && npm run build`, publish `dist`, env `VITE_API_URL=https://<api-host>`. Rewrite `/*` → `/index.html` (keep the zip file as a real file).

## Honesty

Hosted prototype, not NTRO production. Not live PostgreSQL. Extension is Load unpacked, not Chrome Web Store.

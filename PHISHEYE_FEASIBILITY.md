# PHISHEYE feasibility

Prototype: **technically feasible today**. Production at “millions of URLs” is **proposed**, not how Render free SQLite runs.

---

## 1. Technical feasibility — IMPLEMENTED

The stack already implements the loop a jury can demo:

scan input → FastAPI → heuristics + feeds + psychology → score → Simple View → SQLite → (optional) Chrome gate.

Python + FastAPI fits URL/text/image-byte processing and existing tests. Chrome MV3 is the real place to intercept navigation. SQLite is enough for a hackathon prototype.

**Not required for the demo:** a trained CNN, Postgres, Kubernetes.

---

## 2. Operational feasibility — IMPLEMENTED

| User | How they use it |
|---|---|
| Public | Landing: paste/analyze, `/extension` zip |
| Operator | Sign up → `/scanner` tabs: URL, Message, Email, WhatsApp/SMS, Screenshot, QR |
| Browser user | Load unpacked MV3 → navigate → gate page |

Demo ops: wake `GET /health` (free Render sleeps ~15 min). Do not open live phishing kits.

---

## 3. Economic feasibility — QUALITATIVE ONLY

No invented rupee/dollar costs.

Cheap path already used: Render free/static + public intel feeds + optional GSB key.
Cost drivers **if scaled** (proposed): Safe Browsing quota, compute for QPS, managed Postgres, store listing. Do not quote prices.

---

## 4. Deployment feasibility

**Implemented:** `render.yaml` — Python web `phisheye-api` + static `phisheye-web`. Extension zip baked at frontend build. Load unpacked, not Web Store.

Live:

- https://phisheye-web-fhn5.onrender.com
- https://phisheye-api.onrender.com/health
- https://phisheye-web-fhn5.onrender.com/extension

**Limits (say them):** free API sleep; SQLite wipe on deploy without a disk; CORS often `*` on prototype.

**Proposed (label PROPOSED):** CDN frontend, multiple API workers, managed Postgres, secrets manager, custom domain HTTPS (Render already uses HTTPS on `*.onrender.com`), Chrome Web Store or enterprise force-install.

HTTPS on the **live Render URLs** is **IMPLEMENTED** (public https:// hosts). Local is http://127.0.0.1.

---

## 5. Scalability — DISTINGUISH CURRENT VS PROPOSED

| Idea | Current | Proposed |
|---|---|---|
| API | One Uvicorn worker typical on free Render | Stateless replicas behind a load balancer |
| DB | One SQLite file | Managed Postgres + indexes already sketched in SQL |
| Intel | In-process feed warmup | Shared cache (Redis) — **not implemented** |
| Scan cache | Extension 90s client cache | Server cache — **not implemented** |
| Queues / async fusion | Request-thread / sync analyze | Celery/queue — **not implemented** |
| ML GPU farm | None | Only if a real model is added |

**Bottlenecks (honest):** outbound intel HTTP latency; RDAP/TLS; 30s client timeout; SQLite write locks under concurrency; OpenCV on large images (5 MB cap).

**Millions of URLs/day:** **not current**. Would need the proposed column, not SQLite-on-free-Render.

---

## Jury answers (short)

**Why Python?** Fast to express URL/text rules, tests, feed parsers.

**Why FastAPI?** JSON APIs + `/docs` for demo.

**Why not Postgres today?** Prototype speed. Postgres is Future Scope.

**Why combine signals?** Blacklists miss new hosts; SSL is cheap; panic language is a separate signal; fusion + floors encode that.

**Why not SSL-only?** Valid certs on phish kits are common; Simple View even says padlock ≠ genuine.

**Why not blacklist-only?** Zero-day / lookalike before listing; miss ≠ SAFE.

**False positives:** psych cap 35; trusted destinations skip noisy heuristics; confirmed intel still wins.

**False negatives:** miss ≠ SAFE; LOW Simple View is not a guarantee; unavailable intel is stated.

**If intel down:** `unavailable` / `partial` explanations; extension treats API failure as **unavailable**, not safe.

**Retrain:** there is no model to retrain until curated labels exist.

**Production extras:** secrets, CORS lockdown, Postgres + disk, rate limits at edge, store distribution, retention jobs (planned).

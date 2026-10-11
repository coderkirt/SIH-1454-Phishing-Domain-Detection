# PhishEye RAG engine

Small FastAPI service that scores **facts PhishEye already collected**. It never fetches the destination page and never invents 30-day visit or report counts.

```
uvicorn app.main:app --port 8091
```

`GET /health` reports that the process is up.

`POST /assess-link` returns a suspicion-only assessment (`status=ok`) or the caller treats timeouts as unavailable. A missing score must be omitted, not treated as 0.

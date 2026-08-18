# Security model

This product analyzes attacker-controlled URLs.

## Implemented
- SSRF guard before short-link expansion: localhost, private IPs, link-local, cloud metadata (`169.254.169.254`)
- Hop-by-hop redirects (do not follow a redirect into a blocked host)
- Timeouts on outbound HTTP
- URL / scheme validation (http/https only for fetches)
- SQL via parameterized queries
- JWT auth on reports, feedback, delete
- Report rate limits and duplicate blocking
- Upload size limit 5 MB
- FastAPI XSS-safe JSON responses
- Extension does not rewrite hrefs or read password fields

## Keep in mind
- CORS is currently open (`*`) for local development — tighten for production
- SQLite is the live database; PostgreSQL remains planned
- Do not log raw messages or secrets

# Browser extension

Manifest V3. Same FastAPI backend as the dashboard.

## Implemented
- Scan the current tab URL
- Overlay warning on HIGH/CRITICAL (Go back / Continue anyway)
- **Analyze all visible links** (up to 15 http(s) links)
- Outline risky links without changing `href`
- Works on normal sites, Gmail Web, Outlook Web, WhatsApp Web **only for visible links** the page already rendered

## Not implemented / not possible here
- Reading phone SMS
- Native WhatsApp or Gmail inbox APIs
- Collecting passwords, OTPs, cookies, or tokens
- Rewriting original messages

Reload the page after installing so the content script is injected.

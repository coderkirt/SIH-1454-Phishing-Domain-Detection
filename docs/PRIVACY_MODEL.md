# Privacy model

Minimum necessary data.

## Never collected
Passwords, OTPs, PINs, card numbers, cookies, session tokens, authentication headers.

## Stored
- Account username, email, password hash
- URL scan results (score, level, reasons)
- Content-scan **metadata** (source type, scores, extracted URLs) — not the raw message
- Community reports you explicitly submit

## Uploads
QR/screenshot bytes are processed in memory and not saved.

## User controls
- Delete analysis (one scan)
- Delete analysis history (all content scans for the signed-in user)
- Export report without private message text

## Retention
Automatic delete-after-X-days is planned. Until then, use Delete history.

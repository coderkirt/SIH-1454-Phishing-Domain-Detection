# Implementation status — PhishShield AI 2.0 / CyberGuard

Status values: IMPLEMENTED | PARTIALLY IMPLEMENTED | PLANNED | BLOCKED

## IMPLEMENTED
- URL phishing detection (existing `POST /api/v1/threat/check-url`)
- Short-link unwrapping with SSRF blocking (localhost, private IPs, cloud metadata)
- Domain existence and domain age
- Psychological Threat Detection 2.0
- Multi-URL extraction (text, HTML href, shorteners)
- Unified `POST /api/v1/analyze/content` (email, whatsapp, sms, text, url, webpage, qr, screenshot)
- Email / WhatsApp / SMS as **pasted text sources** (not inbox or phone access)
- Sender analysis when the caller provides From / Reply-To
- Brand impersonation (brand mention + bad domain + extra signals)
- Risk engine with documented weights; scam risk; model confidence (not accuracy)
- Simple + Technical view
- Mark as Scam / Risky / Safe (authenticated, rate-limited)
- Community reputation (not treated as proof)
- Detection feedback (helpful yes/no)
- QR decode from uploaded images (OpenCV)
- Link intelligence panel
- Safe Open warning (does not rewrite original messages)
- Export report (no raw message / secrets)
- Delete analysis and delete content-scan history
- Dashboard source distribution + threat timeline
- Community reports page
- Browser extension: current-tab scan + Analyze All visible links (no href rewrite)
- Auth, history, statistics

## PARTIALLY IMPLEMENTED
- Screenshot OCR: works only if Tesseract is installed; otherwise paste the text or use QR
- Safe Browsing: Google key if present, else OpenPhish / local database
- PostgreSQL: **not used**. SQLite is the live database and was extended. Postgres remains planned.
- Gmail / Outlook / WhatsApp Web: visible links only via the extension; no inbox OAuth
- Localization: English UI; Hindi/Hinglish phrase matching in psychology, not a full translation layer
- Attachment safety: filename/extension only

## PLANNED
- Native Android SMS companion (`MobileMessageSource`, not implemented)
- Native mobile WhatsApp
- Official Gmail/Outlook OAuth inbox reading
- Deep attachment scanning (PDF/EXE/APK) without opening files
- Campaign clustering
- Training production ML on user reports (must be curated first)
- Automatic retention deletion after X days
- Calibrated fraud probability

## BLOCKED
- Reading private WhatsApp/Gmail without the user pasting content or granting an official API
- Chrome extension reading phone SMS
- Claiming calibrated fraud probability without a labelled, calibrated model

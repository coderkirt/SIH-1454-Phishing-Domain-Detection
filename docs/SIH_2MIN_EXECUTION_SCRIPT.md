# PHISHEYE — 2-minute execution script (SIH)

**Use:** internal / SIH “how does it actually run?”  
**Length:** ~2:00 · **~280 words** · one speaker  
**Pace:** slow enough to point at the screen. Do not rush the last 20 seconds.

Demo optional: while you speak, show Swagger `/docs` or one Scan Result. If Wi-Fi is bad, speak only.

---

## Spoken script (memorize / read)

**0:00 – 0:20 · Entry**

When a user pastes a URL, or the Chrome extension holds a tab, the client does not decide if the site is safe. It sends one HTTP POST to our FastAPI engine on port 8000. The React dashboard and the extension share the same brain: `check-url` for a single address, or `analyze/content` if the input is a message or a QR.

**0:20 – 0:50 · Normalize, expand, protect**

First we normalize: add https if missing, drop fragments, keep the path, store the query separately, and turn `www.google.com` into the registered domain `google.com`. If it is a short link like bit.ly, we unwrap the redirect chain — but only after an SSRF guard. We will not fetch localhost, private IPs, or cloud metadata. We also do not visit the phishing page just to ask a threat feed.

**0:50 – 1:20 · Intelligence then heuristics**

We query public feeds: OpenPhish, URLhaus, PhishTank, Phishing Army, and Google Safe Browsing if a key is present. A miss is not safe. A timeout is unavailable, not safe. If a feed confirms the URL, that score is floored — heuristics cannot talk it down. In parallel we score lookalikes: paypa1, Levenshtein to SBI or PayPal, free hosts with login in the name, young domains from RDAP, and TLS facts. Psychology is English and Hinglish phrases, not a neural net, and it cannot go CRITICAL alone.

**1:20 – 1:45 · Fuse, explain, store**

Those signals fuse to a score from 0 to 100: LOW, MEDIUM, HIGH, or CRITICAL. The user sees Simple View — do not enter OTP — and Technical View with evidence. We write a row to SQLite. The extension then acts: LOW opens, MEDIUM asks, HIGH and CRITICAL stay closed.

**1:45 – 2:00 · Close**

So execution is one pipeline: input, normalize, analyze, fuse, explain, act. FastAPI, not Flask. SQLite today, not live Postgres. Explainable rules and feeds today, not a trained CNN. That is how PHISHEYE runs, end to end.

---

## If they cut you at 90 seconds

Skip TLS/RDAP. Keep: same engine → normalize → feeds cannot be vetoed → lookalikes → Simple View → extension gate.

## Do not say

Flask · live PostgreSQL · Redis gateway · 99% accuracy · we read WhatsApp/SMS · padlock means genuine SBI · CNN is trained in this repo.

# Content analysis

All channels enter `POST /api/v1/analyze/content`.

```
{ "source_type": "email|whatsapp|sms|text|url|webpage|screenshot|qr", "text": "...", "urls": [], "sender": {}, "language": "en" }
```

`ContentNormalizer` extracts URLs, domains, language, and optional sender metadata. Raw text is **not stored**.

Then:

1. `extract_urls()` — http/https, www, HTML href, known shorteners
2. `URLChecker` on each link (existing phishing engine)
3. `analyze_message()` psychological tags
4. Brand + sender checks
5. Community reputation
6. `RiskEngine.fuse()`

`message_risk_score` is the psychological score for the whole message, even if every URL looks ordinary.

## What is not claimed
- Native phone SMS
- Silent Gmail/WhatsApp inbox access
- Calibrated fraud probability

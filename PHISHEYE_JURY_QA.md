# PHISHEYE jury Q&A (40+)

Answers match **code**. If we do not have it, the answer says so.

---

## Product / problem

**1. What is phishing?**  
A fake site or message that impersonates a trusted party to steal credentials, OTP, UPI, or card data.

**2. What is spear phishing?**  
Targeted phishing. We do not claim a separate spear-phishing classifier. Same engine scores the URL/text you give it.

**3. What is social engineering?**  
Manipulating trust (fear, urgency, authority). Implemented as **phrase rules** in `psychology.py`, not a neural net.

**4. What is typosquatting / domain impersonation?**  
Lookalike hosts (`paypa1`, `sbi-login.xyz`). `brand_detector` + URL heuristics.

**5. Why can a valid SSL cert belong to a phish?**  
Certificates are cheap. Padlock ≠ official SBI. Simple View can say a padlock is not proof.

**6. What is zero-day phishing?**  
A kit not yet in feeds. Miss ≠ SAFE. Heuristics + psych + lookalike still run. We do **not** claim we catch all zero-days.

**7. Why are blacklists insufficient?**  
Listing lags. `decision_engine` treats no-match as not a clean bill of health.

**8. Does PhishEye block websites?**  
**Yes, in the extension gate:** HIGH/CRITICAL (and unavailable) stay closed. LOW auto-opens. MEDIUM requires continue. This is **not** a network firewall or Chrome Web Store product.

**9. Detection vs prevention?**  
Dashboard: detection + explanation. Extension: prevention of **navigation** until scan/decision.

**10. Who is it for?**  
Non-technical OTP/UPI targets + operators on the React console. We do not claim enterprise SOC users in production.

---

## Architecture / stack

**11. Why FastAPI not Flask?**  
The running app **is FastAPI**. Flask is not in this backend.

**12. Why not live PostgreSQL?**  
Live path is **sqlite3** `threats.db`. Postgres is Future Scope. SQLAlchemy models are unused.

**13. Why Python?**  
URL/text/image-byte tooling and pytest already in-repo.

**14. How do clients talk to the backend?**  
HTTPS/JSON (Render) or HTTP localhost. Axios on web; `fetch` in extension. JWT on mutating routes.

**15. What if the backend is down?**  
Extension: `unavailable` — **unknown is not safe**, destination stays closed. Dashboard: request error (do not say “SAFE”).

**16. Latency bottleneck?**  
Outbound intel, RDAP, TLS, 30s extension timeout. No published p95.

**17. Database bottleneck?**  
SQLite write locks; free Render disk ephemeral. Scale = proposed Postgres.

**18. Caching?**  
Extension cache **90 seconds**. No Redis. Proposed for production.

**19. Async/queues?**  
Scan is request-synchronous. Feed warmup is a background thread. No Celery.

**20. How would it support millions of URLs?**  
**Not current.** Proposed: stateless API replicas, managed DB, intel cache. Do not claim we do this now.

---

## AI / ML / NLP

**21. What is AI here?**  
Automated multi-signal scoring + explanation. Not a shipped trained net.

**22. What is ML here?**  
Code key `ml` **copies URL heuristic score**. No Random Forest/XGBoost/CNN in requirements.

**23. What is NLP here?**  
**Rule-based** English+Hinglish substrings. Not BERT.

**24. What is feature engineering?**  
URL lexical + DNS/age/TLS/brand/intel tags in `url_checker`.

**25. What is inference?**  
Synchronous function calls inside FastAPI on each POST.

**26. Training / validation / F1?**  
**Not product metrics.** pytest ≠ F1. Do not quote simulation scripts as official accuracy.

**27. Overfitting?**  
No trained model. Phrase lists can false-positive; **psych cap 35** if no strong technical/intel/brand/community signal.

**28. Class imbalance / drift?**  
N/A for a trained model. Feeds can go stale; statuses include unavailable/partial.

**29. How retrain?**  
You cannot retrain what is not trained. Future: curated reports → then a model.

**30. Why combine signals?**  
SSL-only and list-only miss lookalikes and panic lures. Floors stop heuristics from talking down a confirmed feed hit.

**31. Why not SSL-only?**  
Valid certs on fake pages.

**32. Why not ML-only?**  
There is no trained model; a low `ml` copy must not prove safety.

---

## Psychology / risk

**33. How does psychological detection work?**  
Lowercase substring match; add category points; tags/findings returned.

**34. Can attackers pad marketing language?**  
Yes they can try; cap 35 without strong other signals. They can also avoid known phrases — **limitation**, say it.

**35. Exact risk formula?**  
Content: weighted sum of 10 static weights (see AI/ML file). URL: max(heuristic, intel floor). Levels 0–29 / 30–49 / 50–69 / 70–100.

**36. Are weights learned?**  
**No. Static defaults** in `DEFAULT_WEIGHTS`. “Not proven-optimal” is in the source comment.

**37. What is confidence?**  
`min(95, 35+10×count(signals≥20))` — agreement, **not accuracy**.

**38. Simple vs Technical View?**  
`warnings.py` + UI. LOW Simple View **says it is not a guarantee**.

**39. False positive?**  
Benign urgent email language; mitigated by cap + trusted-host skip. Not zero.

**40. False negative?**  
New lookalike + no feed + no phrases. Miss ≠ SAFE; user still told to check the address bar on LOW.

---

## Security / privacy / extension

**41. Does it store submitted URLs?**  
Yes, scan metadata in SQLite. Raw message body is not the intended stored field (metadata + extracted URLs). QR bytes processed in memory, not saved (`PRIVACY_MODEL.md`).

**42. Passwords/OTPs?**  
Never collected. Extension does not read password fields.

**43. JWT / hashing?**  
bcrypt + JWT. Token in `localStorage` on the web client.

**44. SQL injection?**  
Parameterized `sqlite3` queries.

**45. SSRF?**  
Block localhost, private IPs, `169.254.169.254` before unwrap.

**46. CORS?**  
Often `*` on prototype — **not** enterprise lockdown. Recommended hardening.

**47. HTTPS?**  
Live Render URLs are `https://`. Local demo is http://127.0.0.1.

**48. Rate limits?**  
Reports are rate-limited. Not a full WAF.

**49. Chrome Web Store?**  
**No.** Load unpacked.

**50. Can attackers evade?**  
Yes: new phrases, fresh domains, user clicking Continue on MEDIUM. We do not claim unbreakable prevention.

**51. Hardware?**  
None.

**52. Blockchain?**  
Not implemented.

**53. Flask?**  
Not used.

**54. Team name / college?**  
**Needs verification** — not in repo.

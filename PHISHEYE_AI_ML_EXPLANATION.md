# PHISHEYE AI / ML / NLP explanation (jury)

**One sentence:** PhishEye’s “intelligence” today is **explainable multi-signal scoring**, not a trained classifier sitting in the repo.

If a judge hears “AI/ML” in the README, answer with this file.

---

## What exactly is AI in PhishEye?

**Implemented:** combining several automated analyses (heuristics, feeds, phrase rules) into a decision a user can read.

**Not implemented:** a learned model that was trained on a labelled phishing dataset and shipped as `.pkl` / `.pt` / `.h5`.

Calling the product “AI-powered” in a **marketing** sense is risky. Prefer: **explainable threat scoring** or **multi-signal intelligence**. If the slide says AI/ML, immediately show that `ml` is a **copy of the URL heuristic score**.

---

## What exactly is ML?

**Implemented as a name in code, not as training:**

- `decision_engine.py`: `ml_score` = lexical/heuristic URL score so a **low** “ML” number cannot be used as proof of safety.
- `content_analyzer.py`: fusion key `"ml": url_risk` — same copy.

**Not implemented:** Random Forest, XGBoost, SVM, neural net, transformer, training loop, validation split, class-imbalance handling, model drift pipeline.

**Future Scope:** supervised model **after** curated community reports (`FEATURE_ROADMAP.md` V2).

**Why no model yet (honest):** no labelled production dataset in-repo; training without curation would overfit junk reports.

---

## What exactly is NLP?

**Implemented: rule-based NLP** (substring / phrase match on lowercased text).

`psychology.py` categories with **static points** (not learned):

| Tag | Points | Examples in code |
|---|---|---|
| urgency_detected | 12 | urgent, act now, jaldi karo, abhi click |
| fear_tactics | 12 | account blocked, band ho jayega |
| authority_impersonation | 12 | RBI, cyber cell, kyc department |
| coercion | 10 | mandatory kyc |
| financial_pressure | 10 | pay immediately |
| credential_pressure | 14 | enter otp, share otp, complete kyc |
| countdown | 8 | within 10 minutes |
| greed_bait | 10 | you won, lottery |
| secrecy | 8 | do not tell |
| emotional_manipulation | 10 | help me urgently |

**Not implemented:** tokenization pipeline, embeddings, BERT, sentiment neural net.

On **URL-only** scans, psychology is scaled (~×0.4, cap 40) so a scary hostname string cannot dominate.

---

## Feature engineering (URL) — implemented heuristics

From `url_checker.py` and helpers (mention only these):

- Normalization (scheme, registered domain, www)
- Shortener / redirect hops (after SSRF allow)
- IP-in-host / invalid host
- Suspicious TLD / free-host + login patterns
- Brand lookalike / leetspeak
- Domain DNS existence
- RDAP/WHOIS-style **age** (`new_domain` +20 if < 30 days)
- TLS facts (`ssl_certs.py`)
- Keyword / phishing fragments
- Optional page ad/clutter signals
- Threat-intel match type

**Potential / future:** entropy, hyphen counts, etc. — **do not list unless you verified them in code for this slide.** If unsure, omit.

---

## How signals become a score

### URL path (single `check-url`)

Heuristics accumulate a 0–100-style score, then **floors**:

```
if confirmed intel:
    score = max(heuristic, FLOOR)
FLOOR: exact_url 85, normalized_url 80, hostname 72, registered_domain 55
```

Weights here are **not** the fusion table. Intel **cannot be averaged away**.

### Content path (`analyze/content`)

```
raw = Σ  signal_i × weight_i
score = round(min(raw, 100))
if psych-only (psych ≥ 20 and no strong url/domain/intel/brand/community ≥ 40):
    score = min(score, 35)
confidence = min(95, 35 + 10 × count(signals ≥ 20))
```

**Static weights** (sum 1.0) in `DEFAULT_WEIGHTS` — **starting defaults, not proven-optimal, not learned:**

url 0.22, domain 0.16, ml 0.10, nlp 0.10, psychological 0.10,
threat_intel 0.10, brand 0.08, redirect 0.04, sender 0.05, community 0.05

`nlp` and `psychological` both receive the psychology score on this path.

Levels: LOW 0–29, MEDIUM 30–49, HIGH 50–69, CRITICAL 70–100.

---

## Training, validation, overfitting, drift

| Topic | Status |
|---|---|
| Training | **Not implemented** |
| Validation / test F1 | **Not implemented** as product metric |
| Overfitting | N/A for a trained model; rule lists can over-match marketing language — **mitigated by psych cap 35** |
| Class imbalance | N/A |
| Model drift | N/A; **feeds** can go stale — warmup + fail-soft statuses |
| Retrain | Future: curated reports → then a real model |
| New patterns | Add phrases in `psychology.py` or heuristic tags; add intel feeds |

pytest checks **behaviour** (`backend/tests/`), not academic ML quality.

Scripts `accuracy_simulation.py` / `phishtank_live_eval.py` are **not** official product accuracy. Do not quote them as F1.

---

## Inference

Synchronous HTTP: extension waits up to 30s. No separate ML microservice.

---

## Jury one-liners

- “Our ML key is a copy of URL risk so it cannot launder a bad site as safe.”
- “NLP is English+Hinglish phrase rules, not a language model.”
- “Content fusion uses documented static weights. URL decisions use intel floors.”
- “We do not have a published F1. We have pytest and a working demo.”

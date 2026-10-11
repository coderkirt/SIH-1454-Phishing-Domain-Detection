#!/usr/bin/env python3
"""Generate the PHISHEYE technical architecture PDF.

Output
    docs/phisheye_technical_architecture.pdf
    docs/phisheye_technical_architecture.html   (debug / fallback)

Renderers (first available wins)
    1. weasyprint
    2. playwright (Chromium)

Install either:
    pip install weasyprint
    pip install playwright && python -m playwright install chromium
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_PDF = HERE / "phisheye_technical_architecture.pdf"
DEFAULT_HTML = HERE / "phisheye_technical_architecture.html"


def html_document() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>PHISHEYE: End-to-End URL Scanning Engine &amp; Threat Detection Architecture</title>
<style>
{CSS}
</style>
</head>
<body>

<!-- ===================== COVER ===================== -->
<section class="cover">
  <div class="cover-bar"></div>
  <p class="eyebrow">SIH1454 · NTRO · Blockchain &amp; Cybersecurity · Software</p>
  <h1>PHISHEYE</h1>
  <p class="cover-sub">End-to-End URL Scanning Engine<br/>&amp; Threat Detection Architecture</p>
  <p class="cover-lede">A publication-grade reference for the FastAPI scanning core: ingestion, SSRF-safe expansion, public threat feeds, lookalike heuristics, psychological language analysis, OpenCV QR handoff, weighted fusion, and persistence.</p>
  <div class="cover-meta">
    <div><span>Product</span>PHISHEYE API v2.0.0</div>
    <div><span>Runtime</span>FastAPI · Uvicorn · Python 3</div>
    <div><span>Clients</span>React 19 / Vite · Chrome MV3</div>
    <div><span>Store</span>SQLite <em>threats.db</em></div>
  </div>
  <p class="cover-note">Shipped behaviour is labelled <strong>Live</strong>. Production extensions that are designed but not running in this repository are labelled <strong>Roadmap</strong>. This document does not invent a trained CNN, Redis cluster, or live PostgreSQL.</p>
</section>

<nav class="toc">
  <h2>Contents</h2>
  <ol>
    <li>Executive Architecture Overview &amp; Request Lifecycle</li>
    <li>Ingestion, Normalization &amp; Security Safeguards</li>
    <li>Domain &amp; Infrastructure Footprint Analysis</li>
    <li>Public Threat Intelligence Integrations</li>
    <li>Heuristic &amp; Behavioral Intelligence Engine</li>
    <li>Weighted Fusion Engine &amp; Decision Scoring</li>
    <li>Data Persistence &amp; Production Readiness</li>
  </ol>
</nav>

<!-- ===================== SECTION 1 ===================== -->
<section class="chapter">
  <p class="kicker">Section 01</p>
  <h2>Executive Architecture Overview &amp; Request Lifecycle</h2>

  <p class="lead">PHISHEYE is a <strong>modular monolith</strong>. One FastAPI process on port <code>8000</code> is the threat engine. The React dashboard (<code>127.0.0.1:5173</code>) and the Manifest V3 extension are presentation clients. They share <code>POST /api/v1/threat/check-url</code> and the multi-channel <code>POST /api/v1/analyze/*</code> family. There is no separate API gateway microservice in the current tree.</p>

  <div class="grid-2">
    <article class="card">
      <h3>Live control plane</h3>
      <ul>
        <li><strong>ASGI:</strong> Uvicorn serving <code>app.main:app</code>.</li>
        <li><strong>Validation:</strong> Pydantic v2 request bodies.</li>
        <li><strong>Auth:</strong> passlib bcrypt + python-jose JWT <code>HS256</code>. Claim <code>sub</code> = username. Signup/login issue a 7-day bearer token. URL checks may be anonymous.</li>
        <li><strong>CORS:</strong> <code>allow_origins=["*"]</code> — prototype, not production hardening.</li>
        <li><strong>Startup:</strong> <code>init_db()</code> then a daemon thread warms OpenPhish / URLhaus / PhishTank / Phishing Army unless <code>PHISHEYE_SKIP_FEED_WARMUP=1</code>.</li>
      </ul>
    </article>
    <article class="card">
      <h3>Pipeline slogan</h3>
      <div class="pills">
        <span class="chip">INPUT</span>
        <span class="arrow">→</span>
        <span class="chip">NORMALIZE</span>
        <span class="arrow">→</span>
        <span class="chip">ANALYZE</span>
        <span class="arrow">→</span>
        <span class="chip">FUSE</span>
        <span class="arrow">→</span>
        <span class="chip">EXPLAIN</span>
        <span class="arrow">→</span>
        <span class="chip">ACT</span>
      </div>
      <p>Simple View (plain English) and Technical View (evidence, providers, tags) are built in <code>warnings.py</code>. The extension <em>gates</em> navigation so a destination is scored before it is used as the primary surface.</p>
    </article>
  </div>

  <h3>Authentication (JWT HS256)</h3>
  <p>Routes under <code>/api/v1/user</code> hash passwords with bcrypt. Protected actions (community report, scan delete, profile) require <code>Authorization: Bearer &lt;jwt&gt;</code>. Analyze routes accept an <em>optional</em> bearer so a logged-in user is attached to <code>content_scans.user_id</code>. Default <code>SECRET_KEY</code> is a development fallback and must be rotated for any shared deployment.</p>

  <h3>Rate limiting — live vs roadmap</h3>
  <div class="callout">
    <p><span class="tag tag-live">Live</span> Community reports: one URL per user per 24 hours, 20 reports per day (<code>reputation.add_report</code>). Upload bodies capped at 5&nbsp;MB. Intel HTTP calls use short timeouts (3–8s).</p>
    <p><span class="tag tag-road">Roadmap</span> A dedicated gateway with Redis (or in-process token bucket) in front of <code>/check-url</code> and <code>/analyze/*</code> is <strong>not implemented</strong>. There is no global FastAPI rate-limit middleware and no Redis dependency in <code>requirements.txt</code>. The sequence diagram below shows the live path in solid ink and the limiter as a dashed production insert.</p>
  </div>

  <figure class="figure">
    <figcaption>Figure 1 — Request lifecycle (live path solid; rate limiter dashed / roadmap)</figcaption>
    {SEQUENCE_SVG}
  </figure>

  <h3>Primary JSON contract</h3>
  <pre><code>POST /api/v1/threat/check-url
{{
  "url": "https://sbi-login.xyz/verify",
  "view": "both",
  "page_signals": {{ "buttons": 0, "iframes": 0, "popups": 0, "overlays": 0, "links": 0 }}
}}

→ risk_score, risk_level, classification, safe,
  simple_view, technical_view, evidence, debug, threat_tags</code></pre>
</section>

<!-- ===================== SECTION 2 ===================== -->
<section class="chapter">
  <p class="kicker">Section 02</p>
  <h2>Ingestion, Normalization &amp; Security Safeguards</h2>

  <h3>Scan logic gateway</h3>
  <p>Ingestion is not a separate process. FastAPI routers are the gateway:</p>
  <table>
    <thead><tr><th>Input</th><th>Route</th><th>Normalizer</th></tr></thead>
    <tbody>
      <tr><td>Plain URL</td><td><code>POST /api/v1/threat/check-url</code></td><td>Scheme prepend <code>https://</code> if missing → <code>URLChecker.analyze</code></td></tr>
      <tr><td>Pasted text / SMS / WhatsApp / email</td><td><code>POST /api/v1/analyze/content</code></td><td><code>content_normalizer</code> + <code>url_extractor</code> (multi-link batch from one body)</td></tr>
      <tr><td>QR image</td><td><code>POST /api/v1/analyze/qr</code></td><td>OpenCV decode → URL strings → same content pipeline</td></tr>
      <tr><td>Screenshot</td><td><code>POST /api/v1/analyze/screenshot</code></td><td>QR always; OCR only if Tesseract is installed; optional hint URL</td></tr>
      <tr><td>Browser tab / gated navigation</td><td>Extension → same <code>check-url</code></td><td>Identical engine, different client</td></tr>
    </tbody>
  </table>
  <p>A “batch” in the live product is <strong>N URLs extracted from one message</strong>, each passed through <code>URLChecker</code>, not a bulk CSV job API.</p>

  <h3>URL normalization &amp; expansion</h3>
  <p><code>url_normalize.normalize_url</code> never fetches. It:</p>
  <ul>
    <li>Accepts bare hosts and forces <code>http</code>/<code>https</code> only.</li>
    <li>Strips userinfo (<code>user:pass@host</code>), default ports 80/443, and <code>#fragments</code>.</li>
    <li>Keeps path (so <code>/login</code> ≠ <code>/</code>) and stores query separately (so <code>google.com/?q=phish</code> is not the homepage).</li>
    <li>Computes hostname and registrable domain, including multi-part TLDs such as <code>sbi.co.in</code>.</li>
    <li>IDNA-encodes the host (<code>host.encode("idna")</code>) so punycode/Unicode labels become a stable ASCII key.</li>
  </ul>
  <p><code>redirects.expand_url</code> unwraps known shorteners (<code>bit.ly</code>, <code>t.co</code>, <code>tinyurl.com</code>, <code>cutt.ly</code>, …) hop-by-hop (max 8), HEAD then GET-on-405, after SSRF checks. Scoring: +12 if expanded, +20 if the destination stays hidden, +10 if hops &gt; 2. The <em>final</em> URL is what intel and heuristics see.</p>

  <h3>SSRF mitigation guards</h3>
  <p><code>ssrf.assert_public_http_url</code> runs before any outbound fetch of an attacker-controlled URL (shortener unwrap, optional ad/clutter fetch). Threat-intel matching <strong>does not fetch the submitted phishing page</strong>.</p>
  <div class="grid-2">
    <article class="card tight">
      <h3>Blocked hosts</h3>
      <ul>
        <li><code>localhost</code>, <code>*.localhost</code>, <code>*.local</code></li>
        <li><code>metadata.google.internal</code>, <code>metadata</code>, <code>instance-data</code></li>
        <li><code>0.0.0.0</code></li>
      </ul>
    </article>
    <article class="card tight">
      <h3>Blocked addresses</h3>
      <ul>
        <li>Loopback <code>127.0.0.0/8</code></li>
        <li>RFC1918 <code>10.0.0.0/8</code>, <code>172.16.0.0/12</code>, <code>192.168.0.0/16</code></li>
        <li>Link-local, multicast, reserved, unspecified</li>
        <li>Cloud metadata <code>169.254.169.254</code>, <code>fd00:ec2::254</code></li>
      </ul>
    </article>
  </div>
  <p>Implementation uses <code>ipaddress</code> predicates plus <code>socket.getaddrinfo</code> so a public-looking hostname that resolves to a private IP is also rejected (<code>UnsafeURLError</code>).</p>
</section>

<!-- ===================== SECTION 3 ===================== -->
<section class="chapter">
  <p class="kicker">Section 03</p>
  <h2>Domain &amp; Infrastructure Footprint Analysis</h2>

  <h3>DNS resolution &amp; record validation</h3>
  <p><span class="tag tag-live">Live</span> <code>external_intel.check_domain_exists</code> performs <code>socket.getaddrinfo(host)</code> (3s timeout). That covers A/AAAA reachability as “does this name resolve?” NXDOMAIN → tag <code>domain_not_found</code>, heuristic +35, and <code>safe</code> cannot be true.</p>
  <p><span class="tag tag-road">Roadmap</span> Explicit MX / TXT collection for SPF, DKIM, and DMARC on the <em>sending</em> domain is not a current URLChecker stage. Those records matter for email authentication; the live email path only scores caller-supplied From / Reply-To against brand domain lists in <code>sender_analyzer.py</code>.</p>

  <h3>Domain age &amp; registrar verification</h3>
  <p><span class="tag tag-live">Live</span> Age comes from public <strong>RDAP</strong> (<code>rdap.org/domain/{{name}}</code>, plus Verisign RDAP for <code>.com</code>/<code>.net</code>), not a paid WHOIS parser. Registration event dates yield <code>domain_age_days</code>. Scoring: &lt; 30 days +20 (NRD), &lt; 90 days +10. Cache is in-process.</p>
  <p><span class="tag tag-road">Roadmap</span> Full registrar, nameserver, and privacy-proxy WHOIS fields; automated takedown ticketing.</p>

  <h3>TLS / SSL inspection</h3>
  <p><code>ssl_certs.inspect_tls</code> is SSRF-gated, 5s timeout. A padlock is recorded, never treated as “this is SBI.”</p>
  <table>
    <thead><tr><th>Check</th><th>Live behaviour</th><th>Risk points (cap 40)</th></tr></thead>
    <tbody>
      <tr><td>HTTP URL</td><td>Status <code>http</code>, tag <code>no_https</code>; URLChecker also +5 for missing https</td><td>scheme extra in checker</td></tr>
      <tr><td>Trusted chain + hostname</td><td>Default SSL context + SNI <code>server_hostname=host</code></td><td>0</td></tr>
      <tr><td>Hostname / SNI mismatch</td><td>Status <code>hostname_mismatch</code></td><td>+30</td></tr>
      <tr><td>Self-signed / untrusted issuer</td><td>Issuer vs subject heuristics + verify error</td><td>+20 / +18</td></tr>
      <tr><td>Expired cert</td><td>Parsed <code>notAfter</code></td><td>+25</td></tr>
      <tr><td>Expires ≤ 7 days</td><td>Warning finding</td><td>+8</td></tr>
    </tbody>
  </table>
  <p><span class="tag tag-road">Roadmap</span> Dedicated wildcard-abuse policy (e.g. <code>*.tk</code> issued to a lookalike) as its own detector. Today wildcard names appear in SAN lists but are not a separate scoring rule.</p>
</section>

<!-- ===================== SECTION 4 ===================== -->
<section class="chapter">
  <p class="kicker">Section 04</p>
  <h2>Public Threat Intelligence Integrations</h2>

  <p>Module <code>threat_intel.py</code> + cache <code>feed_cache.py</code>. Feeds persist under <code>backend/data/feeds/</code> (TTL 30 minutes, academic User-Agent). Providers are <strong>independent</strong>: a miss is <code>no_match</code>, a timeout is <code>unavailable</code>. Neither is rewritten to SAFE. Confirmed hits cannot be averaged away by heuristics (<code>decision_engine.py</code>).</p>

  <table class="intel">
    <thead>
      <tr>
        <th>Feed</th>
        <th>How it is queried</th>
        <th>What a hit means</th>
        <th>Weighting in the live engine</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Google Safe Browsing v4</strong></td>
        <td>Optional <code>GOOGLE_SAFE_BROWSING_API_KEY</code>. POST <code>safebrowsing.googleapis.com/v4/threatMatches:find</code> with types SOCIAL_ENGINEERING, MALWARE, UNWANTED_SOFTWARE, POTENTIALLY_HARMFUL_APPLICATION. v5 is not wired.</td>
        <td>API match → <code>confirmed_malicious</code>. Missing key → provider skipped, not a fake clean.</td>
        <td>Feeds into intel overall status. Decision floors 55–85 by match type (see §6). Fusion channel <code>threat_intel</code> weight <strong>0.10</strong> on the content path; URL path uses floors, not that weight alone.</td>
      </tr>
      <tr>
        <td><strong>PhishTank</strong></td>
        <td>Public CSV dump <code>online-valid.csv</code>. Without <code>PHISHTANK_API_KEY</code> only <strong>verified</strong> rows are used. Key enables live lookup of unverified reports.</td>
        <td>Verified listing → confirmed. Unverified → <code>reported_malicious</code> (floor 58), not a court proof.</td>
        <td>Same intel contract. Path/query-aware matching so one dump row cannot burn all of YouTube or Google.</td>
      </tr>
      <tr>
        <td><strong>URLhaus (abuse.ch)</strong></td>
        <td>Public online text feed + optional <code>URLHAUS_AUTH_KEY</code> for API. Cached locally.</td>
        <td>URL listed as malware/botnet payload host → confirmed.</td>
        <td>Independent provider row in <code>evidence.threat_intelligence.providers</code>.</td>
      </tr>
      <tr>
        <td><strong>OpenPhish</strong></td>
        <td><code>https://openphish.com/feed.txt</code> pulled on warmup / TTL. Indexed by raw, normalized URL, and host.</td>
        <td>Exact / normalized / (restricted) path match → confirmed phishing telemetry.</td>
        <td>Trusted-domain generic paths (<code>/watch</code>, <code>/search</code>, <code>/</code>) require query overlap.</td>
      </tr>
      <tr>
        <td><strong>Phishing Army</strong></td>
        <td>Domain blocklist <code>phishing.army/download/phishing_army_blocklist.txt</code>.</td>
        <td>Hostname / registrable-domain listing.</td>
        <td><strong>Skipped on official trusted destinations</strong> (google.com, github.com, Indian banks, …) so a noisy domain list cannot mark the real brand. User-content hosts (<code>sites.google.com</code>, <code>github.io</code>) stay fully scanned.</td>
      </tr>
    </tbody>
  </table>

  <p class="small">Match types, strictest first: exact raw URL → normalized URL → path-related → hostname → registered_domain. Intel floor for exact_url is 85; registered_domain is 55.</p>
</section>

<!-- ===================== SECTION 5 ===================== -->
<section class="chapter">
  <p class="kicker">Section 05</p>
  <h2>Heuristic &amp; Behavioral Intelligence Engine</h2>

  <h3>Typosquatting &amp; homoglyph engine</h3>
  <p><span class="tag tag-live">Live</span> <code>URLChecker._detect_brand</code> compares the registrable <em>label</em> to a <strong>curated brand map</strong> (PayPal, Amazon, Google, YouTube, GitHub, Microsoft, Apple, Meta brands, Netflix, Flipkart, Paytm, PhonePe, SBI, HDFC, ICICI, Axis, IRCTC — not the Tranco top 10k). Pipeline:</p>
  <ol>
    <li>Skip if the domain already <em>is</em> the official brand host.</li>
    <li>Normalize leetspeak (<code>1→l</code>, <code>0→o</code>, <code>@→a</code>, …) and a limited Cyrillic→Latin homoglyph table.</li>
    <li>Substring brand hit <em>or</em> Levenshtein distance 0–2 with similar length → tag <code>brand_impersonation</code>, typically +40.</li>
  </ol>
  <p>Known fragments (<code>paypa1</code>, <code>amaz0n</code>, <code>go0gle</code>, <code>bank-login</code>) add +40 independently. Free-app hosts (<code>vercel.app</code>, <code>lovable.app</code>, <code>pages.dev</code>, <code>github.io</code>, …) plus login/otp/bank tokens add +22 to +34.</p>
  <p><span class="tag tag-road">Roadmap</span> Levenshtein / homograph screening against a top-10k domain list and a fuller IDN confusable table (Unicode TR39).</p>

  <h3>NLP &amp; psychological triggers</h3>
  <p>This is <strong>not</strong> a neural NLP model. <code>psychology.py</code> is deterministic phrase matching (English + Hinglish): urgency, fear, authority, coercion, financial pressure, OTP/credential harvest, countdown, greed/lottery, secrecy. Examples: <em>enter otp</em>, <em>account blocked</em>, <em>abhi click</em>, <em>jaldi karo</em>, <em>aadhaar otp</em>.</p>
  <p><code>brand_detector.detect_impersonation</code> requires brand mention <em>and</em> unofficial domain <em>and</em> an extra scam signal — a news sentence that says “SBI” is not enough.</p>
  <p><strong>False-positive guard:</strong> if psychology is the only strong channel, fused score is capped at <strong>35</strong> (stays LOW/MEDIUM). Marketing “act now” cannot solo-CRITICAL.</p>

  <h3>QR &amp; media extraction (OpenCV)</h3>
  <figure class="figure">
    <figcaption>Figure 2 — QR decode variants before URL handoff (destination is never fetched)</figcaption>
    {QR_SVG}
  </figure>
  <p><code>qr_analyzer.extract_qr_urls</code> runs OpenCV <code>QRCodeDetector</code> on colour, grayscale, invert, Gaussian blur, CLAHE, Otsu, morphological close, and adaptive Gaussian threshold variants, with optional upscale and a Pillow fallback. Payloads are parsed for <code>http(s)</code> or bare hosts (capped at 15 URLs) and handed to <code>analyze_content(source_type="qr")</code>. Images stay in memory (max 5&nbsp;MB).</p>
</section>

<!-- ===================== SECTION 6 ===================== -->
<section class="chapter">
  <p class="kicker">Section 06</p>
  <h2>Weighted Fusion Engine &amp; Decision Scoring</h2>

  <h3>Two cooperating layers</h3>
  <div class="grid-2">
    <article class="card">
      <h3>URL path — decision engine</h3>
      <p>Single-URL scans finalize in <code>calculate_final_risk</code>. Confirmed intel <em>floors</em> the score. Heuristics and the lexical “ml” copy cannot override a feed hit.</p>
    </article>
    <article class="card">
      <h3>Message path — weighted fuse</h3>
      <p><code>risk_engine.fuse</code> combines ten channels. If any child URL was confirmed malicious, the fused score is raised to at least that URL’s decision score.</p>
    </article>
  </div>

  <h3>Conceptual aggregation</h3>
  <p>Architecturally, independent evidence collapses to three families — intel, heuristics/behaviour, network/domain metadata:</p>
  <div class="formula">
    <span>RiskScore</span>
    <span class="op">=</span>
    <span>w<sub>intel</sub>·S<sub>intel</sub></span>
    <span class="op">+</span>
    <span>w<sub>heur</sub>·S<sub>heur</sub></span>
    <span class="op">+</span>
    <span>w<sub>net</sub>·S<sub>net</sub></span>
  </div>
  <p>The <strong>shipped</strong> content fusion is the ten-term expansion (weights sum to 1.0; starting defaults, not proven-optimal):</p>
  <div class="formula small-form">
    0.22&nbsp;url + 0.16&nbsp;domain + 0.10&nbsp;ml + 0.10&nbsp;nlp + 0.10&nbsp;psychological
    + 0.10&nbsp;threat_intel + 0.08&nbsp;brand + 0.05&nbsp;sender + 0.05&nbsp;community + 0.04&nbsp;redirect
  </div>
  <p>The channel named <code>ml</code> is a <strong>copy of the lexical/heuristic URL score</strong>. <code>backend/app/ml/</code> contains no pickle, no TensorFlow graph, and no sklearn classifier. It exists so a low “ML” number cannot be cited as proof of safety when intel has already confirmed malice.</p>
  <p><code>model_confidence = min(95, 35 + 10 × count(signals ≥ 20))</code> — agreement, not detection accuracy. <code>scam_risk</code> is the same 0–100 integer, not a calibrated fraud probability.</p>

  <h3>Intel floors (URL decision engine)</h3>
  <table>
    <thead><tr><th>Situation</th><th>Floor / rule</th><th>Classification</th></tr></thead>
    <tbody>
      <tr><td>Confirmed · exact URL</td><td>max(heuristic, 85)</td><td>CONFIRMED_MALICIOUS</td></tr>
      <tr><td>Confirmed · normalized URL</td><td>max(heuristic, 80)</td><td>CONFIRMED_MALICIOUS</td></tr>
      <tr><td>Confirmed · hostname</td><td>max(heuristic, 72)</td><td>CONFIRMED_MALICIOUS</td></tr>
      <tr><td>Confirmed · registered domain</td><td>max(heuristic, 55)</td><td>CONFIRMED_MALICIOUS</td></tr>
      <tr><td>Unverified report</td><td>max(heuristic, 58)</td><td>SUSPICIOUS</td></tr>
      <tr><td>Heuristic ≥ 50, no confirm</td><td>heuristic</td><td>SUSPICIOUS</td></tr>
      <tr><td>Unavailable or no_match + weak heuristics</td><td>heuristic</td><td>NO_MALICIOUS_EVIDENCE — text states this is not a clean bill of health</td></tr>
    </tbody>
  </table>

  <h3>Verdict categories — live engine</h3>
  <p>These cut-points are implemented in <code>decision_engine._level</code> and <code>risk_engine._level</code>. They are the numbers a jury will see on screen.</p>
  <div class="verdicts">
    <div class="pill-card low"><strong>LOW</strong><span>0 – 29</span><em>No strong malicious indicators. Trusted destinations often land here. Still not a cryptographic identity proof.</em></div>
    <div class="pill-card med"><strong>MEDIUM</strong><span>30 – 49</span><em>Fishy heuristics, young domain, unverified report, or mixed signals. Extension asks before opening.</em></div>
    <div class="pill-card high"><strong>HIGH</strong><span>50 – 69</span><em>Strong lookalike / free-host / heuristic cluster or reported intel. Do not enter OTP.</em></div>
    <div class="pill-card crit"><strong>CRITICAL</strong><span>70 – 100</span><em>Confirmed feed hit (floored) or stacked impersonation. Extension keeps the tab closed.</em></div>
  </div>
  <p class="small"><span class="tag tag-road">Roadmap</span> Alternate bandings (for example 0–19 / 20–49 / 50–79 / 80–100) are a product-calibration choice. Shipping two scales at once would contradict the UI. Recalibrate only with labelled evals, then change both Python helpers and this document together.</p>
</section>

<!-- ===================== SECTION 7 ===================== -->
<section class="chapter">
  <p class="kicker">Section 07</p>
  <h2>Data Persistence &amp; Production Readiness</h2>

  <h3>Current state</h3>
  <p>Live store is a single SQLite file <code>backend/threats.db</code> opened by <code>sqlite3.connect</code> with <code>PRAGMA foreign_keys=ON</code> and <code>Row</code> dict access. Path is anchored to the backend directory regardless of process cwd. All writes use parameterized <code>?</code> placeholders.</p>
  <p><code>sqlalchemy</code> is listed in <code>requirements.txt</code> and declarative models exist under <code>backend/app/models/</code> (<code>User</code>, etc.). <strong>Runtime routes do not use the ORM.</strong> Saying “we query through SQLAlchemy today” would be false.</p>

  <table>
    <thead><tr><th>Table</th><th>Purpose</th></tr></thead>
    <tbody>
      <tr><td><code>users</code></td><td>username, email, bcrypt hash</td></tr>
      <tr><td><code>url_checks</code></td><td>Every check-url row (anonymous user_id allowed)</td></tr>
      <tr><td><code>threats</code></td><td>HIGH/CRITICAL URL rows with heuristic type label</td></tr>
      <tr><td><code>content_scans</code></td><td>Multi-channel scans — raw message text is not stored</td></tr>
      <tr><td><code>extracted_links</code></td><td>Per-URL children of a content scan</td></tr>
      <tr><td><code>user_reports</code> / <code>domain_reputation</code></td><td>Community signal, not proof</td></tr>
      <tr><td><code>scan_feedback</code></td><td>Helpful yes/no for later review</td></tr>
    </tbody>
  </table>

  <h3>Planned target</h3>
  <p><span class="tag tag-road">Roadmap</span> PostgreSQL for concurrent writers, backups, and role separation. <code>DATABASE_URL</code> in <code>config.py</code> is unused by <code>connection.py</code> today. A later phase may add <strong>pgvector</strong> for embedding-similarity of URL/path tokens against curated phishing campaigns — that extension is not in the repository and must not be demoed as live.</p>
  <ul>
    <li>Lock down CORS to the dashboard origin.</li>
    <li>Rotate JWT secret; shorten token TTL; add refresh tokens.</li>
    <li>Global rate limit (Redis or slowapi) in front of scan endpoints.</li>
    <li>Trained supervised model only after curated labels — swap the <code>ml</code> channel without changing the API contract.</li>
    <li>Android SMS companion (<code>mobile_source.py</code> is a stub, <code>implemented = False</code>).</li>
  </ul>

  <h3>Security posture already in the tree</h3>
  <ul>
    <li>bcrypt, JWT, parameterized SQL, SSRF, 5&nbsp;MB upload cap, report quotas.</li>
    <li>Images not persisted; export report strips secrets.</li>
    <li>User can delete content-scan history.</li>
    <li>pytest with live feed downloads blocked (<code>PHISHEYE_SKIP_FEED_WARMUP</code>).</li>
  </ul>
</section>

<section class="appendix">
  <h2>Appendix — Engine file map</h2>
  <pre class="map"><code>backend/app/main.py                 FastAPI + CORS + feed warmup
backend/app/routes/threat_detection.py   check-url, check-message, intel-status
backend/app/routes/analyze.py            content / qr / screenshot
backend/app/services/url_normalize.py
backend/app/services/url_checker.py
backend/app/services/threat_intel.py
backend/app/services/feed_cache.py
backend/app/services/decision_engine.py
backend/app/services/risk_engine.py
backend/app/services/ssrf.py
backend/app/services/ssl_certs.py
backend/app/services/psychology.py
backend/app/services/qr_analyzer.py
backend/app/database/connection.py       sqlite3 live path</code></pre>
  <p class="end">Document generated from the PHISHEYE 2.0 codebase. Classification: internal / academic. Not an NTRO deployment certificate.</p>
</section>

</body>
</html>
"""


CSS = r"""
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap");

:root {
  --slate: #0f172a;
  --slate-2: #1e293b;
  --muted: #475569;
  --cyan: #0ea5e9;
  --teal: #0d9488;
  --card: #f8fafc;
  --border: #e2e8f0;
  --low: #22c55e;
  --med: #eab308;
  --high: #f97316;
  --crit: #ef4444;
}

* { box-sizing: border-box; }
html { font-size: 10.5pt; }
body {
  margin: 0;
  color: var(--slate);
  font-family: Inter, "Helvetica Neue", Helvetica, Roboto, Arial, sans-serif;
  line-height: 1.55;
  background: #fff;
}

@page {
  size: A4;
  margin: 16mm 14mm 18mm 14mm;
  @top-left {
    content: "PHISHEYE  ·  URL Scanning Engine";
    font-family: Inter, Helvetica, sans-serif;
    font-size: 8pt;
    color: #64748b;
    letter-spacing: 0.04em;
  }
  @top-right {
    content: "Technical Architecture";
    font-family: Inter, Helvetica, sans-serif;
    font-size: 8pt;
    color: #64748b;
  }
  @bottom-left {
    content: "SIH1454  ·  NTRO  ·  FastAPI core";
    font-size: 8pt;
    color: #94a3b8;
  }
  @bottom-right {
    content: "Page " counter(page);
    font-size: 8pt;
    color: #64748b;
    font-weight: 600;
  }
}

@page :first {
  margin-top: 12mm;
  @top-left { content: none; }
  @top-right { content: none; }
}

h1, h2, h3 { font-weight: 700; color: var(--slate); break-after: avoid; }
h1 { font-size: 28pt; letter-spacing: -0.03em; line-height: 1.05; margin: 0 0 10px; }
h2 { font-size: 16pt; letter-spacing: -0.02em; margin: 0 0 10px; padding-bottom: 6px; border-bottom: 2px solid var(--cyan); }
h3 { font-size: 11.5pt; margin: 16px 0 6px; color: var(--slate-2); }
p { margin: 0 0 8px; }
.lead { font-size: 11pt; color: var(--slate-2); }
.small, .cover-note { font-size: 8.5pt; color: var(--muted); }
ul, ol { margin: 0 0 10px; padding-left: 1.15em; }
li { margin-bottom: 3px; }
code, pre, .map {
  font-family: "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
  font-size: 8pt;
}
code { background: #f1f5f9; padding: 0.1em 0.35em; border-radius: 3px; }
pre {
  background: var(--card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--teal);
  padding: 10px 12px;
  border-radius: 6px;
  white-space: pre-wrap;
  break-inside: avoid;
}

.cover {
  min-height: 240mm;
  padding: 18mm 8mm 12mm;
  page-break-after: always;
  position: relative;
}
.cover-bar {
  width: 72px; height: 6px; background: linear-gradient(90deg, var(--cyan), var(--teal));
  border-radius: 4px; margin-bottom: 22px;
}
.eyebrow { text-transform: uppercase; letter-spacing: 0.18em; font-size: 8pt; color: var(--teal); font-weight: 700; }
.cover-sub { font-size: 16pt; font-weight: 600; color: var(--slate-2); margin: 0 0 16px; line-height: 1.25; }
.cover-lede { max-width: 150mm; color: var(--muted); }
.cover-meta {
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px 18px;
  margin: 28px 0 24px; max-width: 160mm;
}
.cover-meta div {
  background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px;
}
.cover-meta span { display: block; font-size: 7.5pt; text-transform: uppercase; letter-spacing: 0.12em; color: var(--cyan); font-weight: 700; }
.cover-note { max-width: 160mm; border-top: 1px solid var(--border); padding-top: 12px; }

.toc { page-break-after: always; padding-top: 8mm; }
.toc ol { font-size: 12pt; line-height: 2; color: var(--slate-2); }

.chapter { page-break-before: always; }
.kicker {
  text-transform: uppercase; letter-spacing: 0.2em; font-size: 8pt;
  color: var(--cyan); font-weight: 800; margin: 0 0 4px;
}
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0 12px; }
.card {
  background: var(--card); border: 1px solid var(--border); border-radius: 8px;
  padding: 10px 12px; break-inside: avoid;
}
.card h3 { margin-top: 0; }
.card.tight ul { margin-bottom: 0; }
.callout {
  background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px;
  padding: 10px 12px; margin: 8px 0 12px; break-inside: avoid;
}
.tag {
  display: inline-block; font-size: 7pt; font-weight: 800; letter-spacing: 0.08em;
  text-transform: uppercase; padding: 1px 6px; border-radius: 99px; margin-right: 6px;
  vertical-align: middle;
}
.tag-live { background: #dcfce7; color: #166534; }
.tag-road { background: #fef9c3; color: #854d0e; }

.pills { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; margin: 8px 0 10px; }
.chip {
  background: #fff; border: 1px solid var(--border); border-radius: 99px;
  padding: 3px 9px; font-size: 8pt; font-weight: 700; color: var(--teal);
}
.arrow { color: var(--cyan); font-weight: 700; }

table {
  width: 100%; border-collapse: collapse; margin: 8px 0 12px;
  font-size: 8.5pt; break-inside: avoid;
}
th, td { border: 1px solid var(--border); padding: 6px 8px; text-align: left; vertical-align: top; }
th { background: var(--slate); color: #fff; font-weight: 600; }
tr:nth-child(even) td { background: var(--card); }
table.intel td { font-size: 8pt; }

.figure { margin: 12px 0; break-inside: avoid; }
.figure figcaption {
  font-size: 8pt; color: var(--muted); font-weight: 600; margin-bottom: 6px;
  text-transform: uppercase; letter-spacing: 0.06em;
}
.figure svg { width: 100%; height: auto; }

.formula {
  background: var(--slate); color: #e2e8f0; border-radius: 8px;
  padding: 12px 14px; font-family: "JetBrains Mono", Consolas, monospace;
  font-size: 11pt; text-align: center; margin: 10px 0; break-inside: avoid;
}
.formula span { white-space: nowrap; }
.formula .op { color: var(--cyan); margin: 0 6px; font-weight: 700; }
.formula.small-form { font-size: 8pt; line-height: 1.6; color: #cbd5e1; }

.verdicts { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 10px 0; }
.pill-card {
  border-radius: 8px; padding: 10px 12px; color: #fff; break-inside: avoid;
}
.pill-card strong { display: block; font-size: 10pt; letter-spacing: 0.12em; }
.pill-card span { display: block; font-size: 14pt; font-weight: 800; margin: 2px 0 6px; }
.pill-card em { font-style: normal; font-size: 8pt; opacity: 0.95; }
.pill-card.low { background: var(--low); }
.pill-card.med { background: var(--med); color: #1c1917; }
.pill-card.high { background: var(--high); }
.pill-card.crit { background: var(--crit); }

.appendix { page-break-before: always; }
.map { background: var(--slate); color: #e2e8f0; padding: 12px; border-radius: 8px; border: 0; }
.end { margin-top: 16px; font-size: 8pt; color: var(--muted); }
"""

SEQUENCE_SVG = r"""
<svg viewBox="0 0 860 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="PHISHEYE request sequence">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#0ea5e9"/>
    </marker>
    <marker id="arrd" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8"/>
    </marker>
  </defs>
  <rect x="0" y="0" width="860" height="420" fill="#f8fafc" stroke="#e2e8f0"/>
  <!-- actors -->
  <g font-family="Inter, Helvetica, sans-serif" font-size="11" fill="#0f172a" text-anchor="middle">
    <rect x="20" y="16" width="120" height="36" rx="6" fill="#0f172a"/>
    <text x="80" y="39" fill="#fff" font-weight="700">Client UI</text>
    <rect x="190" y="12" width="150" height="44" rx="6" fill="none" stroke="#94a3b8" stroke-dasharray="5 4" stroke-width="1.5"/>
    <text x="265" y="30" fill="#64748b" font-size="9">ROADMAP</text>
    <text x="265" y="46" fill="#64748b" font-weight="600">Rate limiter</text>
    <rect x="380" y="16" width="130" height="36" rx="6" fill="#0d9488"/>
    <text x="445" y="39" fill="#fff" font-weight="700">FastAPI :8000</text>
    <rect x="550" y="16" width="130" height="36" rx="6" fill="#0ea5e9"/>
    <text x="615" y="39" fill="#fff" font-weight="700">URL pipeline</text>
    <rect x="720" y="16" width="120" height="36" rx="6" fill="#0f172a"/>
    <text x="780" y="39" fill="#fff" font-weight="700">SQLite DB</text>
  </g>
  <!-- lifelines -->
  <g stroke="#cbd5e1" stroke-width="1.2">
    <line x1="80" y1="60" x2="80" y2="400"/>
    <line x1="265" y1="60" x2="265" y2="400" stroke-dasharray="4 4"/>
    <line x1="445" y1="60" x2="445" y2="400"/>
    <line x1="615" y1="60" x2="615" y2="400"/>
    <line x1="780" y1="60" x2="780" y2="400"/>
  </g>
  <g font-family="Inter, Helvetica, sans-serif" font-size="10" fill="#334155">
    <!-- 1 -->
    <line x1="80" y1="88" x2="445" y2="88" stroke="#0ea5e9" stroke-width="1.6" marker-end="url(#arr)"/>
    <text x="262" y="82" text-anchor="middle">1 POST /check-url  JWT optional</text>
    <!-- dashed limiter -->
    <line x1="190" y1="118" x2="340" y2="118" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="5 3" marker-end="url(#arrd)"/>
    <text x="265" y="112" text-anchor="middle" fill="#94a3b8" font-size="9">2 Redis / token bucket (not shipped)</text>
    <!-- 3 pipeline -->
    <line x1="445" y1="150" x2="615" y2="150" stroke="#0ea5e9" stroke-width="1.6" marker-end="url(#arr)"/>
    <text x="530" y="144" text-anchor="middle">3 URLChecker.analyze</text>
    <!-- intel box -->
    <rect x="500" y="168" width="230" height="70" rx="8" fill="#fff" stroke="#0ea5e9"/>
    <text x="615" y="190" text-anchor="middle" font-weight="700" fill="#0f172a">4 Intelligence + heuristics</text>
    <text x="615" y="208" text-anchor="middle" font-size="9">Feeds · RDAP · TLS · lookalikes</text>
    <text x="615" y="224" text-anchor="middle" font-size="9">Psychology · decision floors</text>
    <!-- persist -->
    <line x1="615" y1="260" x2="780" y2="260" stroke="#0d9488" stroke-width="1.6" marker-end="url(#arr)"/>
    <text x="698" y="254" text-anchor="middle">5 INSERT url_checks</text>
    <!-- response -->
    <line x1="445" y1="300" x2="80" y2="300" stroke="#0d9488" stroke-width="1.6" marker-end="url(#arr)"/>
    <text x="262" y="294" text-anchor="middle">6 JSON Simple + Technical views</text>
    <!-- fusion note -->
    <rect x="120" y="330" width="620" height="56" rx="8" fill="#ecfeff" stroke="#0d9488"/>
    <text x="430" y="352" text-anchor="middle" font-weight="700">Fusion</text>
    <text x="430" y="370" text-anchor="middle" font-size="9">Confirmed intel floors score (85/80/72/55). Heuristics cannot veto a feed hit. ml channel = lexical copy.</text>
  </g>
</svg>
"""

QR_SVG = r"""
<svg viewBox="0 0 860 150" xmlns="http://www.w3.org/2000/svg" role="img">
  <rect width="860" height="150" fill="#f8fafc" stroke="#e2e8f0"/>
  <g font-family="Inter, Helvetica, sans-serif" font-size="11" text-anchor="middle">
    <rect x="16" y="40" width="100" height="70" rx="8" fill="#0f172a"/>
    <text x="66" y="80" fill="#fff" font-weight="700">PNG / JPG</text>
    <path d="M124 75 H148" stroke="#0ea5e9" stroke-width="2"/>
    <rect x="152" y="28" width="118" height="94" rx="8" fill="#fff" stroke="#0ea5e9"/>
    <text x="211" y="52" fill="#0f172a" font-weight="700">Pre-process</text>
    <text x="211" y="70" fill="#475569" font-size="9">Gray · invert</text>
    <text x="211" y="86" fill="#475569" font-size="9">CLAHE · Otsu</text>
    <text x="211" y="102" fill="#475569" font-size="9">Adaptive thr.</text>
    <path d="M274 75 H298" stroke="#0ea5e9" stroke-width="2"/>
    <rect x="302" y="40" width="130" height="70" rx="8" fill="#0d9488"/>
    <text x="367" y="72" fill="#fff" font-weight="700">QR decode</text>
    <text x="367" y="90" fill="#ecfdf5" font-size="9">OpenCV + PIL</text>
    <path d="M436 75 H460" stroke="#0ea5e9" stroke-width="2"/>
    <rect x="464" y="40" width="150" height="70" rx="8" fill="#0ea5e9"/>
    <text x="539" y="72" fill="#fff" font-weight="700">Extract URLs</text>
    <text x="539" y="90" fill="#e0f2fe" font-size="9">payload ≤ 15 links</text>
    <path d="M618 75 H642" stroke="#0ea5e9" stroke-width="2"/>
    <rect x="646" y="40" width="196" height="70" rx="8" fill="#0f172a"/>
    <text x="744" y="72" fill="#fff" font-weight="700">URL pipeline</text>
    <text x="744" y="90" fill="#cbd5e1" font-size="9">analyze_content("qr")</text>
  </g>
</svg>
"""


def render_html() -> str:
    return html_document()


def _try_weasyprint(html: str, pdf_path: Path) -> None:
    from weasyprint import HTML

    HTML(string=html, base_url=str(pdf_path.parent)).write_pdf(str(pdf_path))


def _try_playwright(html_path: Path, pdf_path: Path) -> None:
    from playwright.sync_api import sync_playwright

    uri = html_path.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(uri, wait_until="load", timeout=90_000)
        page.wait_for_timeout(1500)
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()


def _chromium_candidates() -> list[Path]:
    local = Path.home() / "AppData" / "Local"
    return [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        local / "Google" / "Chrome" / "Application" / "chrome.exe",
        local / "Microsoft" / "Edge" / "Application" / "msedge.exe",
    ]


def _try_chromium_headless(html_path: Path, pdf_path: Path) -> str:
    import subprocess

    exe = next((p for p in _chromium_candidates() if p.is_file()), None)
    if exe is None:
        raise FileNotFoundError("Edge/Chrome not found for headless PDF print")

    uri = html_path.resolve().as_uri()
    cmd = [
        str(exe),
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path.resolve()}",
        uri,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0 or not pdf_path.is_file() or pdf_path.stat().st_size < 1000:
        raise RuntimeError(
            f"{exe.name} pdf print failed ({proc.returncode}): {proc.stderr[-400:]}"
        )
    return exe.name


def compile_pdf(html: str, pdf_path: Path, html_path: Path) -> str:
    html_path.write_text(html, encoding="utf-8")
    errors: list[str] = []

    try:
        _try_weasyprint(html, pdf_path)
        return "weasyprint"
    except Exception as exc:
        errors.append(f"weasyprint: {exc}")

    try:
        _try_playwright(html_path, pdf_path)
        return "playwright"
    except Exception as exc:
        errors.append(f"playwright: {exc}")

    try:
        engine = _try_chromium_headless(html_path, pdf_path)
        return f"chromium:{engine}"
    except Exception as exc:
        errors.append(f"chromium: {exc}")

    msg = (
        "Could not compile PDF. HTML was written to:\n"
        f"  {html_path}\n\n"
        "Install one renderer:\n"
        "  pip install weasyprint\n"
        "  pip install playwright && python -m playwright install chromium\n"
        "Or install Microsoft Edge / Google Chrome for headless print.\n\n"
        + "\n".join(errors)
    )
    raise SystemExit(msg)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the PHISHEYE architecture PDF.")
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    args = parser.parse_args(argv)

    html = render_html()
    engine = compile_pdf(html, args.pdf, args.html)
    print(f"Wrote {args.html}")
    print(f"Wrote {args.pdf} via {engine}")
    download = Path.home() / "Downloads" / args.pdf.name
    try:
        download.write_bytes(args.pdf.read_bytes())
        print(f"Copied {download}")
    except OSError as exc:
        print(f"Download copy skipped: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

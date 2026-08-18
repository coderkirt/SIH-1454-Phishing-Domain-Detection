"""Build the PhishShield AI viva/presentation handbook PDF from inspected repo facts."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "PhishShield_AI_Presentation_and_Jury_Master_Guide.pdf"

NAVY = colors.HexColor("#070d18")
CYAN = colors.HexColor("#22d3ee")
CARD = colors.HexColor("#0c1424")
SLATE = colors.HexColor("#94a3b8")
WHITE = colors.HexColor("#e8eef8")
AMBER = colors.HexColor("#fbbf24")
RED = colors.HexColor("#f87171")
GREEN = colors.HexColor("#34d399")


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(name="CoverTitle", fontName="Times-Bold", fontSize=26, leading=32, alignment=TA_CENTER, textColor=NAVY))
    s.add(ParagraphStyle(name="CoverSub", fontName="Times-Italic", fontSize=13, leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#334155")))
    s.add(ParagraphStyle(name="H1c", fontName="Times-Bold", fontSize=16, leading=20, spaceBefore=14, spaceAfter=8, textColor=NAVY))
    s.add(ParagraphStyle(name="H2c", fontName="Times-Bold", fontSize=13, leading=17, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor("#0e7490")))
    s.add(ParagraphStyle(name="Bodyc", fontName="Times-Roman", fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=6))
    s.add(ParagraphStyle(name="Tip", fontName="Times-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#155e75"), backColor=colors.HexColor("#ecfeff"), borderPadding=6))
    s.add(ParagraphStyle(name="Warn", fontName="Times-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#9a3412"), backColor=colors.HexColor("#fff7ed")))
    s.add(ParagraphStyle(name="Dont", fontName="Times-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#9f1239"), backColor=colors.HexColor("#fff1f2")))
    s.add(ParagraphStyle(name="Must", fontName="Times-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#166534"), backColor=colors.HexColor("#f0fdf4")))
    s.add(ParagraphStyle(name="CodeBlock", fontName="Courier", fontSize=8, leading=11, backColor=colors.HexColor("#f1f5f9"), leftIndent=6, rightIndent=6))
    s.add(ParagraphStyle(name="Small", fontName="Times-Roman", fontSize=8, leading=11, textColor=colors.HexColor("#475569")))
    s.add(ParagraphStyle(name="Cell", fontName="Times-Roman", fontSize=8, leading=11))
    s.add(ParagraphStyle(name="CellB", fontName="Times-Bold", fontSize=8, leading=11))
    s.add(ParagraphStyle(name="Footer", fontName="Times-Roman", fontSize=8, alignment=TA_CENTER, textColor=SLATE))
    return s


def box(style, text):
    return Paragraph(text, style)


def table(data, col_widths):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0e7490")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    return t


def P(text, st):
    return Paragraph(text.replace("\n", "<br/>"), st)


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(CYAN)
    canvas.setFont("Times-Bold", 9)
    canvas.drawString(16 * mm, A4[1] - 8 * mm, "PhishShield AI  |  SIH 1454  |  Jury & Presentation Master Guide")
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, A4[0], 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Times-Roman", 8)
    canvas.drawString(16 * mm, 4 * mm, "Based on the CyberGuard repository  |  Do not invent metrics")
    canvas.drawRightString(A4[0] - 16 * mm, 4 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build():
    st = styles()
    story = []
    cell = st["Cell"]
    cellb = st["CellB"]

    def C(text, bold=False):
        return Paragraph(str(text), cellb if bold else cell)

    # Cover
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph("PHISHSHIELD AI", st["CoverTitle"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Presentation + Jury Viva Master Guide", st["CoverSub"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("SIH 1454 — Intelligent detection of phishing domains imitating genuine domains", st["CoverSub"]))
    story.append(Spacer(1, 12 * mm))
    story.append(box(st["Warn"], "ACCURACY RULE: This handbook matches the current repository. The running product name is CyberGuard. Backend is FastAPI + SQLite. There is no Flask, no PostgreSQL server, no TensorFlow/CNN, and no published F1/accuracy. Planned items are labeled."))
    story.append(Spacer(1, 8 * mm))
    story.append(P("Companion markdown (full question bank and study plans):", st["Bodyc"]))
    for item in [
        "docs/IMPLEMENTATION_REALITY_CHECK.md",
        "docs/TECH_STACK_STUDY_GUIDE.md",
        "docs/PRESENTATION_MASTER_GUIDE.md",
        "docs/JURY_VIVA_QUESTION_BANK.md (120+ Q&amp;A)",
        "docs/TEAM_STUDY_PLANS.md",
    ]:
        story.append(P(f"• {item}", st["Bodyc"]))
    story.append(PageBreak())

    story.append(Paragraph("1. Table of contents", st["H1c"]))
    toc = [
        "1. Contents and how to use this book",
        "2. Implementation reality check",
        "3. Problem, solution, and honest architecture",
        "4. Technology inventory",
        "5. Detection pipeline and APIs",
        "6. SQLite data model (not PostgreSQL)",
        "7. Machine learning — what exists vs planned",
        "8. Psychological threat detection",
        "9. Security of the system",
        "10. Frontend, dual view, extension",
        "11. Slide script, 2-minute and 5-minute talks",
        "12. How to answer when you do not know",
        "13. One-page cheat sheet",
        "14. Pointer to 120 viva questions",
    ]
    for t in toc:
        story.append(P(t, st["Bodyc"]))
    story.append(box(st["Must"], "MUST KNOW: Web app and extension both call POST /api/v1/threat/check-url with {url, view:'both'}. Same URL → same score."))
    story.append(PageBreak())

    story.append(Paragraph("2. Implementation reality check", st["H1c"]))
    story.append(P("Inspected: backend FastAPI routes/services/tests, React pages, Manifest V3 extension, requirements.txt, package.json, SQLite schema. No git commits in this workspace. SQLAlchemy model files exist but live routes use sqlite3.", st["Bodyc"]))
    rows = [[C("Feature", True), C("Status", True), C("Evidence", True)]]
    facts = [
        ("FastAPI + Uvicorn", "IMPLEMENTED", "backend/app/main.py"),
        ("Flask", "NOT IMPLEMENTED", "not in requirements"),
        ("React + Vite + Tailwind + Axios + Recharts", "IMPLEMENTED", "frontend/package.json"),
        ("SQLite threats.db", "IMPLEMENTED", "database/connection.py"),
        ("PostgreSQL", "NOT IMPLEMENTED", "planned scale-up"),
        ("SQLAlchemy ORM at runtime", "PARTIAL", "models/*.py unused by routes"),
        ("Alembic migrations", "NOT IMPLEMENTED", "init_db() only"),
        ("Rule URL engine", "IMPLEMENTED", "services/url_checker.py"),
        ("Psychology urgency/fear/greed", "IMPLEMENTED", "services/psychology.py"),
        ("Simple + Technical views", "IMPLEMENTED", "services/warnings.py"),
        ("GSB / OpenPhish", "IMPLEMENTED", "external_intel.py (GSB needs key)"),
        ("Aggressive ads / SSRF guards", "IMPLEMENTED", "ad_signals.py"),
        ("CNN / sklearn / TF", "NOT IMPLEMENTED", "no model files"),
        ("ml_confidence", "PARTIAL", "column default 0.0, unused"),
        ("JWT auth", "IMPLEMENTED", "routes/user.py"),
        ("Auth required on scan", "NOT IMPLEMENTED", "check-url is public"),
        ("Extension MV3 auto-scan/toast/warning", "IMPLEMENTED", "extension/"),
        ("Message scanner UI", "PARTIAL", "API yes, React unused"),
        ("Rate limiting", "NOT IMPLEMENTED", "admit gap"),
        ("Published F1/accuracy", "NOT AVAILABLE", "never invent"),
    ]
    for a, b, c in facts:
        rows.append([C(a), C(b), C(c)])
    story.append(table(rows, [70 * mm, 40 * mm, 60 * mm]))
    story.append(Spacer(1, 4 * mm))
    story.append(box(st["Dont"], "DO NOT SAY: We use Flask, PostgreSQL, CNN, 99% accuracy, federated learning, or zero-knowledge proofs. Those are absent or marked Planned in Privacy.jsx."))
    story.append(PageBreak())

    story.append(Paragraph("3. Problem and architecture", st["H1c"]))
    story.append(Paragraph("Beginner", st["H2c"]))
    story.append(P("People get fake bank/UPI links. The site looks real. They type a password. PhishShield AI (CyberGuard code) checks the link, gives a score, and warns in simple English. A Chrome extension can warn while browsing.", st["Bodyc"]))
    story.append(Paragraph("Technical", st["H2c"]))
    story.append(P("SIH 1454 targets domains that imitate genuine brands. The MVP is a multi-signal rule engine plus live threat lists (Google Safe Browsing if keyed, else OpenPhish), DNS, RDAP age, brand impersonation (Levenshtein, leetspeak, limited homoglyphs), Hinglish psychological phrases, and aggressive-ad HTML sampling. React and the extension are clients of one FastAPI process. Persistence is SQLite.", st["Bodyc"]))
    story.append(Preformatted(
        "Extension / React\n    REST JSON  POST /api/v1/threat/check-url\n        FastAPI :8000  (CORS * )\n            URLChecker + psychology + intel + ads\n                sqlite3  threats.db\n            JSON score, simple_view, technical_view",
        st["CodeBlock"],
    ))
    story.append(box(st["Tip"], "JURY TIP: If they draw Flask→Postgres→CNN, politely redraw FastAPI→SQLite→rules. Offer Postgres and a trained classifier as the production roadmap."))
    story.append(Paragraph("Why phishing is hard", st["H2c"]))
    story.append(P("HTTPS is cheap. Logos are copied. Domains are new. SMS uses fear. Blacklists lag. URL-only analysis is incomplete: we do not fully render JS, do not validate certificate chains, and do not OCR the page. The message API exists but the dashboard does not call it yet.", st["Bodyc"]))
    story.append(PageBreak())

    story.append(Paragraph("4. Technology inventory", st["H1c"]))
    rows = [[C("Tech", True), C("Where", True), C("Viva point", True)]]
    tech = [
        ("React 19 / Vite 8 / Tailwind 4", "frontend/", "SPA dashboard"),
        ("Axios + React Router + Recharts", "api.js, App.jsx, Dashboard", "JWT interceptor; live charts"),
        ("FastAPI + Uvicorn + Pydantic", "backend/app", "Not Flask"),
        ("bcrypt + python-jose JWT", "auth.py, user.py", "No plaintext passwords"),
        ("sqlite3 + parameterized SQL", "connection.py, routes", "SQL injection defense"),
        ("requests", "intel + ads", "Timeouts, fail-soft"),
        ("Manifest V3 JS", "extension/", "SW + content + popup"),
        ("pytest + TestClient", "backend/tests", "google LOW, paypa1 HIGH"),
    ]
    for a, b, c in tech:
        rows.append([C(a), C(b), C(c)])
    story.append(table(rows, [62 * mm, 55 * mm, 53 * mm]))
    story.append(P("Planned only: PostgreSQL, Alembic, scikit-learn, TensorFlow/Keras CNN, full i18n UI, rate limits, per-user history.", st["Bodyc"]))
    story.append(PageBreak())

    story.append(Paragraph("5. Pipeline and APIs", st["H1c"]))
    story.append(P("There is no POST /api/analyze. The viva endpoint is POST /api/v1/threat/check-url.", st["Bodyc"]))
    story.append(Paragraph("check-url steps", st["H2c"]))
    steps = [
        "Pydantic body: url, view=both|simple|technical",
        "Trim; prefix https:// if missing",
        "URLChecker.analyze: DNS, GSB/OpenPhish, RDAP age, phishing fragments, piracy list, ad signals, brand, TLD, keywords, IP host, length, HTTPS, email-host, psychology on URL string",
        "Cap score 100; map 30/50/70 to MEDIUM/HIGH/CRITICAL",
        "Trusted allowlist (google.com, sbi.co.in, ...) returns 0 if domain exists",
        "INSERT url_checks (user_id not set; ml_confidence stays 0)",
        "If HIGH/CRITICAL INSERT threats with classify_threat_type",
        "Return simple_view and/or technical_view",
    ]
    for i, stext in enumerate(steps, 1):
        story.append(P(f"{i}. {stext}", st["Bodyc"]))
    rows = [[C("Method", True), C("Path", True), C("Notes", True)]]
    apis = [
        ("GET", "/", "lists endpoints"),
        ("GET", "/health", "{status:ok}"),
        ("POST", "/api/v1/threat/check-url", "main scanner; public"),
        ("POST", "/api/v1/threat/check-message", "psychology ± URL; no UI"),
        ("GET", "/api/v1/threat/stats|recent-urls", "history helpers"),
        ("POST", "/api/v1/user/signup|login", "JWT, bcrypt"),
        ("GET", "/api/v1/user/profile", "Bearer required"),
        ("GET", "/api/v1/stats/*", "overview, types, risk, daily"),
    ]
    for a, b, c in apis:
        rows.append([C(a), C(b), C(c)])
    story.append(table(rows, [22 * mm, 78 * mm, 70 * mm]))
    story.append(box(st["Warn"], "WARNING: daily-summary.average_response_time_ms is hardcoded 245. Do not defend it as a measured SLA."))
    story.append(Paragraph("Risk points (implemented)", st["H2c"]))
    pts = (
        "DNS missing +35; intel flagged +40; age&lt;30d +20 / &lt;90d +10; phishing fragment +40; "
        "piracy +35; brand impersonation +40; suspicious TLD +15; keyword +5; IP URL +30; "
        "many subdomains +10; long URL +8; no HTTPS +5; email host +20; urgency +15; fear +15; greed +12; malvertising +20."
    )
    story.append(P(pts, st["Bodyc"]))
    story.append(PageBreak())

    story.append(Paragraph("6. Database", st["H1c"]))
    story.append(P("Why SQLite: zero ops for SIH demo. Why not Postgres yet: no server to operate; Postgres is the correct later choice for concurrency and backups. ORM: SQLAlchemy classes are not on the live path. Migrations: none.", st["Bodyc"]))
    rows = [[C("Table", True), C("Columns", True), C("Notes", True)]]
    for a, b, c in [
        ("users", "id PK, username, email, password_hash, created_at", "unique user/email"),
        ("url_checks", "id, user_id FK, url, risk_level, risk_score, ml_confidence, timestamp", "user_id unused on INSERT"),
        ("threats", "id, threat_type, threat_data, severity, last_updated", "HIGH/CRITICAL only"),
    ]:
        rows.append([C(a), C(b), C(c)])
    story.append(table(rows, [32 * mm, 95 * mm, 43 * mm]))
    story.append(Preformatted("SELECT url, risk_level, risk_score FROM url_checks ORDER BY id DESC LIMIT 20;", st["CodeBlock"]))
    story.append(P("Two users at once: SQLite serializes writes. DB down: 500, extension says unavailable. SQL injection: '?' placeholders.", st["Bodyc"]))
    story.append(PageBreak())

    story.append(Paragraph("7. Machine learning — honesty section", st["H1c"]))
    story.append(box(st["Dont"], "METRIC NOT YET AVAILABLE. No dataset file, no train/test split, no confusion matrix, no ROC/AUC, no joblib model."))
    story.append(P("If a jury wants ML theory, explain accuracy vs recall with phishing: a dummy always-SAFE model can have high accuracy and still fail victims. Recall (catching phishing) matters more. Then say our current system is a transparent rule engine whose features are exactly the inputs a future Random Forest or URL-CNN would use. The ml_confidence column is reserved.", st["Bodyc"]))
    story.append(Paragraph("CNN (planned only)", st["H2c"]))
    story.append(P("Do not recite a fake Keras Sequential. If asked why CNN later: character-level URL CNNs appear in literature for obfuscated strings. Today Levenshtein + lists cover impersonation without GPU training data.", st["Bodyc"]))
    story.append(PageBreak())

    story.append(Paragraph("8. Psychological threat detection", st["H1c"]))
    story.append(P("Novelty you can defend: English + Hinglish phrase detection for urgency, fear, and greed in psychology.py. Examples: act now, account blocked, you won, jaldi karo, band ho jayega.", st["Bodyc"]))
    story.append(P("Not implemented as separate modules: fake countdown DOM, coercion classifier, credential form detection, authority-seal CV, repeated CTA counting on the rendered page.", st["Bodyc"]))
    story.append(box(st["Must"], "MUST KNOW: A countdown or 'act now' on a real airline sale is not automatically phishing. We add points; CRITICAL needs multiple strong signals (e.g. fake brand + new domain + intel)."))
    story.append(P("Message API combines psychology score with optional URL score. Dashboard does not expose it yet — say PARTIAL.", st["Bodyc"]))
    story.append(PageBreak())

    story.append(Paragraph("9. Security of PhishShield", st["H1c"]))
    rows = [[C("Issue", True), C("Status", True), C("Where / note", True)]]
    for a, b, c in [
        ("SQL injection", "IMPLEMENTED", "parameterized sqlite3"),
        ("Password hashing", "IMPLEMENTED", "bcrypt"),
        ("JWT", "IMPLEMENTED", "HS256; change SECRET_KEY"),
        ("SSRF on ad fetch", "IMPLEMENTED", "block private/loopback, timeout 4s, 150KB"),
        ("XSS", "PARTIAL", "React escape; extension escapeHtml"),
        ("CORS", "WEAK", "allow_origins=['*']"),
        ("Rate limit", "NOT IMPLEMENTED", "scan flood possible"),
        ("Scan auth / user_id", "NOT IMPLEMENTED", "global history"),
        ("Full TLS cert check", "NOT IMPLEMENTED", "only https:// prefix"),
        ("Punycode xn--", "NOT IMPLEMENTED", "limited Cyrillic map only"),
        ("Page password scrape", "NOT DONE (good)", "URL only"),
    ]:
        rows.append([C(a), C(b), C(c)])
    story.append(table(rows, [45 * mm, 40 * mm, 85 * mm]))
    story.append(PageBreak())

    story.append(Paragraph("10. Frontend, dual view, extension", st["H1c"]))
    story.append(P("React components: AuthContext, ProtectedRoute, UrlScanner, ScanResult (sessionStorage), Dashboard/Statistics (Recharts from SQLite counts), History, Settings, Privacy (honest Planned list), Advisor (static FAQ), Landing.", st["Bodyc"]))
    story.append(P("Simple View: DANGER / BE CAREFUL / LOOKS SAFE plus 'do not enter OTP'. Technical View: domain exists, HTTPS, TLD, brand, age, Safe Browsing label, aggressive ads.", st["Bodyc"]))
    story.append(P("Extension: MV3, tabs+storage, auto-scan, 90s cache, badge OK/MED/HIGH/CRIT, page toast for every result, full overlay on HIGH/CRITICAL, CONTINUE ANYWAY session flag, login via same JWT APIs, never SAFE if API down.", st["Bodyc"]))
    story.append(box(st["Tip"], "JURY TIP: Demo google.com (SAFE toast) then paypa1.com or sbi-login.xyz (CRITICAL overlay) in both dashboard and extension. Scores must match."))
    story.append(PageBreak())

    story.append(Paragraph("11. Presentation script", st["H1c"]))
    story.append(Paragraph("20 slides (titles)", st["H2c"]))
    story.append(P("Title → Problem → Gap → Solution → Innovation → Architecture (FastAPI/SQLite) → Pipeline → Intelligent detection current+planned → Psychology → Simple View → Technical View → Extension → Data model → Security → Testing → Stack → Novelty → Limitations → Future → Conclusion/demo.", st["Bodyc"]))
    story.append(Paragraph("2-minute pitch", st["H2c"]))
    story.append(P("Phishing copies banks and UPI apps. HTTPS and logos are not proof. PhishShield AI, in our CyberGuard repo, scores any URL with the same FastAPI engine from the website and the Chrome extension. We combine live intel, brand impersonation, Hinglish urgency/fear language, and shady popup-ad networks into a 0–100 score and a plain-English warning. This version is a multi-signal rule engine plus threat lists, not a trained CNN, and it stores scans in SQLite. The next step is a supervised model and PostgreSQL. The value today is consistent, explainable, real-time protection without invented results.", st["Bodyc"]))
    story.append(Paragraph("5-minute technical", st["H2c"]))
    story.append(P("Architecture; check-url walk; thresholds; psychology tags; SQLite tables; JWT for dashboard; public scans; extension cache/badge/overlay; SSRF/SQL/bcrypt; CORS and rate-limit gaps; pytest; limitations; roadmap.", st["Bodyc"]))
    story.append(PageBreak())

    story.append(Paragraph("12. If you do not know", st["H1c"]))
    story.append(P("Say: 'That is planned / not in this repository. Today we handle it through [existing mechanism]. I will not invent a metric.' Open the file if allowed. Never guess CNN layers, dataset size, or Postgres connection strings.", st["Bodyc"]))
    story.append(box(st["Dont"], "DO NOT SAY: We never send URLs to a server (we do). We block all ads (we don't). We are GDPR certified (we're not)."))
    story.append(PageBreak())

    story.append(Paragraph("13. One-page cheat sheet", st["H1c"]))
    cheat = [
        "Name: PhishShield AI / CyberGuard | Problem: SIH 1454 impersonation phishing",
        "Solution: FastAPI multi-signal URL engine + React + MV3 extension",
        "Novelty: brand impersonation + Hinglish psychology + dual view + identical scores",
        "Stack: React Vite Tailwind Axios Recharts | FastAPI Uvicorn | SQLite | JWT | MV3",
        "API: POST /api/v1/threat/check-url  {url, view:'both'}",
        "Score: additive points, cap 100 | LOW&lt;30 MEDIUM&lt;50 HIGH&lt;70 CRITICAL",
        "ML: NOT TRAINED | METRIC NOT YET AVAILABLE | ml_confidence unused",
        "DB: users, url_checks, threats | user_id not filled",
        "Security: bcrypt, JWT, parameterized SQL, SSRF on ads | CORS * | no rate limit",
        "Limits: URL-centric, no cert chain, no punycode decoder, SQLite, global history",
        "Future: PostgreSQL, supervised ML, per-user history, message UI, tighter CORS",
        "Offline extension: UNAVAILABLE, never SAFE",
    ]
    for line in cheat:
        story.append(P("• " + line, st["Bodyc"]))
    story.append(Paragraph("10 answers to memorize", st["H2c"]))
    tens = [
        "Not Flask — FastAPI.",
        "Not Postgres yet — SQLite.",
        "Not CNN — rules + intel.",
        "Same check-url for web and extension.",
        "HTTPS does not mean safe.",
        "Urgency alone is not phishing.",
        "Backend down ≠ SAFE.",
        "No page passwords/OTPs collected.",
        "METRIC NOT YET AVAILABLE.",
        "Biggest limit: no trained model + URL-centric analysis.",
    ]
    for i, line in enumerate(tens, 1):
        story.append(P(f"{i}. {line}", st["Bodyc"]))
    story.append(PageBreak())

    story.append(Paragraph("14. Viva question bank (index)", st["H1c"]))
    story.append(P("The full 120 questions with short, detailed, project-specific, and do-not-say answers are in docs/JURY_VIVA_QUESTION_BANK.md. Categories: overview, problem, innovation, architecture, backend, SQLite, ML honesty, psychology, cybersecurity, React, extension, APIs, testing, security, deployment, scale, limitations, future.", st["Bodyc"]))
    story.append(Paragraph("Highest-probability questions", st["H2c"]))
    hot = [
        "Is this AI or rules?",
        "Why FastAPI not Flask?",
        "Why SQLite not PostgreSQL?",
        "Show the CNN. (Answer: not implemented.)",
        "What is your accuracy? (METRIC NOT YET AVAILABLE)",
        "HTTPS phishing?",
        "How is the extension talking to the backend?",
        "What if Google Safe Browsing is down?",
        "Do you store user passwords from other sites?",
        "What is novel if Google already has Safe Browsing?",
        "Can urgency on a real bank site flag it?",
        "How do you prevent SSRF / SQL injection?",
        "What fails first at scale?",
        "Why two views?",
        "Are dashboard charts fake?",
    ]
    for q in hot:
        story.append(P("• " + q, st["Bodyc"]))
    story.append(Spacer(1, 6 * mm))
    story.append(box(st["Must"], "FINAL CHECK BEFORE VIVA: Start backend and frontend. Scan google.com and a fake brand URL in both UI and extension. Open Privacy Center and say Planned features out loud. Open url_checker.py if they want code."))

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="PhishShield AI Presentation and Jury Master Guide",
        author="CyberGuard / PhishShield AI team",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()

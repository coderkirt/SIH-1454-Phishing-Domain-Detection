import { useState } from "react";
import { Link } from "react-router-dom";
import UrlScanner from "../components/UrlScanner";
import ScreenshotUploader from "../components/ScreenshotUploader";
import DotMatrixLogo from "../components/DotMatrixLogo";

const pipeline = [
  "URL",
  "Screenshot",
  "Threat intelligence",
  "Analysis",
  "Risk",
];

const capabilities = [
  { title: "URL threat detection", body: "Analyze suspicious links against phishing, brand-fake, and piracy patterns." },
  { title: "Screenshot upload", body: "Drop a WhatsApp, SMS, or website screenshot. PHISHEYE looks for QR codes and visible links." },
  { title: "Risk scoring", body: "Every scan returns a 0–100 score and a LOW, MEDIUM, HIGH, or CRITICAL level." },
  { title: "Threat history", body: "Previous checks are stored in the backend database so you can review them later." },
  { title: "Security analytics", body: "Dashboard charts are built from real scan records, not sample numbers." },
  { title: "Privacy-first approach", body: "Uploaded images are processed in memory and not stored. Passwords stay on your device." },
];

const steps = ["Enter URL", "Analyze", "Understand risk", "Stay protected"];

export default function Landing() {
  const [scanMode, setScanMode] = useState("url");

  return (
    <div className="mx-auto max-w-6xl px-4 pb-20">
      <section className="grid items-start gap-12 py-10 lg:grid-cols-[1.1fr_0.9fr] lg:py-16">
        <div>
          <div className="flex items-center gap-3">
            <DotMatrixLogo />
            <p className="label-tech">PHISHEYE</p>
          </div>
          <h1 className="mt-6 font-display text-4xl font-semibold uppercase leading-[1.05] tracking-tight text-ink sm:text-5xl">
            Web threat
            <br />
            analysis system
          </h1>
          <p className="mt-5 max-w-xl text-lg text-ink-soft">
            Detect phishing domains, brand impersonation, and malicious web behavior before you sign in.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a href="#scan" onClick={() => setScanMode("url")} className="btn-primary px-5 py-3">Analyze URL</a>
            <a href="#scan" onClick={() => setScanMode("screenshot")} className="btn-secondary px-5 py-3">Upload screenshot</a>
            <Link to="/dashboard" className="btn-secondary px-5 py-3">View overview</Link>
          </div>
          <div className="mt-10 grid gap-px border border-line bg-line sm:grid-cols-2">
            <div className="bg-surface p-4">
              <p className="label-tech">System</p>
              <p className="mt-2 flex items-center gap-2 text-sm text-ink-soft">
                <span className="dot dot-active" aria-hidden="true" />
                Online
              </p>
            </div>
            <div className="bg-surface p-4">
              <p className="label-tech">Engine</p>
              <p className="mt-2 font-mono text-sm text-ink-soft">Rule / threat intelligence</p>
            </div>
          </div>
        </div>

        <div id="scan" className="space-y-6">
          <div className="panel-accent panel p-5">
            <p className="label-tech">Analysis pipeline</p>
            <div className="mt-5 space-y-3">
              {pipeline.map((step, index) => (
                <div key={step} className="flex items-center gap-3">
                  <span className={`dot ${index === 0 ? "dot-critical" : "dot-inactive"}`} aria-hidden="true" />
                  <span className="font-mono text-xs uppercase tracking-[0.14em] text-ink-soft">{step}</span>
                  {index < pipeline.length - 1 ? (
                    <span className="ml-auto font-mono text-xs text-muted">↓</span>
                  ) : null}
                </div>
              ))}
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setScanMode("url")}
              className={`px-4 py-2 text-xs uppercase tracking-[0.12em] ${scanMode === "url" ? "btn-primary" : "btn-secondary"}`}
            >
              URL
            </button>
            <button
              type="button"
              onClick={() => setScanMode("screenshot")}
              className={`px-4 py-2 text-xs uppercase tracking-[0.12em] ${scanMode === "screenshot" ? "btn-primary" : "btn-secondary"}`}
            >
              Screenshot
            </button>
          </div>
          {scanMode === "url" ? <UrlScanner /> : <ScreenshotUploader />}
          <p className="meta-tech">Uses the live FastAPI backend. Sign in to access the full console.</p>
        </div>
      </section>

      <section className="rule pt-12">
        <p className="label-tech">Capabilities</p>
        <div className="mt-6 grid gap-px border border-line bg-line sm:grid-cols-2 lg:grid-cols-3">
          {capabilities.map(({ title, body }) => (
            <div key={title} className="bg-surface p-5">
              <p className="font-display text-base font-semibold text-ink">{title}</p>
              <p className="mt-2 text-sm text-muted">{body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-14">
        <p className="label-tech">Process</p>
        <div className="mt-6 grid gap-px border border-line bg-line sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, i) => (
            <div key={step} className="bg-surface p-5">
              <p className="font-mono text-xs text-muted">{String(i + 1).padStart(2, "0")}</p>
              <p className="mt-2 font-display text-base font-medium text-ink">{step}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

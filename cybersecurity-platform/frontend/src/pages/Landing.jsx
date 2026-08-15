import { Link } from "react-router-dom";
import { Shield, Activity, History, BarChart3, Lock, Sparkles } from "lucide-react";
import UrlScanner from "../components/UrlScanner";

const features = [
  { icon: Shield, title: "Real-time URL threat detection", body: "Analyze a suspicious link against phishing, brand-fake, and piracy patterns." },
  { icon: Activity, title: "Risk scoring", body: "Every scan returns a 0–100 score and a LOW, MEDIUM, HIGH, or CRITICAL level." },
  { icon: History, title: "Threat history", body: "Previous checks are stored in the backend database so you can review them later." },
  { icon: BarChart3, title: "Security analytics", body: "Dashboard charts are built from real scan records, not sample numbers." },
  { icon: Lock, title: "Privacy-first approach", body: "We only send the URL you choose to scan. Passwords stay on your device." },
  { icon: Sparkles, title: "AI-powered protection", body: "Rule-based threat analysis with brand impersonation and urgency-language detection." },
];

const steps = ["Enter URL", "Analyze", "Understand Risk", "Stay Protected"];

export default function Landing() {
  return (
    <div className="mx-auto max-w-6xl px-4 pb-20">
      <section className="grid items-center gap-10 py-10 lg:grid-cols-2 lg:py-16">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">CyberGuard</p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight text-white sm:text-5xl">
            AI-Powered Protection Against Phishing
          </h1>
          <p className="mt-4 max-w-xl text-lg text-slate-300">
            Check a suspicious website before you sign in. CyberGuard analyzes the URL, explains the risk in plain English, and keeps a history of what you scanned.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a href="#scan" className="rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950">Scan a URL</a>
            <Link to="/dashboard" className="rounded-xl border border-slate-600 px-5 py-3 font-medium text-slate-200">View Dashboard</Link>
          </div>
        </div>
        <div id="scan" className="card glow p-6">
          <p className="mb-4 text-sm font-medium text-slate-300">Scan a URL</p>
          <UrlScanner />
          <p className="mt-4 text-xs text-slate-500">Uses the live FastAPI backend. Sign in to keep using the full dashboard.</p>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {features.map(({ icon: Icon, title, body }) => (
          <div key={title} className="card p-5">
            <Icon className="text-cyan-300" size={22} />
            <h3 className="mt-3 font-semibold text-white">{title}</h3>
            <p className="mt-2 text-sm text-slate-400">{body}</p>
          </div>
        ))}
      </section>

      <section className="mt-14">
        <h2 className="text-2xl font-semibold text-white">How it works</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-4">
          {steps.map((step, i) => (
            <div key={step} className="card p-5">
              <p className="text-xs text-cyan-300">0{i + 1}</p>
              <p className="mt-2 font-medium">{step}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

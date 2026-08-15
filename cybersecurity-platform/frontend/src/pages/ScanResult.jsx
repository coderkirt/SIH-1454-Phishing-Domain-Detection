import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import RiskBadge from "../components/RiskBadge";
import { loadLastScan, recommendationFor, riskColor } from "../utils/risk";

function formatExists(value) {
  if (value === true) return "Yes — this domain is registered";
  if (value === false) return "No — this domain does not exist";
  return "Could not verify";
}

function formatAge(days) {
  if (days === null || days === undefined) return "Could not determine";
  if (days < 1) return "Registered today";
  const years = Math.floor(days / 365);
  if (years >= 2) return `${days.toLocaleString()} days (about ${years} years)`;
  if (years === 1) return `${days.toLocaleString()} days (about 1 year)`;
  return `${days} days`;
}

function formatSafeBrowsing(tech) {
  if (tech.safe_browsing_label) return tech.safe_browsing_label;
  const value = tech.google_safe_browsing;
  if (Array.isArray(value)) return `Flagged: ${value.join(", ")}`;
  if (value === "clean") return "Clean";
  if (value === "skipped") return "Skipped — domain does not exist";
  return "Lookup failed";
}

export default function ScanResult() {
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    setResult(loadLastScan());
  }, []);

  if (!result) {
    return (
      <div className="card p-8 text-center">
        <p className="text-lg text-white">No scan result yet</p>
        <p className="mt-2 text-slate-400">Scan a URL first to see a detailed report.</p>
        <Link to="/scanner" className="mt-6 inline-block rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950">Scan a URL</Link>
      </div>
    );
  }

  const score = result.risk_score ?? 0;
  const color = riskColor(result.risk_level);
  const warning = result.simple_view?.warning || result.simple_view?.warning_english;
  const reasons = result.reasons || [];
  const tags = result.threat_tags || [];
  const tech = result.technical_view || {};

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-white">Scan result</h1>
          <p className="mt-1 break-all font-mono text-sm text-cyan-200">{result.url}</p>
        </div>
        <button onClick={() => navigate("/scanner")} className="rounded-xl border border-slate-600 px-4 py-2 text-sm">
          Scan another URL
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-[220px_1fr]">
        <div className="card flex flex-col items-center justify-center p-6">
          <div
            className="grid h-36 w-36 place-items-center rounded-full"
            style={{ background: `conic-gradient(${color.hex} ${score * 3.6}deg, rgba(148,163,184,0.18) 0deg)` }}
          >
            <div className="grid h-28 w-28 place-items-center rounded-full bg-[#0b1524] text-center">
              <p className="text-3xl font-semibold text-white">{score}</p>
              <p className="text-xs text-slate-400">/ 100</p>
            </div>
          </div>
          <p className="mt-4 text-sm text-slate-400">Risk score</p>
        </div>

        <div className="card space-y-4 p-6">
          <div className="flex flex-wrap items-center gap-3">
            <RiskBadge level={result.risk_level} />
            <span className={`rounded-full border px-3 py-1 text-sm ${result.safe ? "border-emerald-500/30 text-emerald-300" : "border-red-500/30 text-red-300"}`}>
              {result.safe ? "Safe" : "Unsafe"}
            </span>
            <span className="text-sm text-slate-400">{result.simple_view?.verdict}</span>
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest text-slate-400">Recommendation</p>
            <p className="mt-2 text-slate-200">{recommendationFor(result.risk_level, warning)}</p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card p-6">
          <h2 className="font-medium">Detection reasons</h2>
          {reasons.length === 0 ? (
            <p className="mt-3 text-sm text-slate-400">No suspicious signals were found.</p>
          ) : (
            <ul className="mt-3 list-disc space-y-2 pl-5 text-slate-300">
              {reasons.map((reason) => <li key={reason}>{reason}</li>)}
            </ul>
          )}
        </div>
        <div className="card p-6">
          <h2 className="font-medium">Technical details</h2>
          <dl className="mt-3 space-y-2 text-sm text-slate-300">
            <div className="flex justify-between gap-4"><dt>Domain</dt><dd className="font-mono">{tech.domain || "—"}</dd></div>
            <div className="flex justify-between gap-4"><dt>Domain exists</dt><dd>{formatExists(tech.domain_exists)}</dd></div>
            <div className="flex justify-between gap-4"><dt>HTTPS</dt><dd>{tech.https ? "Yes" : "No"}</dd></div>
            <div className="flex justify-between gap-4"><dt>Suspicious TLD</dt><dd>{tech.suspicious_tld ? "Yes" : "No"}</dd></div>
            <div className="flex justify-between gap-4"><dt>Brand impersonated</dt><dd>{tech.brand_impersonated || "None"}</dd></div>
            <div className="flex justify-between gap-4"><dt>Domain age</dt><dd>{formatAge(tech.domain_age_days)}</dd></div>
            <div className="flex justify-between gap-4"><dt>Safe Browsing</dt><dd className="max-w-[60%] text-right">{formatSafeBrowsing(tech)}</dd></div>
          </dl>
          {tags.length ? (
            <div className="mt-4 flex flex-wrap gap-2">
              {tags.map((tag) => (
                <span key={tag} className="rounded-full bg-slate-800 px-2.5 py-1 text-xs text-slate-300">{tag}</span>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

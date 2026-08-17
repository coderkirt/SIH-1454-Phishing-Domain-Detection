import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import RiskBadge from "../components/RiskBadge";
import EmptyState from "../components/EmptyState";
import PageHeader from "../components/PageHeader";
import TechnicalPanel, { TechnicalRow } from "../components/TechnicalPanel";
import { loadLastScan, recommendationFor, riskColor } from "../utils/risk";

function formatExists(value) {
  if (value === true) return "Registered";
  if (value === false) return "Not registered";
  return "Unknown";
}

function formatAge(days) {
  if (days === null || days === undefined) return "Unknown";
  if (days < 1) return "Registered today";
  const years = Math.floor(days / 365);
  if (years >= 2) return `${days.toLocaleString()} days`;
  if (years === 1) return `${days.toLocaleString()} days`;
  return `${days} days`;
}

function formatSafeBrowsing(tech) {
  if (tech.safe_browsing_label) return tech.safe_browsing_label;
  const value = tech.google_safe_browsing;
  if (Array.isArray(value)) return value.join(", ");
  if (value === "clean") return "Clean";
  if (value === "skipped") return "Skipped";
  if (value === "unavailable") return "Unavailable";
  return "Unknown";
}

function buildTechnicalRows(url, tech) {
  return [
    { label: "Target URL", value: url || "Unknown" },
    { label: "Domain", value: tech.domain || "Unknown" },
    { label: "Domain exists", value: formatExists(tech.domain_exists) },
    { label: "HTTPS", value: tech.https ? "Yes" : "No" },
    { label: "Suspicious TLD", value: tech.suspicious_tld ? "Yes" : "No" },
    { label: "Brand impersonated", value: tech.brand_impersonated || "None" },
    { label: "Domain age", value: formatAge(tech.domain_age_days) },
    { label: "Safe browsing", value: formatSafeBrowsing(tech) },
  ];
}

function buildEvidence(tech, reasons, tags) {
  const rows = [];

  rows.push({
    name: "URL analysis",
    status: reasons.length ? "Detected" : "Clean",
    detail: reasons.length ? `${reasons.length} signal(s)` : "No suspicious signals",
    critical: reasons.length > 0,
  });

  rows.push({
    name: "Domain intelligence",
    status: tech.domain_exists === false ? "Detected" : tech.domain_exists === true ? "Clean" : "Unknown",
    detail: formatExists(tech.domain_exists),
    critical: tech.domain_exists === false,
  });

  rows.push({
    name: "SSL / TLS",
    status: tech.https ? "Clean" : "Review",
    detail: tech.https ? "HTTPS enabled" : "No HTTPS",
    critical: !tech.https,
  });

  rows.push({
    name: "Threat intelligence",
    status: Array.isArray(tech.google_safe_browsing) ? "Detected" : tech.google_safe_browsing === "clean" ? "Clean" : "Unknown",
    detail: formatSafeBrowsing(tech),
    critical: Array.isArray(tech.google_safe_browsing),
  });

  rows.push({
    name: "Brand matching",
    status: tech.brand_impersonated ? "Detected" : "Clean",
    detail: tech.brand_impersonated || "None",
    critical: Boolean(tech.brand_impersonated),
  });

  if (tech.suspicious_tld) {
    rows.push({
      name: "Infrastructure",
      status: "Detected",
      detail: "Suspicious TLD",
      critical: true,
    });
  }

  if (tags.length) {
    rows.push({
      name: "Threat tags",
      status: "Detected",
      detail: tags.join(", "),
      critical: true,
    });
  }

  return rows;
}

export default function ScanResult() {
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    setResult(loadLastScan());
  }, []);

  if (!result) {
    return (
      <div className="mx-auto max-w-3xl space-y-6">
        <PageHeader section="03 / Reports" title="Security report" subtitle="No analysis available." />
        <EmptyState
          title="No data available"
          body="Analyze a URL first to view the security report."
          action={<Link to="/scanner" className="btn-primary px-5 py-3">Analyze URL</Link>}
        />
      </div>
    );
  }

  const score = result.risk_score ?? 0;
  const color = riskColor(result.risk_level);
  const warning = result.simple_view?.warning || result.simple_view?.warning_english;
  const reasons = result.reasons || [];
  const tags = result.threat_tags || [];
  const tech = result.technical_view || {};
  const technicalRows = buildTechnicalRows(result.url, tech);
  const evidence = buildEvidence(tech, reasons, tags);

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <PageHeader
        section="03 / Reports"
        title="Security report"
        subtitle={result.url}
        meta
        actions={
          <button onClick={() => navigate("/scanner")} className="btn-secondary px-4 py-2.5 text-xs">
            Analyze another URL
          </button>
        }
      />

      <section className="grid gap-6 xl:grid-cols-[280px_1fr_320px]">
        <TechnicalPanel title="Risk score" accent>
          <div className="flex items-end gap-2">
            <span className="font-display text-7xl font-semibold leading-none text-ink">{score}</span>
            <span className="pb-2 font-mono text-sm text-muted">/100</span>
          </div>
          <div className="mt-5">
            <RiskBadge level={result.risk_level} />
          </div>
          <p className="mt-4 text-sm text-muted">{result.simple_view?.verdict}</p>
        </TechnicalPanel>

        <TechnicalPanel title="Classification" accent>
          <div className="flex flex-wrap items-center gap-3">
            <span className={`status-pill ${result.safe ? "risk-low" : "risk-high"}`}>
              <span className={`dot ${result.safe ? "dot-active" : "dot-critical"}`} aria-hidden="true" />
              {result.safe ? "Controlled" : "Unsafe"}
            </span>
            <span className="status-pill risk-unknown">{result.risk_level || "UNKNOWN"}</span>
          </div>
          <div className="mt-6 rule pt-6">
            <p className="label-tech">Recommendation</p>
            <p className="mt-3 text-sm leading-6 text-ink-soft">{recommendationFor(result.risk_level, warning)}</p>
          </div>
        </TechnicalPanel>

        <TechnicalPanel title="System metadata">
          <dl className="space-y-3 meta-tech">
            <div className="flex justify-between gap-3 border-b border-line pb-3">
              <dt>Target</dt>
              <dd className="text-right text-ink-soft break-all">{tech.domain || "Unknown"}</dd>
            </div>
            <div className="flex justify-between gap-3 border-b border-line pb-3">
              <dt>Protocol</dt>
              <dd>{tech.https ? "HTTPS" : "HTTP"}</dd>
            </div>
            <div className="flex justify-between gap-3">
              <dt>Threat tags</dt>
              <dd className="text-right">{tags.length ? tags.length : "0"}</dd>
            </div>
          </dl>
        </TechnicalPanel>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <TechnicalPanel title="Analysis evidence" accent>
          <div className="grid gap-px border border-line bg-line sm:grid-cols-2">
            {evidence.map((item, index) => (
              <div key={item.name} className="bg-surface p-4">
                <p className="font-mono text-xs text-muted">{String(index + 1).padStart(2, "0")}</p>
                <p className="mt-2 label-tech">{item.name}</p>
                <p className="mt-3 flex items-center gap-2 text-sm">
                  <span className={`dot ${item.critical ? "dot-critical" : "dot-active"}`} aria-hidden="true" />
                  <span className={item.critical ? "text-[var(--risk-high)]" : "text-[var(--status-safe)]"}>{item.status}</span>
                </p>
                <p className="mt-2 text-xs text-muted">{item.detail}</p>
              </div>
            ))}
          </div>
          {reasons.length ? (
            <div className="mt-6 rule pt-6">
              <p className="label-tech">Detection reasons</p>
              <ul className="mt-3 space-y-2">
                {reasons.map((reason) => (
                  <li key={reason} className="flex items-start gap-2 text-sm text-ink-soft">
                    <span className={`dot mt-1.5 ${color.dot}`} aria-hidden="true" />
                    {reason}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </TechnicalPanel>

        <TechnicalPanel title="Technical data">
          <dl>
            {technicalRows.map((row, index) => (
              <TechnicalRow key={row.label} index={index + 1} label={row.label} value={row.value} />
            ))}
          </dl>
        </TechnicalPanel>
      </section>
    </div>
  );
}

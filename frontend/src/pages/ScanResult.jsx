import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import RiskBadge from "../components/RiskBadge";
import EmptyState from "../components/EmptyState";
import PageHeader from "../components/PageHeader";
import TechnicalPanel, { TechnicalRow } from "../components/TechnicalPanel";
import FlagActions from "../components/FlagActions";
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
    { label: "TLS certificate", value: tech.tls_label || "Not checked" },
    { label: "TLS issuer", value: tech.tls_issuer || "Unknown" },
    { label: "TLS expires", value: tech.tls_valid_to || "Unknown" },
    { label: "TLS hostname match", value: tech.tls_hostname_ok === true ? "Yes" : tech.tls_hostname_ok === false ? "No" : "Unknown" },
    { label: "Suspicious TLD", value: tech.suspicious_tld ? "Yes" : "No" },
    { label: "Brand impersonated", value: tech.brand_impersonated || "None" },
    { label: "Domain age", value: formatAge(tech.domain_age_days) },
    { label: "Safe browsing", value: formatSafeBrowsing(tech) },
  ];
}

function buildEvidence(tech, reasons, tags) {
  const hops = Number(tech.redirect_hops) || 0;
  const psychTags = (tags || []).filter((tag) =>
    /urgenc|fear|credential|otp|greed|secret|emotion|authorit|countdown|prize|lottery|pressure/i.test(tag)
  );
  const infraBits = [];
  if (tech.suspicious_tld) infraBits.push("Suspicious TLD");
  if (tech.shortened) infraBits.push("Shortened URL");
  if (hops > 1) infraBits.push(`${hops} redirect hops`);
  const manipulation = [...psychTags.slice(0, 3), ...infraBits];

  return [
    {
      name: "URL analysis",
      status: reasons.length ? "Detected" : "Clean",
      detail: reasons.length ? `${reasons.length} signal(s) in the URL and page path` : "No suspicious URL or path signals",
      critical: reasons.length > 0,
    },
    {
      name: "Domain intelligence",
      status: tech.domain_exists === false ? "Detected" : tech.domain_exists === true ? "Clean" : "Unknown",
      detail: `${formatExists(tech.domain_exists)} · ${formatAge(tech.domain_age_days)}`,
      critical: tech.domain_exists === false,
    },
    {
      name: "SSL / TLS",
      status: ["hostname_mismatch", "expired", "self_signed", "untrusted", "http"].includes(tech.tls_status)
        ? "Detected"
        : tech.https && tech.tls_status === "ok"
          ? "Clean"
          : "Review",
      detail: tech.tls_label || (tech.https ? "HTTPS enabled" : "No HTTPS"),
      critical: ["hostname_mismatch", "expired", "self_signed", "untrusted", "http"].includes(tech.tls_status) || !tech.https,
    },
    {
      name: "Threat intelligence",
      status: Array.isArray(tech.google_safe_browsing) ? "Detected" : tech.google_safe_browsing === "clean" ? "Clean" : "Unknown",
      detail: formatSafeBrowsing(tech),
      critical: Array.isArray(tech.google_safe_browsing),
    },
    {
      name: "Brand matching",
      status: tech.brand_impersonated ? "Detected" : "Clean",
      detail: tech.brand_impersonated ? `Looks like ${tech.brand_impersonated}` : "No bank or brand impersonation",
      critical: Boolean(tech.brand_impersonated),
    },
    {
      name: "Manipulation & redirects",
      status: manipulation.length ? "Detected" : "Clean",
      detail: manipulation.length
        ? manipulation.join(" · ")
        : "No urgency language, odd TLD, or shortener",
      critical: manipulation.length > 0,
    },
  ];
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
  const targetUrl = result.url || result.links?.[0]?.url || tech.url || "";
  const technicalRows = buildTechnicalRows(targetUrl, tech);
  const evidence = buildEvidence(tech, reasons, tags);

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <PageHeader
        section="03 / Reports"
        title="Security report"
        subtitle={targetUrl || result.source_type || "Screenshot / QR scan"}
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
            <div className="flex justify-between gap-3 border-b border-line pb-3">
              <dt>TLS issuer</dt>
              <dd className="text-right text-ink-soft break-all">{tech.tls_issuer || "Unknown"}</dd>
            </div>
            <div className="flex justify-between gap-3">
              <dt>Threat tags</dt>
              <dd className="text-right">{tags.length ? tags.length : "0"}</dd>
            </div>
          </dl>
        </TechnicalPanel>
      </section>

      {targetUrl || result.links?.[0]?.url ? (
        <TechnicalPanel title="Flag this target">
          <p className="text-sm text-muted">
            Community flags are one extra signal. They do not change this score by themselves and are not legal proof.
          </p>
          <FlagActions url={targetUrl || result.links?.[0]?.url} heading="" />
        </TechnicalPanel>
      ) : null}

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

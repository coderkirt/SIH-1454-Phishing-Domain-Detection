import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import RiskBadge from "../components/RiskBadge";
import EmptyState from "../components/EmptyState";
import PageHeader from "../components/PageHeader";
import TechnicalPanel, { TechnicalRow } from "../components/TechnicalPanel";
import FlagActions from "../components/FlagActions";
import RagPopup from "../components/RagPopup";
import { consumeRagPopupPending, loadLastScan, recommendationFor, riskColor } from "../utils/risk";

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
  if (value === "flagged") return "Confirmed malicious";
  if (value === "no_match") return "No match (not a safety guarantee)";
  if (value === "partial") return "Partial — some feeds unavailable";
  if (value === "clean") return "No match (legacy label)";
  if (value === "skipped") return "Skipped";
  if (value === "unavailable") return "Threat intelligence unavailable";
  return "Unknown";
}

function intelTile(tech) {
  const overall = tech.threat_intelligence?.overall_status || tech.google_safe_browsing;
  if (overall === "confirmed_malicious" || overall === "flagged" || Array.isArray(tech.google_safe_browsing)) {
    return { status: "Confirmed", critical: true, detail: formatSafeBrowsing(tech) };
  }
  if (overall === "reported_malicious") {
    return { status: "Reported", critical: true, detail: "Unverified threat-intelligence report — not safe to treat as clean" };
  }
  if (overall === "unavailable") {
    return { status: "Unavailable", critical: false, detail: "Threat intelligence unavailable — unknown is not safe" };
  }
  if (overall === "partial") {
    return { status: "Partial", critical: false, detail: formatSafeBrowsing(tech) };
  }
  if (overall === "no_match") {
    return { status: "No match", critical: false, detail: "No match in queried feeds. That does not confirm the site is legitimate." };
  }
  return { status: "Unknown", critical: false, detail: formatSafeBrowsing(tech) };
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
    { label: "Normalized URL", value: tech.debug?.normalized_url || tech.original_url || "Unknown" },
    { label: "Classification", value: tech.classification || "Unknown" },
    { label: "RAG rule", value: formatRag(tech.rag || tech.evidence?.rag) },
    { label: "PhishEye opens (30d)", value: formatOpens(tech.local_activity || tech.evidence?.local_activity) },
    { label: "This browser (30d)", value: formatBrowserOpens(tech.local_activity || tech.evidence?.local_activity) },
    { label: "30-day activity", value: formatActivity(tech.local_activity || tech.evidence?.local_activity) },
  ];
}

function formatRag(rag) {
  if (!rag || rag.status === "unavailable") return "Unavailable (weight omitted)";
  if (rag.rule_id) return `${rag.rule_id} · suspicion ${rag.suspicion_score ?? "—"}`;
  if (rag.status === "ok") return `Evaluated · suspicion ${rag.suspicion_score ?? 0}`;
  return rag.status || "Unknown";
}

function formatOpens(activity) {
  if (!activity) return "Unknown";
  if (!(activity.opens || activity.users_opened || activity.scans) && activity.status === "unknown") {
    return "Unknown — no PhishEye users opened this address in 30 days";
  }
  const used = activity.used ? ` · used in score · suspicion ${activity.suspicion_score ?? 0}` : "";
  return `${activity.opens ?? 0} opens · ${activity.users_opened ?? 0} users · ${activity.scans ?? 0} scans${used}`;
}

function formatBrowserOpens(activity) {
  const opens = Number(activity?.this_browser_opens) || 0;
  if (opens > 0 || activity?.this_browser_status === "observed") {
    const used = activity.this_browser_used || activity.used
      ? ` · used in score · suspicion ${activity.suspicion_score ?? 0}`
      : "";
    return `${opens} open${opens === 1 ? "" : "s"} in this browser in 30 days${used}`;
  }
  if (!activity || activity.this_browser_status === "unavailable") {
    return "Unknown — this browser has not recorded an open yet";
  }
  return "Unknown — this browser has no opens in 30 days";
}

function formatActivity(activity) {
  if (!activity) return "Unknown";
  if (activity.status === "unknown") return "Unknown — no scans, opens, or reports in 30 days";
  const used = activity.used ? `Used in score · suspicion ${activity.suspicion_score ?? 0}` : "Recorded";
  return [
    used,
    `${activity.opens ?? 0} PhishEye opens`,
    `${activity.users_opened ?? 0} users`,
    `${activity.scans ?? 0} scans`,
    `${activity.signed_in_users ?? 0} signed-in users`,
    `${activity.high_risk_scans ?? 0} high-risk`,
    `${activity.scam_reports ?? 0} scam reports`,
    `${activity.risky_reports ?? 0} risky reports`,
    `${activity.safe_reports ?? 0} safe reports`,
  ].join(" · ");
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
  const intel = intelTile(tech);

  return [
    {
      name: "URL analysis",
      status: reasons.length ? "Detected" : "No indicators",
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
      status: intel.status,
      detail: intel.detail,
      critical: intel.critical,
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
    {
      name: "Knowledge-base (RAG)",
      status: ragTile(tech.rag || tech.evidence?.rag).status,
      detail: ragTile(tech.rag || tech.evidence?.rag).detail,
      critical: ragTile(tech.rag || tech.evidence?.rag).critical,
    },
    {
      name: "PhishEye 30-day history",
      status: activityTile(tech.local_activity || tech.evidence?.local_activity).status,
      detail: activityTile(tech.local_activity || tech.evidence?.local_activity).detail,
      critical: activityTile(tech.local_activity || tech.evidence?.local_activity).critical,
    },
    {
      name: "This browser (30d)",
      status: browserTile(tech.local_activity || tech.evidence?.local_activity).status,
      detail: browserTile(tech.local_activity || tech.evidence?.local_activity).detail,
      critical: false,
    },
  ];
}

function ragTile(rag) {
  if (!rag || rag.status === "unavailable") {
    return { status: "Unavailable", critical: false, detail: "RAG weight omitted — unavailable is not treated as zero." };
  }
  if (rag.status === "ok") {
    return {
      status: rag.used ? "Raised suspicion" : "Evaluated",
      critical: Boolean(rag.used),
      detail: rag.rule_summary || rag.rule_id || "Knowledge-base checked this URL.",
    };
  }
  return { status: rag.status || "Unknown", critical: false, detail: rag.rule_summary || "Knowledge-base response was incomplete." };
}

function browserTile(activity) {
  const opens = Number(activity?.this_browser_opens) || 0;
  const observed = opens > 0 || activity?.this_browser_status === "observed";
  return {
    status: activity?.this_browser_used || (observed && activity?.used)
      ? "Used in score"
      : observed
        ? "Observed"
        : "Unknown",
    critical: false,
    detail: formatBrowserOpens(activity),
  };
}

function activityTile(activity) {
  if (!activity || activity.status === "unknown") {
    return { status: "Unknown", critical: false, detail: "No PhishEye opens, scans, or reports in 30 days. Unknown is not safe." };
  }
  const scam = Number(activity.scam_reports) || 0;
  const risky = Number(activity.risky_reports) || 0;
  return {
    status: activity.used ? "Used in score" : scam + risky ? "Reported" : "Observed",
    critical: scam + risky > 0,
    detail: formatActivity(activity),
  };
}

const BANDS = [
  { name: "Low", until: 29 },
  { name: "Medium", until: 49 },
  { name: "High", until: 69 },
  { name: "Critical", until: 100 },
];

function readingFor(level) {
  switch ((level || "").toUpperCase()) {
    case "CRITICAL":
    case "HIGH":
      return {
        meaning: "This page is not safe to open.",
        next: "Do not type a password, OTP, or card number. Close it and open the real site yourself.",
      };
    case "MEDIUM":
      return {
        meaning: "A few things on this page look off.",
        next: "Read the address before you sign in or pay.",
      };
    default:
      return {
        meaning: "Nothing here looks like a scam.",
        next: "You can open it. Still check the address before you sign in.",
      };
  }
}

function ScoreBoard({ score, level, verdict, color, tech }) {
  const reading = readingFor(level);
  const mark = Math.min(100, Math.max(0, Number(score) || 0));
  const https = tech.https ? "Uses HTTPS" : "Not using HTTPS";
  const domain = tech.domain_exists === false ? "Domain is not registered" : tech.domain_exists === true ? "Domain is registered" : "Domain status unknown";
  const intel = intelTile(tech);
  return (
    <section className={`panel panel-accent ${color.border}`}>
      <div className="border-b border-line px-5 py-3">
        <p className="label-tech">Risk score</p>
      </div>
      <div className="grid items-center gap-8 p-5 lg:grid-cols-[200px_1fr_280px]">
        <div>
          <div className="flex items-end gap-2">
            <span className={`font-display text-7xl font-semibold leading-none ${color.text}`}>{score}</span>
            <span className="pb-2 font-mono text-sm text-muted">/100</span>
          </div>
          <div className="mt-4 flex flex-wrap items-center gap-2">
            <RiskBadge level={level} />
          </div>
          {verdict ? <p className="mt-3 text-sm text-muted">{verdict}</p> : null}
          {tech.final_url && tech.original_url && tech.final_url.replace(/\/$/, "") !== tech.original_url.replace(/\/$/, "") ? (
            <p className="mt-3 break-all text-sm text-ink-soft">Opens {tech.final_url}</p>
          ) : null}
        </div>

        <div>
          <p className="label-tech">Where this score sits</p>
          <div className="relative mt-4 h-2 bg-line">
            <div className="absolute inset-y-0 left-0 bg-[var(--accent)]" style={{ width: `${mark}%` }} />
            <span
              className="absolute top-1/2 h-4 w-px -translate-y-1/2 bg-ink"
              style={{ left: `calc(${mark}% - 1px)` }}
              aria-hidden="true"
            />
          </div>
          <div className="mt-2 grid grid-cols-4 font-mono text-[10px] uppercase tracking-[0.12em] text-muted">
            {BANDS.map((band) => (
              <span key={band.name}>{band.name}</span>
            ))}
          </div>
          <p className="mt-4 text-sm leading-6 text-ink">{reading.meaning}</p>
          <p className="mt-1 text-sm leading-6 text-ink-soft">{reading.next}</p>
        </div>

        <div className="border-t border-line pt-4 lg:border-l lg:border-t-0 lg:pl-6 lg:pt-0">
          <p className="label-tech">What we checked</p>
          <ul className="mt-3 space-y-2 text-sm text-ink-soft">
            <li>{https}</li>
            <li>{domain}</li>
            <li>Threat feeds: {intel.status}</li>
          </ul>
        </div>
      </div>
    </section>
  );
}

export default function ScanResult() {
  const [result, setResult] = useState(null);
  const [ragOpen, setRagOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const load = () => {
      const data = loadLastScan();
      setResult(data);
      if (data && consumeRagPopupPending()) setRagOpen(true);
    };
    load();
    window.addEventListener("phisheye-report", load);
    return () => window.removeEventListener("phisheye-report", load);
  }, []);

  if (!result) {
    return (
      <div className="mx-auto max-w-3xl space-y-6">
        <PageHeader section="03 / Last result" title="Security report" subtitle="No analysis available." />
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
  const explanationText =
    typeof result.explanation === "string"
      ? result.explanation
      : result.explanation?.what || result.explanation?.headline || "";
  const reasons = result.reasons || [];
  const tags = result.threat_tags || [];
  const tech = result.technical_view || {};
  const qrPayloads = result.qr_payloads || [];
  const qrUrls = result.qr_urls || [];
  const qrCodes = (result.qr_codes && result.qr_codes.length)
    ? result.qr_codes
    : qrPayloads.map((payload) => ({ payload, type: "Text", urls: [], details: [] }));
  const targetUrl = result.url || qrUrls[0] || result.links?.[0]?.url || tech.url || "";
  const technicalRows = buildTechnicalRows(targetUrl, tech);
  const evidence = buildEvidence(tech, reasons, tags);

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <RagPopup result={result} open={ragOpen} onClose={() => setRagOpen(false)} />
      <PageHeader
        section="03 / Last result"
        title="Security report"
        subtitle={targetUrl || result.source_type || "Screenshot / QR scan"}
        meta
        actions={
          <div className="flex flex-wrap gap-2">
            {["HIGH", "CRITICAL"].includes(String(result.risk_level || "").toUpperCase()) ? null : (
              <button
                type="button"
                onClick={() => {
                  const open = targetUrl;
                  if (window.PhishEyeNative?.openCheckedUrl) window.PhishEyeNative.openCheckedUrl(open);
                  else window.open(open, "_blank", "noopener,noreferrer");
                }}
                className="btn-secondary px-4 py-2.5 text-xs"
              >
                Open website
              </button>
            )}
            <button onClick={() => navigate("/scanner")} className="btn-secondary px-4 py-2.5 text-xs">
              Analyze another URL
            </button>
          </div>
        }
      />

      <ScoreBoard
        score={score}
        level={result.risk_level}
        verdict={result.simple_view?.verdict}
        color={color}
        tech={tech}
      />

      <section className="grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">
        <TechnicalPanel title="Classification" accent>
          <div className="flex h-full flex-col justify-between gap-6">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <span className={`status-pill ${result.safe ? "risk-low" : "risk-high"}`}>
                  <span className={`dot ${result.safe ? "dot-active" : "dot-critical"}`} aria-hidden="true" />
                  {result.classification === "CONFIRMED_MALICIOUS"
                    ? "Confirmed malicious"
                    : result.classification === "SUSPICIOUS"
                      ? "Suspicious"
                      : result.safe
                        ? "No malicious indicators"
                        : "Unsafe"}
                </span>
                <span className="status-pill risk-unknown">{result.risk_level || "UNKNOWN"}</span>
              </div>
              {explanationText ? (
                <p className="mt-4 text-sm leading-6 text-ink-soft">{explanationText}</p>
              ) : null}
            </div>
            <div className="rule pt-6">
              <p className="label-tech">Recommendation</p>
              <p className="mt-3 text-sm leading-6 text-ink-soft">{recommendationFor(result.risk_level, warning)}</p>
            </div>
          </div>
        </TechnicalPanel>

        <TechnicalPanel title="System metadata">
          <dl className="flex h-full flex-col justify-between meta-tech">
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

      {result.source_type === "qr" || qrCodes.length || qrUrls.length ? (
        <TechnicalPanel title={qrCodes.length > 1 ? `Decoded from QR (${qrCodes.length})` : "Decoded from QR"} accent>
          {qrCodes.length ? qrCodes.map((code, index) => (
            <div key={`${code.payload}-${index}`} className={index ? "mt-5 border-t border-line pt-5" : ""}>
              <p className="label-tech">{code.type || "Payload"}{qrCodes.length > 1 ? ` ${index + 1}` : ""}</p>
              <p className="mt-2 break-all font-mono text-sm text-ink">{code.payload || "No text payload"}</p>
              {(code.details || []).length ? (
                <dl className="mt-3 space-y-2">
                  {code.details.map((item) => (
                    <div key={`${item.label}-${item.value}`} className="flex justify-between gap-3 text-sm">
                      <dt className="text-muted">{item.label}</dt>
                      <dd className="break-all text-right font-mono text-ink">{item.value}</dd>
                    </div>
                  ))}
                </dl>
              ) : null}
              {(code.urls || []).length ? (
                <ul className="mt-3 space-y-2">
                  {code.urls.map((url) => (
                    <li key={url} className="break-all font-mono text-sm text-accent">{url}</li>
                  ))}
                </ul>
              ) : (
                <p className="mt-3 text-sm text-muted">This code has no website link. The payload above is what was encoded.</p>
              )}
            </div>
          )) : (
            <p className="text-sm text-muted">No QR code was decoded from this image.</p>
          )}
        </TechnicalPanel>
      ) : null}

      {(result.links || []).length ? (
        <TechnicalPanel title="Scored links">
          <ul className="space-y-3">
            {result.links.map((link) => (
              <li key={link.url} className="border-b border-line pb-3 last:border-0 last:pb-0">
                <p className="break-all font-mono text-sm text-accent">{link.url}</p>
                <p className="mt-1 text-xs text-muted">{link.classification} · {link.risk_score}/100</p>
              </li>
            ))}
          </ul>
        </TechnicalPanel>
      ) : null}

      {targetUrl || result.links?.[0]?.url ? (
        <TechnicalPanel title="Flag this target">
          <p className="text-sm text-muted">
            Community flags are one extra signal. They do not change this score by themselves and are not legal proof.
          </p>
          <FlagActions url={targetUrl || result.links?.[0]?.url} heading="" />
        </TechnicalPanel>
      ) : null}

      {result.explanation?.rag_grounded ? (
        <section className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {!result.explanation?.matched_playbook && result.explanation?.what ? (
            <TechnicalPanel title="Knowledge-base evaluation" accent>
              <p className="text-sm leading-relaxed text-ink-soft">{result.explanation.what}</p>
              {(result.explanation.why || []).length ? (
                <ul className="mt-3 space-y-1.5 text-xs text-muted">
                  {result.explanation.why.slice(0, 3).map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              ) : null}
            </TechnicalPanel>
          ) : null}

          {result.explanation?.matched_playbook ? (
            <TechnicalPanel title="Matched Attack Playbook" accent>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="status-pill risk-high">
                    {result.explanation.matched_playbook.playbook_id?.replace("playbook-", "").toUpperCase() || "PLAYBOOK"}
                  </span>
                </div>
                <p className="font-display text-base font-semibold text-ink">
                  {result.explanation.matched_playbook.title}
                </p>
                <p className="text-xs leading-relaxed text-muted">
                  {result.explanation.matched_playbook.mechanism}
                </p>
                {(result.explanation.matched_playbook.warning_signs || []).length ? (
                  <div className="mt-3 border-t border-line pt-3">
                    <p className="label-tech text-[10px]">Analyst Warning Signs</p>
                    <ul className="mt-2 space-y-1.5 text-xs text-ink-soft">
                      {result.explanation.matched_playbook.warning_signs.slice(0, 3).map((sign, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="dot dot-critical mt-1" aria-hidden="true" />
                          <span>{sign}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
              </div>
            </TechnicalPanel>
          ) : null}

          {result.explanation?.brand_analysis ? (
            <TechnicalPanel title="Brand Security & Allowlists" accent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="label-tech text-[10px]">Target Brand</span>
                  <span className="font-mono text-xs font-bold text-accent uppercase">
                    {result.explanation.brand_analysis.impersonated_brand}
                  </span>
                </div>
                <div>
                  <p className="label-tech text-[10px]">Official Verified Domains</p>
                  <div className="mt-1.5 flex flex-wrap gap-1.5">
                    {(result.explanation.brand_analysis.official_domains || []).slice(0, 4).map((dom) => (
                      <span key={dom} className="rounded bg-surface px-2 py-0.5 font-mono text-[11px] text-ink border border-line">
                        {dom}
                      </span>
                    ))}
                  </div>
                </div>
                {(result.explanation.brand_analysis.never_does_rules || []).length ? (
                  <div className="border-t border-line pt-3">
                    <p className="label-tech text-[10px] text-risk-high">Official Brand Security Rules</p>
                    <ul className="mt-2 space-y-1 text-xs text-muted">
                      {result.explanation.brand_analysis.never_does_rules.slice(0, 3).map((rule, idx) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <span className="text-risk-high">✕</span>
                          <span>{rule}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
              </div>
            </TechnicalPanel>
          ) : null}

          {(result.explanation?.citations || []).length ? (
            <TechnicalPanel title="Authoritative Citations" accent>
              <div className="space-y-3">
                <p className="label-tech text-[10px]">Attributed Cybersecurity Sources</p>
                <ul className="space-y-2.5">
                  {result.explanation.citations.map((cite, idx) => (
                    <li key={idx} className="border-b border-line pb-2.5 last:border-0 last:pb-0">
                      <div className="flex items-center justify-between">
                        <span className="rounded bg-accent/10 px-1.5 py-0.5 font-mono text-[10px] text-accent font-semibold">
                          [cite-{idx + 1}]
                        </span>
                        <span className="text-[10px] font-mono text-muted">{cite.source}</span>
                      </div>
                      <p className="mt-1 text-xs font-medium text-ink">{cite.title}</p>
                      {cite.source_url ? (
                        <a
                          href={cite.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-1 block truncate text-[11px] text-accent hover:underline"
                        >
                          {cite.source_url}
                        </a>
                      ) : null}
                    </li>
                  ))}
                </ul>
              </div>
            </TechnicalPanel>
          ) : null}
        </section>
      ) : null}

      <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <TechnicalPanel title="Analysis evidence" accent collapsible hint={`${evidence.length} signals · click to open`}>
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

        <TechnicalPanel title="Technical data" collapsible hint={`${technicalRows.length} fields · click to open`}>
          <dl>
            {technicalRows.map((row, index) => (
              <TechnicalRow key={row.label} index={index + 1} label={row.label} value={row.value} />
            ))}
          </dl>
        </TechnicalPanel>
      </section>

      {(tech.threat_intelligence?.providers || []).length ? (
        <TechnicalPanel title="Threat-intelligence providers">
          <ul className="space-y-3">
            {tech.threat_intelligence.providers.map((row) => (
              <li key={row.provider} className="flex items-start justify-between gap-4 border-b border-line pb-3 last:border-0 last:pb-0">
                <div>
                  <p className="label-tech">{row.provider}</p>
                  <p className="mt-1 text-sm text-ink-soft">{row.detail || row.status}</p>
                </div>
                <span className={`status-pill ${row.status === "confirmed_malicious" || row.status === "reported_malicious" ? "risk-high" : "risk-unknown"}`}>
                  {row.status === "confirmed_malicious"
                    ? `Match · ${row.match_type}`
                    : row.status === "reported_malicious"
                      ? `Reported · ${row.match_type}`
                      : row.status === "no_match"
                        ? "No match"
                        : "Unavailable"}
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-xs text-muted">
            No match is not the same as confirmed legitimate. Unavailable is not the same as safe.
          </p>
        </TechnicalPanel>
      ) : null}

      {tech.debug?.normalized_url ? (
        <TechnicalPanel title="Debug">
          <dl>
            {[
              ["Original URL", tech.debug.original_url],
              ["Normalized URL", tech.debug.normalized_url],
              ["Hostname", tech.debug.hostname],
              ["Registered domain", tech.debug.registered_domain],
              ["PhishTank", tech.debug.phishtank],
              ["OpenPhish", tech.debug.openphish],
              ["URLhaus", tech.debug.urlhaus],
              ["Phishing Army", tech.debug.phishing_army],
              ["Google Safe Browsing", tech.debug.google_safe_browsing],
              ["ML / lexical score", `${Math.round((tech.debug.ml_probability || 0) * 100)} / 100 (not a trained model)`],
              ["Heuristic score", tech.debug.heuristic_score],
              ["Final risk", tech.debug.final_risk_score],
              ["Final classification", tech.debug.final_classification],
              ["Why", tech.debug.reason_for_classification],
            ].map(([label, value], index) => (
              <TechnicalRow key={label} index={index + 1} label={label} value={value ?? "—"} />
            ))}
          </dl>
        </TechnicalPanel>
      ) : null}
    </div>
  );
}

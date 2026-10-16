import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import PageHeader from "../components/PageHeader";
import RiskBadge from "../components/RiskBadge";
import { checkUrl, getErrorMessage } from "../services/api";
import { extractHttpUrl } from "../utils/incomingUrl";
import { saveLastScan } from "../utils/risk";

function openInSystemBrowser(url) {
  if (window.Capacitor?.isNativePlatform?.()) {
    window.open(url, "_system");
    return;
  }
  window.open(url, "_blank", "noopener,noreferrer");
}

export default function IncomingScan() {
  const [params] = useSearchParams();
  const raw = params.get("url") || "";
  const url = extractHttpUrl(raw);
  const [loading, setLoading] = useState(Boolean(url));
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (!url) {
      setLoading(false);
      setError("No website address was found in that share.");
      return undefined;
    }
    let cancelled = false;
    setLoading(true);
    setError("");
    setResult(null);
    checkUrl(url)
      .then(({ data }) => {
        if (cancelled) return;
        saveLastScan(data);
        setResult(data);
        const level = String(data.risk_level || "").toUpperCase();
        if (level === "LOW" && data.safe) {
          openInSystemBrowser(data.final_url || data.url || url);
        }
      })
      .catch((err) => {
        if (!cancelled) setError(getErrorMessage(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [url]);

  const level = String(result?.risk_level || "").toUpperCase();
  const blocked = level === "HIGH" || level === "CRITICAL";
  const opened = result?.final_url && result.final_url !== result.url ? result.final_url : result?.url || url;

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <PageHeader
        section="Link check"
        title="This link was opened on your phone"
        subtitle="Chrome on Android cannot run the desktop extension. Share a link to PhishEye, or open the link with PhishEye, and it is checked before the site loads."
      />

      {loading ? <p className="text-sm text-ink-soft">Checking the address…</p> : null}
      {error ? <p className="text-sm text-[var(--risk-high)]">{error}</p> : null}

      {result ? (
        <section className="panel space-y-4 p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <RiskBadge level={result.risk_level} />
            <p className="font-mono text-sm text-ink">{result.risk_score}/100</p>
          </div>
          <p className="break-all font-mono text-xs text-ink-soft">{opened}</p>
          <p className="text-sm leading-6 text-ink">
            {result.simple_view?.headline || result.simple_view?.summary || result.explanation?.headline || "Check complete."}
          </p>
          {blocked ? (
            <p className="text-sm leading-6 text-[var(--risk-high)]">
              This looks dangerous. Do not sign in or pay here. Keep it closed.
            </p>
          ) : null}
          <div className="flex flex-col gap-3">
            {blocked ? null : (
              <button type="button" className="btn-primary py-3" onClick={() => openInSystemBrowser(opened)}>
                Open website
              </button>
            )}
            <button type="button" className={blocked ? "btn-primary py-3" : "btn-secondary py-3"} onClick={() => window.history.back()}>
              Keep this site closed
            </button>
          </div>
        </section>
      ) : null}
    </div>
  );
}

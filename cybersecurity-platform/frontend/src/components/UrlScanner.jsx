import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { checkUrl, getErrorMessage } from "../services/api";
import { saveLastScan } from "../utils/risk";

export default function UrlScanner({ compact = false }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    const value = url.trim();
    if (!value) {
      setError("Please enter a website URL.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const { data } = await checkUrl(value);
      saveLastScan(data);
      navigate("/scan-result");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const ready = url.trim().length > 0 && !loading;

  return (
    <form onSubmit={onSubmit} className={compact ? "" : "w-full"}>
      <div className="panel p-4">
        <label htmlFor="target-url" className="label-tech">Target URL</label>
        <div className="mt-3 border border-line">
          <input
            id="target-url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            className="field field-mono w-full border-0 bg-transparent px-3 py-3 focus:shadow-none"
          />
        </div>
        <div className="mt-4 grid gap-3 border-t border-line pt-4 sm:grid-cols-2">
          <div>
            <p className="label-tech">Supported protocol</p>
            <p className="mt-1 font-mono text-sm text-ink-soft">HTTPS</p>
          </div>
          <div>
            <p className="label-tech">Analysis mode</p>
            <p className="mt-1 font-mono text-sm text-ink-soft">Rule / threat intelligence</p>
          </div>
        </div>
        <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
          <p className="flex items-center gap-2 text-xs uppercase tracking-[0.12em] text-muted">
            <span className={`dot ${loading ? "dot-critical scan-pulse" : ready ? "dot-active" : "dot-inactive"}`} aria-hidden="true" />
            {loading ? "Analyzing" : ready ? "Ready" : "Awaiting input"}
          </p>
          <button type="submit" disabled={loading} className="btn-primary px-5 py-2.5">
            {loading ? "Analyze" : "Analyze URL"}
          </button>
        </div>
      </div>
      {loading ? (
        <div className="mt-3 flex items-center gap-3">
          <span className="scan-dots scan-pulse" aria-hidden="true">
            <span className="dot dot-active" />
            <span className="dot dot-active" />
            <span className="dot dot-queued" />
            <span className="dot dot-inactive" />
            <span className="dot dot-inactive" />
          </span>
          <p className="label-tech">Analyzing domain</p>
        </div>
      ) : null}
      {error ? (
        <div className="mt-3 panel border border-[rgba(255,0,0,0.35)] p-3">
          <p className="flex items-center gap-2 text-sm text-[var(--risk-high)]">
            <span className="dot dot-critical" aria-hidden="true" />
            {error}
          </p>
        </div>
      ) : null}
    </form>
  );
}

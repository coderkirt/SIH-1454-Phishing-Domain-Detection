import { useState } from "react";
import { useNavigate } from "react-router-dom";
import UrlScanner from "../components/UrlScanner";
import ScreenshotUploader from "../components/ScreenshotUploader";
import PageHeader from "../components/PageHeader";
import RiskBadge from "../components/RiskBadge";
import FlagActions from "../components/FlagActions";
import { analyzeContent, getErrorMessage } from "../services/api";
import { saveLastScan } from "../utils/risk";

const TABS = [
  { id: "url", label: "URL" },
  { id: "text", label: "Message" },
  { id: "email", label: "Email" },
  { id: "whatsapp", label: "WhatsApp / SMS" },
  { id: "screenshot", label: "Screenshot" },
  { id: "qr", label: "QR" },
];

export default function Scanner() {
  const [tab, setTab] = useState("url");
  const [text, setText] = useState("");
  const [senderEmail, setSenderEmail] = useState("");
  const [senderName, setSenderName] = useState("");
  const [replyTo, setReplyTo] = useState("");
  const [warnLink, setWarnLink] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  const runText = async (sourceType) => {
    setError("");
    setLoading(true);
    try {
      const payload = { source_type: sourceType, text };
      if (sourceType === "email") {
        payload.sender = {
          email: senderEmail,
          display_name: senderName,
          reply_to: replyTo,
        };
      }
      const { data } = await analyzeContent(payload);
      saveLastScan(data);
      setResult(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const openSafely = (link) => {
    const level = (link.classification || "").toUpperCase();
    if (level === "HIGH" || level === "CRITICAL") {
      setWarnLink(link);
      return;
    }
    window.open(link.url, "_blank", "noopener,noreferrer");
  };

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <PageHeader
        section="02 / Scan"
        title="Analyze target"
        subtitle="URL, pasted message, email text, WhatsApp/SMS text, screenshot, or QR image."
      />

      <div className="flex flex-wrap gap-2">
        {TABS.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => {
              setTab(item.id);
              setResult(null);
              setError("");
            }}
            className={`px-4 py-2 text-xs uppercase tracking-[0.12em] ${
              tab === item.id ? "btn-primary" : "btn-secondary"
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      {tab === "url" ? <UrlScanner /> : null}

      {["text", "email", "whatsapp"].includes(tab) ? (
        <div className="panel space-y-4 p-4">
          <label className="label-tech">Message text</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={8}
            placeholder="Paste the full message, including every link..."
            className="field field-mono w-full px-3 py-3"
          />
          {tab === "email" ? (
            <div className="grid gap-3 sm:grid-cols-3">
              <input value={senderName} onChange={(e) => setSenderName(e.target.value)} placeholder="Display name" className="field px-3 py-2" />
              <input value={senderEmail} onChange={(e) => setSenderEmail(e.target.value)} placeholder="From email" className="field px-3 py-2" />
              <input value={replyTo} onChange={(e) => setReplyTo(e.target.value)} placeholder="Reply-To" className="field px-3 py-2" />
            </div>
          ) : null}
          {tab === "whatsapp" ? (
            <p className="text-xs text-muted">Paste visible WhatsApp or SMS text. Chrome cannot read phone SMS.</p>
          ) : null}
          <button
            type="button"
            disabled={loading}
            onClick={() => runText(tab === "whatsapp" ? "whatsapp" : tab)}
            className="btn-primary px-5 py-2.5"
          >
            {loading ? "Analyzing" : "Analyze message"}
          </button>
        </div>
      ) : null}

      {tab === "screenshot" ? <ScreenshotUploader /> : null}
      {tab === "qr" ? <ScreenshotUploader mode="qr" /> : null}

      {error ? (
        <div className="panel border border-[rgba(255,0,0,0.35)] p-3">
          <p className="text-sm text-risk-high">{error}</p>
        </div>
      ) : null}

      {result ? (
        <div className="space-y-4">
          <div className="panel p-5">
            <div className="flex flex-wrap items-center gap-3">
              <RiskBadge level={result.risk_level} />
              <span className="font-display text-2xl">{result.risk_score}/100</span>
            </div>
            <p className="mt-3 text-ink-soft">{result.explanation?.what || result.simple_view?.warning}</p>
            <p className="mt-2 text-sm text-muted">{result.explanation?.what_to_do}</p>
            <p className="mt-3 text-xs text-muted">
              Model confidence {result.model_confidence}% is signal agreement, not accuracy.
            </p>
            <button type="button" onClick={() => navigate("/scan-result")} className="btn-secondary mt-4 px-4 py-2 text-xs">
              Open full result
            </button>
          </div>
          {(result.links || []).map((link) => (
            <div key={link.url} className="panel space-y-2 p-5">
              <p className="break-all font-mono text-sm text-accent">{link.url}</p>
              <div className="flex flex-wrap items-center gap-2">
                <RiskBadge level={link.classification} />
                <span className="font-mono text-sm">{link.risk_score}/100</span>
              </div>
              <p className="text-sm text-muted">{(link.reasons || [])[0]}</p>
              <FlagActions url={link.url} compact onOpen={() => openSafely(link)} heading="Community flag" />
            </div>
          ))}
        </div>
      ) : null}

      {warnLink ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4">
          <div className="panel max-w-md space-y-4 p-6">
            <p className="font-display text-lg text-risk-high">High risk</p>
            <p className="text-sm text-muted">This link may be dangerous. The original message was not changed.</p>
            <p className="break-all font-mono text-xs">{warnLink.url}</p>
            <div className="flex gap-2">
              <button type="button" onClick={() => setWarnLink(null)} className="btn-primary px-4 py-2">Go back</button>
              <button
                type="button"
                onClick={() => {
                  window.open(warnLink.url, "_blank", "noopener,noreferrer");
                  setWarnLink(null);
                }}
                className="btn-secondary px-4 py-2"
              >
                Open anyway
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

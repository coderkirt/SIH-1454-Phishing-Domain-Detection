import { useState } from "react";
import { getErrorMessage, reportUrl } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function FlagActions({ url, compact = false, onOpen, heading = "Operator action" }) {
  const { isAuthenticated } = useAuth();
  const [busy, setBusy] = useState("");
  const [note, setNote] = useState("");

  if (!url) return null;

  const mark = async (label) => {
    if (!isAuthenticated) {
      setNote("Sign in to send a community flag.");
      return;
    }
    setBusy(label);
    setNote("");
    try {
      await reportUrl({ url, label, reason: "operator-flag" });
      const copy = {
        scam: "Flagged as phishing. This is one community signal, not legal proof.",
        risky: "Flagged as suspicious. Other operators will see this signal.",
        safe: "Marked as legitimate. This does not override the engine score.",
      };
      setNote(copy[label] || "Report saved.");
    } catch (err) {
      setNote(getErrorMessage(err));
    } finally {
      setBusy("");
    }
  };

  const openSafely = () => {
    if (onOpen) {
      onOpen();
      return;
    }
    window.open(url, "_blank", "noopener,noreferrer");
  };

  return (
    <div className={compact ? "mt-3" : "mt-5"}>
      {heading ? <p className="label-tech">{heading}</p> : null}
      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        <button type="button" onClick={openSafely} className="flag-btn flag-open">
          Open in isolated tab
        </button>
        <button type="button" disabled={busy === "scam"} onClick={() => mark("scam")} className="flag-btn flag-scam">
          {busy === "scam" ? "Sending…" : "Flag as phishing"}
        </button>
        <button type="button" disabled={busy === "risky"} onClick={() => mark("risky")} className="flag-btn flag-risky">
          {busy === "risky" ? "Sending…" : "Flag as suspicious"}
        </button>
        <button type="button" disabled={busy === "safe"} onClick={() => mark("safe")} className="flag-btn flag-safe">
          {busy === "safe" ? "Sending…" : "Mark as legitimate"}
        </button>
      </div>
      {note ? <p className="mt-3 text-xs text-muted">{note}</p> : null}
    </div>
  );
}

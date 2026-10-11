import { useEffect, useRef, useState } from "react";

export const RAG_POPUP_MS = 3000;

export function extractRag(result) {
  return result?.technical_view?.rag || result?.evidence?.rag || {};
}

export function ragPopupCopy(rag) {
  if (!rag || rag.status === "unavailable") {
    return {
      status: "Unavailable",
      rule: "—",
      detail: "Knowledge-base weight omitted. Unavailable is not treated as zero.",
    };
  }
  return {
    status: rag.used ? "Raised suspicion" : rag.status === "ok" ? "Evaluated" : rag.status || "Unknown",
    rule: rag.rule_id || "kb-checked",
    detail: rag.rule_summary || "Knowledge-base checked this URL.",
  };
}

export default function RagPopup({ result, open, onClose }) {
  const [canClose, setCanClose] = useState(false);
  const onCloseRef = useRef(onClose);
  const canCloseRef = useRef(false);
  onCloseRef.current = onClose;

  useEffect(() => {
    if (!open) return undefined;
    setCanClose(false);
    canCloseRef.current = false;
    const unlock = window.setTimeout(() => {
      canCloseRef.current = true;
      setCanClose(true);
    }, RAG_POPUP_MS);
    const hide = window.setTimeout(() => onCloseRef.current?.(), RAG_POPUP_MS + 400);
    const onKey = (event) => {
      if (event.key === "Escape" && canCloseRef.current) onCloseRef.current?.();
    };
    window.addEventListener("keydown", onKey);
    return () => {
      window.clearTimeout(unlock);
      window.clearTimeout(hide);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  if (!open || !result) return null;

  const rag = extractRag(result);
  const copy = ragPopupCopy(rag);
  const score = result.risk_score ?? "—";

  return (
    <div className="rag-popup-scrim" role="dialog" aria-live="polite" aria-label="Knowledge-base evaluation">
      <div className="rag-popup-card panel">
        <p className="label-tech">Knowledge-base (RAG)</p>
        <p className="mt-2 font-display text-xl text-ink">Score ready · {score}/100</p>
        <p className="mt-2 font-mono text-xs uppercase tracking-[0.12em] text-accent">{copy.status}</p>
        <p className="mt-3 font-mono text-sm text-ink-soft">{copy.rule}</p>
        <p className="mt-3 text-sm leading-6 text-muted">{copy.detail}</p>
        <button
          type="button"
          className="btn-primary mt-5 px-4 py-2 text-xs"
          disabled={!canClose}
          onClick={() => onClose?.()}
        >
          {canClose ? "Continue" : "Showing 3s"}
        </button>
      </div>
    </div>
  );
}

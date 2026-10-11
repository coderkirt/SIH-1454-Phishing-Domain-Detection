const MIN_MS = 3000;
const HOST_ID = "phisheye-rag-popup";

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

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

export function showRagPopup(result) {
  if (!result || result.risk_score == null) return;
  document.getElementById(HOST_ID)?.remove();
  const rag = extractRag(result);
  const copy = ragPopupCopy(rag);
  const host = document.createElement("div");
  host.id = HOST_ID;
  host.innerHTML = `
    <div class="rag-popup-scrim">
      <div class="panel rag-popup-card">
        <p class="label-tech">Knowledge-base (RAG)</p>
        <p class="rag-popup-score">Score ready · ${escapeHtml(result.risk_score ?? "—")}/100</p>
        <p class="rag-popup-status">${escapeHtml(copy.status)}</p>
        <p class="rag-popup-rule">${escapeHtml(copy.rule)}</p>
        <p class="rag-popup-detail">${escapeHtml(copy.detail)}</p>
      </div>
    </div>
  `;
  document.body.appendChild(host);
  window.setTimeout(() => host.remove(), MIN_MS + 400);
}

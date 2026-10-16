export function extractHttpUrl(raw) {
  if (!raw) return "";
  const text = String(raw).trim();
  if (/^https?:\/\/localhost\b/i.test(text) || /^capacitor:/i.test(text)) return "";
  const match = text.match(/https?:\/\/[^\s<>"']+/i);
  if (match) return match[0].replace(/[),.;]+$/, "");
  if (/^[a-z0-9.-]+\.[a-z]{2,}([/:?#].*)?$/i.test(text)) {
    return `https://${text.replace(/^\/+/, "")}`;
  }
  return "";
}

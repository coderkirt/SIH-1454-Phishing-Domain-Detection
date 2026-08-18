export const LAST_SCAN_KEY = "cg_last_scan";

export function riskColor(level) {
  switch ((level || "").toUpperCase()) {
    case "CRITICAL":
      return { text: "text-[var(--risk-high)]", bg: "bg-[rgba(255,0,0,0.08)]", border: "border-[rgba(255,0,0,0.35)]", hex: "#ff0000", dot: "dot-critical", className: "risk-critical" };
    case "HIGH":
      return { text: "text-[var(--risk-high)]", bg: "bg-[rgba(255,0,0,0.06)]", border: "border-[rgba(255,0,0,0.3)]", hex: "#ff0000", dot: "dot-critical", className: "risk-high" };
    case "MEDIUM":
      return { text: "text-[var(--risk-medium)]", bg: "bg-[rgba(196,160,0,0.08)]", border: "border-[rgba(196,160,0,0.35)]", hex: "#c4a000", dot: "dot-active", className: "risk-medium" };
    case "LOW":
      return { text: "text-[var(--risk-low)]", bg: "bg-transparent", border: "border-[var(--line)]", hex: "#808080", dot: "dot-active", className: "risk-low" };
    default:
      return { text: "text-[var(--risk-unknown)]", bg: "bg-transparent", border: "border-[var(--line)]", hex: "#606060", dot: "dot-inactive", className: "risk-unknown" };
  }
}

export function recommendationFor(level, warning) {
  if (warning) return warning;
  switch ((level || "").toUpperCase()) {
    case "CRITICAL":
    case "HIGH":
      return "Do not enter passwords, OTPs, or payment information on this website. Close the page and report it if you received the link from a message.";
    case "MEDIUM":
      return "Be careful. Double-check the address bar before signing in or making a payment.";
    default:
      return "This website looks safe. Still verify the name in the address bar before you sign in.";
  }
}

export function saveLastScan(result) {
  sessionStorage.setItem(LAST_SCAN_KEY, JSON.stringify(result));
}

export function loadLastScan() {
  try {
    const raw = sessionStorage.getItem(LAST_SCAN_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

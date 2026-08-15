export const LAST_SCAN_KEY = "cg_last_scan";

export function riskColor(level) {
  switch ((level || "").toUpperCase()) {
    case "CRITICAL":
      return { text: "text-red-400", bg: "bg-red-500/15", border: "border-red-500/30", hex: "#f87171" };
    case "HIGH":
      return { text: "text-orange-400", bg: "bg-orange-500/15", border: "border-orange-500/30", hex: "#fb923c" };
    case "MEDIUM":
      return { text: "text-amber-300", bg: "bg-amber-400/15", border: "border-amber-400/30", hex: "#fbbf24" };
    default:
      return { text: "text-emerald-400", bg: "bg-emerald-500/15", border: "border-emerald-500/30", hex: "#34d399" };
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

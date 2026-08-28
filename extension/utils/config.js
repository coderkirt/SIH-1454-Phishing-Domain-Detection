/**
 * PHISHEYE extension configuration.
 *
 * Change the default backend URL here, or in the extension Settings page.
 * The Settings page value wins after the user saves it.
 *
 * Development:  http://127.0.0.1:8000
 * Production:   set your deployed FastAPI URL in Settings.
 */
export const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
export const DEFAULT_DASHBOARD_URL = "http://127.0.0.1:5173";

/** Reuse a scan result for this many milliseconds. Do not cache forever. */
export const CACHE_TTL_MS = 90 * 1000;

/** Backend request timeout. */
export const REQUEST_TIMEOUT_MS = 30 * 1000;

export const STORAGE_KEYS = {
  apiBaseUrl: "cg_api_base_url",
  dashboardUrl: "cg_dashboard_url",
  autoScan: "cg_auto_scan",
  warnings: "cg_warnings",
  pagePopup: "cg_page_popup",
  preNavigate: "cg_pre_navigate",
  scanAllPages: "cg_scan_all_pages",
  token: "cg_token",
  user: "cg_user",
  welcomeSeen: "cg_welcome_seen",
  cache: "cg_scan_cache",
  continued: "cg_continued",
  gateAllow: "cg_gate_allow",
};

export const MULTI_TLDS = [
  "co.in", "com.au", "co.uk", "org.in", "net.in", "gov.in",
  "ac.in", "edu.in", "co.jp", "com.br",
];

export function registeredDomain(hostname) {
  const host = String(hostname || "").split(":")[0].toLowerCase().replace(/^www\./, "").replace(/\.$/, "");
  const parts = host.split(".").filter(Boolean);
  if (parts.length >= 3) {
    const tail = `${parts[parts.length - 2]}.${parts[parts.length - 1]}`;
    if (MULTI_TLDS.includes(tail)) return parts.slice(-3).join(".");
  }
  if (parts.length >= 2) return parts.slice(-2).join(".");
  return host;
}

export const SKIP_PROTOCOLS = [
  "chrome:",
  "edge:",
  "about:",
  "file:",
  "devtools:",
  "chrome-extension:",
  "moz-extension:",
  "brave:",
  "opera:",
  "vivaldi:",
  "safari:",
  "view-source:",
];

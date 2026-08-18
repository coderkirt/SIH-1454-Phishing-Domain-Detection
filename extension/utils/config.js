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
  token: "cg_token",
  user: "cg_user",
  welcomeSeen: "cg_welcome_seen",
  cache: "cg_scan_cache",
  continued: "cg_continued",
};

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

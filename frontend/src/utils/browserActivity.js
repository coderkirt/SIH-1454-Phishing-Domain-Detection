const STORE_KEY = "cg_browser_opens";
const INSTALL_KEY = "cg_install_id";
const WINDOW_MS = 30 * 24 * 60 * 60 * 1000;

function normalizeKey(url) {
  try {
    const parsed = new URL(url.startsWith("http") ? url : `https://${url}`);
    parsed.hash = "";
    let href = parsed.href;
    if (href.endsWith("/")) href = href.slice(0, -1);
    return href.toLowerCase();
  } catch {
    return String(url || "").trim().toLowerCase();
  }
}

function loadStore() {
  try {
    return JSON.parse(localStorage.getItem(STORE_KEY) || "{}") || {};
  } catch {
    return {};
  }
}

function saveStore(store) {
  const now = Date.now();
  const cleaned = {};
  Object.entries(store || {}).forEach(([key, stamps]) => {
    const kept = prune(stamps, now);
    if (kept.length) cleaned[key] = kept;
  });
  localStorage.setItem(STORE_KEY, JSON.stringify(cleaned));
}

function prune(stamps, now) {
  return (stamps || []).filter((stamp) => now - Number(stamp) <= WINDOW_MS);
}

export function getInstallId() {
  let id = localStorage.getItem(INSTALL_KEY);
  if (!id) {
    id = (crypto.randomUUID && crypto.randomUUID()) || `web-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    localStorage.setItem(INSTALL_KEY, id);
  }
  return id;
}

export function recordBrowserOpen(url) {
  const key = normalizeKey(url);
  if (!key) return { this_browser_opens: 0, this_browser_status: "unknown" };
  const now = Date.now();
  const store = loadStore();
  const stamps = prune(store[key], now);
  stamps.push(now);
  store[key] = stamps;
  saveStore(store);
  return {
    this_browser_opens: stamps.length,
    this_browser_status: "observed",
  };
}

export function peekBrowserOpens(url) {
  const key = normalizeKey(url);
  if (!key) return { this_browser_opens: 0, this_browser_status: "unknown" };
  const stamps = prune(loadStore()[key], Date.now());
  return {
    this_browser_opens: stamps.length,
    this_browser_status: stamps.length ? "observed" : "unknown",
  };
}

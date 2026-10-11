import {
  CACHE_TTL_MS,
  DEFAULT_API_BASE_URL,
  DEFAULT_DASHBOARD_URL,
  REQUEST_TIMEOUT_MS,
  SKIP_PROTOCOLS,
  STORAGE_KEYS,
  registeredDomain,
} from "./config.js";

const api = typeof browser !== "undefined" ? browser : chrome;

function sessionStore() {
  return api.storage.session || api.storage.local;
}

export async function getSettings() {
  const data = await api.storage.local.get([
    STORAGE_KEYS.apiBaseUrl,
    STORAGE_KEYS.dashboardUrl,
    STORAGE_KEYS.autoScan,
    STORAGE_KEYS.warnings,
    STORAGE_KEYS.pagePopup,
    STORAGE_KEYS.preNavigate,
    STORAGE_KEYS.scanAllPages,
    STORAGE_KEYS.token,
    STORAGE_KEYS.user,
    STORAGE_KEYS.welcomeSeen,
  ]);
  return {
    apiBaseUrl: (data[STORAGE_KEYS.apiBaseUrl] || DEFAULT_API_BASE_URL).replace(/\/$/, ""),
    dashboardUrl: (data[STORAGE_KEYS.dashboardUrl] || DEFAULT_DASHBOARD_URL).replace(/\/$/, ""),
    autoScan: data[STORAGE_KEYS.autoScan] !== false,
    warnings: data[STORAGE_KEYS.warnings] !== false,
    pagePopup: data[STORAGE_KEYS.pagePopup] !== false,
    preNavigate: data[STORAGE_KEYS.preNavigate] !== false,
    scanAllPages: data[STORAGE_KEYS.scanAllPages] === true,
    token: data[STORAGE_KEYS.token] || "",
    user: data[STORAGE_KEYS.user] || null,
    welcomeSeen: Boolean(data[STORAGE_KEYS.welcomeSeen]),
  };
}

export async function saveSettings(partial) {
  const mapped = {};
  if (partial.apiBaseUrl !== undefined) mapped[STORAGE_KEYS.apiBaseUrl] = partial.apiBaseUrl.replace(/\/$/, "");
  if (partial.dashboardUrl !== undefined) mapped[STORAGE_KEYS.dashboardUrl] = partial.dashboardUrl.replace(/\/$/, "");
  if (partial.autoScan !== undefined) mapped[STORAGE_KEYS.autoScan] = Boolean(partial.autoScan);
  if (partial.warnings !== undefined) mapped[STORAGE_KEYS.warnings] = Boolean(partial.warnings);
  if (partial.pagePopup !== undefined) mapped[STORAGE_KEYS.pagePopup] = Boolean(partial.pagePopup);
  if (partial.preNavigate !== undefined) mapped[STORAGE_KEYS.preNavigate] = Boolean(partial.preNavigate);
  if (partial.scanAllPages !== undefined) mapped[STORAGE_KEYS.scanAllPages] = Boolean(partial.scanAllPages);
  if (partial.token !== undefined) mapped[STORAGE_KEYS.token] = partial.token;
  if (partial.user !== undefined) mapped[STORAGE_KEYS.user] = partial.user;
  if (partial.welcomeSeen !== undefined) mapped[STORAGE_KEYS.welcomeSeen] = Boolean(partial.welcomeSeen);
  await api.storage.local.set(mapped);
}

export function isScannableUrl(url) {
  if (!url || typeof url !== "string") return false;
  try {
    const parsed = new URL(url);
    if (SKIP_PROTOCOLS.includes(parsed.protocol)) return false;
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

export function displayHost(url) {
  try {
    return new URL(url).hostname || url;
  } catch {
    return url || "";
  }
}

function authHeaders(token) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function request(path, { method = "GET", body, timeout = REQUEST_TIMEOUT_MS } = {}) {
  const settings = await getSettings();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetch(`${settings.apiBaseUrl}${path}`, {
      method,
      headers: authHeaders(settings.token),
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = typeof data.detail === "string" ? data.detail : `Backend error (${response.status})`;
      const error = new Error(detail);
      error.status = response.status;
      error.unavailable = response.status >= 500;
      throw error;
    }
    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      const timeoutError = new Error("The security server took too long to respond.");
      timeoutError.unavailable = true;
      throw timeoutError;
    }
    if (error.status) throw error;
    const networkError = new Error("Protection service unavailable.");
    networkError.unavailable = true;
    throw networkError;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Same endpoint and payload as the React web app.
 * POST /api/v1/threat/check-url  { url, view: "both" }
 */
export function checkUrl(url, pageSignals, extra = {}) {
  const body = { url, view: "both" };
  if (pageSignals && typeof pageSignals === "object") body.page_signals = pageSignals;
  if (extra.this_browser_opens != null) body.this_browser_opens = extra.this_browser_opens;
  if (extra.this_browser_status) body.this_browser_status = extra.this_browser_status;
  return request("/api/v1/threat/check-url", {
    method: "POST",
    body,
  });
}

export async function getInstallId() {
  const data = await api.storage.local.get(STORAGE_KEYS.installId);
  let id = data[STORAGE_KEYS.installId];
  if (!id || String(id).length < 8) {
    id = (crypto.randomUUID && crypto.randomUUID()) || `pe-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    await api.storage.local.set({ [STORAGE_KEYS.installId]: id });
  }
  return id;
}

export async function recordVisit(url) {
  try {
    if (!isScannableUrl(url) || await isOwnAppUrl(url)) return;
    const client_id = await getInstallId();
    await request("/api/v1/visits", {
      method: "POST",
      body: { url, client_id },
      timeout: 4000,
    });
  } catch {
    // Fire-and-forget. A missed visit must not block the badge.
  }
}

export async function countBrowserOpens(url) {
  if (!isScannableUrl(url) || !api.history || !api.history.search) {
    return { this_browser_opens: 0, this_browser_status: "unavailable" };
  }
  try {
    const parsed = new URL(url);
    const domain = registeredDomain(parsed.hostname);
    const startTime = Date.now() - 30 * 24 * 60 * 60 * 1000;
    const items = await api.history.search({
      text: parsed.hostname,
      startTime,
      maxResults: 200,
    });
    let opens = 0;
    for (const item of items || []) {
      try {
        const itemHost = new URL(item.url).hostname;
        if (registeredDomain(itemHost) !== domain) continue;
        if (api.history.getVisits) {
          const visits = await api.history.getVisits({ url: item.url });
          opens += (visits || []).filter((visit) => Number(visit.visitTime || 0) >= startTime).length;
        } else {
          opens += Number(item.visitCount || 1);
        }
      } catch {
        // Skip a single history row that cannot be parsed.
      }
    }
    return {
      this_browser_opens: opens,
      this_browser_status: opens > 0 ? "observed" : "unknown",
    };
  } catch {
    return { this_browser_opens: 0, this_browser_status: "unavailable" };
  }
}

export function analyzeContent(payload) {
  return request("/api/v1/analyze/content", {
    method: "POST",
    body: payload,
    timeout: 60000,
  });
}

export function login(username, password) {
  return request("/api/v1/user/login", {
    method: "POST",
    body: { username, password },
  });
}

export function getProfile() {
  return request("/api/v1/user/profile");
}

export function healthCheck() {
  return request("/health", { timeout: 5000 });
}

export async function getCachedScan(url) {
  const data = await sessionStore().get(STORAGE_KEYS.cache);
  const cache = data[STORAGE_KEYS.cache] || {};
  const entry = cache[url];
  if (!entry || !entry.result || !entry.at) return null;
  if (Date.now() - entry.at > CACHE_TTL_MS) return null;
  return entry.result;
}

export async function setCachedScan(url, result) {
  const store = sessionStore();
  const data = await store.get(STORAGE_KEYS.cache);
  const cache = data[STORAGE_KEYS.cache] || {};
  const now = Date.now();
  for (const key of Object.keys(cache)) {
    if (now - (cache[key].at || 0) > CACHE_TTL_MS) delete cache[key];
  }
  cache[url] = { result, at: now };
  await store.set({ [STORAGE_KEYS.cache]: cache });
}

export async function clearCache() {
  await sessionStore().set({
    [STORAGE_KEYS.cache]: {},
    [STORAGE_KEYS.continued]: {},
    [STORAGE_KEYS.gateAllow]: {},
  });
}

export function normalizeHttpUrl(url) {
  if (!url || typeof url !== "string") return "";
  const trimmed = url.trim();
  if (!trimmed) return "";
  try {
    const parsed = new URL(trimmed.includes("://") ? trimmed : `https://${trimmed}`);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return "";
    parsed.hash = "";
    return parsed.href;
  } catch {
    return "";
  }
}

export function isExtensionPage(url) {
  if (!url) return false;
  try {
    return url.startsWith(api.runtime.getURL(""));
  } catch {
    return url.startsWith("chrome-extension://") || url.startsWith("moz-extension://");
  }
}

export async function isOwnAppUrl(url) {
  if (!url) return false;
  try {
    const parsed = new URL(url);
    const settings = await getSettings();
    const hosts = new Set();
    for (const raw of [settings.dashboardUrl, settings.apiBaseUrl]) {
      try {
        hosts.add(new URL(raw).origin);
      } catch {
        // Ignore bad settings values.
      }
    }
    if (hosts.has(parsed.origin)) return true;
    if ((parsed.hostname === "127.0.0.1" || parsed.hostname === "localhost") && (parsed.port === "5173" || parsed.port === "8000")) {
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

export async function wasGateAllowed(url) {
  const key = normalizeHttpUrl(url);
  if (!key) return false;
  const data = await sessionStore().get(STORAGE_KEYS.gateAllow);
  return Boolean((data[STORAGE_KEYS.gateAllow] || {})[key]);
}

export async function markGateAllowed(url) {
  const key = normalizeHttpUrl(url);
  if (!key) return;
  const store = sessionStore();
  const data = await store.get(STORAGE_KEYS.gateAllow);
  const allowed = data[STORAGE_KEYS.gateAllow] || {};
  allowed[key] = Date.now();
  await store.set({ [STORAGE_KEYS.gateAllow]: allowed });
}

export function canOpenAfterScan(status, { forceContinue = false } = {}) {
  if (status === "safe") return true;
  if (status === "medium" && forceContinue) return true;
  return false;
}

export async function wasContinued(url) {
  const data = await sessionStore().get(STORAGE_KEYS.continued);
  return Boolean((data[STORAGE_KEYS.continued] || {})[url]);
}

export async function markContinued(url) {
  const store = sessionStore();
  const data = await store.get(STORAGE_KEYS.continued);
  const continued = data[STORAGE_KEYS.continued] || {};
  continued[url] = true;
  await store.set({ [STORAGE_KEYS.continued]: continued });
}

export function statusFromResult(result) {
  const level = String(result?.risk_level || "").toUpperCase();
  if (level === "CRITICAL") return "critical";
  if (level === "HIGH") return "high";
  if (level === "MEDIUM") return "medium";
  if (level === "LOW") return "safe";
  return "unknown";
}

export function headlineFor(status) {
  switch (status) {
    case "critical":
      return "THREAT DETECTED";
    case "high":
      return "THREAT DETECTED";
    case "medium":
      return "FISHY";
    case "safe":
      return "NO THREAT";
    case "checking":
      return "SCANNING";
    case "unavailable":
      return "UNAVAILABLE";
    case "unsupported":
      return "UNSUPPORTED PAGE";
    case "failed":
      return "SCAN FAILED";
    default:
      return "UNKNOWN";
  }
}

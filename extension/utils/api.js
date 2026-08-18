import {
  CACHE_TTL_MS,
  DEFAULT_API_BASE_URL,
  DEFAULT_DASHBOARD_URL,
  REQUEST_TIMEOUT_MS,
  SKIP_PROTOCOLS,
  STORAGE_KEYS,
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
export function checkUrl(url) {
  return request("/api/v1/threat/check-url", {
    method: "POST",
    body: { url, view: "both" },
  });
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
  });
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

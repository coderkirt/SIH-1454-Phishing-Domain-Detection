import axios from "axios";
import { getInstallId, recordBrowserOpen } from "../utils/browserActivity";

let resolvedBase = "";

function normalizeBase(value) {
  return String(value || "").trim().replace(/\/$/, "");
}

export function syncNativeApi(url) {
  try {
    window.PhishEyeNative?.setApiUrl?.(url);
  } catch {
    /* ignore */
  }
}

export function setApiBase(url) {
  const next = normalizeBase(url);
  if (!/^https?:\/\//i.test(next)) return getApiBase();
  resolvedBase = next;
  try {
    localStorage.setItem("cg_api_url", next);
  } catch {
    /* ignore */
  }
  syncNativeApi(next);
  return next;
}

export function apiCandidates() {
  const list = [];
  const push = (value) => {
    const next = normalizeBase(value);
    if (/^https?:\/\//i.test(next) && !list.includes(next)) list.push(next);
  };
  try {
    push(localStorage.getItem("cg_api_url"));
  } catch {
    /* ignore */
  }
  push(resolvedBase);
  push(import.meta.env.VITE_API_URL);
  push("http://10.12.4.184:8000");
  push("http://172.16.33.52:8000");
  push("http://192.168.137.1:8000");
  push("http://192.168.1.1:8000");
  push("http://192.168.0.1:8000");
  push("http://10.0.0.1:8000");
  push("http://127.0.0.1:8000");
  return list;
}

export function getApiBase() {
  if (resolvedBase) return resolvedBase;
  try {
    const stored = localStorage.getItem("cg_api_url");
    if (stored && /^https?:\/\//i.test(stored.trim())) {
      resolvedBase = normalizeBase(stored);
      return resolvedBase;
    }
  } catch {
    /* ignore */
  }
  resolvedBase = normalizeBase(import.meta.env.VITE_API_URL || "http://127.0.0.1:8000");
  return resolvedBase;
}

async function fetchHealth(base) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 2500);
  try {
    return await fetch(`${base}/health`, { signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

export async function connectApi(preferred) {
  const tries = apiCandidates();
  if (preferred) tries.unshift(normalizeBase(preferred));
  for (const base of tries) {
    try {
      const response = await fetchHealth(base);
      if (response.ok) {
        setApiBase(base);
        return { ok: true, base };
      }
    } catch {
      /* try next */
    }
  }
  return { ok: false, base: getApiBase() };
}

const api = axios.create({
  baseURL: getApiBase(),
  timeout: 12000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  config.baseURL = getApiBase();
  const path = String(config.url || "");
  const token = localStorage.getItem("cg_token");
  const isAuthCall = path.includes("/user/login") || path.includes("/user/signup");
  if (token && !isAuthCall) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (typeof FormData !== "undefined" && config.data instanceof FormData) {
    if (config.headers && typeof config.headers.delete === "function") {
      config.headers.delete("Content-Type");
    } else {
      delete config.headers["Content-Type"];
    }
  }
  return config;
});

export function getErrorMessage(error) {
  if (!error.response) {
    return "Phone cannot reach the PhishEye API. Use the same Wi-Fi as this PC, keep the backend running on port 8000, then save the PC address in Settings.";
  }
  const status = error.response.status;
  const detail = error.response.data?.detail;
  if (status === 401) {
    if (typeof detail === "string" && detail.trim()) return detail;
    return "That username or password was not accepted. Create an account if you have not signed up on this PC.";
  }
  if (status === 403) return "You do not have permission to do that.";
  if (status === 400) return typeof detail === "string" ? detail : "Invalid request. Please check your input and try again.";
  if (status >= 500) return "The security server had an internal error. Please try again.";
  return typeof detail === "string" ? detail : "Something went wrong. Please try again.";
}

export const healthCheck = () => api.get("/health");
export const signup = (payload) => api.post("/api/v1/user/signup", payload);
export const login = (payload) => api.post("/api/v1/user/login", payload);
export const getProfile = () => api.get("/api/v1/user/profile");
export const checkUrl = (url) => {
  const browser = recordBrowserOpen(url);
  api.post("/api/v1/visits", { url, client_id: getInstallId() }).catch(() => {});
  return api.post("/api/v1/threat/check-url", {
    url,
    view: "both",
    this_browser_opens: browser.this_browser_opens,
    this_browser_status: browser.this_browser_status,
    client_id: getInstallId(),
  });
};
export const checkMessage = (message, url) => api.post("/api/v1/threat/check-message", { message, url });
export const analyzeContent = (payload) => api.post("/api/v1/analyze/content", payload);
export const analyzeImage = async (endpoint, file, hint = "") => {
  const body = new FormData();
  body.append("file", file, file.name || "upload.png");
  if (hint && String(hint).trim()) body.append("hint", String(hint).trim());
  const base = getApiBase();
  const token = localStorage.getItem("cg_token");
  const response = await fetch(`${base}${endpoint}`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body,
  });
  let data = {};
  try {
    data = await response.json();
  } catch {
    data = {};
  }
  if (!response.ok) {
    const error = new Error(typeof data.detail === "string" ? data.detail : "Upload failed");
    error.response = { status: response.status, data };
    throw error;
  }
  return { data };
};
export const reportUrl = (payload) => api.post("/api/v1/report", payload);
export const sendFeedback = (payload) => api.post("/api/v1/feedback", payload);
export const getReputation = (domain) => api.get(`/api/v1/reputation/domain/${encodeURIComponent(domain)}`);
export const getThreatStats = () => api.get("/api/v1/threat/stats");
export const getRecentUrls = (limit = 50) => api.get("/api/v1/threat/recent-urls", { params: { limit } });
export const getOverview = () => api.get("/api/v1/stats/overview");
export const getThreatTypes = () => api.get("/api/v1/stats/threat-types");
export const getRiskDistribution = () => api.get("/api/v1/stats/risk-distribution");
export const getDailySummary = () => api.get("/api/v1/stats/daily-summary");
export const getSources = () => api.get("/api/v1/stats/sources");
export const getTimeline = () => api.get("/api/v1/stats/timeline");
export const getReportsSummary = () => api.get("/api/v1/stats/reports-summary");
export const getContentScans = (limit = 50) => api.get("/api/v1/scans", { params: { limit } });
export const deleteScan = (scanId) => api.delete(`/api/v1/scans/${scanId}`);
export const deleteScanHistory = () => api.delete("/api/v1/scans");
export const getMyReports = () => api.get("/api/v1/reports/mine");

export default api;

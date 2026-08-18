import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("cg_token");
  if (token) {
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
    return "Unable to connect to the security server. Please make sure the backend is running.";
  }
  const status = error.response.status;
  const detail = error.response.data?.detail;
  if (status === 401) return "Your session has expired. Please sign in again.";
  if (status === 403) return "You do not have permission to do that.";
  if (status === 400) return typeof detail === "string" ? detail : "Invalid request. Please check your input and try again.";
  if (status >= 500) return "The security server had an internal error. Please try again.";
  return typeof detail === "string" ? detail : "Something went wrong. Please try again.";
}

export const healthCheck = () => api.get("/health");
export const signup = (payload) => api.post("/api/v1/user/signup", payload);
export const login = (payload) => api.post("/api/v1/user/login", payload);
export const getProfile = () => api.get("/api/v1/user/profile");
export const checkUrl = (url) => api.post("/api/v1/threat/check-url", { url, view: "both" });
export const checkMessage = (message, url) => api.post("/api/v1/threat/check-message", { message, url });
export const analyzeContent = (payload) => api.post("/api/v1/analyze/content", payload);
export const analyzeImage = async (endpoint, file, hint = "") => {
  const body = new FormData();
  body.append("file", file, file.name || "upload.png");
  if (hint && String(hint).trim()) body.append("hint", String(hint).trim());
  const base = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
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

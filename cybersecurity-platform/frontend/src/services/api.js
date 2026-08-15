import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("cg_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
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
export const getThreatStats = () => api.get("/api/v1/threat/stats");
export const getRecentUrls = (limit = 50) => api.get("/api/v1/threat/recent-urls", { params: { limit } });
export const getOverview = () => api.get("/api/v1/stats/overview");
export const getThreatTypes = () => api.get("/api/v1/stats/threat-types");
export const getRiskDistribution = () => api.get("/api/v1/stats/risk-distribution");
export const getDailySummary = () => api.get("/api/v1/stats/daily-summary");

export default api;

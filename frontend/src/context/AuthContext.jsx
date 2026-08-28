import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getErrorMessage, getProfile, login as loginRequest, signup as signupRequest } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("cg_token"));
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("cg_user") || "null");
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(!!token);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    getProfile()
      .then(({ data }) => {
        setUser(data);
        localStorage.setItem("cg_user", JSON.stringify(data));
      })
      .catch(() => {
        localStorage.removeItem("cg_token");
        localStorage.removeItem("cg_user");
        setToken(null);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, [token]);

  const signup = async (payload) => {
    setError("");
    try {
      const { data } = await signupRequest(payload);
      localStorage.setItem("cg_token", data.access_token);
      localStorage.setItem("cg_user", JSON.stringify({ username: data.username }));
      setToken(data.access_token);
      setUser({ username: data.username });
      return data;
    } catch (err) {
      const message = getErrorMessage(err);
      setError(message);
      throw new Error(message);
    }
  };

  const login = async (payload) => {
    setError("");
    try {
      const { data } = await loginRequest(payload);
      localStorage.setItem("cg_token", data.access_token);
      localStorage.setItem("cg_user", JSON.stringify({ username: data.username }));
      setToken(data.access_token);
      setUser({ username: data.username });
      return data;
    } catch (err) {
      const message = getErrorMessage(err);
      setError(message);
      throw new Error(message);
    }
  };

  const logout = () => {
    localStorage.removeItem("cg_token");
    localStorage.removeItem("cg_user");
    setToken(null);
    setUser(null);
  };

  const value = useMemo(
    () => ({ token, user, loading, error, signup, login, logout, isAuthenticated: Boolean(token) }),
    [token, user, loading, error]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}

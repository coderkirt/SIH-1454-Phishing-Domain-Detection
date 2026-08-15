import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { getErrorMessage, getProfile } from "../services/api";

export default function Settings() {
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState(user);
  const [error, setError] = useState("");
  const { theme, setTheme } = useTheme();
  const [notify, setNotify] = useState(localStorage.getItem("cg_notify") !== "false");
  const [strict, setStrict] = useState(localStorage.getItem("cg_strict") === "true");
  const navigate = useNavigate();

  useEffect(() => {
    getProfile()
      .then(({ data }) => setProfile(data))
      .catch((err) => setError(getErrorMessage(err)));
  }, []);

  const persist = (key, value, setter) => {
    setter(value);
    localStorage.setItem(key, String(value));
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Settings</h1>
        <p className="text-muted">Profile data comes from the backend. Preferences stay in this browser.</p>
      </div>
      <div className="card space-y-2 p-6">
        <h2 className="font-medium">Profile</h2>
        {error ? <p className="text-sm text-red-400">{error}</p> : null}
        <p className="text-sm text-ink-soft">Username: <span className="text-ink">{profile?.username || "—"}</span></p>
        <p className="text-sm text-ink-soft">Email: <span className="text-ink">{profile?.email || "Not returned until profile loads"}</span></p>
      </div>
      <div className="card space-y-4 p-6">
        <h2 className="font-medium">Preferences</h2>
        <label className="flex items-center justify-between text-sm">
          Theme
          <select value={theme} onChange={(e) => setTheme(e.target.value)} className="field w-auto min-w-40">
            <option value="dark">Dark</option>
            <option value="light">Light</option>
          </select>
        </label>
        <label className="flex items-center justify-between text-sm">
          Scan notifications
          <input type="checkbox" checked={notify} onChange={(e) => persist("cg_notify", e.target.checked, setNotify)} />
        </label>
        <label className="flex items-center justify-between text-sm">
          Stricter detection preference
          <input type="checkbox" checked={strict} onChange={(e) => persist("cg_strict", e.target.checked, setStrict)} />
        </label>
        <p className="text-xs text-muted">Stricter scoring is a UI preference for now. The live checker uses the backend rules.</p>
      </div>
      <button
        onClick={() => { logout(); navigate("/"); }}
        className="rounded-xl border border-red-500/40 px-4 py-3 text-red-300"
      >
        Log out
      </button>
    </div>
  );
}

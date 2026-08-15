import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getErrorMessage, getProfile } from "../services/api";

export default function Settings() {
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState(user);
  const [error, setError] = useState("");
  const [theme, setTheme] = useState(localStorage.getItem("cg_theme") || "dark");
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
        <h1 className="text-2xl font-semibold text-white">Settings</h1>
        <p className="text-slate-400">Profile data comes from the backend. Preferences stay in this browser.</p>
      </div>
      <div className="card space-y-2 p-6">
        <h2 className="font-medium">Profile</h2>
        {error ? <p className="text-sm text-red-400">{error}</p> : null}
        <p className="text-sm text-slate-300">Username: <span className="text-white">{profile?.username || "—"}</span></p>
        <p className="text-sm text-slate-300">Email: <span className="text-white">{profile?.email || "Not returned until profile loads"}</span></p>
      </div>
      <div className="card space-y-4 p-6">
        <h2 className="font-medium">Preferences</h2>
        <label className="flex items-center justify-between text-sm">
          Theme
          <select value={theme} onChange={(e) => persist("cg_theme", e.target.value, setTheme)} className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2">
            <option value="dark">Dark (current product theme)</option>
            <option value="light">Light (planned)</option>
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
        <p className="text-xs text-slate-500">Stricter scoring is a UI preference for now. The live checker uses the backend rules.</p>
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

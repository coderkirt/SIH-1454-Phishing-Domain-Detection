import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { getErrorMessage, getProfile } from "../services/api";
import PageHeader from "../components/PageHeader";
import TechnicalPanel from "../components/TechnicalPanel";
import LoadingState from "../components/LoadingState";

export default function Settings() {
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState(user);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { theme, setTheme } = useTheme();
  const [notify, setNotify] = useState(localStorage.getItem("cg_notify") !== "false");
  const [strict, setStrict] = useState(localStorage.getItem("cg_strict") === "true");
  const navigate = useNavigate();

  useEffect(() => {
    getProfile()
      .then(({ data }) => setProfile(data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  const persist = (key, value, setter) => {
    setter(value);
    localStorage.setItem(key, String(value));
  };

  if (loading) return <LoadingState label="Loading settings" />;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <PageHeader
        section="08 / Settings"
        title="Configuration"
        subtitle="Profile data comes from the backend. Preferences stay in this browser."
      />

      <TechnicalPanel title="01 / Account">
        {error ? (
          <p className="mb-4 flex items-center gap-2 text-sm text-[var(--risk-high)]">
            <span className="dot dot-critical" aria-hidden="true" />
            {error}
          </p>
        ) : null}
        <div className="space-y-0">
          <p className="flex justify-between gap-4 border-b border-line py-3 text-sm">
            <span className="text-muted">Username</span>
            <span className="font-mono text-ink">{profile?.username || "—"}</span>
          </p>
          <p className="flex justify-between gap-4 py-3 text-sm">
            <span className="text-muted">Email</span>
            <span className="font-mono text-ink">{profile?.email || "Unknown"}</span>
          </p>
        </div>
      </TechnicalPanel>

      <TechnicalPanel title="02 / Preferences">
        <label className="flex items-center justify-between gap-4 border-b border-line pb-4 text-sm">
          <span className="text-ink-soft">Appearance</span>
          <select value={theme} onChange={(e) => setTheme(e.target.value)} className="field w-auto min-w-40">
            <option value="dark">Dark</option>
            <option value="light">Light</option>
          </select>
        </label>
        <label className="flex items-center justify-between gap-4 border-b border-line py-4 text-sm">
          <span className="text-ink-soft">Scan notifications</span>
          <input type="checkbox" checked={notify} onChange={(e) => persist("cg_notify", e.target.checked, setNotify)} />
        </label>
        <label className="flex items-center justify-between gap-4 pt-4 text-sm">
          <span className="text-ink-soft">Stricter detection preference</span>
          <input type="checkbox" checked={strict} onChange={(e) => persist("cg_strict", e.target.checked, setStrict)} />
        </label>
        <p className="mt-4 text-xs text-muted">Stricter scoring is a UI preference for now. The live checker uses the backend rules.</p>
      </TechnicalPanel>

      <TechnicalPanel title="03 / Session">
        <button
          onClick={() => { logout(); navigate("/"); }}
          className="btn-danger w-full py-3"
        >
          Log out
        </button>
      </TechnicalPanel>
    </div>
  );
}

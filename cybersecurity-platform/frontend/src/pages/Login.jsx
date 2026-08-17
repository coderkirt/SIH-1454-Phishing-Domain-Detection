import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import DotMatrixLogo from "../components/DotMatrixLogo";

export default function Login() {
  const { login, error } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [localError, setLocalError] = useState("");
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from || "/dashboard";

  const onSubmit = async (e) => {
    e.preventDefault();
    setLocalError("");
    setBusy(true);
    try {
      await login({ username, password });
      navigate(from, { replace: true });
    } catch (err) {
      setLocalError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto flex max-w-md px-4 py-16">
      <form onSubmit={onSubmit} className="panel-accent panel w-full p-6">
        <div className="flex items-center gap-3">
          <DotMatrixLogo size="sm" />
          <p className="label-tech">System access</p>
        </div>
        <h1 className="mt-4 font-display text-3xl font-semibold uppercase text-ink">Log in</h1>
        <p className="mt-2 text-sm text-muted">Use your PhishShield account. This talks to the real backend.</p>
        <label className="mt-6 block label-tech">Username</label>
        <input className="field mt-2 w-full" value={username} onChange={(e) => setUsername(e.target.value)} required />
        <label className="mt-4 block label-tech">Password</label>
        <input type="password" className="field mt-2 w-full" value={password} onChange={(e) => setPassword(e.target.value)} required />
        {(localError || error) ? (
          <p className="mt-4 flex items-center gap-2 text-sm text-[var(--risk-high)]">
            <span className="dot dot-critical" aria-hidden="true" />
            {localError || error}
          </p>
        ) : null}
        <button disabled={busy} className="btn-primary mt-6 w-full py-3">
          {busy ? "Signing in..." : "Log in"}
        </button>
        <p className="mt-4 text-sm text-muted">No account? <Link className="text-ink underline-offset-4 hover:underline" to="/signup">Sign up</Link></p>
      </form>
    </div>
  );
}

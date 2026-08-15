import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

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
      <form onSubmit={onSubmit} className="card w-full p-6">
        <h1 className="text-2xl font-semibold text-ink">Log in</h1>
        <p className="mt-2 text-sm text-muted">Use your CyberGuard account. This talks to the real backend.</p>
        <label className="mt-6 block text-sm text-ink-soft">Username</label>
        <input className="field mt-1 w-full" value={username} onChange={(e) => setUsername(e.target.value)} required />
        <label className="mt-4 block text-sm text-ink-soft">Password</label>
        <input type="password" className="field mt-1 w-full" value={password} onChange={(e) => setPassword(e.target.value)} required />
        {(localError || error) ? <p className="mt-4 text-sm text-red-400">{localError || error}</p> : null}
        <button disabled={busy} className="btn-accent mt-6 w-full py-3">
          {busy ? "Signing in..." : "Log in"}
        </button>
        <p className="mt-4 text-sm text-muted">No account? <Link className="text-accent" to="/signup">Sign up</Link></p>
      </form>
    </div>
  );
}

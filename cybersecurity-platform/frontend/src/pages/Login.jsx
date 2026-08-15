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
        <h1 className="text-2xl font-semibold text-white">Log in</h1>
        <p className="mt-2 text-sm text-slate-400">Use your CyberGuard account. This talks to the real backend.</p>
        <label className="mt-6 block text-sm text-slate-300">Username</label>
        <input className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-3" value={username} onChange={(e) => setUsername(e.target.value)} required />
        <label className="mt-4 block text-sm text-slate-300">Password</label>
        <input type="password" className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-3" value={password} onChange={(e) => setPassword(e.target.value)} required />
        {(localError || error) ? <p className="mt-4 text-sm text-red-400">{localError || error}</p> : null}
        <button disabled={busy} className="mt-6 w-full rounded-xl bg-cyan-400 py-3 font-semibold text-slate-950 disabled:opacity-60">
          {busy ? "Signing in..." : "Log in"}
        </button>
        <p className="mt-4 text-sm text-slate-400">No account? <Link className="text-cyan-300" to="/signup">Sign up</Link></p>
      </form>
    </div>
  );
}

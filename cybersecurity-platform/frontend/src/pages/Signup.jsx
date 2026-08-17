import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import DotMatrixLogo from "../components/DotMatrixLogo";

export default function Signup() {
  const { signup } = useAuth();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await signup({ username, email, password });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto flex max-w-md px-4 py-16">
      <form onSubmit={onSubmit} className="panel-accent panel w-full p-6">
        <div className="flex items-center gap-3">
          <DotMatrixLogo size="sm" />
          <p className="label-tech">System registration</p>
        </div>
        <h1 className="mt-4 font-display text-3xl font-semibold uppercase text-ink">Create account</h1>
        <p className="mt-2 text-sm text-muted">Your username, email, and hashed password are stored in SQLite.</p>
        <label className="mt-6 block label-tech">Username</label>
        <input className="field mt-2 w-full" value={username} onChange={(e) => setUsername(e.target.value)} required minLength={3} />
        <label className="mt-4 block label-tech">Email</label>
        <input type="email" className="field mt-2 w-full" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <label className="mt-4 block label-tech">Password</label>
        <input type="password" className="field mt-2 w-full" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
        {error ? (
          <p className="mt-4 flex items-center gap-2 text-sm text-[var(--risk-high)]">
            <span className="dot dot-critical" aria-hidden="true" />
            {error}
          </p>
        ) : null}
        <button disabled={busy} className="btn-primary mt-6 w-full py-3">
          {busy ? "Creating account..." : "Create account"}
        </button>
        <p className="mt-4 text-sm text-muted">Already have an account? <Link className="text-ink underline-offset-4 hover:underline" to="/login">Log in</Link></p>
      </form>
    </div>
  );
}

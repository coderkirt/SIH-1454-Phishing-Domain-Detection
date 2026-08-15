import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

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
      <form onSubmit={onSubmit} className="card w-full p-6">
        <h1 className="text-2xl font-semibold text-ink">Create an account</h1>
        <p className="mt-2 text-sm text-muted">Your username, email, and hashed password are stored in SQLite.</p>
        <label className="mt-6 block text-sm text-ink-soft">Username</label>
        <input className="field mt-1 w-full" value={username} onChange={(e) => setUsername(e.target.value)} required minLength={3} />
        <label className="mt-4 block text-sm text-ink-soft">Email</label>
        <input type="email" className="field mt-1 w-full" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <label className="mt-4 block text-sm text-ink-soft">Password</label>
        <input type="password" className="field mt-1 w-full" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
        {error ? <p className="mt-4 text-sm text-red-400">{error}</p> : null}
        <button disabled={busy} className="btn-accent mt-6 w-full py-3">
          {busy ? "Creating account..." : "Sign up"}
        </button>
        <p className="mt-4 text-sm text-muted">Already have an account? <Link className="text-accent" to="/login">Log in</Link></p>
      </form>
    </div>
  );
}

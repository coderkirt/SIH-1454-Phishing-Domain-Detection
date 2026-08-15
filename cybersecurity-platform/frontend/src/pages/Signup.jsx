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
        <h1 className="text-2xl font-semibold text-white">Create an account</h1>
        <p className="mt-2 text-sm text-slate-400">Your username, email, and hashed password are stored in SQLite.</p>
        <label className="mt-6 block text-sm text-slate-300">Username</label>
        <input className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-3" value={username} onChange={(e) => setUsername(e.target.value)} required minLength={3} />
        <label className="mt-4 block text-sm text-slate-300">Email</label>
        <input type="email" className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-3" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <label className="mt-4 block text-sm text-slate-300">Password</label>
        <input type="password" className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-3" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
        {error ? <p className="mt-4 text-sm text-red-400">{error}</p> : null}
        <button disabled={busy} className="mt-6 w-full rounded-xl bg-cyan-400 py-3 font-semibold text-slate-950 disabled:opacity-60">
          {busy ? "Creating account..." : "Sign up"}
        </button>
        <p className="mt-4 text-sm text-slate-400">Already have an account? <Link className="text-cyan-300" to="/login">Log in</Link></p>
      </form>
    </div>
  );
}

import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="grid min-h-[70vh] place-items-center px-4 text-center">
      <div>
        <p className="text-sm tracking-[0.3em] text-cyan-300">404</p>
        <h1 className="mt-3 text-3xl font-semibold text-white">Page not found</h1>
        <p className="mt-2 text-slate-400">That route does not exist in CyberGuard.</p>
        <Link to="/" className="mt-6 inline-block rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950">Go home</Link>
      </div>
    </div>
  );
}

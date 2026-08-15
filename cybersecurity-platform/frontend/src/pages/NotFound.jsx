import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="grid min-h-screen place-items-center bg-page px-4 text-center">
      <div>
        <p className="text-sm tracking-[0.3em] text-accent">404</p>
        <h1 className="mt-3 text-3xl font-semibold text-ink">Page not found</h1>
        <p className="mt-2 text-muted">That route does not exist in CyberGuard.</p>
        <Link to="/" className="btn-accent mt-6 px-5 py-3">Go home</Link>
      </div>
    </div>
  );
}

import { Link, Outlet } from "react-router-dom";
import { Shield } from "lucide-react";
import ThemeToggle from "../components/ThemeToggle";

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-page text-ink">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5">
        <Link to="/" className="flex items-center gap-2 font-semibold text-ink">
          <Shield className="text-accent" size={22} />
          CyberGuard
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          <Link to="/login" className="rounded-lg px-3 py-2 text-ink-soft hover:text-ink">Log in</Link>
          <Link to="/signup" className="btn-accent px-3 py-2">Sign up</Link>
          <ThemeToggle />
        </nav>
      </header>
      <Outlet />
    </div>
  );
}

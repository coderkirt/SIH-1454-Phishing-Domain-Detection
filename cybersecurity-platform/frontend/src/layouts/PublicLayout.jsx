import { Link, Outlet } from "react-router-dom";
import { Shield } from "lucide-react";

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-[#070d18] text-slate-100">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <Shield className="text-cyan-300" size={22} />
          CyberGuard
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          <Link to="/login" className="rounded-lg px-3 py-2 text-slate-300 hover:text-white">Log in</Link>
          <Link to="/signup" className="rounded-lg bg-cyan-400 px-3 py-2 font-medium text-slate-950">Sign up</Link>
        </nav>
      </header>
      <Outlet />
    </div>
  );
}

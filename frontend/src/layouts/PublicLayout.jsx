import { Link, Outlet } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle";
import DotMatrixLogo from "../components/DotMatrixLogo";
import SystemTopBar from "../components/SystemTopBar";

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-page text-ink">
      <SystemTopBar>
        <nav className="flex items-center gap-2 text-xs uppercase tracking-[0.12em]">
          <Link to="/login" className="btn-secondary px-3 py-2">Log in</Link>
          <Link to="/signup" className="btn-primary px-3 py-2">Sign up</Link>
          <ThemeToggle />
        </nav>
      </SystemTopBar>
      <div className="border-b border-line">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-4">
          <DotMatrixLogo />
          <Link to="/" className="font-display text-base font-semibold tracking-[0.12em] text-ink">
            PHISHEYE
          </Link>
        </div>
      </div>
      <Outlet />
    </div>
  );
}

import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import ThemeToggle from "../components/ThemeToggle";
import DotMatrixLogo from "../components/DotMatrixLogo";
import SystemTopBar from "../components/SystemTopBar";

const links = [
  { to: "/dashboard", num: "01", label: "Dashboard" },
  { to: "/scanner", num: "02", label: "Scan" },
  { to: "/scan-result", num: "03", label: "Last Result" },
  { to: "/history", num: "04", label: "History" },
  { to: "/reports", num: "05", label: "Reports" },
  { to: "/statistics", num: "06", label: "Statistics" },
  { to: "/privacy", num: "07", label: "Privacy" },
  { to: "/advisor", num: "08", label: "Advisor" },
  { to: "/settings", num: "09", label: "Settings" },
  { to: "/extension", num: "10", label: "Extension" },
];

function NavItem({ to, num, label, onNavigate }) {
  return (
    <NavLink
      to={to}
      onClick={onNavigate}
      className={({ isActive }) => `nav-item ${isActive ? "nav-item-active" : ""}`}
    >
      {({ isActive }) => (
        <>
          <span className={`nav-num font-mono text-xs ${isActive ? "text-accent" : "text-muted"}`}>{num}</span>
          <span className="nav-label flex items-center gap-2">
            <span className={`dot ${isActive ? "dot-critical" : "dot-inactive"}`} aria-hidden="true" />
            {label}
          </span>
        </>
      )}
    </NavLink>
  );
}

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const closeMenu = () => setOpen(false);

  const onLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-page text-ink">
      <div className="flex">
        {open ? (
          <button
            type="button"
            className="fixed inset-0 z-20 bg-black/50 lg:hidden"
            aria-label="Close menu overlay"
            onClick={closeMenu}
          />
        ) : null}
        <aside className={`fixed z-30 flex h-screen w-72 flex-col border-r border-line bg-sidebar transition-transform lg:static lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}>
          <div className="border-b border-line p-5">
            <div className="flex items-center gap-3">
              <DotMatrixLogo />
              <div>
                <p className="font-display text-base font-semibold tracking-[0.12em] text-ink">PHISHEYE</p>
                <p className="label-tech">Security operating system</p>
              </div>
            </div>
          </div>
          <nav className="flex-1 overflow-y-auto p-3">
            {links.map((link) => (
              <NavItem key={link.to} {...link} onNavigate={closeMenu} />
            ))}
          </nav>
          <div className="border-t border-line p-4">
            <div className="space-y-3 meta-tech">
              <div>
                <p className="label-tech">Engine</p>
                <p className="mt-1">Rule / threat intelligence</p>
              </div>
              <div>
                <p className="label-tech">Operator</p>
                <p className="mt-1 truncate">{user?.username || "Unknown"}</p>
              </div>
            </div>
            <button onClick={onLogout} className="btn-secondary mt-4 w-full py-2 text-xs">
              Logout
            </button>
          </div>
        </aside>

        <div className="min-h-screen min-w-0 flex-1">
          <SystemTopBar operator={user?.username}>
            <button type="button" className="icon-btn lg:hidden" onClick={() => setOpen(true)} aria-label="Open menu">
              <span className="font-mono text-xs">≡</span>
            </button>
            <ThemeToggle />
          </SystemTopBar>
          <main className="px-4 py-6 lg:px-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}

import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  ScanSearch,
  History,
  BarChart3,
  Shield,
  FileSearch,
  Settings,
  LifeBuoy,
  LogOut,
  Menu,
  X,
} from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import ThemeToggle from "../components/ThemeToggle";

const links = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/scanner", label: "URL Scanner", icon: ScanSearch },
  { to: "/scan-result", label: "Last Result", icon: FileSearch },
  { to: "/history", label: "Threat History", icon: History },
  { to: "/statistics", label: "Statistics", icon: BarChart3 },
  { to: "/privacy", label: "Privacy Center", icon: Shield },
  { to: "/advisor", label: "Security Advisor", icon: LifeBuoy },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

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
            className="fixed inset-0 z-20 bg-black/40 lg:hidden"
            aria-label="Close menu overlay"
            onClick={() => setOpen(false)}
          />
        ) : null}
        <aside className={`fixed z-30 flex h-screen w-64 flex-col border-r border-line bg-sidebar p-5 transition-transform lg:static lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}>
          <div className="mb-8 flex items-center justify-between">
            <div>
              <p className="text-lg font-semibold tracking-wide text-ink">CyberGuard</p>
              <p className="text-xs text-muted">Threat detection platform</p>
            </div>
            <button className="icon-btn lg:hidden" onClick={() => setOpen(false)} aria-label="Close menu">
              <X size={18} />
            </button>
          </div>
          <nav className="space-y-1">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm ${isActive ? "bg-nav-active text-accent" : "text-ink-soft hover:bg-nav-active"}`
                }
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="mt-auto pt-6">
            <p className="mb-3 truncate text-sm text-muted">{user?.username || "User"}</p>
            <button onClick={onLogout} className="flex w-full items-center gap-2 rounded-xl border border-line px-3 py-2 text-sm text-ink-soft hover:bg-nav-active">
              <LogOut size={16} /> Logout
            </button>
          </div>
        </aside>

        <div className="min-h-screen min-w-0 flex-1">
          <header className="sticky top-0 z-20 flex items-center justify-between gap-3 border-b border-line bg-header px-4 py-3 backdrop-blur lg:px-8">
            <button className="icon-btn lg:hidden" onClick={() => setOpen(true)} aria-label="Open menu">
              <Menu size={18} />
            </button>
            <div className="ml-auto flex items-center gap-3">
              <p className="text-sm text-muted">Signed in as <span className="font-medium text-ink">{user?.username}</span></p>
              <ThemeToggle />
            </div>
          </header>
          <main className="px-4 py-6 lg:px-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}

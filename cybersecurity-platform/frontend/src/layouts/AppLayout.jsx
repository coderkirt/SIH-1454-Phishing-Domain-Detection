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
    <div className="min-h-screen bg-[#070d18] text-slate-100">
      <div className="flex">
        <aside className={`fixed z-30 h-screen w-64 border-r border-slate-800 bg-[#0a1322] p-5 transition-transform lg:static lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}>
          <div className="mb-8 flex items-center justify-between">
            <div>
              <p className="text-lg font-semibold tracking-wide text-white">CyberGuard</p>
              <p className="text-xs text-slate-400">Threat detection platform</p>
            </div>
            <button className="lg:hidden" onClick={() => setOpen(false)} aria-label="Close menu">
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
                  `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm ${isActive ? "bg-cyan-400/10 text-cyan-300" : "text-slate-300 hover:bg-slate-800/70"}`
                }
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="absolute bottom-5 left-5 right-5">
            <p className="mb-3 truncate text-sm text-slate-400">{user?.username || "User"}</p>
            <button onClick={onLogout} className="flex w-full items-center gap-2 rounded-xl border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800">
              <LogOut size={16} /> Logout
            </button>
          </div>
        </aside>

        <div className="min-h-screen flex-1 lg:ml-0">
          <header className="sticky top-0 z-20 flex items-center justify-between border-b border-slate-800 bg-[#070d18]/85 px-4 py-3 backdrop-blur lg:px-8">
            <button className="rounded-lg border border-slate-700 p-2 lg:hidden" onClick={() => setOpen(true)} aria-label="Open menu">
              <Menu size={18} />
            </button>
            <p className="text-sm text-slate-400">Signed in as <span className="text-white">{user?.username}</span></p>
          </header>
          <main className="px-4 py-6 lg:px-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}

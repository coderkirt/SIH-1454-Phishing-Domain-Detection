import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis } from "recharts";
import { Activity, ShieldAlert, Percent, ScanSearch } from "lucide-react";
import StatCard from "../components/StatCard";
import RiskBadge from "../components/RiskBadge";
import EmptyState from "../components/EmptyState";
import UrlScanner from "../components/UrlScanner";
import { getDailySummary, getErrorMessage, getOverview, getRecentUrls, getRiskDistribution, getThreatTypes } from "../services/api";
import { riskColor } from "../utils/risk";

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [overview, setOverview] = useState(null);
  const [daily, setDaily] = useState(null);
  const [recent, setRecent] = useState([]);
  const [risk, setRisk] = useState(null);
  const [types, setTypes] = useState(null);

  useEffect(() => {
    Promise.all([getOverview(), getDailySummary(), getRecentUrls(8), getRiskDistribution(), getThreatTypes()])
      .then(([o, d, r, rd, t]) => {
        setOverview(o.data);
        setDaily(d.data);
        setRecent(r.data.recent_urls || []);
        setRisk(rd.data);
        setTypes(t.data);
      })
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-400">Loading dashboard...</p>;
  if (error) return <p className="text-red-400">{error}</p>;

  const riskData = Object.entries(risk?.risk_distribution || {}).map(([name, value]) => ({
    name,
    value,
    fill: riskColor(name).hex,
  }));
  const typeData = Object.entries(types?.threat_types || {}).map(([name, value]) => ({ name, value }));
  const latest = recent[0];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Dashboard</h1>
        <p className="text-slate-400">Live numbers from your FastAPI + SQLite backend.</p>
      </div>

      <div className="card p-5">
        <p className="mb-3 text-sm font-medium text-slate-300">Scan a URL</p>
        <UrlScanner compact />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard icon={ScanSearch} label="Total URLs checked" value={overview?.total_urls_checked ?? 0} />
        <StatCard icon={ShieldAlert} label="Threats detected" value={overview?.threats_detected ?? 0} />
        <StatCard icon={Percent} label="Safety rate" value={overview?.safety_rate || "0.0%"} />
        <StatCard icon={Activity} label="Checked today" value={daily?.urls_checked_today ?? 0} hint={`${daily?.threats_blocked_today ?? 0} threats today`} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card p-5">
          <h2 className="mb-4 font-medium">Risk distribution</h2>
          {(risk?.total || 0) === 0 ? (
            <EmptyState title="No scans yet" body="Run a URL scan to populate this chart." />
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={riskData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80}>
                    {riskData.map((entry) => <Cell key={entry.name} fill={entry.fill} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
        <div className="card p-5">
          <h2 className="mb-4 font-medium">Threat types</h2>
          {(types?.total || 0) === 0 ? (
            <EmptyState title="No threats recorded" body="HIGH and CRITICAL scans appear here." />
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={typeData}>
                  <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                  <YAxis stroke="#94a3b8" allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#22d3ee" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-medium">Recent scans</h2>
            <Link to="/history" className="text-sm text-cyan-300">View all</Link>
          </div>
          {recent.length === 0 ? (
            <EmptyState title="No scans yet" body="Your latest checks will show up here." />
          ) : (
            <ul className="space-y-3">
              {recent.map((item, i) => (
                <li key={`${item.url}-${item.timestamp}-${i}`} className="flex items-start justify-between gap-3 border-b border-slate-800 pb-3 last:border-0">
                  <p className="truncate font-mono text-sm text-slate-300">{item.url}</p>
                  <RiskBadge level={item.risk_level} />
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="card p-5">
          <h2 className="mb-4 font-medium">Latest scan</h2>
          {!latest ? (
            <EmptyState title="No scans yet" body="Scan a URL to see the latest result." />
          ) : (
            <div>
              <p className="break-all font-mono text-sm text-cyan-200">{latest.url}</p>
              <div className="mt-3"><RiskBadge level={latest.risk_level} /></div>
              <p className="mt-2 text-sm text-slate-400">{latest.timestamp}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

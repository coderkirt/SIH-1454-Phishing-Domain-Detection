import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis } from "recharts";
import StatCard from "../components/StatCard";
import EmptyState from "../components/EmptyState";
import { getDailySummary, getErrorMessage, getOverview, getRiskDistribution, getThreatTypes } from "../services/api";
import { riskColor } from "../utils/risk";
import { Percent, ShieldAlert, ScanSearch, CalendarDays } from "lucide-react";

export default function Statistics() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [overview, setOverview] = useState(null);
  const [daily, setDaily] = useState(null);
  const [risk, setRisk] = useState(null);
  const [types, setTypes] = useState(null);

  useEffect(() => {
    Promise.all([getOverview(), getDailySummary(), getRiskDistribution(), getThreatTypes()])
      .then(([o, d, r, t]) => {
        setOverview(o.data);
        setDaily(d.data);
        setRisk(r.data);
        setTypes(t.data);
      })
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-400">Loading statistics...</p>;
  if (error) return <p className="text-red-400">{error}</p>;

  const riskData = Object.entries(risk?.risk_distribution || {}).map(([name, value]) => ({ name, value, fill: riskColor(name).hex }));
  const typeData = Object.entries(types?.threat_types || {}).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Statistics</h1>
        <p className="text-slate-400">Charts are generated from actual SQLite records.</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard icon={ScanSearch} label="URLs scanned" value={overview?.total_urls_checked ?? 0} />
        <StatCard icon={ShieldAlert} label="Threats detected" value={overview?.threats_detected ?? 0} />
        <StatCard icon={Percent} label="Safety percentage" value={overview?.safety_rate || "0.0%"} />
        <StatCard icon={CalendarDays} label="Today" value={`${daily?.urls_checked_today ?? 0} scans`} hint={`${daily?.threats_blocked_today ?? 0} threats blocked`} />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card p-5">
          <h2 className="mb-4 font-medium">Risk distribution</h2>
          {(risk?.total || 0) === 0 ? <EmptyState title="No scans yet" body="Charts appear after the first URL check." /> : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={riskData} dataKey="value" nameKey="name" outerRadius={90} label>
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
          {(types?.total || 0) === 0 ? <EmptyState title="No threat types yet" body="HIGH/CRITICAL scans create threat-type records." /> : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={typeData}>
                  <XAxis dataKey="name" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#22d3ee" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

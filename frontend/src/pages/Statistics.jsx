import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import ChartTooltip from "../components/ChartTooltip";
import StatCard from "../components/StatCard";
import EmptyState from "../components/EmptyState";
import PageHeader from "../components/PageHeader";
import LoadingState from "../components/LoadingState";
import TechnicalPanel from "../components/TechnicalPanel";
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

  if (loading) return <LoadingState label="Loading statistics" />;

  if (error) {
    return (
      <TechnicalPanel title="System error" accent>
        <p className="flex items-center gap-2 text-sm text-[var(--risk-high)]">
          <span className="dot dot-critical" aria-hidden="true" />
          {error}
        </p>
      </TechnicalPanel>
    );
  }

  const riskData = Object.entries(risk?.risk_distribution || {}).map(([name, value]) => ({ name, value, fill: riskColor(name).hex }));
  const typeData = Object.entries(types?.threat_types || {}).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-8">
      <PageHeader
        section="05 / Statistics"
        title="Threat analytics"
        subtitle="Charts are generated from actual SQLite records."
      />

      <div className="grid gap-px border border-line bg-line sm:grid-cols-2 xl:grid-cols-4">
        <StatCard icon={ScanSearch} label="URLs scanned" value={overview?.total_urls_checked ?? 0} />
        <StatCard icon={ShieldAlert} label="Threats detected" value={overview?.threats_detected ?? 0} />
        <StatCard icon={Percent} label="Safety percentage" value={overview?.safety_rate || "0.0%"} />
        <StatCard icon={CalendarDays} label="Today" value={`${daily?.urls_checked_today ?? 0} scans`} hint={`${daily?.threats_blocked_today ?? 0} threats blocked`} />
      </div>

      <section className="grid gap-6 lg:grid-cols-2">
        <TechnicalPanel title="Risk distribution">
          {(risk?.total || 0) === 0 ? (
            <EmptyState title="No scans yet" body="Charts appear after the first URL check." />
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={riskData} dataKey="value" nameKey="name" outerRadius={90} stroke="var(--surface)" label={{ fill: "var(--chart-axis)", fontSize: 11 }}>
                    {riskData.map((entry) => <Cell key={entry.name} fill={entry.fill} />)}
                  </Pie>
                  <Tooltip content={<ChartTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </TechnicalPanel>
        <TechnicalPanel title="Threat types">
          {(types?.total || 0) === 0 ? (
            <EmptyState title="No threat types yet" body="HIGH/CRITICAL scans create threat-type records." />
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={typeData}>
                  <CartesianGrid stroke="var(--chart-grid)" vertical={false} />
                  <XAxis dataKey="name" stroke="var(--chart-axis)" tick={{ fill: "var(--chart-axis)", fontSize: 11 }} />
                  <YAxis stroke="var(--chart-axis)" tick={{ fill: "var(--chart-axis)", fontSize: 11 }} allowDecimals={false} />
                  <Tooltip content={<ChartTooltip />} />
                  <Bar dataKey="value" fill="var(--muted)" radius={0} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </TechnicalPanel>
      </section>
    </div>
  );
}

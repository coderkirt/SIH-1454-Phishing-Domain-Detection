import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import ChartTooltip from "../components/ChartTooltip";
import { Activity, ShieldAlert, Percent, ScanSearch } from "lucide-react";
import StatCard from "../components/StatCard";
import RiskBadge from "../components/RiskBadge";
import EmptyState from "../components/EmptyState";
import UrlScanner from "../components/UrlScanner";
import ScreenshotUploader from "../components/ScreenshotUploader";
import PageHeader from "../components/PageHeader";
import LoadingState from "../components/LoadingState";
import TechnicalPanel from "../components/TechnicalPanel";
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
  const [quickMode, setQuickMode] = useState("url");

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

  if (loading) return <LoadingState label="Loading console" />;

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

  const riskData = Object.entries(risk?.risk_distribution || {}).map(([name, value]) => ({
    name,
    value,
    fill: riskColor(name).hex,
  }));
  const typeData = Object.entries(types?.threat_types || {}).map(([name, value]) => ({ name, value }));
  const latest = recent[0];

  return (
    <div className="space-y-8">
      <PageHeader
        section="01 / Dashboard"
        title="Security console"
        subtitle="Live metrics from your FastAPI + SQLite backend."
      />

      <section>
        <p className="label-tech">Quick analysis</p>
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setQuickMode("url")}
            className={`px-4 py-2 text-xs uppercase tracking-[0.12em] ${quickMode === "url" ? "btn-primary" : "btn-secondary"}`}
          >
            URL
          </button>
          <button
            type="button"
            onClick={() => setQuickMode("screenshot")}
            className={`px-4 py-2 text-xs uppercase tracking-[0.12em] ${quickMode === "screenshot" ? "btn-primary" : "btn-secondary"}`}
          >
            Screenshot
          </button>
        </div>
        <div className="mt-4">
          {quickMode === "url" ? <UrlScanner compact /> : <ScreenshotUploader compact />}
        </div>
      </section>

      <TechnicalPanel title="System status" accent>
        <div className="flex items-center gap-2 text-sm text-ink-soft">
          <span className="dot dot-active" aria-hidden="true" />
          Protection active
        </div>
        <div className="mt-6 grid gap-px border border-line bg-line sm:grid-cols-2 xl:grid-cols-4">
          <StatCard icon={ScanSearch} label="Total scans" value={overview?.total_urls_checked ?? 0} />
          <StatCard icon={ShieldAlert} label="Threats detected" value={overview?.threats_detected ?? 0} />
          <StatCard icon={Percent} label="Safety rate" value={overview?.safety_rate || "0.0%"} />
          <StatCard icon={Activity} label="Checked today" value={daily?.urls_checked_today ?? 0} hint={`${daily?.threats_blocked_today ?? 0} threats today`} />
        </div>
      </TechnicalPanel>

      <section className="grid gap-6 lg:grid-cols-2">
        <TechnicalPanel title="Risk distribution">
          {(risk?.total || 0) === 0 ? (
            <EmptyState title="No scans yet" body="Run a URL analysis to populate this chart." />
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={riskData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80} stroke="var(--surface)">
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
            <EmptyState title="No threats recorded" body="HIGH and CRITICAL scans appear here." />
          ) : (
            <div className="h-64">
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

      <section className="grid gap-6 lg:grid-cols-2">
        <TechnicalPanel title="Recent analysis">
          <div className="mb-4 flex items-center justify-between gap-3">
            <span className="meta-tech">{recent.length} records</span>
            <Link to="/history" className="meta-tech hover:text-ink">View all</Link>
          </div>
          {recent.length === 0 ? (
            <EmptyState title="No scans yet" body="Your latest checks will show up here." />
          ) : (
            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Target</th>
                    <th>Risk</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {recent.map((item, i) => (
                    <tr key={`${item.url}-${item.timestamp}-${i}`}>
                      <td className="max-w-[240px] truncate font-mono">{item.url}</td>
                      <td><RiskBadge level={item.risk_level} /></td>
                      <td className="meta-tech">{item.timestamp}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </TechnicalPanel>
        <TechnicalPanel title="Latest scan">
          {!latest ? (
            <EmptyState title="No scans yet" body="Analyze a URL to see the latest result." />
          ) : (
            <div>
              <p className="break-all font-mono text-sm text-ink-soft">{latest.url}</p>
              <div className="mt-3"><RiskBadge level={latest.risk_level} /></div>
              <p className="mt-3 meta-tech">{latest.timestamp}</p>
            </div>
          )}
        </TechnicalPanel>
      </section>
    </div>
  );
}

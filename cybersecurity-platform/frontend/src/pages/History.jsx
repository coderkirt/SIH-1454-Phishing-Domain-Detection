import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import RiskBadge from "../components/RiskBadge";
import EmptyState from "../components/EmptyState";
import PageHeader from "../components/PageHeader";
import LoadingState from "../components/LoadingState";
import TechnicalPanel from "../components/TechnicalPanel";
import { getErrorMessage, getRecentUrls } from "../services/api";
import { riskColor } from "../utils/risk";

export default function History() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState("ALL");
  const [sort, setSort] = useState("newest");

  useEffect(() => {
    getRecentUrls(100)
      .then(({ data }) => setRows(data.recent_urls || []))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    let list = [...rows];
    if (query.trim()) {
      const q = query.toLowerCase();
      list = list.filter((row) => (row.url || "").toLowerCase().includes(q));
    }
    if (level !== "ALL") list = list.filter((row) => row.risk_level === level);
    list.sort((a, b) => {
      if (sort === "score") return (b.risk_score || 0) - (a.risk_score || 0);
      return String(b.timestamp || "").localeCompare(String(a.timestamp || ""));
    });
    return list;
  }, [rows, query, level, sort]);

  if (loading) return <LoadingState label="Loading history" />;

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

  return (
    <div className="space-y-6">
      <PageHeader
        section="04 / History"
        title="Report history"
        subtitle="Real checks stored in SQLite. Nothing here is invented."
      />

      <div className="grid gap-3 sm:grid-cols-[1fr_auto_auto]">
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search URL" className="field field-mono" />
        <select value={level} onChange={(e) => setLevel(e.target.value)} className="field sm:w-40">
          {["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"].map((opt) => <option key={opt}>{opt}</option>)}
        </select>
        <select value={sort} onChange={(e) => setSort(e.target.value)} className="field sm:w-44">
          <option value="newest">Newest</option>
          <option value="score">Highest score</option>
        </select>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title="No analyses yet"
          body="Analyze a URL to build your threat history."
          action={<Link to="/scanner" className="btn-primary px-4 py-2.5">Analyze URL</Link>}
        />
      ) : (
        <TechnicalPanel title="Threat records">
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Target</th>
                  <th>Score</th>
                  <th>Risk</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((row, i) => {
                  const c = riskColor(row.risk_level);
                  return (
                    <tr key={`${row.url}-${row.timestamp}-${i}`}>
                      <td className="max-w-[320px] truncate font-mono">{row.url}</td>
                      <td className="font-mono">{row.risk_score ?? "—"}</td>
                      <td><RiskBadge level={row.risk_level} /></td>
                      <td>
                        <span className="flex items-center gap-2">
                          <span className={`dot ${c.dot}`} aria-hidden="true" />
                          {row.risk_level === "LOW" ? "Controlled" : "Review"}
                        </span>
                      </td>
                      <td className="meta-tech">{row.timestamp}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </TechnicalPanel>
      )}
    </div>
  );
}

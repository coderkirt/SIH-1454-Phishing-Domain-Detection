import { useEffect, useMemo, useState } from "react";
import RiskBadge from "../components/RiskBadge";
import EmptyState from "../components/EmptyState";
import { getErrorMessage, getRecentUrls } from "../services/api";

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

  if (loading) return <p className="text-slate-400">Loading history...</p>;
  if (error) return <p className="text-red-400">{error}</p>;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold text-white">Threat history</h1>
        <p className="text-slate-400">Real checks stored in SQLite. Nothing here is invented.</p>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row">
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search URL" className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5" />
        <select value={level} onChange={(e) => setLevel(e.target.value)} className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5">
          {["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"].map((opt) => <option key={opt}>{opt}</option>)}
        </select>
        <select value={sort} onChange={(e) => setSort(e.target.value)} className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5">
          <option value="newest">Newest</option>
          <option value="score">Highest score</option>
        </select>
      </div>
      {filtered.length === 0 ? (
        <EmptyState title="No scans yet" body="Scan a URL to build your threat history." />
      ) : (
        <div className="card overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-slate-800 text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">URL</th>
                <th className="px-4 py-3 font-medium">Risk score</th>
                <th className="px-4 py-3 font-medium">Risk level</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((row, i) => (
                <tr key={`${row.url}-${row.timestamp}-${i}`} className="border-b border-slate-800/80 last:border-0">
                  <td className="max-w-[320px] truncate px-4 py-3 font-mono text-cyan-200">{row.url}</td>
                  <td className="px-4 py-3">{row.risk_score ?? "—"}</td>
                  <td className="px-4 py-3"><RiskBadge level={row.risk_level} /></td>
                  <td className="px-4 py-3">{row.risk_level === "LOW" ? "Safe" : "Unsafe"}</td>
                  <td className="px-4 py-3 text-slate-400">{row.timestamp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import PageHeader from "../components/PageHeader";
import { getErrorMessage, getMyReports, getReportsSummary } from "../services/api";

export default function Reports() {
  const [summary, setSummary] = useState(null);
  const [mine, setMine] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getReportsSummary(), getMyReports().catch(() => ({ data: { reports: [] } }))])
      .then(([s, m]) => {
        setSummary(s.data);
        setMine(m.data.reports || []);
      })
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-muted">Loading reports...</p>;
  if (error) return <p className="text-risk-high">{error}</p>;

  return (
    <div className="space-y-6">
      <PageHeader
        section="05 / Reports"
        title="Community reports"
        subtitle="User labels are one signal, not proof that a site is malicious."
      />
      <div className="grid gap-4 sm:grid-cols-4">
        {[
          ["Total", summary?.total_reports],
          ["Scam", summary?.scam_reports],
          ["Risky", summary?.risky_reports],
          ["Safe", summary?.safe_reports],
        ].map(([label, value]) => (
          <div key={label} className="panel p-4 text-center">
            <p className="label-tech">{label}</p>
            <p className="mt-1 font-display text-2xl">{value ?? 0}</p>
          </div>
        ))}
      </div>
      <div className="panel p-5">
        <h2 className="font-display text-lg">Recent community reports</h2>
        {(summary?.recent || []).length === 0 ? (
          <div className="mt-4">
            <EmptyState title="No reports yet" body="Use Mark as Scam / Risky / Safe after a scan." />
          </div>
        ) : (
          <ul className="mt-3 space-y-3">
            {(summary.recent || []).map((row, i) => (
              <li key={`${row.url}-${row.created_at}-${i}`} className="flex justify-between gap-3 border-b border-line pb-3 last:border-0">
                <p className="truncate font-mono text-sm">{row.url}</p>
                <span className="label-tech">{row.user_label}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="panel p-5">
        <h2 className="font-display text-lg">Your reports</h2>
        {mine.length === 0 ? (
          <p className="mt-3 text-sm text-muted">You have not submitted reports in this account yet.</p>
        ) : (
          <ul className="mt-3 space-y-3">
            {mine.map((row, i) => (
              <li key={`${row.url}-${i}`} className="border-b border-line pb-3 last:border-0">
                <p className="truncate font-mono text-sm">{row.url}</p>
                <p className="text-xs text-muted">{row.user_label} · {row.created_at}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

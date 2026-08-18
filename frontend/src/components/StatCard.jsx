export default function StatCard({ label, value, hint, icon: Icon }) {
  return (
    <div className="panel p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="label-tech">{label}</p>
          <p className="mt-2 font-display text-3xl font-semibold tracking-tight text-ink">{value}</p>
          {hint ? <p className="mt-1 text-sm text-muted">{hint}</p> : null}
        </div>
        {Icon ? (
          <div className="border border-line p-2 text-muted">
            <Icon size={18} strokeWidth={1.5} />
          </div>
        ) : null}
      </div>
    </div>
  );
}

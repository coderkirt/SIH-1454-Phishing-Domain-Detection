export default function StatCard({ label, value, hint, icon: Icon }) {
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-muted">{label}</p>
          <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
          {hint ? <p className="mt-1 text-sm text-muted">{hint}</p> : null}
        </div>
        {Icon ? (
          <div className="rounded-xl bg-nav-active p-2 text-accent">
            <Icon size={20} />
          </div>
        ) : null}
      </div>
    </div>
  );
}

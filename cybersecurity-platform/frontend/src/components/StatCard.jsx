export default function StatCard({ label, value, hint, icon: Icon }) {
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{label}</p>
          <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
          {hint ? <p className="mt-1 text-sm text-slate-400">{hint}</p> : null}
        </div>
        {Icon ? (
          <div className="rounded-xl bg-cyan-400/10 p-2 text-cyan-300">
            <Icon size={20} />
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default function TechnicalPanel({ title, accent = false, className = "", children }) {
  return (
    <section className={`panel ${accent ? "panel-accent" : ""} ${className}`.trim()}>
      {title ? (
        <div className="border-b border-line px-5 py-3">
          <p className="label-tech">{title}</p>
        </div>
      ) : null}
      <div className="p-5">{children}</div>
    </section>
  );
}

export function TechnicalRow({ index, label, value }) {
  return (
    <div className="grid grid-cols-[72px_1fr] items-start gap-4 border-b border-line py-3 last:border-0 sm:grid-cols-[120px_1fr]">
      <dt className="font-mono text-xs uppercase tracking-[0.12em] text-muted">
        {String(index).padStart(2, "0")} {label}
      </dt>
      <dd className="text-right font-mono text-sm text-ink-soft break-all">{value}</dd>
    </div>
  );
}

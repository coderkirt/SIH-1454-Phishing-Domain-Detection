import { useState } from "react";

export default function TechnicalPanel({ title, accent = false, className = "", collapsible = false, hint = "Click to open", children }) {
  const [open, setOpen] = useState(false);
  const expanded = !collapsible || open;

  return (
    <section className={`panel flex h-full min-h-0 flex-col ${accent ? "panel-accent" : ""} ${className}`.trim()}>
      {title ? (
        collapsible ? (
          <button
            type="button"
            className="flex w-full shrink-0 cursor-pointer items-center justify-between gap-3 border-b border-line bg-transparent px-5 py-3 text-left"
            aria-expanded={expanded}
            onClick={() => setOpen((value) => !value)}
          >
            <span>
              <span className="label-tech">{title}</span>
              <span className="mt-1 block font-mono text-[11px] uppercase tracking-[0.08em] text-muted">
                {expanded ? "Click to close" : hint}
              </span>
            </span>
            <span className="font-mono text-xs text-muted" aria-hidden="true">{expanded ? "−" : "+"}</span>
          </button>
        ) : (
          <div className="shrink-0 border-b border-line px-5 py-3">
            <p className="label-tech">{title}</p>
          </div>
        )
      ) : null}
      {expanded ? <div className="flex min-h-0 flex-1 flex-col p-5">{children}</div> : null}
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

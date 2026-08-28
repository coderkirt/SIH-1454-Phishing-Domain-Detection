export default function PageHeader({ section, title, subtitle, meta, actions }) {
  return (
    <div className="border-b border-line pb-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          {section ? <p className="label-tech">{section}</p> : null}
          <h1 className="mt-2 font-display text-3xl font-semibold uppercase tracking-tight text-ink sm:text-4xl">
            {title}
          </h1>
          {subtitle ? (
            <p className={`mt-3 ${meta ? "break-all font-mono text-sm text-ink-soft" : "max-w-3xl text-muted"}`}>
              {subtitle}
            </p>
          ) : null}
        </div>
        {actions ? <div className="flex shrink-0 flex-wrap gap-2">{actions}</div> : null}
      </div>
    </div>
  );
}

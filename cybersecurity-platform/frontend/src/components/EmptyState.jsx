export default function EmptyState({ title, body, action }) {
  return (
    <div className="panel-elevated border border-dashed border-line p-8 text-center">
      <span className="dot dot-inactive mx-auto" aria-hidden="true" />
      <p className="mt-4 font-display text-lg font-semibold text-ink">{title}</p>
      <p className="mt-2 text-sm text-muted">{body}</p>
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  );
}

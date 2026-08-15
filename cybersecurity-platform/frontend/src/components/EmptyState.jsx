export default function EmptyState({ title, body }) {
  return (
    <div className="rounded-xl border border-line bg-surface-2 p-8 text-center text-ink-soft">
      <p className="text-lg font-medium text-ink">{title}</p>
      <p className="mt-2 text-sm text-muted">{body}</p>
    </div>
  );
}

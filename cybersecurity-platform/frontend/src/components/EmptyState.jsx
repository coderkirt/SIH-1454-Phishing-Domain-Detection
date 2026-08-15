export default function EmptyState({ title, body }) {
  return (
    <div className="card p-8 text-center text-slate-300">
      <p className="text-lg font-medium text-white">{title}</p>
      <p className="mt-2 text-sm text-slate-400">{body}</p>
    </div>
  );
}

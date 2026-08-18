export default function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;

  return (
    <div
      className="border px-3 py-2 text-sm"
      style={{
        background: "var(--chart-tooltip-bg)",
        borderColor: "var(--chart-tooltip-border)",
        color: "var(--ink)",
      }}
    >
      {label ? <p className="mb-1 font-mono text-xs uppercase tracking-[0.12em] text-muted">{label}</p> : null}
      {payload.map((item) => (
        <p key={item.name} className="font-mono text-sm text-ink-soft">
          {item.name}: {item.value}
        </p>
      ))}
    </div>
  );
}

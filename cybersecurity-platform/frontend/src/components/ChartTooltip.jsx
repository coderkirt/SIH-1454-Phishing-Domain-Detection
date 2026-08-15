export default function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;

  return (
    <div
      className="rounded-xl border px-3 py-2 text-sm shadow-sm"
      style={{
        background: "var(--chart-tooltip-bg)",
        borderColor: "var(--chart-tooltip-border)",
        color: "var(--ink)",
      }}
    >
      {label ? <p className="mb-1 font-medium">{label}</p> : null}
      {payload.map((item) => (
        <p key={item.name} className="text-ink-soft">
          {item.name}: {item.value}
        </p>
      ))}
    </div>
  );
}

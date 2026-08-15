import { riskColor } from "../utils/risk";

export default function RiskBadge({ level }) {
  const c = riskColor(level);
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold tracking-wide ${c.bg} ${c.text} border ${c.border}`}>
      {level || "UNKNOWN"}
    </span>
  );
}

import { riskColor } from "../utils/risk";

export default function RiskBadge({ level }) {
  const c = riskColor(level);
  return (
    <span className={`status-pill ${c.className}`}>
      <span className={`dot ${c.dot}`} aria-hidden="true" />
      {level || "UNKNOWN"}
    </span>
  );
}

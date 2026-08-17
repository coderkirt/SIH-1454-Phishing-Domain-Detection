export default function DotMatrixLogo({ size = "md", className = "" }) {
  const dotSize = size === "sm" ? "h-1 w-1" : "h-1.5 w-1.5";
  const gap = size === "sm" ? "gap-0.5" : "gap-1";

  return (
    <div className={`dot-matrix-logo inline-grid grid-cols-3 ${gap} ${className}`} aria-hidden="true">
      {Array.from({ length: 9 }).map((_, index) => (
        <span
          key={index}
          className={`${dotSize} rounded-full ${index === 4 ? "bg-accent" : "bg-ink"}`}
        />
      ))}
    </div>
  );
}

import { useEffect, useState } from "react";

function formatClock(date) {
  return date.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

function formatDate(date) {
  return date
    .toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" })
    .toUpperCase();
}

export default function SystemTopBar({ operator, children }) {
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(id);
  }, []);

  return (
    <header className="sticky top-0 z-20 border-b border-line bg-header backdrop-blur">
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 lg:px-8">
        <div className="flex flex-wrap items-center gap-3 meta-tech">
          <span className="flex items-center gap-2">
            <span className="dot dot-active" aria-hidden="true" />
            System online
          </span>
          <span className="hidden text-muted sm:inline">│</span>
          <span className="hidden sm:inline">{formatClock(now)}</span>
          <span className="hidden text-muted md:inline">│</span>
          <span className="hidden md:inline">{formatDate(now)}</span>
        </div>
        <div className="ml-auto flex items-center gap-3">
          {operator ? (
            <p className="hidden text-xs uppercase tracking-[0.12em] text-muted sm:block">
              Operator / <span className="text-ink">{operator}</span>
            </p>
          ) : null}
          {children}
        </div>
      </div>
    </header>
  );
}

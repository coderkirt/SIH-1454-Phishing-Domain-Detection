export default function LoadingState({ label = "Loading" }) {
  return (
    <div className="flex items-center gap-3 py-8">
      <span className="scan-dots scan-pulse" aria-hidden="true">
        <span className="dot dot-active" />
        <span className="dot dot-active" />
        <span className="dot dot-queued" />
        <span className="dot dot-inactive" />
        <span className="dot dot-inactive" />
      </span>
      <p className="label-tech">{label}</p>
    </div>
  );
}

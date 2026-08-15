import UrlScanner from "../components/UrlScanner";

export default function Scanner() {
  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="text-2xl font-semibold text-white">URL Scanner</h1>
      <p className="mt-2 text-slate-400">Paste a website address. The backend analyzes it and returns a real risk score.</p>
      <div className="card glow mt-6 p-6">
        <UrlScanner />
      </div>
    </div>
  );
}

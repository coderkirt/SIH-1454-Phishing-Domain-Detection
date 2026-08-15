import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ScanSearch } from "lucide-react";
import { checkUrl, getErrorMessage } from "../services/api";
import { saveLastScan } from "../utils/risk";

export default function UrlScanner({ compact = false }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    const value = url.trim();
    if (!value) {
      setError("Please enter a website URL.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const { data } = await checkUrl(value);
      saveLastScan(data);
      navigate("/scan-result");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className={compact ? "" : "w-full"}>
      <div className="flex flex-col gap-3 sm:flex-row">
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter website URL........................"
          className="w-full rounded-xl border border-slate-600/60 bg-slate-950/70 px-4 py-3.5 text-slate-100 outline-none placeholder:text-slate-500 focus:border-cyan-400/70 focus:ring-2 focus:ring-cyan-400/20"
        />
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-cyan-400 px-6 py-3.5 font-semibold text-slate-950 hover:bg-cyan-300 disabled:opacity-60"
        >
          <ScanSearch size={18} />
          {loading ? "SCANNING" : "SCAN"}
        </button>
      </div>
      {loading ? (
        <p className="mt-3 flex items-center gap-2 text-sm text-cyan-300">
          <span className="h-2 w-2 rounded-full bg-cyan-300 scan-pulse" />
          Analyzing URL...
        </p>
      ) : null}
      {error ? <p className="mt-3 text-sm text-red-400">{error}</p> : null}
    </form>
  );
}

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { connectApi, getApiBase, setApiBase } from "../services/api";

export default function ProtectHome() {
  const [apiUrl, setApiUrl] = useState(getApiBase());
  const [status, setStatus] = useState("Checking the security server…");
  const [ok, setOk] = useState(false);

  const test = async (value) => {
    setStatus("Checking the security server…");
    const result = await connectApi(value);
    setOk(result.ok);
    setApiUrl(result.base);
    setStatus(result.ok ? `Engine connected · ${result.base}` : "Engine not reachable. Save this PC address, for example http://172.16.33.52:8000");
  };

  useEffect(() => {
    test(getApiBase());
  }, []);

  return (
    <div className="mx-auto min-h-screen max-w-lg px-4 py-6">
      <header className="flex items-end justify-between border-b border-line pb-4">
        <div>
          <p className="label-tech">PhishEye Guard · build 9</p>
          <h1 className="mt-2 font-display text-3xl font-semibold uppercase leading-none text-ink">Link guard</h1>
        </div>
        <p className={`font-mono text-xs uppercase tracking-[0.14em] ${ok ? "text-[var(--risk-low)]" : "text-[var(--risk-medium)]"}`}>
          {ok ? "Live" : "Offline"}
        </p>
      </header>

      <section className="panel mt-5 p-5">
        <p className="label-tech">01 / Engine</p>
        <p className="mt-3 text-sm leading-6 text-ink">{status}</p>
        <input
          className="field mt-4 w-full font-mono"
          value={apiUrl}
          onChange={(e) => setApiUrl(e.target.value)}
          placeholder="http://172.16.33.52:8000"
          autoComplete="off"
        />
        <button
          type="button"
          className="btn-primary mt-3 w-full py-3"
          onClick={() => {
            setApiBase(apiUrl);
            test(apiUrl);
          }}
        >
          Save and test
        </button>
      </section>

      <section className="mt-4 grid gap-px border border-line bg-line">
        <button type="button" className="bg-surface p-4 text-left" onClick={() => window.PhishEyeNative?.requestBrowserRole?.()}>
          <p className="label-tech">02 / Default browser</p>
          <p className="mt-2 text-sm text-ink">WhatsApp, SMS, and mail open here first. Every tap is scored before the page loads.</p>
        </button>
        <button type="button" className="bg-surface p-4 text-left" onClick={() => window.PhishEyeNative?.openAccessibility?.()}>
          <p className="label-tech">03 / Chrome guard</p>
          <p className="mt-2 text-sm text-ink">Turn on PhishEye in Accessibility. A dangerous Chrome page is stopped from the address bar.</p>
        </button>
      </section>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <Link className="btn-secondary py-3 text-center" to="/dashboard">Console</Link>
        <Link className="btn-secondary py-3 text-center" to="/scanner">Scan</Link>
      </div>
    </div>
  );
}

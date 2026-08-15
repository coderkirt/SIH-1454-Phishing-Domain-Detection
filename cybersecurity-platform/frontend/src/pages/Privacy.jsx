import { useState } from "react";

const stored = [
  { name: "Account username, email, and password hash", status: "Stored on the server (SQLite)" },
  { name: "URLs you choose to scan, plus risk score and reasons", status: "Stored on the server (SQLite)" },
  { name: "JWT access token", status: "Stored in this browser (localStorage)" },
];

const sent = [
  "The URL you submit for analysis",
  "Signup and login details",
  "Your JWT token on protected requests such as profile",
];

const local = [
  "Theme and notification preferences (this browser only)",
  "The last scan result kept in session storage for the result page",
];

const planned = [
  "Client-side processing of URLs without sending them to a server",
  "Zero-knowledge proofs",
  "Decentralized threat database",
  "End-to-end encrypted history",
];

export default function Privacy() {
  const [shareHistory, setShareHistory] = useState(readPref("cg_share_history", false));
  const [saveHistory, setSaveHistory] = useState(readPref("cg_save_history", true));

  function readPref(key, fallback) {
    const value = localStorage.getItem(key);
    if (value === null) return fallback;
    return value === "true";
  }

  const toggle = (key, value, setter) => {
    setter(value);
    localStorage.setItem(key, String(value));
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Privacy Center</h1>
        <p className="text-muted">This page describes what the current MVP actually does. Planned ideas are labeled clearly.</p>
      </div>
      <div className="card p-6">
        <h2 className="font-medium">What this application stores</h2>
        <ul className="mt-3 space-y-2 text-sm text-ink-soft">
          {stored.map((item) => (
            <li key={item.name} className="flex flex-col gap-1 border-b border-line py-2 last:border-0 sm:flex-row sm:justify-between">
              <span>{item.name}</span>
              <span className="text-accent">{item.status}</span>
            </li>
          ))}
        </ul>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="card p-6">
          <h2 className="font-medium">Sent to the backend</h2>
          <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-ink-soft">
            {sent.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
        <div className="card p-6">
          <h2 className="font-medium">Stays locally</h2>
          <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-ink-soft">
            {local.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
      </div>
      <div className="card p-6 space-y-4">
        <h2 className="font-medium">Current privacy settings</h2>
        <label className="flex items-center justify-between gap-4 text-sm">
          Keep scan history on the server
          <input type="checkbox" checked={saveHistory} onChange={(e) => toggle("cg_save_history", e.target.checked, setSaveHistory)} />
        </label>
        <p className="text-xs text-muted">The current backend always saves scans so the dashboard can show real statistics. This toggle is a UI preference for a future per-user setting.</p>
        <label className="flex items-center justify-between gap-4 text-sm">
          Allow community threat sharing
          <input type="checkbox" checked={shareHistory} onChange={(e) => toggle("cg_share_history", e.target.checked, setShareHistory)} />
        </label>
        <p className="text-xs text-muted">Planned. Community sharing is not implemented yet.</p>
      </div>
      <div className="card p-6">
        <h2 className="font-medium">Planned (not implemented)</h2>
        <ul className="mt-3 space-y-2 text-sm text-muted">
          {planned.map((item) => (
            <li key={item} className="flex items-center justify-between gap-3">
              <span>{item}</span>
              <span className="rounded-full border border-amber-400/30 px-2 py-0.5 text-xs text-amber-300">Planned</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

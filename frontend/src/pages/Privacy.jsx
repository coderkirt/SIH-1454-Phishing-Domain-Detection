import { useState } from "react";
import PageHeader from "../components/PageHeader";
import TechnicalPanel from "../components/TechnicalPanel";

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
      <PageHeader
        section="06 / Privacy"
        title="Privacy center"
        subtitle="This page describes what the current MVP actually does. Planned ideas are labeled clearly."
      />

      <TechnicalPanel title="01 / Stored data">
        <ul className="space-y-0">
          {stored.map((item) => (
            <li key={item.name} className="grid gap-2 border-b border-line py-3 last:border-0 sm:grid-cols-[1fr_auto] sm:items-center">
              <span className="text-sm text-ink-soft">{item.name}</span>
              <span className="font-mono text-xs text-muted sm:text-right">{item.status}</span>
            </li>
          ))}
        </ul>
      </TechnicalPanel>

      <div className="grid gap-6 md:grid-cols-2">
        <TechnicalPanel title="02 / Sent to backend">
          <ul className="space-y-2">
            {sent.map((item, index) => (
              <li key={item} className="flex items-start gap-3 text-sm text-ink-soft">
                <span className="font-mono text-xs text-muted">{String(index + 1).padStart(2, "0")}</span>
                {item}
              </li>
            ))}
          </ul>
        </TechnicalPanel>
        <TechnicalPanel title="03 / Stays locally">
          <ul className="space-y-2">
            {local.map((item, index) => (
              <li key={item} className="flex items-start gap-3 text-sm text-ink-soft">
                <span className="font-mono text-xs text-muted">{String(index + 1).padStart(2, "0")}</span>
                {item}
              </li>
            ))}
          </ul>
        </TechnicalPanel>
      </div>

      <TechnicalPanel title="04 / Privacy settings">
        <label className="flex items-center justify-between gap-4 border-b border-line pb-4 text-sm">
          Keep scan history on the server
          <input type="checkbox" checked={saveHistory} onChange={(e) => toggle("cg_save_history", e.target.checked, setSaveHistory)} />
        </label>
        <p className="text-xs text-muted">The current backend always saves scans so the dashboard can show real statistics. This toggle is a UI preference for a future per-user setting.</p>
        <label className="mt-4 flex items-center justify-between gap-4 text-sm">
          Allow community threat sharing
          <input type="checkbox" checked={shareHistory} onChange={(e) => toggle("cg_share_history", e.target.checked, setShareHistory)} />
        </label>
        <p className="mt-2 text-xs text-muted">Planned. Community sharing is not implemented yet.</p>
      </TechnicalPanel>

      <TechnicalPanel title="05 / Planned">
        <ul className="space-y-0">
          {planned.map((item) => (
            <li key={item} className="flex items-center justify-between gap-3 border-b border-line py-3 last:border-0 text-sm text-muted">
              <span>{item}</span>
              <span className="status-pill risk-medium">Planned</span>
            </li>
          ))}
        </ul>
      </TechnicalPanel>
    </div>
  );
}

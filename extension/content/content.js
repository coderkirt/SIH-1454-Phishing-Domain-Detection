(() => {
  const api = typeof browser !== "undefined" ? browser : chrome;
  const WARNING_ID = "cyberguard-warning-host";
  const TOAST_ID = "cyberguard-toast-host";
  let currentUrl = location.href;

  function reasonsFrom(result) {
    if (!result) return [];
    if (Array.isArray(result.reasons) && result.reasons.length) return result.reasons;
    const warning = result.simple_view?.warning || result.simple_view?.warning_english;
    return warning ? [warning] : [];
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function palette(status) {
    if (status === "critical" || status === "high") {
      return {
        accent: "#ff2a2a",
        bg: "#1a0505",
        panel: "rgba(255, 42, 42, 0.18)",
        text: "#ffe4e4",
        muted: "#ffb4b4",
        label: "THREAT DETECTED",
        tag: status === "critical" ? "CRITICAL" : "HIGH RISK",
        pulse: "threat",
      };
    }
    if (status === "medium") {
      return {
        accent: "#f5c400",
        bg: "#1a1504",
        panel: "rgba(245, 196, 0, 0.16)",
        text: "#fff1b8",
        muted: "#e6d48a",
        label: "FISHY",
        tag: "CHECK THIS PAGE",
        pulse: "fishy",
      };
    }
    if (status === "safe") {
      return {
        accent: "#22c55e",
        bg: "#04140a",
        panel: "rgba(34, 197, 94, 0.16)",
        text: "#d4ffe4",
        muted: "#9be0b6",
        label: "NO THREAT",
        tag: "PAGE LOOKS CLEAR",
        pulse: "",
      };
    }
    return {
      accent: "#c4c4c4",
      bg: "#111111",
      panel: "rgba(255, 255, 255, 0.04)",
      text: "#f5f5f5",
      muted: "#b0b0b0",
      label: headlineFallback(status),
      tag: "SCANNING",
      pulse: "scan",
    };
  }

  function headlineFallback(status) {
    if (status === "checking") return "SCANNING";
    if (status === "unavailable") return "UNAVAILABLE";
    if (status === "failed") return "SCAN FAILED";
    return "UNKNOWN";
  }

  function removeWarning() {
    document.getElementById(WARNING_ID)?.remove();
  }

  function removeToast() {
    document.getElementById(TOAST_ID)?.remove();
  }

  function showToast(payload) {
    const status = payload?.status || "unknown";
    if (status === "unsupported" || status === "off") {
      removeToast();
      return;
    }

    removeToast();
    const host = document.createElement("div");
    host.id = TOAST_ID;
    const shadow = host.attachShadow({ mode: "closed" });
    const result = payload.result;
    const theme = palette(status);
    const score = Number(result?.risk_score);
    const scoreText = Number.isFinite(score) ? String(score) : "—";
    const bar = Number.isFinite(score) ? Math.max(6, Math.min(100, score)) : (status === "checking" ? 35 : 8);
    const level = result?.risk_level || theme.tag;
    const reason = reasonsFrom(result)[0] || payload.error || (
      status === "safe"
        ? "No phishing signals on this page. Still check the name in the address bar before you sign in."
        : status === "medium"
          ? "Something looks off. Check the address bar before you enter a password or OTP."
          : "PHISHEYE is watching this website."
    );

    shadow.innerHTML = `
      <style>
        :host { all: initial; }
        @keyframes slide-in {
          from { transform: translateX(28px); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        @keyframes pulse-threat {
          0%, 100% { box-shadow: 0 0 0 0 rgba(255, 42, 42, 0.55); }
          50% { box-shadow: 0 0 0 10px rgba(255, 42, 42, 0); }
        }
        @keyframes pulse-fishy {
          0%, 100% { box-shadow: 0 0 0 0 rgba(245, 196, 0, 0.45); }
          50% { box-shadow: 0 0 0 8px rgba(245, 196, 0, 0); }
        }
        @keyframes scan {
          0% { background-position: 0% 50%; }
          100% { background-position: 100% 50%; }
        }
        .card {
          position: fixed;
          top: 16px;
          right: 16px;
          z-index: 2147483646;
          width: min(360px, calc(100vw - 24px));
          background: ${theme.bg};
          color: ${theme.text};
          border: 2px solid ${theme.accent};
          box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45), 0 0 28px ${theme.accent}55;
          font-family: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
          padding: 16px 16px 14px;
          animation: slide-in 220ms ease-out;
        }
        .card.pulse-threat { animation: slide-in 220ms ease-out, pulse-threat 1.4s ease-out infinite; }
        .card.pulse-fishy { animation: slide-in 220ms ease-out, pulse-fishy 1.8s ease-out infinite; }
        .top { display: flex; justify-content: space-between; gap: 10px; align-items: center; }
        .brand {
          display: flex;
          align-items: center;
          gap: 8px;
          color: ${theme.accent};
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.18em;
          text-transform: uppercase;
        }
        .brand svg { display: block; width: 22px; height: 22px; }
        .tag {
          margin-left: auto;
          border: 1px solid ${theme.accent};
          background: ${theme.panel};
          color: ${theme.accent};
          font-size: 10px;
          font-weight: 700;
          letter-spacing: 0.12em;
          padding: 3px 7px;
          text-transform: uppercase;
        }
        .close {
          border: 1px solid ${theme.accent}66;
          background: transparent;
          color: ${theme.text};
          width: 28px;
          height: 28px;
          font-size: 18px;
          line-height: 1;
          cursor: pointer;
        }
        h2 {
          margin: 12px 0 4px;
          font-size: 26px;
          letter-spacing: 0.04em;
          text-transform: uppercase;
          font-family: "Space Grotesk", "Segoe UI", sans-serif;
          color: ${theme.accent};
        }
        .meta { margin: 0; color: ${theme.muted}; font-size: 12px; font-family: "IBM Plex Mono", Consolas, monospace; }
        .bar {
          margin: 12px 0 8px;
          height: 7px;
          background: rgba(255, 255, 255, 0.08);
          overflow: hidden;
        }
        .bar > span {
          display: block;
          height: 100%;
          width: ${bar}%;
          background: ${theme.accent};
        }
        .card.pulse-scan .bar > span {
          width: 40%;
          background: linear-gradient(90deg, transparent, ${theme.accent}, transparent);
          background-size: 200% 100%;
          animation: scan 1.1s linear infinite;
        }
        .reason { margin: 8px 0 0; color: ${theme.muted}; font-size: 13px; line-height: 1.45; }
      </style>
      <aside class="card ${theme.pulse ? `pulse-${theme.pulse}` : ""}" role="status" aria-live="polite">
        <div class="top">
          <span class="brand">
            <svg viewBox="0 0 32 32" fill="none" aria-hidden="true">
              <path d="M16 3L27 8.2v8.1c0 7.2-5.3 12.4-11 14.7C10.3 28.7 5 23.5 5 16.3V8.2L16 3z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
              <path d="M8.5 16c2.4-4.2 5.2-6.3 7.5-6.3S21.1 11.8 23.5 16c-2.4 4.2-5.2 6.3-7.5 6.3S10.9 20.2 8.5 16z" stroke="currentColor" stroke-width="1.4"/>
              <circle cx="16" cy="16" r="2.6" fill="${theme.accent}"/>
            </svg>
            PHISHEYE
          </span>
          <span class="tag">${escapeHtml(theme.tag)}</span>
          <button class="close" type="button" id="cg-close" aria-label="Hide PHISHEYE result">×</button>
        </div>
        <h2>${escapeHtml(theme.label)}</h2>
        <p class="meta">Risk ${escapeHtml(scoreText)} / 100 · ${escapeHtml(level)}</p>
        <div class="bar" aria-hidden="true"><span></span></div>
        <p class="reason">${escapeHtml(reason)}</p>
      </aside>
    `;
    shadow.getElementById("cg-close").addEventListener("click", removeToast);
    document.documentElement.appendChild(host);
  }

  function showWarning(payload) {
    if (!payload?.result) return;
    removeWarning();
    const host = document.createElement("div");
    host.id = WARNING_ID;
    const shadow = host.attachShadow({ mode: "closed" });
    const result = payload.result;
    const reasons = reasonsFrom(result);
    const score = result.risk_score ?? "—";
    const level = result.risk_level || "UNKNOWN";

    shadow.innerHTML = `
      <style>
        :host { all: initial; }
        .wrap {
          position: fixed;
          inset: 0;
          z-index: 2147483647;
          display: grid;
          place-items: center;
          padding: 24px;
          background: rgba(8, 8, 8, 0.86);
          font-family: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
          color: #f5f5f5;
        }
        .card {
          width: min(520px, 100%);
          background: #111111;
          border: 1px solid #292929;
          position: relative;
          padding: 28px;
        }
        .card::before, .card::after {
          content: "";
          position: absolute;
          width: 10px;
          height: 10px;
          border-color: #ff0000;
          border-style: solid;
        }
        .card::before { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
        .card::after { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }
        .brand { color: #777777; font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; }
        h1 { margin: 16px 0 8px; font-size: 28px; letter-spacing: 0.04em; text-transform: uppercase; font-family: "Space Grotesk", "Segoe UI", sans-serif; }
        .lead { color: #b0b0b0; }
        .meta { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 18px 0; }
        .pill { background: #151515; border: 1px solid #292929; padding: 12px; }
        .pill span { display: block; color: #777777; font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; }
        .warn { color: #ff0000; }
        ul { padding-left: 18px; color: #b0b0b0; }
        .actions { display: flex; gap: 10px; margin-top: 22px; flex-wrap: wrap; }
        button { border-radius: 0; padding: 12px 16px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; cursor: pointer; font-size: 12px; }
        .back { background: #ff0000; color: #ffffff; border: 1px solid #ff0000; }
        .continue { background: transparent; color: #b0b0b0; border: 1px solid #292929; }
        .note { color: #777777; font-size: 13px; }
      </style>
      <div class="wrap" role="alertdialog" aria-modal="true" aria-labelledby="cg-title">
        <div class="card">
          <div class="brand">PHISHEYE</div>
          <h1 id="cg-title">Website Warning</h1>
          <p class="lead">PHISHEYE detected a potentially dangerous website.</p>
          <div class="meta">
            <div class="pill"><span>Risk Score</span><strong>${escapeHtml(score)} / 100</strong></div>
            <div class="pill"><span>Risk Level</span><strong class="warn">${escapeHtml(level)}</strong></div>
          </div>
          <p>Detected because:</p>
          <ul>${reasons.map((item) => `<li>${escapeHtml(item)}</li>`).join("") || "<li>The PHISHEYE backend marked this site as high risk.</li>"}</ul>
          <p class="note">Do not enter passwords, OTPs, card details, or other sensitive information.</p>
          <div class="actions">
            <button class="back" type="button" id="cg-back">Go back to safety</button>
            <button class="continue" type="button" id="cg-continue">Continue anyway</button>
          </div>
        </div>
      </div>
    `;
    shadow.getElementById("cg-back").addEventListener("click", () => {
      api.runtime.sendMessage({ type: "GO_BACK" });
    });
    shadow.getElementById("cg-continue").addEventListener("click", () => {
      api.runtime.sendMessage({ type: "CONTINUE_ANYWAY", url: currentUrl });
      removeWarning();
    });
    document.documentElement.appendChild(host);
  }

  api.runtime.onMessage.addListener((message) => {
    if (message?.type === "SHOW_RESULT") {
      currentUrl = message.payload?.url || location.href;
      showToast(message.payload);
    }
    if (message?.type === "SHOW_WARNING") {
      currentUrl = message.payload?.url || location.href;
      showWarning(message.payload);
    }
    if (message?.type === "COLLECT_LINKS") {
      return Promise.resolve({ ok: true, urls: collectVisibleLinks(), host: location.hostname });
    }
    if (message?.type === "HIGHLIGHT_LINKS") {
      highlightLinks(message.links || []);
      return Promise.resolve({ ok: true });
    }
  });

  function collectVisibleLinks() {
    const urls = [];
    const seen = new Set();
    document.querySelectorAll("a[href]").forEach((anchor) => {
      if (!anchor.getClientRects().length) return;
      let href = "";
      try {
        const parsed = new URL(anchor.href, location.href);
        if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return;
        href = parsed.href;
      } catch {
        return;
      }
      if (seen.has(href)) return;
      seen.add(href);
      urls.push(href);
    });
    return urls.slice(0, 15);
  }

  function highlightLinks(links) {
    if (!document.getElementById("cg-link-style")) {
      const style = document.createElement("style");
      style.id = "cg-link-style";
      style.textContent = `
        a[data-cg-risk="CRITICAL"] { outline: 2px solid #ff0000; outline-offset: 2px; }
        a[data-cg-risk="HIGH"] { outline: 2px solid #ff0000; outline-offset: 2px; }
        a[data-cg-risk="MEDIUM"] { outline: 2px solid #c4a000; outline-offset: 2px; }
        a[data-cg-risk="LOW"] { outline: 2px solid #6b8f71; outline-offset: 2px; }
      `;
      document.documentElement.appendChild(style);
    }
    (links || []).forEach((link) => {
      const target = (link.url || "").replace(/\/$/, "");
      const finalUrl = (link.final_url || "").replace(/\/$/, "");
      document.querySelectorAll("a[href]").forEach((anchor) => {
        const href = (anchor.href || "").replace(/\/$/, "");
        if (href === target || (finalUrl && href === finalUrl)) {
          anchor.setAttribute("data-cg-risk", link.classification || "LOW");
        }
      });
    });
  }

  function collectPageSignals() {
    const onclickPopups = [...document.querySelectorAll("[onclick]")].filter((el) =>
      String(el.getAttribute("onclick") || "").toLowerCase().includes("window.open")
    ).length;
    return {
      buttons: document.querySelectorAll("button, [role='button'], input[type='submit'], input[type='button']").length,
      iframes: document.querySelectorAll("iframe").length,
      popups: onclickPopups,
      overlays: document.querySelectorAll("dialog, [aria-modal='true']").length,
      links: document.querySelectorAll("a[href]").length,
    };
  }

  api.runtime.sendMessage({ type: "PAGE_READY", url: location.href, page_signals: collectPageSignals() });
})();

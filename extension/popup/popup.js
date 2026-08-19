import { loadTheme, toggleTheme } from "../utils/theme.js";

const protection = document.getElementById("protection-status");
const accountChip = document.getElementById("account-chip");
const sitePanel = document.getElementById("site-panel");
const headlineEl = document.getElementById("headline");
const messageEl = document.getElementById("message");
const metricsEl = document.getElementById("metrics");
const scoreEl = document.getElementById("score");
const levelEl = document.getElementById("level");
const reasonsWrap = document.getElementById("reasons-wrap");
const reasonsTitle = document.getElementById("reasons-title");
const reasonsEl = document.getElementById("reasons");
const scanBtn = document.getElementById("scan-again");
const clockEl = document.getElementById("clock");
const hostEl = document.getElementById("host");

function tickClock() {
  clockEl.textContent = new Date().toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

function send(type, extra = {}) {
  return chrome.runtime.sendMessage({ type, ...extra });
}

function toneClass(status) {
  return `tone-${status || "unknown"}`;
}

function render(payload) {
  const status = payload.status || "unknown";
  const user = payload.user;
  accountChip.textContent = user?.username ? user.username : "Not signed in";

  hostEl.textContent = payload.host || payload.url || "—";
  headlineEl.className = `headline ${toneClass(status)}`;
  headlineEl.textContent = payload.headline || status.toUpperCase();
  if (sitePanel) sitePanel.className = `panel panel-accent site ${toneClass(status)}`;

  const result = payload.result;
  const hasResult = Boolean(result);
  metricsEl.hidden = !hasResult;
  reasonsWrap.hidden = !hasResult && status !== "unavailable" && status !== "failed" && status !== "unsupported" && status !== "off";

  if (hasResult) {
    scoreEl.textContent = `${result.risk_score ?? "—"} / 100`;
    levelEl.textContent = result.risk_level || "—";
    const reasons = result.reasons?.length ? result.reasons : [];
    reasonsTitle.textContent = status === "safe" ? "Why this result?" : "Why was this flagged?";
    reasonsEl.innerHTML = "";
    (reasons.length ? reasons : ["No suspicious signals were found."]).forEach((reason) => {
      const li = document.createElement("li");
      li.textContent = reason;
      reasonsEl.appendChild(li);
    });
    reasonsWrap.hidden = false;
  } else {
    reasonsEl.innerHTML = "";
  }

  const copy = {
    checking: ["Checking", "Asking the PHISHEYE backend about this page."],
    safe: ["No threat", "No malicious indicators detected. That is not a guarantee of safety."],
    medium: ["Fishy", "Something looks off. Check the address before you sign in."],
    high: ["Threat detected", "Do not enter passwords, OTPs, or card details."],
    critical: ["Threat detected", "Do not enter passwords, OTPs, or card details."],
    unavailable: ["Service unavailable", "PHISHEYE cannot say this site is safe. Unknown is not safe."],
    failed: ["Scan failed", payload.error || "The backend could not complete this scan."],
    unsupported: ["Ready", payload.error || "This browser page cannot be scanned."],
    off: ["Automatic scanning off", "Use Scan again to check this website now."],
    unknown: ["Ready", payload.error || "No result yet."],
  };
  const [statusText, message] = copy[status] || copy.unknown;
  protection.textContent = statusText;
  protection.className = `status ${toneClass(status)}`;
  messageEl.textContent = message;
}

async function loadStatus(force = false) {
  scanBtn.disabled = true;
  render({ status: "checking", headline: "CHECKING", host: hostEl.textContent, result: null });
  try {
    const payload = force ? await send("SCAN_NOW") : await send("GET_STATUS");
    if (!payload?.ok && payload?.error) {
      render({ status: "failed", headline: "SCAN FAILED", error: payload.error, result: null });
      return;
    }
    render(payload);
  } catch {
    render({
      status: "unavailable",
      headline: "UNAVAILABLE",
      error: "Protection service unavailable.",
      result: null,
    });
  } finally {
    scanBtn.disabled = false;
  }
}

scanBtn.addEventListener("click", () => loadStatus(true));
document.getElementById("open-dashboard").addEventListener("click", () => send("OPEN_DASHBOARD"));
document.getElementById("open-settings").addEventListener("click", () => send("OPEN_SETTINGS"));
document.getElementById("open-full").addEventListener("click", () => send("OPEN_PANEL", { size: "full" }));
document.getElementById("open-compact").addEventListener("click", () => send("OPEN_PANEL", { size: "compact" }));
document.getElementById("analyze-links").addEventListener("click", analyzeLinks);

async function analyzeLinks() {
  const btn = document.getElementById("analyze-links");
  btn.disabled = true;
  const wrap = document.getElementById("links-wrap");
  const counts = document.getElementById("link-counts");
  const list = document.getElementById("link-list");
  wrap.hidden = false;
  counts.innerHTML = "<p class='note'>Analyzing visible links...</p>";
  list.innerHTML = "";
  try {
    const payload = await send("ANALYZE_PAGE_LINKS");
    if (!payload?.ok) {
      counts.innerHTML = `<p class="note">${payload?.error || "Could not analyze links."}</p>`;
      return;
    }
    const summary = payload.link_summary || {};
    counts.innerHTML = ["safe", "suspicious", "risky", "phishing"].map((key) => (
      `<div class="count"><span>${key}</span><strong>${summary[key] ?? 0}</strong></div>`
    )).join("");
    list.innerHTML = "";
    (payload.links || []).forEach((link) => {
      const li = document.createElement("li");
      li.textContent = `${link.classification || "?"} ${link.risk_score}/100 — ${link.url}`;
      list.appendChild(li);
    });
    if (!(payload.links || []).length) {
      const li = document.createElement("li");
      li.textContent = "No visible http(s) links were found on this page.";
      list.appendChild(li);
    }
  } catch {
    counts.innerHTML = "<p class='note'>Protection service unavailable.</p>";
  } finally {
    btn.disabled = false;
  }
}

document.getElementById("theme-toggle").addEventListener("click", toggleTheme);
tickClock();
setInterval(tickClock, 1000);
loadTheme().then(() => loadStatus());

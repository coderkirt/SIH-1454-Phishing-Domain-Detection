import { loadTheme, toggleTheme } from "../utils/theme.js";

const form = document.getElementById("scan-form");
const input = document.getElementById("url-input");
const scanBtn = document.getElementById("scan-btn");
const panel = document.getElementById("result-panel");
const hostEl = document.getElementById("host");
const headlineEl = document.getElementById("headline");
const messageEl = document.getElementById("message");
const metricsEl = document.getElementById("metrics");
const scoreEl = document.getElementById("score");
const levelEl = document.getElementById("level");
const reasonsEl = document.getElementById("reasons");
const openSiteBtn = document.getElementById("open-site");
const openAnywayBtn = document.getElementById("open-anyway");
const stayHereBtn = document.getElementById("stay-here");
const statusLine = document.getElementById("status-line");

let compact = window.outerWidth > 0 && window.outerWidth < 700;
let currentUrl = "";
let currentStatus = "";
let opening = false;

function send(type, extra = {}) {
  return chrome.runtime.sendMessage({ type, ...extra });
}

function targetFromQuery() {
  const raw = new URLSearchParams(location.search).get("target") || "";
  return raw.trim();
}

function toneClass(status) {
  return `tone-${status || "unknown"}`;
}

function copyFor(status, error) {
  const map = {
    checking: ["Asking the PHISHEYE backend. The website is still closed.", "SCANNING"],
    safe: ["No threat found. Opening this website.", "NO THREAT"],
    medium: ["This looks fishy. PHISHEYE will not open it unless you insist.", "FISHY"],
    high: ["Threat detected. This website stays closed.", "THREAT DETECTED"],
    critical: ["Threat detected. This website stays closed.", "THREAT DETECTED"],
    unavailable: ["Protection is down. Unknown is not safe, so this stays closed.", "UNAVAILABLE"],
    failed: [error || "The scan failed. This website stays closed.", "SCAN FAILED"],
    unsupported: [error || "This address cannot be scanned.", "UNSUPPORTED"],
    unknown: ["Enter a website address to scan it before it opens.", "READY"],
  };
  return map[status] || map.unknown;
}

function render(payload) {
  const status = payload.status || "unknown";
  currentStatus = status;
  currentUrl = payload.url || currentUrl;
  panel.hidden = false;
  panel.className = `panel panel-accent site ${status === "unknown" ? "idle" : toneClass(status)}`;
  hostEl.textContent = payload.host || payload.url || "Waiting for an address";
  const [message, fallbackHeadline] = copyFor(status, payload.error);
  headlineEl.className = `headline ${toneClass(status)}`;
  headlineEl.textContent = payload.headline || fallbackHeadline;
  messageEl.textContent = message;

  const result = payload.result;
  metricsEl.hidden = !result;
  reasonsEl.innerHTML = "";
  if (result) {
    scoreEl.textContent = `${result.risk_score ?? "—"} / 100`;
    levelEl.textContent = result.risk_level || "—";
    const reasons = result.reasons?.length ? result.reasons : ["No suspicious signals were found."];
    reasons.slice(0, 3).forEach((reason) => {
      const li = document.createElement("li");
      li.textContent = reason;
      reasonsEl.appendChild(li);
    });
  } else if (payload.error) {
    const li = document.createElement("li");
    li.textContent = payload.error;
    reasonsEl.appendChild(li);
  }

  const fishy = status === "medium";
  const blocked = status === "high" || status === "critical" || status === "unavailable" || status === "failed";
  openSiteBtn.hidden = status !== "safe";
  openAnywayBtn.hidden = !fishy;
  stayHereBtn.hidden = !(fishy || blocked);

  if (status === "checking") {
    openSiteBtn.hidden = true;
    statusLine.textContent = "Scanning. The website is not open yet.";
  } else if (status === "safe") {
    openSiteBtn.hidden = true;
    statusLine.textContent = "Clear. Opening…";
  } else if (blocked || fishy) {
    statusLine.textContent = "Website not opened.";
  } else {
    statusLine.textContent = "Enter a website, or wait if PHISHEYE intercepted one.";
  }
}

async function scan(url) {
  const address = (url || input.value || "").trim();
  if (!address) {
    statusLine.textContent = "Enter a website address first.";
    input.focus();
    return;
  }
  input.value = address;
  scanBtn.disabled = true;
  openSiteBtn.hidden = true;
  openAnywayBtn.hidden = true;
  stayHereBtn.hidden = true;
  render({ status: "checking", headline: "SCANNING", url: address, host: address, result: null });
  try {
    const payload = await send("SCAN_URL", { url: address });
    if (!payload?.ok && payload?.error) {
      render({ status: "failed", error: payload.error, url: address, result: null });
      return;
    }
    render(payload);
    if (payload.status === "safe") {
      await openSite();
    }
  } catch {
    render({
      status: "unavailable",
      error: "Protection service unavailable.",
      url: address,
      result: null,
    });
  } finally {
    scanBtn.disabled = false;
  }
}

async function openSite({ forceContinue = false } = {}) {
  if (!currentUrl || opening) return;
  opening = true;
  statusLine.textContent = "Opening…";
  openSiteBtn.disabled = true;
  openAnywayBtn.disabled = true;
  try {
    const payload = await send("OPEN_AFTER_SCAN", {
      url: currentUrl,
      forceContinue,
      replaceTab: !compact,
    });
    if (!payload?.ok) {
      render(payload || { status: currentStatus, url: currentUrl, result: null, error: "PHISHEYE will not open this website." });
      statusLine.textContent = payload?.error || "Website not opened.";
      if (currentStatus === "safe") openSiteBtn.hidden = false;
      return;
    }
    if (compact) statusLine.textContent = "Opened in a new tab.";
  } catch {
    statusLine.textContent = "Could not open the website.";
    if (currentStatus === "safe") openSiteBtn.hidden = false;
  } finally {
    opening = false;
    openSiteBtn.disabled = false;
    openAnywayBtn.disabled = false;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  scan(input.value);
});

openSiteBtn.addEventListener("click", () => openSite());
openAnywayBtn.addEventListener("click", () => openSite({ forceContinue: true }));
stayHereBtn.addEventListener("click", () => {
  statusLine.textContent = "Website kept closed. Scan a different address if you need to.";
  input.focus();
});
document.getElementById("theme-toggle").addEventListener("click", toggleTheme);

loadTheme().then(async () => {
  try {
    const win = await chrome.windows.getCurrent();
    compact = win?.type === "popup";
  } catch {
    // Keep width-based fallback.
  }
  const target = targetFromQuery();
  if (target) {
    input.value = target;
    scan(target);
  } else {
    input.focus();
  }
});

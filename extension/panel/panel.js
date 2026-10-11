import { showRagPopup } from "../utils/rag-popup.js";
import { fillVersionLabels, loadTheme, toggleTheme } from "../utils/theme.js";

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
const briefEl = document.getElementById("rag-brief");
const openSiteBtn = document.getElementById("open-site");
const openAnywayBtn = document.getElementById("open-anyway");
const stayHereBtn = document.getElementById("stay-here");
const statusLine = document.getElementById("status-line");

let compact = window.outerWidth > 0 && window.outerWidth < 700;
let currentUrl = "";
let currentStatus = "";
let opening = false;
let awaitingScore = false;

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

function worseStatus(status, result) {
  const level = String(result?.risk_level || "").toUpperCase();
  const fromLevel = { CRITICAL: "critical", HIGH: "high", MEDIUM: "medium", LOW: "safe" }[level] || "";
  const rank = { critical: 5, high: 4, unavailable: 4, failed: 4, medium: 2, safe: 1 };
  const current = String(status || "").toLowerCase();
  if ((rank[fromLevel] || 0) > (rank[current] || 0)) return fromLevel;
  return current || fromLevel || "unknown";
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
}

function brandName(result) {
  const raw = result?.explanation?.brand_analysis?.impersonated_brand || result?.brand_impersonated || "";
  return String(raw).trim();
}

function plainSummary(result, status) {
  const name = brandName(result).toUpperCase();
  if (status === "critical" || status === "high") {
    return name
      ? `This page is pretending to be ${name}. It is not the real site. Do not enter your password, OTP, or card details.`
      : "This page looks like a scam. Do not enter your password, OTP, or card details.";
  }
  if (status === "medium") {
    return "Something looks off. Open the real website yourself before you sign in or send money.";
  }
  if (status === "safe") return "No threat found. Opening this website.";
  return "";
}

function renderBrief(result) {
  briefEl.replaceChildren();
  const exp = result?.explanation;
  const reasons = (result?.reasons || []).filter(Boolean).slice(0, 4);
  const brand = exp?.brand_analysis;
  const playbook = exp?.matched_playbook;
  const hasBrand = Boolean(brand?.impersonated_brand || (brand?.official_domains || []).length);
  const hasPlaybook = Boolean(playbook?.title || (playbook?.warning_signs || []).length);
  if (!reasons.length && !hasBrand && !hasPlaybook && !exp?.what_to_do) {
    briefEl.hidden = true;
    return;
  }
  briefEl.hidden = false;
  const grid = el("div", "brief-grid");

  if (reasons.length) {
    const card = el("article", "brief-card");
    card.append(el("h3", "", "Why we stopped it"));
    const list = el("ul", "brief-list");
    reasons.forEach((reason) => list.appendChild(el("li", "", reason)));
    card.appendChild(list);
    grid.appendChild(card);
  }

  const steps = el("article", "brief-card brief-action");
  steps.append(el("h3", "", "What you should do"));
  const actions = el("ul", "brief-list");
  actions.appendChild(el("li", "", "Do not type your password, OTP, or card number here."));
  const realDomain = (brand?.official_domains || []).find(Boolean);
  actions.appendChild(el("li", "", realDomain ? `Open the real site yourself: ${realDomain}` : "Type the real website yourself. Do not use this link."));
  actions.appendChild(el("li", "", "If you already entered details, change that password in the official app."));
  steps.appendChild(actions);
  grid.appendChild(steps);

  if (hasBrand) {
    const card = el("article", "brief-card");
    card.append(el("h3", "", "Who it is copying"));
    card.append(el("p", "brief-title", brandName(result).toUpperCase() || "A known brand"));
    const domains = (brand.official_domains || []).filter(Boolean).slice(0, 3);
    if (domains.length) {
      const chips = el("div", "chip-row");
      domains.forEach((domain) => chips.appendChild(el("span", "chip", domain)));
      card.appendChild(chips);
    }
    const rule = (brand.never_does_rules || []).find(Boolean);
    if (rule) card.append(el("p", "brief-rule", rule));
    grid.appendChild(card);
  }

  if (hasPlaybook) {
    const address = String(result?.url || result?.final_url || "").toLowerCase();
    const prizeInAddress = /\b(won|lottery|prize|cashback|jackpot|congratulations)\b/.test(address);
    const accessInAddress = /\b(verify|login|signin|sign-in|account|suspended|password|kyc|secure)\b/.test(address);
    const card = el("article", "brief-card brief-playbook");
    card.append(el("h3", "", "This kind of scam"));
    const list = el("ul", "brief-list");
    if (accessInAddress && !prizeInAddress) {
      card.append(el("p", "brief-title", "Trying to steal your account"));
      ["The link asks you to verify or sign in.", "The real bank does not unlock an account through a link like this."].forEach((sign) => {
        list.appendChild(el("li", "", sign));
      });
    } else if (String(playbook.playbook_id || "") === "playbook-account-suspension-lure") {
      card.append(el("p", "brief-title", "Trying to steal your account"));
      ["It says your account is locked and you must verify it.", "A real bank does not ask for your password in a link."].forEach((sign) => {
        list.appendChild(el("li", "", sign));
      });
    } else {
      if (playbook.title) card.append(el("p", "brief-title", playbook.title));
      (playbook.warning_signs || []).filter(Boolean).slice(0, 2).forEach((sign) => {
        list.appendChild(el("li", "", sign.replace(/^"|"$/g, "")));
      });
    }
    if (list.childElementCount) card.appendChild(list);
    grid.appendChild(card);
  }

  briefEl.appendChild(grid);
}

function applyActions(status) {
  const blocked = status === "high" || status === "critical" || status === "unavailable" || status === "failed" || status === "unsupported";
  const fishy = status === "medium";
  openSiteBtn.hidden = true;
  openAnywayBtn.hidden = !fishy;
  stayHereBtn.hidden = !(fishy || blocked);
  stayHereBtn.textContent = blocked ? "Keep this site closed" : "Keep closed";
  stayHereBtn.className = blocked ? "btn-primary" : "btn-danger";
  openAnywayBtn.textContent = "Open anyway";
}

function render(payload) {
  const status = worseStatus(payload.status, payload.result);
  currentStatus = status;
  currentUrl = payload.url || currentUrl;
  panel.hidden = false;
  panel.className = `panel panel-accent site ${status === "unknown" ? "idle" : toneClass(status)}`;
  hostEl.textContent = payload.host || payload.url || "Waiting for an address";
  const [message, fallbackHeadline] = copyFor(status, payload.error);
  headlineEl.className = `headline ${toneClass(status)}`;
  headlineEl.textContent = payload.headline || fallbackHeadline;
  const opened = payload.result?.final_url || payload.result?.technical_view?.final_url || "";
  const entered = payload.result?.original_url || payload.result?.technical_view?.original_url || payload.url || "";
  const summary = plainSummary(payload.result, status) || message;
  messageEl.textContent = opened && entered && opened.replace(/\/$/, "") !== entered.replace(/\/$/, "")
    ? `This link opens ${opened}. ${summary}`
    : summary;

  const result = payload.result;
  metricsEl.hidden = !result;
  reasonsEl.hidden = false;
  reasonsEl.replaceChildren();
  if (result) {
    scoreEl.textContent = `${result.risk_score ?? "—"} / 100`;
    if (awaitingScore && status !== "checking" && result.risk_score != null) {
      awaitingScore = false;
      showRagPopup(result);
    }
    levelEl.textContent = result.risk_level || "—";
    const reasons = result.reasons?.length ? result.reasons : ["No suspicious signals were found."];
    reasons.forEach((reason) => {
      reasonsEl.appendChild(el("li", "", reason));
    });
    reasonsEl.hidden = Boolean(result.explanation || result.reasons?.length);
  } else if (payload.error) {
    reasonsEl.appendChild(el("li", "", payload.error));
  }
  renderBrief(result);
  applyActions(status);

  if (status === "checking") {
    briefEl.hidden = true;
    statusLine.textContent = "Scanning. The website is not open yet.";
  } else if (status === "safe") {
    statusLine.textContent = "Clear. Opening…";
  } else if (status === "medium" || status === "high" || status === "critical" || status === "unavailable" || status === "failed") {
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
  awaitingScore = true;
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
  fillVersionLabels();
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

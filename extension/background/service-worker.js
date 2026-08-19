import {
  analyzeContent,
  canOpenAfterScan,
  checkUrl,
  clearCache,
  displayHost,
  getCachedScan,
  getProfile,
  getSettings,
  headlineFor,
  isExtensionPage,
  isOwnAppUrl,
  isScannableUrl,
  login,
  markContinued,
  markGateAllowed,
  normalizeHttpUrl,
  saveSettings,
  setCachedScan,
  statusFromResult,
  wasContinued,
  wasGateAllowed,
} from "../utils/api.js";
import { STORAGE_KEYS, registeredDomain } from "../utils/config.js";

const api = typeof browser !== "undefined" ? browser : chrome;
const inflight = new Map();
const tabState = new Map();
const gatingTabs = new Set();
let preNavigateEnabled = true;
let scanAllPagesEnabled = false;
const allowedNow = new Set();
const allowedHosts = new Set();
const allowedDomains = new Set();
const domainScan = new Map();

function hostnameOf(url) {
  try {
    return new URL(url).hostname;
  } catch {
    return "";
  }
}

function domainOf(url) {
  return registeredDomain(hostnameOf(url));
}

function rememberAllowed(url, state = null) {
  const key = normalizeHttpUrl(url);
  if (key) allowedNow.add(key);
  const host = hostnameOf(key || url);
  if (host) allowedHosts.add(host);
  const domain = registeredDomain(host);
  if (domain) {
    allowedDomains.add(domain);
    if (state) domainScan.set(domain, state);
  }
}

function loadAllowedMap(allowed) {
  allowedNow.clear();
  allowedHosts.clear();
  allowedDomains.clear();
  for (const [url, at] of Object.entries(allowed || {})) {
    if (at) rememberAllowed(url);
  }
}

async function hydrateGateState() {
  const settings = await getSettings();
  preNavigateEnabled = settings.preNavigate !== false;
  scanAllPagesEnabled = settings.scanAllPages === true;
  const data = await (api.storage.session || api.storage.local).get(STORAGE_KEYS.gateAllow);
  loadAllowedMap(data[STORAGE_KEYS.gateAllow] || {});
}

hydrateGateState().catch(() => {});
api.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && changes[STORAGE_KEYS.preNavigate]) {
    preNavigateEnabled = changes[STORAGE_KEYS.preNavigate].newValue !== false;
  }
  if (area === "local" && changes[STORAGE_KEYS.scanAllPages]) {
    scanAllPagesEnabled = changes[STORAGE_KEYS.scanAllPages].newValue === true;
  }
  if ((area === "session" || area === "local") && changes[STORAGE_KEYS.gateAllow]) {
    loadAllowedMap(changes[STORAGE_KEYS.gateAllow].newValue || {});
  }
});

function panelPageUrl(target) {
  const base = api.runtime.getURL("panel/panel.html");
  if (!target) return base;
  return `${base}?target=${encodeURIComponent(target)}`;
}

function isPanelUrl(url) {
  if (!url) return false;
  return url.startsWith(api.runtime.getURL("panel/panel.html"));
}

function setTabState(tabId, state) {
  tabState.set(tabId, { ...state, updatedAt: Date.now() });
}

function getTabState(tabId) {
  return tabState.get(tabId) || null;
}

function badgeFor(status) {
  switch (status) {
    case "checking":
      return { text: "...", color: "#606060", title: "PHISHEYE — Checking this website" };
    case "safe":
      return { text: "OK", color: "#6b8f71", title: "PHISHEYE — This website looks safe" };
    case "medium":
      return { text: "MED", color: "#c4a000", title: "PHISHEYE — Suspicious website" };
    case "high":
      return { text: "HIGH", color: "#ff0000", title: "PHISHEYE — High risk website" };
    case "critical":
      return { text: "CRIT", color: "#ff0000", title: "PHISHEYE — Critical threat" };
    case "unavailable":
      return { text: "!", color: "#606060", title: "PHISHEYE — Protection service unavailable" };
    case "failed":
      return { text: "!", color: "#606060", title: "PHISHEYE — Scan failed" };
    case "unsupported":
      return { text: "", color: "#606060", title: "PHISHEYE — This page cannot be scanned" };
    case "off":
      return { text: "OFF", color: "#606060", title: "PHISHEYE — Automatic scanning is off" };
    default:
      return { text: "", color: "#606060", title: "PHISHEYE" };
  }
}

async function updateBadge(tabId, status) {
  const badge = badgeFor(status);
  try {
    await api.action.setBadgeText({ tabId, text: badge.text });
    await api.action.setBadgeBackgroundColor({ tabId, color: badge.color });
    await api.action.setTitle({ tabId, title: badge.title });
  } catch {
    // Tab may have closed.
  }
}

async function notifyTab(tabId, message) {
  try {
    await api.tabs.sendMessage(tabId, message);
  } catch {
    // Content script may not be injected on this page.
  }
}

async function scanUrl(url, { force = false, pageSignals = null } = {}) {
  if (!isScannableUrl(url)) {
    return { status: "unsupported", url, result: null, error: "This browser page cannot be scanned." };
  }

  if (!force && !pageSignals) {
    const cached = await getCachedScan(url);
    if (cached) {
      return { status: statusFromResult(cached), url, result: cached, error: "" };
    }
  }

  const inflightKey = pageSignals ? `${url}::signals` : url;
  if (inflight.has(inflightKey)) {
    return inflight.get(inflightKey);
  }

  const promise = (async () => {
    try {
      const result = await checkUrl(url, pageSignals);
      await setCachedScan(url, result);
      return { status: statusFromResult(result), url, result, error: "" };
    } catch (error) {
      return {
        status: error.unavailable ? "unavailable" : "failed",
        url,
        result: null,
        error: error.message || "Protection service unavailable.",
      };
    } finally {
      inflight.delete(inflightKey);
    }
  })();

  inflight.set(inflightKey, promise);
  return promise;
}

async function scanTab(tabId, url, { force = false, pageSignals = null } = {}) {
  const settings = await getSettings();
  if (!url) {
    const state = { status: "unsupported", url: "", result: null, error: "No URL is available on this tab." };
    setTabState(tabId, state);
    await updateBadge(tabId, "unsupported");
    return state;
  }

  if (!isScannableUrl(url)) {
    const state = { status: "unsupported", url, result: null, error: "PHISHEYE does not scan browser internal pages." };
    setTabState(tabId, state);
    await updateBadge(tabId, "unsupported");
    return state;
  }

  if (!settings.autoScan && !force) {
    const cached = await getCachedScan(url);
    if (cached) {
      const state = { status: statusFromResult(cached), url, result: cached, error: "" };
      setTabState(tabId, state);
      await updateBadge(tabId, state.status);
      return state;
    }
    const state = { status: "off", url, result: null, error: "Automatic scanning is turned off. Use Scan again." };
    setTabState(tabId, state);
    await updateBadge(tabId, "off");
    return state;
  }

  const domain = domainOf(url);
  const scanEveryPage = settings.scanAllPages === true || scanAllPagesEnabled;
  if (!force && !pageSignals && !scanEveryPage && domain && allowedDomains.has(domain)) {
    const prior = domainScan.get(domain);
    const state = prior
      ? { ...prior, url, host: displayHost(url) }
      : { status: "safe", url, result: null, error: "" };
    setTabState(tabId, state);
    await updateBadge(tabId, state.status);
    return state;
  }

  setTabState(tabId, { status: "checking", url, result: null, error: "" });
  await updateBadge(tabId, "checking");
  await notifyPage(tabId, { status: "checking", url, result: null, error: "" }, settings);

  const state = await scanUrl(url, { force, pageSignals });
  setTabState(tabId, state);
  await updateBadge(tabId, state.status);
  await notifyPage(tabId, state, settings);
  if (state.status === "safe") rememberAllowed(url, state);
  else if (domain) domainScan.set(domain, state);
  return state;
}

async function notifyPage(tabId, state, settings) {
  if (settings.pagePopup !== false) {
    await notifyTab(tabId, { type: "SHOW_RESULT", payload: state });
  }
  if (settings.warnings && (state.status === "high" || state.status === "critical")) {
    const continued = await wasContinued(state.url);
    if (!continued) {
      await notifyTab(tabId, { type: "SHOW_WARNING", payload: state });
    }
  }
}

async function activeTab() {
  const tabs = await api.tabs.query({ active: true, currentWindow: true });
  return tabs[0] || null;
}

api.runtime.onInstalled.addListener(async (details) => {
  const settings = await getSettings();
  await saveSettings({
    apiBaseUrl: settings.apiBaseUrl,
    dashboardUrl: settings.dashboardUrl,
    autoScan: settings.autoScan,
    warnings: settings.warnings,
    preNavigate: settings.preNavigate,
    scanAllPages: settings.scanAllPages === true,
  });
  if (details.reason === "install") {
    api.tabs.create({ url: api.runtime.getURL("welcome/welcome.html") });
  }
});

api.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  const url = changeInfo.url || (changeInfo.status === "loading" ? tab.url : "");
  if (url) {
    pullTabToGate(tabId, url).catch(() => {});
  }
  if (changeInfo.status === "complete" && tab.url) {
    if (isPanelUrl(tab.url) || isExtensionPage(tab.url)) return;
    (async () => {
      if (await shouldGate(tab.url)) {
        await pullTabToGate(tabId, tab.url);
        return;
      }
      await scanTab(tabId, tab.url);
    })().catch(() => {});
  }
});

api.tabs.onActivated.addListener(async ({ tabId }) => {
  try {
    const tab = await api.tabs.get(tabId);
    if (!tab?.url) return;
    await pullTabToGate(tabId, tab.url);
    await scanTab(tabId, tab.url);
  } catch {
    // Ignore missing tabs.
  }
});

api.tabs.onRemoved.addListener((tabId) => {
  tabState.delete(tabId);
  gatingTabs.delete(tabId);
});

const SKIP_GATE_TRANSITIONS = new Set(["auto_subframe", "manual_subframe"]);

async function shouldGate(url) {
  if (!url || isPanelUrl(url) || isExtensionPage(url)) return false;
  if (!isScannableUrl(url)) return false;
  if (await isOwnAppUrl(url)) return false;
  if (preNavigateEnabled === false) {
    const settings = await getSettings();
    if (settings.preNavigate === false) return false;
    preNavigateEnabled = settings.preNavigate !== false;
  }
  const key = normalizeHttpUrl(url);
  const host = hostnameOf(key || url);
  const domain = registeredDomain(host);
  if (key && allowedNow.has(key)) return false;
  if (host && allowedHosts.has(host)) return false;
  if (domain && allowedDomains.has(domain)) return false;
  if (await wasGateAllowed(url)) {
    rememberAllowed(url);
    return false;
  }
  return true;
}

async function sendTabToGate(tabId, url) {
  if (tabId < 0 || gatingTabs.has(tabId)) return;
  gatingTabs.add(tabId);
  try {
    await api.tabs.update(tabId, { url: panelPageUrl(url) });
  } catch {
    gatingTabs.delete(tabId);
  } finally {
    setTimeout(() => gatingTabs.delete(tabId), 2500);
  }
}

async function pullTabToGate(tabId, url) {
  if (!url || tabId < 0) return;
  if (!(await shouldGate(url))) return;
  await sendTabToGate(tabId, url);
}

async function interceptNavigation(details) {
  if (details.frameId !== 0 || details.tabId < 0) return;
  if (SKIP_GATE_TRANSITIONS.has(details.transitionType)) return;
  await pullTabToGate(details.tabId, details.url);
}

if (api.webNavigation?.onBeforeNavigate) {
  api.webNavigation.onBeforeNavigate.addListener((details) => {
    interceptNavigation(details).catch(() => {});
  });
}

if (api.webNavigation?.onCommitted) {
  api.webNavigation.onCommitted.addListener((details) => {
    interceptNavigation(details).catch(() => {});
  });
}

api.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message, sender).then(sendResponse).catch((error) => {
    sendResponse({ ok: false, error: error.message || "Unexpected extension error." });
  });
  return true;
});

async function handleMessage(message, sender) {
  const type = message?.type;
  const tab = sender.tab;

  if (type === "GET_STATUS") {
    const current = await activeTab();
    if (!current) {
      return { ok: true, status: "unsupported", url: "", result: null, error: "No active tab.", host: "", headline: headlineFor("unsupported"), user: (await getSettings()).user };
    }
    const existing = getTabState(current.id);
    if (existing && existing.url === current.url && existing.status !== "checking") {
      return { ok: true, ...existing, host: displayHost(existing.url), headline: headlineFor(existing.status), user: (await getSettings()).user };
    }
    const state = await scanTab(current.id, current.url, { force: Boolean(message.force) });
    return { ok: true, ...state, host: displayHost(state.url), headline: headlineFor(state.status), user: (await getSettings()).user };
  }

  if (type === "SCAN_NOW") {
    const current = await activeTab();
    if (!current) return { ok: false, error: "No active tab." };
    const state = await scanTab(current.id, current.url, { force: true });
    return { ok: true, ...state, host: displayHost(state.url), headline: headlineFor(state.status), user: (await getSettings()).user };
  }

  if (type === "GATE_SHOULD_HOLD") {
    const settings = await getSettings();
    if (settings.preNavigate === false) return { hold: false, gatedOff: true };
    const url = normalizeHttpUrl(message.url || tab?.url || "");
    if (!url || !(await shouldGate(url))) return { hold: false };
    return { hold: true, panelUrl: panelPageUrl(url) };
  }

  if (type === "PAGE_READY") {
    if (!tab?.id) return { ok: true };
    const url = tab.url || message.url;
    if (url && (await shouldGate(url))) {
      await sendTabToGate(tab.id, url);
      return { ok: true, gated: true };
    }
    const pageSignals = message.page_signals || null;
    const existing = getTabState(tab.id);
    if (existing && existing.url === url && !pageSignals) {
      await notifyPage(tab.id, existing, await getSettings());
      return { ok: true, ...existing };
    }
    const state = await scanTab(tab.id, url, { force: false, pageSignals });
    return { ok: true, ...state };
  }

  if (type === "GATE_NAVIGATE") {
    const url = normalizeHttpUrl(message.url);
    if (!url) return { ok: false, error: "No website address." };
    if (!(await shouldGate(url))) {
      const tabId = tab?.id;
      if (message.newTab) await api.tabs.create({ url, active: true });
      else if (tabId) await api.tabs.update(tabId, { url });
      return { ok: true, skipped: true };
    }
    if (message.newTab) {
      await api.tabs.create({ url: panelPageUrl(url), active: true });
    } else if (tab?.id) {
      await sendTabToGate(tab.id, url);
    } else {
      await api.tabs.create({ url: panelPageUrl(url), active: true });
    }
    return { ok: true };
  }

  if (type === "CONTINUE_ANYWAY") {
    const url = message.url || tab?.url;
    if (url) await markContinued(url);
    return { ok: true };
  }

  if (type === "GO_BACK") {
    const tabId = tab?.id || (await activeTab())?.id;
    if (!tabId) return { ok: false, error: "No tab to leave." };
    try {
      await api.tabs.goBack(tabId);
    } catch {
      await api.tabs.update(tabId, { url: "chrome://newtab/" });
    }
    return { ok: true };
  }

  if (type === "LOGIN") {
    const data = await login(message.username, message.password);
    const user = { username: data.username };
    await saveSettings({ token: data.access_token, user });
    try {
      const profile = await getProfile();
      await saveSettings({ user: profile });
      return { ok: true, user: profile };
    } catch {
      return { ok: true, user };
    }
  }

  if (type === "LOGOUT") {
    await saveSettings({ token: "", user: null });
    return { ok: true };
  }

  if (type === "GET_SETTINGS") {
    return { ok: true, settings: await getSettings() };
  }

  if (type === "SAVE_SETTINGS") {
    await saveSettings(message.settings || {});
    await clearCache();
    return { ok: true, settings: await getSettings() };
  }

  if (type === "CLEAR_CACHE") {
    await clearCache();
    return { ok: true };
  }

  if (type === "OPEN_DASHBOARD") {
    const settings = await getSettings();
    const path = message.path || "/dashboard";
    await api.tabs.create({ url: `${settings.dashboardUrl}${path}` });
    return { ok: true };
  }

  if (type === "OPEN_SETTINGS") {
    if (api.runtime.openOptionsPage) await api.runtime.openOptionsPage();
    else await api.tabs.create({ url: api.runtime.getURL("settings/settings.html") });
    return { ok: true };
  }

  if (type === "OPEN_PANEL") {
    const compact = message.size === "compact";
    if (compact) {
      await api.windows.create({
        url: panelPageUrl(message.url || ""),
        type: "popup",
        width: 420,
        height: 740,
        focused: true,
      });
    } else {
      await api.windows.create({
        url: panelPageUrl(message.url || ""),
        type: "normal",
        state: "maximized",
        focused: true,
      });
    }
    return { ok: true };
  }

  if (type === "SCAN_URL") {
    const url = normalizeHttpUrl(message.url);
    if (!url) return { ok: false, error: "Enter a website address first." };
    const state = await scanUrl(url, { force: true, pageSignals: message.page_signals || null });
    return {
      ok: true,
      ...state,
      host: displayHost(state.url),
      headline: headlineFor(state.status),
      user: (await getSettings()).user,
    };
  }

  if (type === "OPEN_AFTER_SCAN") {
    const url = normalizeHttpUrl(message.url);
    if (!url) return { ok: false, error: "No website address." };
    const state = await scanUrl(url, { force: Boolean(message.force) });
    if (!canOpenAfterScan(state.status, { forceContinue: Boolean(message.forceContinue) })) {
      return {
        ok: false,
        blocked: true,
        ...state,
        host: displayHost(state.url),
        headline: headlineFor(state.status),
        error: state.error || "PHISHEYE will not open this website.",
      };
    }
    await markGateAllowed(url);
    rememberAllowed(url, state);
    const replaceTab = message.replaceTab !== false && tab?.id;
    if (replaceTab) {
      await api.tabs.update(tab.id, { url });
    } else {
      await api.tabs.create({ url, active: true });
    }
    return {
      ok: true,
      ...state,
      host: displayHost(state.url),
      headline: headlineFor(state.status),
    };
  }

  if (type === "ANALYZE_PAGE_LINKS") {
    const current = await activeTab();
    if (!current?.id) return { ok: false, error: "No active tab." };
    if (!isScannableUrl(current.url)) {
      return { ok: false, error: "This browser page cannot be scanned." };
    }
    let collected;
    try {
      collected = await api.tabs.sendMessage(current.id, { type: "COLLECT_LINKS" });
    } catch {
      return { ok: false, error: "Reload the page so the PHISHEYE content script can run. Password fields and cookies are never read." };
    }
    const urls = (collected?.urls || []).slice(0, 15);
    if (!urls.length) {
      return { ok: true, links: [], link_summary: { total: 0, safe: 0, suspicious: 0, risky: 0, phishing: 0 } };
    }
    try {
      const result = await analyzeContent({
        source_type: "webpage",
        urls,
        text: urls.join("\n"),
      });
      await api.tabs.sendMessage(current.id, { type: "HIGHLIGHT_LINKS", links: result.links || [] }).catch(() => {});
      return {
        ok: true,
        links: result.links || [],
        link_summary: result.link_summary || {},
        risk_score: result.risk_score,
        risk_level: result.risk_level,
      };
    } catch (error) {
      return { ok: false, error: error.message || "Could not analyze page links." };
    }
  }

  return { ok: false, error: "Unknown message." };
}

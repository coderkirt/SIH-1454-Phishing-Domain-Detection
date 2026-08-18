import {
  analyzeContent,
  checkUrl,
  clearCache,
  displayHost,
  getCachedScan,
  getProfile,
  getSettings,
  headlineFor,
  isScannableUrl,
  login,
  markContinued,
  saveSettings,
  setCachedScan,
  statusFromResult,
  wasContinued,
} from "../utils/api.js";

const api = typeof browser !== "undefined" ? browser : chrome;
const inflight = new Map();
const tabState = new Map();

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

async function scanUrl(url, { force = false } = {}) {
  if (!isScannableUrl(url)) {
    return { status: "unsupported", url, result: null, error: "This browser page cannot be scanned." };
  }

  if (!force) {
    const cached = await getCachedScan(url);
    if (cached) {
      return { status: statusFromResult(cached), url, result: cached, error: "" };
    }
  }

  if (inflight.has(url)) {
    return inflight.get(url);
  }

  const promise = (async () => {
    try {
      const result = await checkUrl(url);
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
      inflight.delete(url);
    }
  })();

  inflight.set(url, promise);
  return promise;
}

async function scanTab(tabId, url, { force = false } = {}) {
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

  setTabState(tabId, { status: "checking", url, result: null, error: "" });
  await updateBadge(tabId, "checking");
  await notifyPage(tabId, { status: "checking", url, result: null, error: "" }, settings);

  const state = await scanUrl(url, { force });
  setTabState(tabId, state);
  await updateBadge(tabId, state.status);
  await notifyPage(tabId, state, settings);
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
  });
  if (details.reason === "install") {
    api.tabs.create({ url: api.runtime.getURL("welcome/welcome.html") });
  }
});

api.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url) {
    scanTab(tabId, tab.url);
  }
});

api.tabs.onActivated.addListener(async ({ tabId }) => {
  try {
    const tab = await api.tabs.get(tabId);
    if (tab?.url) scanTab(tabId, tab.url);
  } catch {
    // Ignore missing tabs.
  }
});

api.tabs.onRemoved.addListener((tabId) => {
  tabState.delete(tabId);
});

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

  if (type === "PAGE_READY") {
    if (!tab?.id) return { ok: true };
    const url = tab.url || message.url;
    const existing = getTabState(tab.id);
    if (existing && existing.url === url) {
      await notifyPage(tab.id, existing, await getSettings());
      return { ok: true, ...existing };
    }
    const state = await scanTab(tab.id, url);
    return { ok: true, ...state };
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

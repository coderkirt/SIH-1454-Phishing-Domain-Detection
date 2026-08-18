import { loadTheme, toggleTheme } from "../utils/theme.js";

const accountLine = document.getElementById("account-line");
const loginForm = document.getElementById("login-form");
const logoutBtn = document.getElementById("logout");
const authStatus = document.getElementById("auth-status");
const saveStatus = document.getElementById("save-status");
const autoScan = document.getElementById("auto-scan");
const pagePopup = document.getElementById("page-popup");
const warnings = document.getElementById("warnings");
const apiUrl = document.getElementById("api-url");
const dashboardUrl = document.getElementById("dashboard-url");

function send(type, extra = {}) {
  return chrome.runtime.sendMessage({ type, ...extra });
}

function showAccount(user) {
  if (user?.username) {
    accountLine.textContent = `Signed in as ${user.username}${user.email ? ` (${user.email})` : ""}.`;
    loginForm.hidden = true;
    logoutBtn.hidden = false;
  } else {
    accountLine.textContent = "Not signed in. You can still scan because the backend allows URL checks without a login.";
    loginForm.hidden = false;
    logoutBtn.hidden = true;
  }
}

async function load() {
  const payload = await send("GET_SETTINGS");
  const settings = payload.settings || {};
  autoScan.checked = settings.autoScan !== false;
  pagePopup.checked = settings.pagePopup !== false;
  warnings.checked = settings.warnings !== false;
  apiUrl.value = settings.apiBaseUrl || "";
  dashboardUrl.value = settings.dashboardUrl || "";
  showAccount(settings.user);
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  authStatus.textContent = "Signing in...";
  try {
    const payload = await send("LOGIN", {
      username: document.getElementById("username").value.trim(),
      password: document.getElementById("password").value,
    });
    document.getElementById("password").value = "";
    if (!payload.ok) throw new Error(payload.error || "Login failed.");
    showAccount(payload.user);
    authStatus.textContent = "Signed in. The password was not stored.";
  } catch (error) {
    authStatus.textContent = error.message || "Login failed.";
  }
});

logoutBtn.addEventListener("click", async () => {
  await send("LOGOUT");
  showAccount(null);
  authStatus.textContent = "Signed out.";
});

document.getElementById("save").addEventListener("click", async () => {
  saveStatus.textContent = "Saving...";
  await send("SAVE_SETTINGS", {
    settings: {
      autoScan: autoScan.checked,
      pagePopup: pagePopup.checked,
      warnings: warnings.checked,
      apiBaseUrl: apiUrl.value.trim(),
      dashboardUrl: dashboardUrl.value.trim(),
    },
  });
  saveStatus.textContent = "Settings saved. Temporary scan cache was cleared.";
});

document.getElementById("clear-cache").addEventListener("click", async () => {
  await send("CLEAR_CACHE");
  saveStatus.textContent = "Temporary cache cleared.";
});

document.getElementById("open-dashboard").addEventListener("click", () => send("OPEN_DASHBOARD"));
document.getElementById("theme-toggle").addEventListener("click", toggleTheme);

loadTheme().then(() => load());

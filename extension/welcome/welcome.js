import { loadTheme } from "../utils/theme.js";

const startPanel = document.getElementById("start-panel");
const nextPanel = document.getElementById("next-panel");
const authStatus = document.getElementById("auth-status");

function send(type, extra = {}) {
  return chrome.runtime.sendMessage({ type, ...extra });
}

document.getElementById("get-started").addEventListener("click", async () => {
  await send("SAVE_SETTINGS", { settings: { welcomeSeen: true } });
  startPanel.hidden = true;
  nextPanel.hidden = false;
});

document.getElementById("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  authStatus.textContent = "Signing in...";
  try {
    const payload = await send("LOGIN", {
      username: document.getElementById("username").value.trim(),
      password: document.getElementById("password").value,
    });
    document.getElementById("password").value = "";
    if (!payload.ok) throw new Error(payload.error || "Login failed.");
    authStatus.textContent = "Signed in. You can close this tab and pin PHISHEYE.";
  } catch (error) {
    authStatus.textContent = error.message || "Login failed.";
  }
});

document.getElementById("continue").addEventListener("click", async () => {
  await send("SAVE_SETTINGS", { settings: { welcomeSeen: true } });
  window.close();
});

loadTheme();

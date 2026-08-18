const THEME_KEY = "phishshield-theme";

export function applyTheme(theme) {
  const next = theme === "light" ? "light" : "dark";
  document.documentElement.classList.remove("light", "dark");
  document.documentElement.classList.add(next);
  document.documentElement.dataset.theme = next;
  document.documentElement.style.colorScheme = next;
  return next;
}

export async function loadTheme() {
  const data = await chrome.storage.local.get(THEME_KEY);
  return applyTheme(data[THEME_KEY] === "light" ? "light" : "dark");
}

export async function toggleTheme() {
  const current = document.documentElement.classList.contains("light") ? "light" : "dark";
  const next = current === "dark" ? "light" : "dark";
  applyTheme(next);
  await chrome.storage.local.set({ [THEME_KEY]: next });
  return next;
}

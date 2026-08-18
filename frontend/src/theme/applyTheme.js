export const THEME_KEY = "cyberguard-theme";
export const LEGACY_THEME_KEY = "cg_theme";

export function readStoredTheme() {
  try {
    const stored = localStorage.getItem(THEME_KEY) || localStorage.getItem(LEGACY_THEME_KEY);
    return stored === "light" ? "light" : "dark";
  } catch {
    return "dark";
  }
}

export function applyTheme(theme) {
  const next = theme === "light" ? "light" : "dark";
  const root = document.documentElement;
  root.classList.remove("light", "dark");
  root.classList.add(next);
  root.dataset.theme = next;
  root.style.colorScheme = next;
  try {
    localStorage.setItem(THEME_KEY, next);
  } catch {
    /* ignore quota / private mode */
  }
  return next;
}

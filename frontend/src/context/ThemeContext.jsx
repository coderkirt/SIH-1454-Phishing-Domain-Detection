import { createContext, useContext, useMemo, useState } from "react";
import { applyTheme, readStoredTheme } from "../theme/applyTheme";

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(() => {
    const initial = readStoredTheme();
    applyTheme(initial);
    return initial;
  });

  const value = useMemo(() => ({
    theme,
    isDark: theme === "dark",
    setTheme: (next) => setThemeState(applyTheme(next)),
    toggleTheme: () => setThemeState((current) => applyTheme(current === "dark" ? "light" : "dark")),
  }), [theme]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used inside ThemeProvider");
  return ctx;
}

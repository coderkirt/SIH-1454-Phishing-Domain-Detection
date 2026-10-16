export function isNativeApp() {
  if (typeof window === "undefined") return false;
  const capacitor = window.Capacitor;
  if (!capacitor) return false;
  try {
    if (typeof capacitor.isNativePlatform === "function") {
      return Boolean(capacitor.isNativePlatform());
    }
  } catch {
    /* ignore */
  }
  const platform = typeof capacitor.getPlatform === "function" ? capacitor.getPlatform() : capacitor.platform;
  return platform === "android" || platform === "ios";
}

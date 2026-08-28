/**
 * Stop the destination from becoming usable before PHISHEYE scans it.
 * Link clicks never start the navigation. Address-bar loads are hidden, then
 * replaced with the gate unless this host was already allowed after a scan.
 */
(() => {
  const api = typeof browser !== "undefined" ? browser : chrome;
  const PASS_KEY = "phisheye_host_pass";

  function isHttpUrl(value) {
    try {
      const parsed = new URL(value, location.href);
      return parsed.protocol === "http:" || parsed.protocol === "https:";
    } catch {
      return false;
    }
  }

  function isLocalApp(value) {
    try {
      const parsed = new URL(value, location.href);
      const host = parsed.hostname;
      if (host !== "127.0.0.1" && host !== "localhost") return false;
      return parsed.port === "5173" || parsed.port === "8000";
    } catch {
      return false;
    }
  }

  function registeredDomain(hostname) {
    const host = String(hostname || "").split(":")[0].toLowerCase().replace(/^www\./, "");
    const parts = host.split(".").filter(Boolean);
    const multi = ["co.in", "com.au", "co.uk", "org.in", "net.in", "gov.in", "ac.in", "edu.in", "co.jp", "com.br"];
    if (parts.length >= 3 && multi.includes(`${parts[parts.length - 2]}.${parts[parts.length - 1]}`)) {
      return parts.slice(-3).join(".");
    }
    return parts.length >= 2 ? parts.slice(-2).join(".") : host;
  }

  function sameSite(value) {
    try {
      const parsed = new URL(value, location.href);
      return registeredDomain(parsed.hostname) === registeredDomain(location.hostname);
    } catch {
      return false;
    }
  }

  function siteAlreadyOpen() {
    try {
      return sessionStorage.getItem(PASS_KEY) === "1";
    } catch {
      return false;
    }
  }

  function sameDocument(value) {
    try {
      const parsed = new URL(value, location.href);
      return parsed.origin === location.origin && parsed.pathname === location.pathname && parsed.search === location.search;
    } catch {
      return false;
    }
  }

  function releaseHold() {
    const html = document.documentElement;
    if (!html) return;
    html.style.setProperty("visibility", "visible", "important");
    if (document.body) document.body.style.setProperty("visibility", "visible", "important");
  }

  function resolveHref(anchor) {
    const raw = anchor.getAttribute("href");
    if (!raw || raw.startsWith("#") || raw.startsWith("javascript:") || raw.startsWith("mailto:") || raw.startsWith("tel:")) {
      return "";
    }
    try {
      return new URL(raw, location.href).href;
    } catch {
      return "";
    }
  }

  function goToGate(url, newTab) {
    api.runtime.sendMessage({ type: "GATE_NAVIGATE", url, newTab }).catch(() => {
      if (newTab) window.open(url, "_blank", "noopener");
      else location.assign(url);
    });
  }

  function gateClick(event) {
    if (event.defaultPrevented) return;
    if (event.button !== 0 && event.button !== 1) return;
    const anchor = event.target?.closest?.("a[href]");
    if (!anchor) return;
    const href = resolveHref(anchor);
    if (!href || !isHttpUrl(href) || isLocalApp(href) || sameDocument(href)) return;
    if (siteAlreadyOpen() && sameSite(href)) return;
    event.preventDefault();
    event.stopPropagation();
    const newTab = event.button === 1 || event.metaKey || event.ctrlKey || anchor.target === "_blank";
    goToGate(href, newTab);
  }

  function gateSubmit(event) {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    if ((form.method || "get").toLowerCase() === "post") return;
    const action = form.action || location.href;
    if (!isHttpUrl(action) || isLocalApp(action)) return;
    let next;
    try {
      next = new URL(action, location.href);
      const data = new FormData(form);
      for (const [key, value] of data.entries()) {
        if (typeof value === "string") next.searchParams.append(key, value);
      }
    } catch {
      return;
    }
    if (sameDocument(next.href) || (siteAlreadyOpen() && sameSite(next.href))) return;
    event.preventDefault();
    event.stopPropagation();
    goToGate(next.href, form.target === "_blank");
  }

  function decideHold() {
    if (isLocalApp(location.href)) {
      releaseHold();
      return;
    }
    try {
      if (sessionStorage.getItem(PASS_KEY) === "1") {
        releaseHold();
        return;
      }
    } catch {
      // Private mode may block sessionStorage. Ask the background script.
    }

    api.runtime.sendMessage({ type: "GATE_SHOULD_HOLD", url: location.href }, (response) => {
      if (api.runtime.lastError || !response || response.hold === false) {
        if (!response?.gatedOff) {
          try {
            sessionStorage.setItem(PASS_KEY, "1");
          } catch {
            // Ignore storage failures.
          }
        }
        releaseHold();
        return;
      }
      window.stop();
      if (response.panelUrl) location.replace(response.panelUrl);
      else releaseHold();
    });
  }

  decideHold();
  document.addEventListener("click", gateClick, true);
  document.addEventListener("auxclick", gateClick, true);
  document.addEventListener("submit", gateSubmit, true);
})();

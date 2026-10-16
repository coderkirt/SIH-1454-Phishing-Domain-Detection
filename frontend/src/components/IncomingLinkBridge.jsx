import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { extractHttpUrl } from "../utils/incomingUrl";

function openIncoming(navigate, raw) {
  const url = extractHttpUrl(raw);
  if (!url) return;
  navigate(`/incoming?url=${encodeURIComponent(url)}`, { replace: true });
}

export default function IncomingLinkBridge() {
  const navigate = useNavigate();

  useEffect(() => {
    const go = (raw) => openIncoming(navigate, raw);
    const onCustom = (event) => go(event.detail);
    window.addEventListener("phisheye-incoming", onCustom);

    const params = new URLSearchParams(window.location.search);
    if (params.get("incoming")) go(params.get("incoming"));

    let handle = null;
    try {
      const App = window.Capacitor?.Plugins?.App;
      if (typeof App?.addListener === "function") {
        const result = App.addListener("appUrlOpen", (data) => go(data?.url));
        if (result && typeof result.then === "function") {
          result.then((value) => {
            handle = value;
          }).catch(() => {});
        } else {
          handle = result;
        }
      }
      if (typeof App?.getLaunchUrl === "function") {
        const launch = App.getLaunchUrl();
        if (launch && typeof launch.then === "function") {
          launch.then((result) => go(result?.url)).catch(() => {});
        }
      }
    } catch {
      /* Capacitor App plugin is optional on this screen */
    }

    return () => {
      window.removeEventListener("phisheye-incoming", onCustom);
      try {
        handle?.remove?.();
      } catch {
        /* ignore */
      }
    };
  }, [navigate]);

  return null;
}

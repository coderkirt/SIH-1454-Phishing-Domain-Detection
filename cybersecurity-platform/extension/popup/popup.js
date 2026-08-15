const API_URL = "http://localhost:8000";

const urlInput = document.getElementById("url");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");

async function loadCurrentUrl() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab?.url) urlInput.value = tab.url;
  } catch {
    urlInput.value = "";
  }
}

document.getElementById("scan").addEventListener("click", async () => {
  const url = urlInput.value.trim();
  if (!url) {
    statusEl.textContent = "Enter a URL first.";
    return;
  }
  statusEl.textContent = "Analyzing URL...";
  resultEl.hidden = true;
  try {
    const response = await fetch(`${API_URL}/api/v1/threat/check-url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, view: "both" }),
    });
    if (!response.ok) throw new Error("Backend error");
    const data = await response.json();
    document.getElementById("score").textContent = `${data.risk_score}/100`;
    document.getElementById("level").textContent = data.risk_level;
    document.getElementById("safe").textContent = data.safe ? "Yes" : "No";
    document.getElementById("warning").textContent = data.simple_view?.warning || (data.reasons || []).join("; ");
    resultEl.hidden = false;
    statusEl.textContent = "Result from CyberGuard backend.";
  } catch {
    statusEl.textContent = "Unable to connect to the security server. Start the backend on http://localhost:8000.";
  }
});

loadCurrentUrl();

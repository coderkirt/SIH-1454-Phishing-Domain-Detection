"""Capture real UI screenshots for the synopsis (Fig. 8 scan result, Fig. 9 history).

Starts the FastAPI backend (on a throw-away SQLite file so backend/threats.db is
untouched) and the Vite dev server, drives the web console with Playwright and
saves PNGs into synopsis_generator/figures/.  Nothing in the project source is
modified.  If anything fails, the build script falls back to a placeholder.
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)

API = "http://127.0.0.1:8000"
WEB = "http://127.0.0.1:5173"
SAMPLE_URL = "http://sbi-netbanking-secure-verify-kyc.xyz/login/update-account"


def wait_http(url: str, timeout: float = 90) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                if r.status < 500:
                    return True
        except Exception:
            time.sleep(1)
    return False


def port_free(port: int) -> bool:
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def main() -> int:
    procs = []
    tmpdb = Path(tempfile.mkdtemp(prefix="phisheye_shot_")) / "shots.db"
    try:
        if port_free(8000):
            env = dict(os.environ, PHISHEYE_SKIP_FEED_WARMUP="1", DATABASE_PATH=str(tmpdb))
            py = BACKEND / "venv" / "Scripts" / "python.exe"
            procs.append(subprocess.Popen(
                [str(py), "-m", "uvicorn", "app.main:app", "--port", "8000"],
                cwd=BACKEND, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        if port_free(5173):
            procs.append(subprocess.Popen(
                "npm run dev -- --port 5173 --strictPort", shell=True, cwd=FRONTEND,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        if not wait_http(API + "/health"):
            print("backend did not start"); return 1
        if not wait_http(WEB):
            print("frontend did not start"); return 1

        # account via API
        body = json.dumps({"username": "synopsis_demo", "email": "demo@example.com", "password": "Demo#12345"}).encode()
        req = urllib.request.Request(API + "/api/v1/user/signup", data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                auth = json.loads(r.read())
        except Exception:
            req = urllib.request.Request(API + "/api/v1/user/login", data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                auth = json.loads(r.read())
        token = auth["access_token"]

        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome")
            ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
            page = ctx.new_page()
            page.goto(WEB + "/")
            page.evaluate(
                "([t,u]) => { localStorage.setItem('cg_token', t); localStorage.setItem('cg_user', JSON.stringify({username: u})); }",
                [token, "synopsis_demo"],
            )
            # two scans so history has content
            for url in (SAMPLE_URL, "https://www.wikipedia.org/"):
                page.goto(WEB + "/scanner")
                page.wait_for_selector("#target-url", timeout=30000)
                page.fill("#target-url", url)
                page.click("button:has-text('Analyze URL')")
                page.wait_for_url("**/scan-result", timeout=120000)
                page.wait_for_timeout(1500)
                if url == SAMPLE_URL:
                    # compose: header + summary panels + evidence/technical panels
                    main = page.locator("main").first if page.locator("main").count() else page.locator("body")
                    top = page.locator("section", has_text="Risk score").first
                    evid = page.locator("section", has_text="Analysis evidence").first
                    top.scroll_into_view_if_needed()
                    top.screenshot(path=str(OUT / "_fig8_top.png"))
                    evid.scroll_into_view_if_needed()
                    page.evaluate(
                        "() => { for (const el of document.querySelectorAll('*')) { const p = getComputedStyle(el).position; "
                        "if (p === 'sticky' || p === 'fixed') { el.dataset.synHidden = '1'; el.style.visibility = 'hidden'; } } }"
                    )
                    page.wait_for_timeout(200)
                    evid.screenshot(path=str(OUT / "_fig8_evidence.png"))
                    page.evaluate(
                        "() => { for (const el of document.querySelectorAll('[data-syn-hidden]')) { el.style.visibility = ''; } }"
                    )
                    page.evaluate("window.scrollTo(0,0)")
                    page.wait_for_timeout(300)
                    page.screenshot(path=str(OUT / "_fig8_header.png"), clip={"x": 0, "y": 0, "width": 1440, "height": 160})
                    from PIL import Image
                    parts = [Image.open(OUT / n) for n in ("_fig8_header.png", "_fig8_top.png", "_fig8_evidence.png")]
                    w = max(im.width for im in parts)
                    gap = 24
                    h = sum(im.height for im in parts) + gap * (len(parts) - 1)
                    canvas = Image.new("RGB", (w, h), (10, 10, 12))
                    y = 0
                    for im in parts:
                        canvas.paste(im, ((w - im.width) // 2, y))
                        y += im.height + gap
                    canvas.save(OUT / "fig8_scan_result.png")
                    for n in ("_fig8_header.png", "_fig8_top.png", "_fig8_evidence.png"):
                        (OUT / n).unlink(missing_ok=True)
                    print("saved fig8_scan_result.png")
            page.goto(WEB + "/history")
            page.wait_for_timeout(2500)
            page.screenshot(path=str(OUT / "fig9_history.png"), full_page=False)
            print("saved fig9_history.png")
            browser.close()
        return 0
    finally:
        for pr in procs:
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pr.pid)], capture_output=True)
            except Exception:
                pr.kill()
        shutil.rmtree(tmpdb.parent, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())

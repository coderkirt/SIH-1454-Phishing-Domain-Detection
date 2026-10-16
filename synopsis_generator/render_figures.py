"""
Render synopsis figures as SVG and rasterise them to 300-dpi-class PNGs
(2800 px wide) with Playwright + the locally installed Chrome.

Figures 1-7 are drawn here. Figures 8-9 are screenshots (capture_screenshots.py).
"""

from __future__ import annotations

import html
from pathlib import Path

OUT = Path(__file__).resolve().parent / "figures"

NAVY = "#0B1F3A"
TEAL = "#12A4A4"
BG = "#EAF1F8"
AMBER = "#F5A623"
RED = "#D64545"
GREEN = "#2FA66A"
ORANGE = "#E8762B"
WHITE = "#FFFFFF"
INK = "#1F2A37"
MUTED = "#4A5568"
LINE = "#8FA3BA"

TEAL_TINT = "#D9F2F2"
AMBER_TINT = "#FFF1D6"
GREEN_TINT = "#E2F4EA"
RED_TINT = "#FBE3E3"
ORANGE_TINT = "#FCE8DA"
GREY_TINT = "#EDF0F4"

FONT = "'Segoe UI', 'Inter', Arial, sans-serif"


class Canvas:
    def __init__(self, width: int, height: int):
        self.w = width
        self.h = height
        self.parts: list[str] = []

    # ------------------------------------------------------------------ core
    def text(self, x, y, s, *, size=26, color=INK, anchor="middle", weight=500, italic=False, family=FONT):
        style = f"font-family:{family};font-size:{size}px;font-weight:{weight};fill:{color};"
        if italic:
            style += "font-style:italic;"
        self.parts.append(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="middle" style="{style}">{html.escape(str(s))}</text>'
        )

    def lines(self, cx, cy, lines, *, size=26, color=INK, gap=1.25, weight=500, anchor="middle", italic=False):
        n = len(lines)
        step = size * gap
        start = cy - (n - 1) * step / 2
        for i, line in enumerate(lines):
            self.text(cx, start + i * step, line, size=size, color=color, anchor=anchor, weight=weight, italic=italic)

    def box(self, x, y, w, h, lines, *, fill=BG, stroke=NAVY, color=INK, size=26, weight=600, rx=18, sw=3, shadow=True, icon=None, icon_size=None, dashed=False, icon_top=False):
        flt = ' filter="url(#shadow)"' if shadow else ""
        dash = ' stroke-dasharray="14 10"' if dashed else ""
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}{flt}/>'
        )
        if icon and icon_top:
            isz = icon_size or int(h * 0.3)
            self.text(x + w / 2, y + isz * 0.75, icon, size=isz, family="'Segoe UI Emoji','Segoe UI Symbol'")
            self.lines(x + w / 2, y + isz * 1.3 + (h - isz * 1.3) / 2, lines, size=size, color=color, weight=weight)
        elif icon:
            isz = icon_size or int(h * 0.42)
            self.text(x + 34 + isz / 2, y + h / 2, icon, size=isz, family="'Segoe UI Emoji','Segoe UI Symbol'")
            self.lines(x + isz + 60 + (w - isz - 60) / 2, y + h / 2, lines, size=size, color=color, weight=weight)
        else:
            self.lines(x + w / 2, y + h / 2, lines, size=size, color=color, weight=weight)
        return {"x": x, "y": y, "w": w, "h": h, "cx": x + w / 2, "cy": y + h / 2, "l": x, "r": x + w, "t": y, "b": y + h}

    def circle(self, cx, cy, r, lines, *, fill=BG, stroke=NAVY, size=24, number=None, color=INK):
        self.parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="3.5" filter="url(#shadow)"/>'
        )
        if number is not None:
            self.parts.append(
                f'<line x1="{cx - r * 0.72}" y1="{cy - r * 0.42}" x2="{cx + r * 0.72}" y2="{cy - r * 0.42}" stroke="{stroke}" stroke-width="2.5"/>'
            )
            self.text(cx, cy - r * 0.66, number, size=size + 2, color=NAVY, weight=700)
            self.lines(cx, cy + r * 0.2, lines, size=size, color=color, weight=600)
        else:
            self.lines(cx, cy, lines, size=size, color=color, weight=600)
        return {"cx": cx, "cy": cy, "r": r, "l": cx - r, "r_": cx + r, "t": cy - r, "b": cy + r}

    def ellipse(self, cx, cy, rx, ry, lines, *, fill=WHITE, stroke=NAVY, size=24):
        self.parts.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="3" filter="url(#shadow)"/>'
        )
        self.lines(cx, cy, lines, size=size, weight=600)
        return {"cx": cx, "cy": cy, "l": cx - rx, "r": cx + rx, "t": cy - ry, "b": cy + ry}

    def diamond(self, cx, cy, hw, hh, lines, *, fill=AMBER_TINT, stroke=AMBER, size=24):
        pts = f"{cx},{cy - hh} {cx + hw},{cy} {cx},{cy + hh} {cx - hw},{cy}"
        self.parts.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="3.5" filter="url(#shadow)"/>')
        self.lines(cx, cy, lines, size=size, weight=700)
        return {"cx": cx, "cy": cy, "l": cx - hw, "r": cx + hw, "t": cy - hh, "b": cy + hh}

    def arrow(self, pts, *, color=NAVY, width=4.5, label=None, label_size=22, label_dx=0, label_dy=-14, dashed=False, head=True, label_anchor="middle", label_color=None):
        d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
        marker = f' marker-end="url(#arrow-{self._mk(color)})"' if head else ""
        dash = ' stroke-dasharray="16 11"' if dashed else ""
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{dash}{marker}/>')
        if label:
            # place label at midpoint of the longest segment
            best = None
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                length = abs(x2 - x1) + abs(y2 - y1)
                if best is None or length > best[0]:
                    best = (length, (x1 + x2) / 2, (y1 + y2) / 2)
            _, mx, my = best
            self.label(mx + label_dx, my + label_dy, label, size=label_size, anchor=label_anchor, color=label_color or color)

    def label(self, x, y, s, *, size=22, anchor="middle", color=NAVY, weight=600):
        # white halo for readability over lines
        style = f"font-family:{FONT};font-size:{size}px;font-weight:{weight};"
        self.parts.append(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="middle" style="{style}fill:{color};stroke:{WHITE};stroke-width:9px;paint-order:stroke;stroke-linejoin:round;">{html.escape(str(s))}</text>'
        )

    def band(self, x, y, w, h, title, *, fill="#F6F9FC", stroke="#CBD6E2"):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        pill_w = 18 * len(title) * 0.62 + 40
        self.parts.append(f'<rect x="{x + 18}" y="{y - 20}" width="{pill_w}" height="40" rx="20" fill="{NAVY}"/>')
        self.text(x + 18 + pill_w / 2, y, title, size=19, color=WHITE, weight=700)

    def datastore(self, x, y, w, h, code, name):
        # open-ended rectangle (Gane-Sarson)
        self.parts.append(f'<path d="M {x + w},{y} L {x},{y} L {x},{y + h} L {x + w},{y + h}" fill="{GREY_TINT}" stroke="{NAVY}" stroke-width="3.5"/>')
        self.parts.append(f'<line x1="{x + 70}" y1="{y}" x2="{x + 70}" y2="{y + h}" stroke="{NAVY}" stroke-width="3"/>')
        self.text(x + 35, y + h / 2, code, size=24, weight=700, color=NAVY)
        self.text(x + 70 + (w - 70) / 2, y + h / 2, name, size=24, weight=600)
        return {"l": x, "r": x + w, "t": y, "b": y + h, "cx": x + w / 2, "cy": y + h / 2}

    def entity(self, x, y, w, h, lines, *, size=24):
        return self.box(x, y, w, h, lines, fill=TEAL_TINT, stroke=TEAL, size=size, rx=6, weight=700)

    def actor(self, cx, cy, label, *, color=NAVY):
        r = 22
        self.parts.append(f'<circle cx="{cx}" cy="{cy - 70}" r="{r}" fill="{WHITE}" stroke="{color}" stroke-width="4"/>')
        self.parts.append(f'<line x1="{cx}" y1="{cy - 48}" x2="{cx}" y2="{cy + 10}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
        self.parts.append(f'<line x1="{cx - 36}" y1="{cy - 30}" x2="{cx + 36}" y2="{cy - 30}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
        self.parts.append(f'<line x1="{cx}" y1="{cy + 10}" x2="{cx - 30}" y2="{cy + 60}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
        self.parts.append(f'<line x1="{cx}" y1="{cy + 10}" x2="{cx + 30}" y2="{cy + 60}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
        self.lines(cx, cy + 100, label if isinstance(label, list) else [label], size=23, weight=700, color=color)
        return {"cx": cx, "cy": cy, "t": cy - 92, "b": cy + 60, "l": cx - 36, "r": cx + 36}

    def legend(self, x, y, items, *, size=21, swatch=26, gap=34):
        cy = y
        for fill, stroke, label in items:
            self.parts.append(f'<rect x="{x}" y="{cy - swatch / 2}" width="{swatch}" height="{swatch}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')
            self.text(x + swatch + 14, cy, label, size=size, anchor="start", color=MUTED, weight=600)
            cy += gap

    def legend_row(self, x, y, items, *, size=21, swatch=26, spacing=None):
        cx = x
        for fill, stroke, label in items:
            self.parts.append(f'<rect x="{cx}" y="{y - swatch / 2}" width="{swatch}" height="{swatch}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')
            self.text(cx + swatch + 12, y, label, size=size, anchor="start", color=MUTED, weight=600)
            cx += swatch + 12 + (spacing or (len(label) * size * 0.56 + 44))

    # ---------------------------------------------------------------- output
    @staticmethod
    def _mk(color):
        return color.strip("#").lower()

    def svg(self) -> str:
        colors = {NAVY, TEAL, RED, GREEN, AMBER, ORANGE, MUTED, LINE}
        markers = "".join(
            f'<marker id="arrow-{self._mk(c)}" markerWidth="16" markerHeight="16" refX="14" refY="8" orient="auto" markerUnits="userSpaceOnUse">'
            f'<path d="M1,1 L15,8 L1,15 Z" fill="{c}"/></marker>'
            for c in colors
        )
        defs = (
            "<defs>"
            '<filter id="shadow" x="-10%" y="-10%" width="130%" height="140%">'
            f'<feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="{NAVY}" flood-opacity="0.16"/>'
            "</filter>"
            f"{markers}</defs>"
        )
        body = "".join(self.parts)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
            f'<rect width="100%" height="100%" fill="{WHITE}"/>{defs}{body}</svg>'
        )


# ====================================================================== figures

def fig1_architecture() -> Canvas:
    c = Canvas(1400, 1330)
    left, width = 40, 1080

    # Layer 1 clients
    c.band(left, 70, width, 190, "LAYER 1 · CLIENTS", fill="#F2FBFB", stroke="#A9DEDE")
    web = c.box(130, 118, 400, 100, ["React web console", "scan, history, reports"], fill=TEAL_TINT, stroke=TEAL, icon="🌐", size=25)
    ext = c.box(630, 118, 400, 100, ["Chrome extension (MV3)", "scan-before-open gate"], fill=TEAL_TINT, stroke=TEAL, icon="🧩", size=25)

    # Layer 2 service
    c.band(left, 310, width, 160, "LAYER 2 · SERVICE")
    api = c.box(230, 350, 700, 90, ["FastAPI service", "REST / JSON API · login · request validation"], fill=NAVY, stroke=NAVY, color=WHITE, icon="⚙️", size=25)

    # Layer 3 analysis
    c.band(left, 520, width, 250, "LAYER 3 · ANALYSIS ENGINES")
    ey, eh, ew = 580, 150, 232
    ex0 = left + 22
    qr = c.box(ex0, ey, ew, eh, ["QR decoder", "(OpenCV)"], icon="📷", size=22, icon_top=True)
    url = c.box(ex0 + ew + 70, ey, ew, eh, ["URL & domain", "heuristics"], icon="🔍", size=22, icon_top=True)
    intel = c.box(ex0 + 2 * ew + 92, ey, ew, eh, ["Threat-intelligence", "feeds"], icon="🛰️", size=22, icon_top=True)
    psych = c.box(ex0 + 3 * ew + 114, ey, ew, eh, ["Psychological /", "NLP rules"], icon="🧠", size=22, icon_top=True)

    # Layer 4 decision
    c.band(left, 810, width, 160, "LAYER 4 · RISK DECISION", fill="#FFF8EC", stroke="#F3D59A")
    dec = c.box(230, 850, 700, 90, ["Risk decision engine", "weighted signal fusion · confirmed-feed minimum score"], fill=AMBER_TINT, stroke=AMBER, icon="⚖️", size=25)

    # Layer 5 explainability
    c.band(left, 1020, width, 190, "LAYER 5 · EXPLAINABILITY", fill="#F1FAF4", stroke="#A9DDBD")
    simple = c.box(130, 1068, 400, 100, ["Simple View", "plain-language warning"], fill=GREEN_TINT, stroke=GREEN, icon="💬", size=25)
    tech = c.box(630, 1068, 400, 100, ["Technical View", "signals and feed matches"], fill=GREEN_TINT, stroke=GREEN, icon="🧾", size=25)

    # Storage column
    db = c.box(1160, 560, 200, 300, ["SQLite", "database", "", "users · scans", "reports"], fill=GREY_TINT, stroke=MUTED, size=23, rx=26)
    c.text(1260, 596, "🗄️", size=52, family="'Segoe UI Emoji'")
    c.parts.append(f'<rect x="1160" y="560" width="200" height="300" rx="26" fill="none" stroke="{MUTED}" stroke-width="3"/>')

    # arrows clients -> api
    c.arrow([(web["cx"], web["b"]), (web["cx"], api["t"])], label="HTTPS / JSON", label_dx=-120)
    c.arrow([(ext["cx"], ext["b"]), (ext["cx"], api["t"])], label="HTTPS / JSON", label_dx=120)

    # api -> engines via bus
    bus_y = 505
    c.arrow([(api["cx"], api["b"]), (api["cx"], bus_y)], head=False)
    c.parts.append(f'<line x1="{qr["cx"]}" y1="{bus_y}" x2="{psych["cx"]}" y2="{bus_y}" stroke="{NAVY}" stroke-width="4.5" stroke-linecap="round"/>')
    for b in (qr, url, intel, psych):
        c.arrow([(b["cx"], bus_y), (b["cx"], b["t"])])
    c.label(api["cx"] + 150, bus_y - 16, "submitted URL, message text or image", size=20)

    # qr -> url heuristics (decoded url)
    c.arrow([(qr["r"], qr["cy"]), (url["l"], url["cy"])], color=TEAL)
    c.label((qr["r"] + url["l"]) / 2, ey - 22, "decoded URL", size=18, color=TEAL)

    # engines -> decision via bus
    bus2 = 790
    for b in (url, intel, psych):
        c.arrow([(b["cx"], b["b"]), (b["cx"], bus2)], head=False)
    c.parts.append(f'<line x1="{url["cx"]}" y1="{bus2}" x2="{psych["cx"]}" y2="{bus2}" stroke="{NAVY}" stroke-width="4.5" stroke-linecap="round"/>')
    c.arrow([(dec["cx"], bus2), (dec["cx"], dec["t"])])
    c.label(dec["cx"] + 230, bus2 - 16, "independent signals (0–100 each)", size=20)

    # decision -> explainability
    bus3 = 1000
    c.arrow([(dec["cx"], dec["b"]), (dec["cx"], bus3)], head=False)
    c.parts.append(f'<line x1="{simple["cx"]}" y1="{bus3}" x2="{tech["cx"]}" y2="{bus3}" stroke="{NAVY}" stroke-width="4.5" stroke-linecap="round"/>')
    c.arrow([(simple["cx"], bus3), (simple["cx"], simple["t"])])
    c.arrow([(tech["cx"], bus3), (tech["cx"], tech["t"])])
    c.label(dec["cx"], bus3 - 16, "score 0–100 + level", size=20)

    # storage arrows
    c.arrow([(api["r"], api["cy"]), (1260, api["cy"]), (1260, db["t"])], color=MUTED, label="accounts, history", label_dy=-16, label_dx=40)
    c.arrow([(dec["r"], dec["cy"]), (1260, dec["cy"]), (1260, db["b"])], color=MUTED, label="save scan result", label_dy=18, label_dx=40)

    # response note
    c.text(580, 1250, "Both views are returned to the client (web console or extension) through the FastAPI service.", size=20, color=MUTED, italic=True)

    # legend
    c.legend_row(60, 1300, [
        (TEAL_TINT, TEAL, "Clients"),
        (NAVY, NAVY, "Service"),
        (BG, NAVY, "Analysis engines"),
        (AMBER_TINT, AMBER, "Risk decision"),
        (GREEN_TINT, GREEN, "Explainability"),
        (GREY_TINT, MUTED, "Storage"),
    ], size=20)
    return c


def fig2_dfd0() -> Canvas:
    c = Canvas(1400, 720)
    sys = c.circle(700, 360, 165, ["PhishEye", "phishing detection", "system"], number="0", size=26)
    user = c.entity(40, 130, 300, 110, ["User", "(web console)"])
    ext = c.entity(40, 480, 300, 110, ["Chrome extension"])
    feeds = c.entity(1080, 290, 280, 100, ["Threat-intelligence", "feed services"], size=23)

    # user flows (two parallel-ish lines, no crossing)
    c.arrow([(user["r"], 160), (sys["cx"] - 115, 245)], label="URL, message text, QR image", label_dy=-28, label_dx=-40)
    c.arrow([(sys["cx"] - 155, 290), (user["r"], 215)], label="risk score, level, explanation", label_dy=30, label_dx=-10)
    # extension flows
    c.arrow([(ext["r"], 510), (sys["cx"] - 155, 435)], label="page URL before it opens", label_dy=-30, label_dx=-10)
    c.arrow([(sys["cx"] - 115, 480), (ext["r"], 565)], label="open / ask / block decision", label_dy=44, label_dx=-20)
    # feeds
    c.arrow([(sys["r_"], 318), (feeds["l"], 318)], label="lookup request", label_dy=-24, label_size=21)
    c.arrow([(feeds["l"], 362), (sys["r_"], 362)], label="match / miss / unavailable", label_dy=26, label_size=21)

    c.legend_row(60, 670, [(TEAL_TINT, TEAL, "External entity"), (BG, NAVY, "Process"), (WHITE, NAVY, "Data flow (labelled arrow)")], size=20)
    return c


def fig3_dfd1() -> Canvas:
    c = Canvas(1400, 1000)
    r = 92
    user = c.entity(20, 130, 180, 100, ["User /", "extension"], size=23)
    p1 = c.circle(330, 180, r, ["Receive &", "normalise input"], number="1.0", size=21)
    p2 = c.circle(660, 180, r, ["Analyse URL", "& domain"], number="2.0", size=21)
    p3 = c.circle(990, 180, r, ["Check threat", "feeds"], number="3.0", size=21)
    p4 = c.circle(330, 540, r, ["Detect psycho-", "logical patterns"], number="4.0", size=21)
    p5 = c.circle(660, 540, r, ["Compute risk", "score & level"], number="5.0", size=21)
    p6 = c.circle(990, 540, r, ["Build Simple &", "Technical view"], number="6.0", size=21)
    feedsvc = c.entity(1170, 130, 200, 100, ["Threat-feed", "services"], size=23)
    d2 = c.datastore(1150, 360, 230, 64, "D2", "Feed cache")
    d1 = c.datastore(480, 770, 430, 64, "D1", "SQLite database")
    user2 = c.entity(20, 490, 180, 100, ["User /", "extension"], size=23)

    c.arrow([(user["r"], 180), (p1["l"], 180)], label="input", label_dy=-26, label_size=20)
    c.arrow([(p1["r_"], 180), (p2["l"], 180)], label="URLs found", label_dy=-24, label_size=20)
    c.arrow([(p2["r_"], 180), (p3["l"], 180)], label="clean URL", label_dy=-24, label_size=20)
    c.arrow([(p3["r_"], 160), (feedsvc["l"], 160)], label="query", label_dy=-20, label_size=20)
    c.arrow([(feedsvc["l"], 200), (p3["r_"], 200)], label="verdict", label_dy=22, label_size=20)
    c.arrow([(p3["cx"] + 50, p3["b"] - 14), (1200, d2["t"])], color=MUTED, label="cache hit / store", label_dy=-18, label_dx=50, label_size=20)
    c.arrow([(p1["cx"], p1["b"]), (p4["cx"], p4["t"])], label="message text", label_dx=-95, label_dy=0, label_anchor="middle")
    c.arrow([(p2["cx"], p2["b"]), (p5["cx"], p5["t"])], label="URL / domain signals", label_dx=0, label_dy=-30)
    c.arrow([(p3["cx"] - 40, p3["b"] - 12), (p5["cx"] + 68, p5["t"] + 22)], label="feed verdict", label_dy=-10, label_dx=60)
    c.arrow([(p4["r_"], 540), (p5["l"], 540)], label="psychology score", label_dy=-22)
    c.arrow([(p5["r_"], 540), (p6["l"], 540)], label="score & level", label_dy=-22)
    c.arrow([(p5["cx"], p5["b"]), (p5["cx"], d1["t"])], label="save scan", label_dx=80, label_dy=0)
    c.arrow([(p6["cx"], p6["b"]), (p6["cx"], 900), (110, 900), (110, user2["b"])], label="explanation & decision", label_dy=22)
    c.legend_row(40, 960, [(TEAL_TINT, TEAL, "External entity"), (BG, NAVY, "Process (numbered)"), (GREY_TINT, NAVY, "Data store")], size=20)
    return c


def fig4_use_case() -> Canvas:
    c = Canvas(1400, 1040)
    c.parts.append(f'<rect x="300" y="40" width="820" height="960" rx="24" fill="#F7FAFD" stroke="{NAVY}" stroke-width="3"/>')
    c.text(710, 80, "PhishEye", size=30, weight=700, color=NAVY)

    lx = 490
    ys = [150, 260, 370, 480, 590, 700, 810, 920]
    names = [
        ["Register / login"],
        ["Scan URL"],
        ["Scan QR / screenshot"],
        ["Scan pasted message"],
        ["View Simple &", "Technical report"],
        ["Report as scam /", "risky / safe"],
        ["Give feedback", "on a result"],
        ["View & delete", "history"],
    ]
    ovals = [c.ellipse(lx, y, 150, 38, n, size=22) for y, n in zip(ys, names)]

    rx = 930
    gate = c.ellipse(rx, 150, 150, 38, ["Gate browser", "navigation"], size=22)
    feeds = c.ellipse(rx, 480, 150, 38, ["Query threat-", "intelligence feeds"], size=22)

    user = c.actor(130, 520, "User")
    for o in ovals:
        c.arrow([(user["r"], 500), (o["l"], o["cy"])], head=False, width=3, color=MUTED)
    extn = c.actor(1270, 150, ["Chrome", "extension"])
    c.arrow([(extn["l"], 140), (gate["r"], gate["cy"])], head=False, width=3, color=MUTED)
    feedact = c.actor(1270, 480, ["Threat-feed", "services"])
    c.arrow([(feedact["l"], 470), (feeds["r"], feeds["cy"])], head=False, width=3, color=MUTED)

    # include / extend
    scan_url = ovals[1]
    scan_qr = ovals[2]
    view = ovals[4]
    report = ovals[5]
    fb = ovals[6]
    c.arrow([(gate["l"], gate["cy"] + 10), (scan_url["r"], scan_url["cy"] - 10)], dashed=True, color=TEAL, width=3, label="<<include>>", label_dy=-18)
    c.arrow([(scan_url["r"], scan_url["cy"] + 12), (feeds["l"], feeds["cy"] - 10)], dashed=True, color=TEAL, width=3, label="<<include>>", label_dy=22, label_dx=30)
    c.arrow([(scan_qr["cx"], scan_qr["t"]), (scan_url["cx"], scan_url["b"])], dashed=True, color=TEAL, width=3, label="<<include>>", label_dx=120, label_dy=0)
    c.arrow([(report["cx"], report["t"]), (view["cx"], view["b"])], dashed=True, color=TEAL, width=3, label="<<extend>>", label_dx=120, label_dy=0)
    c.arrow([(fb["r"], fb["cy"]), (700, fb["cy"]), (700, view["cy"]), (view["r"], view["cy"])], dashed=True, color=TEAL, width=3, label="<<extend>>", label_dx=0, label_dy=0, label_anchor="middle")

    c.legend_row(300, 1020, [(WHITE, NAVY, "Use case"), (WHITE, MUTED, "Association"), (WHITE, TEAL, "<<include>> / <<extend>> (dashed)")], size=20)
    return c


def fig5_er() -> Canvas:
    c = Canvas(1400, 1230)
    DY = 50

    def entity(x, y, name, rows):
        y = y + DY
        w, hh, rh = 320, 50, 32
        h = hh + rh * len(rows) + 14
        c.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{WHITE}" stroke="{NAVY}" stroke-width="3" filter="url(#shadow)"/>')
        c.parts.append(f'<path d="M {x + 12},{y} H {x + w - 12} Q {x + w},{y} {x + w},{y + 12} V {y + hh} H {x} V {y + 12} Q {x},{y} {x + 12},{y}" fill="{NAVY}"/>')
        c.text(x + w / 2, y + hh / 2, name, size=25, weight=700, color=WHITE)
        for i, (col, tag) in enumerate(rows):
            yy = y + hh + 10 + i * rh + rh / 2
            c.text(x + 18, yy, col, size=21, anchor="start", weight=600 if tag else 500, color=INK)
            if tag:
                color = TEAL if tag == "PK" else AMBER
                c.parts.append(f'<rect x="{x + w - 64}" y="{yy - 13}" width="48" height="26" rx="8" fill="{color}"/>')
                c.text(x + w - 40, yy, tag, size=16, weight=700, color=WHITE)
        return {"l": x, "r": x + w, "t": y, "b": y + h, "cx": x + w / 2, "cy": y + h / 2}

    users = entity(60, 70, "users", [("id", "PK"), ("username", ""), ("email", ""), ("password_hash", ""), ("created_at", "")])
    urlc = entity(540, 70, "url_checks", [("id", "PK"), ("user_id", "FK"), ("url", ""), ("risk_level", ""), ("risk_score", ""), ("ml_confidence", ""), ("timestamp", "")])
    cs = entity(1020, 70, "content_scans", [("id", "PK"), ("user_id", "FK"), ("source_type", ""), ("url", ""), ("risk_level / risk_score", ""), ("scam_risk / confidence", ""), ("created_at", "")])
    reports = entity(60, 520, "user_reports", [("id", "PK"), ("user_id", "FK"), ("url", ""), ("domain", ""), ("user_label", ""), ("reason", ""), ("created_at", "")])
    fb = entity(540, 560, "scan_feedback", [("id", "PK"), ("scan_id", "FK"), ("helpful", ""), ("created_at", "")])
    links = entity(1020, 520, "extracted_links", [("id", "PK"), ("scan_id", "FK"), ("url", ""), ("domain", ""), ("risk_score", ""), ("classification", "")])
    rep = entity(60, 880, "domain_reputation", [("domain", "PK"), ("scam_reports", ""), ("risky_reports", ""), ("safe_reports", ""), ("last_reported", "")])
    threats = entity(540, 880, "threats (feed snapshot)", [("id", "PK"), ("threat_type", ""), ("threat_data", ""), ("severity", ""), ("last_updated", "")])

    def one_bar(x, y, horiz, dir_):
        # bar perpendicular to the line, 22px from endpoint
        if horiz:
            bx = x - dir_ * 22
            c.parts.append(f'<line x1="{bx}" y1="{y - 14}" x2="{bx}" y2="{y + 14}" stroke="{NAVY}" stroke-width="3.5"/>')
        else:
            by = y - dir_ * 22
            c.parts.append(f'<line x1="{x - 14}" y1="{by}" x2="{x + 14}" y2="{by}" stroke="{NAVY}" stroke-width="3.5"/>')

    def crow(x, y, horiz, dir_, color=NAVY):
        # dir_ = +1 means the line arrives moving in +x (or +y); foot opens toward the entity edge at (x,y)
        if horiz:
            sx = x - dir_ * 30
            for off in (-14, 0, 14):
                c.parts.append(f'<line x1="{sx}" y1="{y}" x2="{x}" y2="{y + off}" stroke="{color}" stroke-width="3.5"/>')
        else:
            sy = y - dir_ * 30
            for off in (-14, 0, 14):
                c.parts.append(f'<line x1="{x}" y1="{sy}" x2="{x + off}" y2="{y}" stroke="{color}" stroke-width="3.5"/>')

    def rel(pts, *, one_at_start=True, dashed=False, color=NAVY, label=None, label_dx=0, label_dy=-16):
        d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
        dash = ' stroke-dasharray="14 10"' if dashed else ""
        c.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3.5" stroke-linejoin="round"{dash}/>')
        (x0, y0), (x1, y1) = pts[0], pts[1]
        horiz0 = y0 == y1
        dir0 = 1 if (x1 > x0 if horiz0 else y1 > y0) else -1
        (xa, ya), (xb, yb) = pts[-2], pts[-1]
        horiz1 = ya == yb
        dir1 = 1 if (xb > xa if horiz1 else yb > ya) else -1
        if one_at_start:
            one_bar(x0, y0, horiz0, -dir0)
            crow(xb, yb, horiz1, dir1, color)
        else:
            crow(x0, y0, horiz0, -dir0, color)
            one_bar(xb, yb, horiz1, dir1)
        if label:
            mx = (pts[0][0] + pts[-1][0]) / 2 + label_dx
            my = (pts[0][1] + pts[-1][1]) / 2 + label_dy
            c.label(mx, my, label, size=19, color=color)

    # declared foreign keys (solid)
    rel([(users["r"], 160 + DY), (urlc["l"], 160 + DY)], label="1 : N", label_dy=-20)
    rel([(cs["cx"] + 40, cs["b"]), (links["cx"] + 40, links["t"])], label="1 : N", label_dx=60, label_dy=0)
    # logical references (dashed, no FK constraint)
    top_y = 40
    rel([(users["cx"], users["t"]), (users["cx"], top_y), (cs["cx"], top_y), (cs["cx"], cs["t"])], dashed=True, color=MUTED)
    c.label((users["cx"] + cs["cx"]) / 2, top_y - 20, "1 : N (logical user_id, no constraint)", size=19, color=MUTED)
    rel([(users["cx"] - 60, users["b"]), (reports["cx"] - 60, reports["t"])], dashed=True, color=MUTED, label="1 : N (logical)", label_dx=100, label_dy=0)
    rel([(cs["cx"] - 60, cs["b"]), (cs["cx"] - 60, 470 + DY), (fb["cx"], 470 + DY), (fb["cx"], fb["t"])], dashed=True, color=MUTED, label="1 : N (logical scan_id)", label_dy=-18, label_dx=-60)
    rel([(rep["cx"], rep["t"]), (reports["cx"], reports["b"])], one_at_start=True, dashed=True, color=TEAL, label="aggregated by domain", label_dx=150, label_dy=0)

    c.lines(threats["cx"], threats["b"] + 30, ["independent table filled from public feeds"], size=19, color=MUTED, italic=True)

    # legend (bottom right, inside canvas)
    lx, ly = 1000, 1010 + DY
    c.parts.append(f'<rect x="{lx - 20}" y="{ly - 30}" width="380" height="150" rx="14" fill="#F7FAFD" stroke="#CBD6E2" stroke-width="2"/>')
    c.parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 60}" y2="{ly}" stroke="{NAVY}" stroke-width="3.5"/>')
    c.parts.append(f'<line x1="{lx + 30}" y1="{ly - 14}" x2="{lx + 30}" y2="{ly + 14}" stroke="{NAVY}" stroke-width="3.5"/>')
    c.text(lx + 75, ly, "one", size=19, anchor="start", color=MUTED, weight=600)
    c.parts.append(f'<line x1="{lx + 150}" y1="{ly}" x2="{lx + 210}" y2="{ly}" stroke="{NAVY}" stroke-width="3.5"/>')
    for off in (-14, 0, 14):
        c.parts.append(f'<line x1="{lx + 180}" y1="{ly}" x2="{lx + 210}" y2="{ly + off}" stroke="{NAVY}" stroke-width="3.5"/>')
    c.text(lx + 225, ly, "many", size=19, anchor="start", color=MUTED, weight=600)
    c.parts.append(f'<line x1="{lx}" y1="{ly + 42}" x2="{lx + 60}" y2="{ly + 42}" stroke="{NAVY}" stroke-width="3.5"/>')
    c.text(lx + 75, ly + 42, "declared foreign key", size=19, anchor="start", color=MUTED, weight=600)
    c.parts.append(f'<line x1="{lx}" y1="{ly + 84}" x2="{lx + 60}" y2="{ly + 84}" stroke="{MUTED}" stroke-width="3.5" stroke-dasharray="14 10"/>')
    c.text(lx + 75, ly + 84, "logical reference (no constraint)", size=19, anchor="start", color=MUTED, weight=600)
    return c


def fig6_risk_flow() -> Canvas:
    c = Canvas(1400, 1330)
    start = c.box(450, 40, 500, 84, ["Input: URL, pasted message or QR image"], fill=TEAL_TINT, stroke=TEAL, rx=42, size=25)
    norm = c.box(400, 180, 600, 96, ["Normalise the address, unwrap short links,", "block internal-network destinations"], size=23)
    c.arrow([(start["cx"], start["b"]), (norm["cx"], norm["t"])])

    bus = 320
    c.arrow([(norm["cx"], norm["b"]), (norm["cx"], bus)], head=False)
    a = c.box(100, 360, 380, 110, ["URL & domain heuristics", "lookalike brand, new domain, TLS"], size=22)
    b = c.box(510, 360, 380, 110, ["Psychological language rules", "urgency, fear, OTP request"], size=22)
    d = c.box(920, 360, 380, 110, ["Brand & sender checks", "impersonation, reply-to mismatch"], size=22)
    c.parts.append(f'<line x1="{a["cx"]}" y1="{bus}" x2="{d["cx"]}" y2="{bus}" stroke="{NAVY}" stroke-width="4.5" stroke-linecap="round"/>')
    for bx in (a, b, d):
        c.arrow([(bx["cx"], bus), (bx["cx"], bx["t"])])
    c.label(a["cx"] - 60, bus - 18, "parallel analysis", size=20)

    bus2 = 520
    for bx in (a, b, d):
        c.arrow([(bx["cx"], bx["b"]), (bx["cx"], bus2)], head=False)
    c.parts.append(f'<line x1="{a["cx"]}" y1="{bus2}" x2="{d["cx"]}" y2="{bus2}" stroke="{NAVY}" stroke-width="4.5" stroke-linecap="round"/>')
    feed = c.box(400, 570, 600, 90, ["Threat-feed check", "OpenPhish · URLhaus · PhishTank · Phishing Army"], size=22)
    c.arrow([(feed["cx"], bus2), (feed["cx"], feed["t"])])

    dia = c.diamond(700, 790, 190, 80, ["Confirmed", "malicious match?"], size=22)
    c.arrow([(feed["cx"], feed["b"]), (dia["cx"], dia["t"])])
    floor = c.box(960, 748, 380, 84, ["Raise score to the feed", "minimum (55 – 85)"], fill=RED_TINT, stroke=RED, size=22)
    c.arrow([(dia["r"], dia["cy"]), (floor["l"], floor["cy"])], color=RED, label="yes", label_dy=-18)
    fuse = c.box(400, 930, 600, 96, ["Combine weighted signals", "(message-language signals alone cap the score at MEDIUM)"], fill=AMBER_TINT, stroke=AMBER, size=22)
    c.arrow([(dia["cx"], dia["b"]), (fuse["cx"], fuse["t"])], label="no", label_dx=-30)
    c.arrow([(floor["cx"], floor["b"]), (floor["cx"], fuse["cy"]), (fuse["r"], fuse["cy"])], color=RED)

    score = c.box(500, 1080, 400, 80, ["Risk score 0 – 100"], fill=NAVY, stroke=NAVY, color=WHITE, size=25)
    c.arrow([(fuse["cx"], fuse["b"]), (score["cx"], score["t"])])

    bus3 = 1195
    c.arrow([(score["cx"], score["b"]), (score["cx"], bus3)], head=False)
    levels = [
        (100, "LOW", "0 – 29", GREEN_TINT, GREEN),
        (430, "MEDIUM", "30 – 49", AMBER_TINT, AMBER),
        (760, "HIGH", "50 – 69", ORANGE_TINT, ORANGE),
        (1090, "CRITICAL", "70 – 100", RED_TINT, RED),
    ]
    boxes = []
    for x, name, rng, fill, stroke in levels:
        bx = c.box(x, 1230, 210, 80, [name, rng], fill=fill, stroke=stroke, size=22)
        boxes.append(bx)
    c.parts.append(f'<line x1="{boxes[0]["cx"]}" y1="{bus3}" x2="{boxes[-1]["cx"]}" y2="{bus3}" stroke="{NAVY}" stroke-width="4.5" stroke-linecap="round"/>')
    for bx in boxes:
        c.arrow([(bx["cx"], bus3), (bx["cx"], bx["t"])])
    return c


def fig7_extension_flow() -> Canvas:
    c = Canvas(1400, 1130)
    s = c.box(400, 40, 600, 84, ["User clicks a link or types a web address"], fill=TEAL_TINT, stroke=TEAL, rx=42, size=25, icon="🧑‍💻")
    hold = c.box(350, 180, 700, 96, ["Extension intercepts the navigation and", "holds the page on the PhishEye gate screen"], size=23, icon="🛡️")
    c.arrow([(s["cx"], s["b"]), (hold["cx"], hold["t"])])
    call = c.box(350, 330, 700, 96, ["Send the URL to the PhishEye API", "(result cached for 90 s · 30 s timeout)"], size=23, icon="📡")
    c.arrow([(hold["cx"], hold["b"]), (call["cx"], call["t"])])

    d1 = c.diamond(700, 540, 180, 76, ["Response", "received?"], size=23)
    c.arrow([(call["cx"], call["b"]), (d1["cx"], d1["t"])])
    unavailable = c.box(960, 498, 400, 84, ["Stays blocked", "“unknown is not safe”"], fill=RED_TINT, stroke=RED, size=23, icon="⛔")
    c.arrow([(d1["r"], d1["cy"]), (unavailable["l"], unavailable["cy"])], color=RED, label="no / timeout", label_dy=-18)

    d2 = c.diamond(700, 740, 180, 76, ["Risk", "level?"], size=23)
    c.arrow([(d1["cx"], d1["b"]), (d2["cx"], d2["t"])], label="yes", label_dx=-30)

    low = c.box(60, 880, 380, 96, ["LOW", "opens automatically"], fill=GREEN_TINT, stroke=GREEN, size=23, icon="✅")
    med = c.box(510, 880, 380, 96, ["MEDIUM", "user is asked first"], fill=AMBER_TINT, stroke=AMBER, size=23, icon="⚠️")
    high = c.box(960, 880, 380, 96, ["HIGH / CRITICAL", "stays blocked"], fill=RED_TINT, stroke=RED, size=23, icon="⛔")
    c.arrow([(d2["l"], d2["cy"]), (low["cx"], d2["cy"]), (low["cx"], low["t"])], color=GREEN, label="LOW", label_dy=-18, label_dx=-60)
    c.arrow([(d2["cx"], d2["b"]), (med["cx"], med["t"])], color=AMBER, label="MEDIUM", label_dx=70)
    c.arrow([(d2["r"], d2["cy"]), (high["cx"], d2["cy"]), (high["cx"], high["t"])], color=RED, label="HIGH / CRITICAL", label_dy=-18, label_dx=60)

    yes = c.box(470, 1030, 220, 70, ["“Open anyway”", "→ site opens"], fill=WHITE, stroke=AMBER, size=20)
    no = c.box(720, 1030, 220, 70, ["“Go back”", "→ stays on gate"], fill=WHITE, stroke=AMBER, size=20)
    c.arrow([(med["cx"] - 60, med["b"]), (yes["cx"], yes["t"])], color=AMBER, width=3)
    c.arrow([(med["cx"] + 60, med["b"]), (no["cx"], no["t"])], color=AMBER, width=3)
    return c


FIGURES = {
    "fig1_system_architecture": fig1_architecture,
    "fig2_dfd_level0": fig2_dfd0,
    "fig3_dfd_level1": fig3_dfd1,
    "fig4_use_case": fig4_use_case,
    "fig5_er_diagram": fig5_er,
    "fig6_risk_decision_flow": fig6_risk_flow,
    "fig7_extension_gating_flow": fig7_extension_flow,
}


def render_all(scale: float = 2.0) -> dict[str, Path]:
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        for name, fn in FIGURES.items():
            canvas = fn()
            svg = canvas.svg()
            (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
            page = browser.new_page(viewport={"width": canvas.w, "height": canvas.h}, device_scale_factor=scale)
            page.set_content(f"<html><body style='margin:0;background:white'>{svg}</body></html>")
            page.wait_for_timeout(150)
            out = OUT / f"{name}.png"
            page.screenshot(path=str(out), full_page=False)
            page.close()
            paths[name] = out
            print("rendered", out.name)
        browser.close()
    return paths


if __name__ == "__main__":
    render_all()

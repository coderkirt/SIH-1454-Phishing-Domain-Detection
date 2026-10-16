"""Render academic diagrams for the PhishEye synopsis (matplotlib, 300 dpi)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Ellipse

OUT = Path(__file__).resolve().parent / "diagrams"
NAVY = "#1B365D"
INK = "#1A1A1A"
FILL = "#EEF3F8"
ACCENT = "#D6E4F0"
WHITE = "#FFFFFF"


def _fig(w_in: float, h_in: float):
    fig, ax = plt.subplots(figsize=(w_in, h_in), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)
    return fig, ax


def _box(ax, x, y, w, h, text, *, fill=FILL, fs=8.2, weight="medium"):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.25,rounding_size=0.8",
        linewidth=1.15,
        edgecolor=NAVY,
        facecolor=fill,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fs,
        color=INK,
        fontname="Times New Roman",
        fontweight=weight,
        wrap=True,
        linespacing=1.25,
    )
    return (x + w / 2, y + h / 2)


def _arrow(ax, p1, p2, text=""):
    ax.add_patch(
        FancyArrowPatch(
            p1,
            p2,
            arrowstyle="-|>",
            mutation_scale=11,
            linewidth=1.05,
            color=NAVY,
            shrinkA=2,
            shrinkB=2,
        )
    )
    if text:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ax.text(
            mx,
            my + 2.2,
            text,
            ha="center",
            va="bottom",
            fontsize=6.6,
            color=NAVY,
            fontname="Times New Roman",
        )


def _save(fig, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=WHITE, pad_inches=0.18)
    plt.close(fig)
    return path


def system_architecture() -> Path:
    fig, ax = _fig(10.0, 5.0)
    _box(ax, 8, 86, 38, 10, "Web application\n(React 19 + Vite 8)", fill=ACCENT, fs=8.5)
    _box(ax, 54, 86, 38, 10, "Chrome extension MV3 1.8.0\nscan-before-open gate", fill=ACCENT, fs=8.5)
    _arrow(ax, (27, 86), (27, 76), "")
    _arrow(ax, (73, 86), (73, 76), "")
    _box(ax, 22, 64, 56, 12, "PHISHEYE API 2.0.0\nFastAPI + Uvicorn  :8000\nHTTPS JSON  (check-url / analyze / report)", fill="#DDE7F2", fs=8.6, weight="semibold")
    _arrow(ax, (50, 64), (50, 55))

    y = 42
    boxes = [
        (4, "URL / domain\nheuristics\nTLS, age, lookalike"),
        (28, "Threat intel\nOpenPhish, URLhaus\nPhishTank, Army"),
        (52, "Psychology rules\nEN + Hinglish\nphrase match"),
        (76, "QR decode\nOpenCV\n(no destination fetch)"),
    ]
    for x, t in boxes:
        _box(ax, x, y, 20, 13, t, fs=7.2)
        _arrow(ax, (x + 10, 64), (x + 10, y + 13))

    _box(ax, 8, 24, 40, 12, "Risk decision\nURL path: intel floors\nContent path: static weighted fuse", fs=7.6)
    _box(ax, 52, 24, 40, 12, "Explainability\nSimple View + Technical View\nwarnings.py", fs=7.6)
    _arrow(ax, (14, 42), (22, 36))
    _arrow(ax, (38, 42), (28, 36))
    _arrow(ax, (62, 42), (72, 36))
    _arrow(ax, (86, 42), (78, 36))
    _arrow(ax, (48, 30), (52, 30))

    _box(ax, 28, 4, 44, 12, "SQLite  threats.db  (live path)\nusers, url_checks, content_scans, reports", fill=ACCENT, fs=7.8)
    _arrow(ax, (50, 24), (50, 16))
    return _save(fig, "fig1_system_architecture.png")


def dfd_level0() -> Path:
    fig, ax = _fig(10.0, 4.4)
    ext = Ellipse((16, 50), 22, 22, linewidth=1.2, edgecolor=NAVY, facecolor=ACCENT)
    ax.add_patch(ext)
    ax.text(16, 50, "User\n(browser / paste)", ha="center", va="center", fontsize=8.5, fontname="Times New Roman", color=INK)

    sys = Rectangle((38, 32), 24, 36, linewidth=1.4, edgecolor=NAVY, facecolor="#DDE7F2")
    ax.add_patch(sys)
    ax.text(50, 50, "PhishEye\nSystem", ha="center", va="center", fontsize=10, fontweight="semibold", fontname="Times New Roman", color=INK)

    feeds = Ellipse((84, 50), 22, 22, linewidth=1.2, edgecolor=NAVY, facecolor=ACCENT)
    ax.add_patch(feeds)
    ax.text(84, 50, "Public threat\nfeeds / RDAP", ha="center", va="center", fontsize=8.2, fontname="Times New Roman", color=INK)

    _arrow(ax, (27, 54), (38, 54), "URL / text / QR")
    _arrow(ax, (38, 46), (27, 46), "risk + views")
    _arrow(ax, (62, 54), (73, 54), "lookup")
    _arrow(ax, (73, 46), (62, 46), "match / miss")
    return _save(fig, "fig2_dfd_level0.png")


def dfd_level1() -> Path:
    fig, ax = _fig(10.0, 5.0)
    _box(ax, 2, 78, 16, 14, "D1\nUser /\nExtension", fill=ACCENT, fs=7.5)
    _box(ax, 24, 80, 20, 10, "P1 Input &\npreprocess", fs=7.6)
    _box(ax, 50, 80, 20, 10, "P2 URL / domain\nanalysis", fs=7.6)
    _box(ax, 76, 80, 20, 10, "P3 Threat intel", fs=7.6)

    _box(ax, 24, 50, 20, 12, "P4 Psychology\nphrase rules", fs=7.6)
    _box(ax, 50, 50, 20, 12, "P5 Risk engine\nfloors / fuse", fs=7.6)
    _box(ax, 76, 50, 20, 12, "P6 Explain\nSimple+Technical", fs=7.6)

    _box(ax, 36, 18, 28, 12, "D2 SQLite store\nscans · reports · users", fill=ACCENT, fs=7.6)
    _box(ax, 76, 18, 20, 12, "D3 Feed cache\n(in-memory TTL)", fill=ACCENT, fs=7.4)

    _arrow(ax, (18, 85), (24, 85), "request")
    _arrow(ax, (44, 85), (50, 85))
    _arrow(ax, (70, 85), (76, 85))
    _arrow(ax, (34, 80), (34, 62))
    _arrow(ax, (60, 80), (60, 62))
    _arrow(ax, (86, 80), (86, 62))
    _arrow(ax, (44, 56), (50, 56))
    _arrow(ax, (70, 56), (76, 56))
    _arrow(ax, (60, 50), (50, 30), "persist")
    _arrow(ax, (86, 50), (86, 30), "lookup")
    _arrow(ax, (24, 78), (10, 78), "result")
    return _save(fig, "fig3_dfd_level1.png")


def use_case() -> Path:
    fig, ax = _fig(10.0, 5.0)
    sys = FancyBboxPatch((22, 8), 56, 84, boxstyle="round,pad=0.4,rounding_size=1.2", linewidth=1.2, edgecolor=NAVY, facecolor="#F7FAFC")
    ax.add_patch(sys)
    ax.text(50, 88, "PhishEye", ha="center", va="center", fontsize=10, fontweight="semibold", fontname="Times New Roman", color=NAVY)

    cases = [
        (50, 76, "Register / log in"),
        (50, 66, "Scan URL or pasted message"),
        (50, 56, "Scan QR / screenshot"),
        (50, 46, "View Simple + Technical result"),
        (50, 36, "View history and reports"),
        (50, 26, "Mark community signal"),
        (50, 16, "Gate Chrome navigation"),
    ]
    for x, y, t in cases:
        e = Ellipse((x, y), 34, 8.2, linewidth=1.1, edgecolor=NAVY, facecolor=WHITE)
        ax.add_patch(e)
        ax.text(x, y, t, ha="center", va="center", fontsize=7.4, fontname="Times New Roman", color=INK)

    def actor(x, y, label):
        ax.add_patch(Circle((x, y + 10), 2.3, fill=False, edgecolor=NAVY, linewidth=1.2))
        ax.plot([x, x], [y + 7.7, y + 2], color=NAVY, lw=1.2)
        ax.plot([x - 3, x + 3], [y + 5.5, y + 5.5], color=NAVY, lw=1.2)
        ax.plot([x, x - 2.4], [y + 2, y - 2], color=NAVY, lw=1.2)
        ax.plot([x, x + 2.4], [y + 2, y - 2], color=NAVY, lw=1.2)
        ax.text(x, y - 6, label, ha="center", va="top", fontsize=7.4, fontname="Times New Roman", color=INK)

    actor(8, 52, "End user")
    actor(92, 70, "Browser\nextension")
    actor(92, 22, "Threat-intel\nfeeds")
    _arrow(ax, (12, 60), (33, 66))
    _arrow(ax, (12, 48), (33, 46))
    _arrow(ax, (12, 40), (33, 36))
    _arrow(ax, (88, 68), (67, 16))
    _arrow(ax, (88, 28), (67, 66))
    return _save(fig, "fig4_use_case.png")


def er_diagram() -> Path:
    fig, ax = _fig(10.0, 4.8)

    def ent(x, y, w, h, title, fields):
        ax.add_patch(Rectangle((x, y), w, h, linewidth=1.15, edgecolor=NAVY, facecolor=WHITE))
        ax.add_patch(Rectangle((x, y + h - 6.5), w, 6.5, linewidth=0, facecolor=ACCENT))
        ax.plot([x, x + w], [y + h - 6.5, y + h - 6.5], color=NAVY, lw=1.1)
        ax.text(x + w / 2, y + h - 3.25, title, ha="center", va="center", fontsize=7.4, fontweight="semibold", fontname="Times New Roman", color=NAVY)
        ax.text(x + 1.2, y + h - 8.4, fields, ha="left", va="top", fontsize=6.3, fontname="Times New Roman", color=INK, linespacing=1.35)

    ent(4, 58, 28, 34, "users", "id PK\nusername\nemail\npassword_hash\ncreated_at")
    ent(38, 58, 26, 34, "url_checks", "id PK\nuser_id FK\nurl\nrisk_level, score\nml_confidence\ntimestamp")
    ent(70, 58, 26, 34, "content_scans", "id PK\nuser_id FK\nsource_type\nrisk_score\nconfidence")
    ent(4, 8, 28, 34, "user_reports", "id PK\nuser_id FK\nurl, domain\nuser_label\nreason")
    ent(38, 8, 26, 34, "extracted_links", "id PK\nscan_id FK\nurl, domain\nrisk_score")
    ent(70, 8, 26, 34, "domain_reputation", "domain PK\nscam / risky / safe\ncounts")

    _arrow(ax, (32, 78), (38, 78), "1:N")
    _arrow(ax, (18, 58), (18, 42))
    ax.text(20, 50, "1:N", fontsize=6.4, fontname="Times New Roman", color=NAVY)
    _arrow(ax, (64, 78), (70, 78), "1:N")
    _arrow(ax, (83, 58), (83, 42), "1:N")
    _arrow(ax, (51, 58), (51, 42), "1:N")
    ax.text(53, 48, "scan to links", ha="left", fontsize=6.2, fontname="Times New Roman", color=NAVY)
    return _save(fig, "fig5_er_diagram.png")


def render_all() -> dict[str, Path]:
    return {
        "architecture": system_architecture(),
        "dfd0": dfd_level0(),
        "dfd1": dfd_level1(),
        "usecase": use_case(),
        "er": er_diagram(),
    }


if __name__ == "__main__":
    paths = render_all()
    for key, path in paths.items():
        print(f"{key}: {path}")

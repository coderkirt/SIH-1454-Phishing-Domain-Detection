"""QA helper: export the v2 synopsis to PDF with Word, render pages to PNG, print page stats.

Usage: python synopsis_generator/qa_pdf.py  [preview_dir]
Preview PNGs are written outside the repo by default (%TEMP%/phisheye_synopsis_preview).
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "PhishEye_Synopsis_v2.docx"
PDF = ROOT / "PhishEye_Synopsis_v2.pdf"


def export_pdf():
    import win32com.client  # type: ignore
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(str(DOCX), ReadOnly=True)
        doc.Fields.Update()
        doc.SaveAs2(str(PDF), FileFormat=17)
        pages = doc.ComputeStatistics(2)
        doc.Close(False)
    finally:
        word.Quit()
    return pages


def render(preview: Path):
    import fitz  # pymupdf
    preview.mkdir(parents=True, exist_ok=True)
    for old in preview.glob("page*.png"):
        old.unlink()
    pdf = fitz.open(str(PDF))
    for i, page in enumerate(pdf, 1):
        r = page.rect
        pix = page.get_pixmap(dpi=80)
        pix.save(str(preview / f"page{i:02d}.png"))
        text = page.get_text()
        flags = []
        if "[VERIFY" in text:
            flags.append("VERIFY-marker")
        ys = [b[3] for b in page.get_text("blocks")] + [im["bbox"][3] for im in page.get_image_info()]
        ys = [y for y in ys if y < r.height - 60]  # ignore footer page number
        used = (max(ys) - 72) / 72 * 2.54 if ys else 0
        print(f"page {i:02d}: {r.width/72*2.54:.2f} x {r.height/72*2.54:.2f} cm  used={used:5.1f} cm  "
              f"free={24.6-used:5.1f} cm  imgs={len(page.get_image_info())}  {' '.join(flags)}")
    return len(pdf)


if __name__ == "__main__":
    import time
    preview = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.gettempdir()) / f"phisheye_synopsis_preview_{int(time.time())}"
    pages = export_pdf()
    print("Word page count:", pages)
    n = render(preview)
    print("PDF pages:", n, "preview:", preview)

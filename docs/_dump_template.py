import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

z = zipfile.ZipFile(r"c:\Users\HRITIK KUMAR\cybersecurity-platform\docs\_sih_template.pptx")
out = Path(r"c:\Users\HRITIK KUMAR\cybersecurity-platform\docs\_sih_template_dump.txt")
lines = []
pres = z.read("ppt/presentation.xml").decode("utf-8")
lines.append("=== presentation.xml sldSz ===")
if "sldSz" in pres:
    i = pres.find("sldSz")
    lines.append(pres[i:i+250])
lines.append("\n=== theme1 schemeClr / srgbClr sample ===")
theme = z.read("ppt/theme/theme1.xml").decode("utf-8")
lines.append(theme[:2000])
for i in range(1, 8):
    xml = z.read(f"ppt/slides/slide{i}.xml").decode("utf-8")
    root = ET.fromstring(xml)
    texts = []
    for t in root.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}t"):
        if t.text:
            texts.append(t.text)
        elif t.tail:
            texts.append(t.tail)
    lines.append(f"\n===== SLIDE {i} =====")
    lines.append("\n".join(texts))
    lines.append(f"xml bytes={len(xml)}")
out.write_text("\n".join(lines), encoding="utf-8")
print("wrote", out, "chars", out.stat().st_size)

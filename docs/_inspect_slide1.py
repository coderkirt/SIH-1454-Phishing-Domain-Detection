import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
z = zipfile.ZipFile(r"c:\Users\HRITIK KUMAR\cybersecurity-platform\docs\_sih_template.pptx")
xml = z.read("ppt/slides/slide1.xml")
root = ET.fromstring(xml)
out = []
for sp in root.iter("{http://schemas.openxmlformats.org/presentationml/2006/main}sp"):
    nv = sp.find(".//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr")
    name = nv.get("name") if nv is not None else "?"
    xfrm = sp.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}off")
    ext = sp.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}ext")
    texts = [t.text or "" for t in sp.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}t")]
    x = xfrm.get("x") if xfrm is not None else ""
    y = xfrm.get("y") if xfrm is not None else ""
    cx = ext.get("cx") if ext is not None else ""
    cy = ext.get("cy") if ext is not None else ""
    out.append(f"{name} x={x} y={y} cx={cx} cy={cy} text={' | '.join(texts)[:120]}")
Path(r"c:\Users\HRITIK KUMAR\cybersecurity-platform\docs\_slide1_shapes.txt").write_text("\n".join(out), encoding="utf-8")
# extract media
media = Path(r"c:\Users\HRITIK KUMAR\cybersecurity-platform\docs\_sih_media")
media.mkdir(exist_ok=True)
for n in z.namelist():
    if n.startswith("ppt/media/"):
        (media / Path(n).name).write_bytes(z.read(n))
print("shapes", len(out), "media", list(media.iterdir()))

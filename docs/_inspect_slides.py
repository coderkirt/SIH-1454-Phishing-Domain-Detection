import zipfile, xml.etree.ElementTree as ET
from pathlib import Path
z=zipfile.ZipFile(r"c:\Users\HRITIK KUMAR\cybersecurity-platform\docs\_sih_template.pptx")
lines=[]
for i in range(2,7):
    root=ET.fromstring(z.read(f"ppt/slides/slide{i}.xml"))
    lines.append(f"\nSLIDE {i}")
    for sp in list(root.iter("{http://schemas.openxmlformats.org/presentationml/2006/main}sp")):
        nv=sp.find(".//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr")
        name=nv.get("name") if nv is not None else "?"
        off=sp.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}off")
        ext=sp.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}ext")
        texts=[t.text or "" for t in sp.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}t")]
        x=off.get("x") if off is not None else ""
        y=off.get("y") if off is not None else ""
        lines.append(f"  {name} y={y} text={' | '.join(texts)[:90]}")
Path(r"c:\Users\HRITIK KUMAR\cybersecurity-platform\docs\_slides26_shapes.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")

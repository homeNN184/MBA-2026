# -*- coding: utf-8 -*-
import io, os, sys, zipfile, shutil, tempfile
from PIL import Image

src, out, maxw, q = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
tmp = tempfile.mkdtemp()
with zipfile.ZipFile(src) as z:
    z.extractall(tmp)
md = os.path.join(tmp, "word", "media")
n = 0
if os.path.isdir(md):
    for f in sorted(os.listdir(md)):
        p = os.path.join(md, f)
        try:
            im = Image.open(p)
        except Exception:
            continue
        if im.width <= maxw and os.path.getsize(p) < 150_000:
            continue
        w = min(maxw, im.width)
        im = im.convert("RGB").resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save(p, format="JPEG", quality=q, optimize=True)
        n += 1
zf = zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9)
for root, _, files in os.walk(tmp):
    for f in files:
        full = os.path.join(root, f)
        zf.write(full, os.path.relpath(full, tmp))
zf.close()
shutil.rmtree(tmp)
print("пересжато", n, "|", os.path.getsize(out))

# -*- coding: utf-8 -*-
"""Пересжатие изображений в файле docx с сохранением четкости штриховой графики.

Схемы, графики и снимки экрана состоят из плоских заливок и линий, поэтому формат
PNG с ограниченной палитрой дает меньший размер и не размывает линии. Фотографии и
сканированные листы содержат градиенты, для них выгоднее формат JPEG при меньшем
разрешении. Вид изображения определяется числом различных цветов.

Вызов: shrink_docx2.py вход выход ширина_штриховой ширина_фото качество_jpeg цвета
"""
import io, os, sys, zipfile, shutil, tempfile
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
maxw = int(sys.argv[3]) if len(sys.argv) > 3 else 2100
phw = int(sys.argv[4]) if len(sys.argv) > 4 else 1200
q = int(sys.argv[5]) if len(sys.argv) > 5 else 75
cols = int(sys.argv[6]) if len(sys.argv) > 6 else 64
LIMIT = 8000          # граница между штриховой графикой и фотографией по числу цветов

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
            im.load()
        except Exception:
            continue
        rgb0 = im.convert("RGB")
        uniq = rgb0.getcolors(maxcolors=LIMIT)
        line_art = uniq is not None
        target = maxw if line_art else phw
        w = min(target, rgb0.width)
        rgb = rgb0 if w == rgb0.width else rgb0.resize(
            (w, round(rgb0.height * w / rgb0.width)), Image.LANCZOS)
        b = io.BytesIO()
        if line_art:
            rgb.quantize(colors=cols, method=Image.MEDIANCUT, dither=Image.NONE).save(
                b, format="PNG", optimize=True)
        else:
            rgb.save(b, format="JPEG", quality=q, optimize=True, subsampling=0)
        if b.tell() >= os.path.getsize(p):
            continue
        with open(p, "wb") as fh:
            fh.write(b.getvalue())
        n += 1

zf = zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9)
for root, _, files in os.walk(tmp):
    for f in files:
        full = os.path.join(root, f)
        zf.write(full, os.path.relpath(full, tmp))
zf.close()
shutil.rmtree(tmp)
print("пересжато %d | %.2f МБ" % (n, os.path.getsize(out) / 1048576))

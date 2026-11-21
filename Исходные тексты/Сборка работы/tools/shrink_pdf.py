# -*- coding: utf-8 -*-
import io, sys, pikepdf
from PIL import Image

src, out, maxw, q = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
pdf = pikepdf.open(src)
n = 0
for page in pdf.pages:
    for name, raw in list(page.get_images().items()):
        try:
            im = pikepdf.PdfImage(raw).as_pil_image()
        except Exception:
            continue
        if im.width <= maxw:
            continue
        im = im.convert("RGB").resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, format="JPEG", quality=q, optimize=True)
        raw.write(buf.getvalue(), filter=pikepdf.Name("/DCTDecode"))
        raw.ColorSpace = pikepdf.Name("/DeviceRGB"); raw.BitsPerComponent = 8
        raw.Width, raw.Height = im.width, im.height
        n += 1
pdf.save(out, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
print(n)

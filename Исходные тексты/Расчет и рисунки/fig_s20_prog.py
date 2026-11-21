# -*- coding: utf-8 -*-
"""Слайд 20. Программная реализация расчетной модели, снимок экрана целиком."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.image as mpimg

W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")

SRC = "/mnt/user-data/attachments/dd9faf01-b370-5003-bf0f-0f5597645131/40cb9715-image.png"
img = mpimg.imread(SRC)
if img.ndim == 3 and img.shape[2] == 4:
    img = img[:, :, :3]
ih, iw = img.shape[0], img.shape[1]

MAXW, MAXH = 98.0, YM - 1.0
sc = min(MAXW / iw, MAXH / ih)
pw, ph = iw * sc, ih * sc
x0 = (100 - pw) / 2.0
y0 = (YM - ph) / 2.0
ax.imshow(img, extent=(x0, x0 + pw, y0, y0 + ph), zorder=3, aspect="auto")
ax.add_patch(Rectangle((x0, y0), pw, ph, fc="none", ec="#C9D8E8", lw=1.0, zorder=5))

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s20_prog.png", dpi=660, facecolor="white")
print("ok", iw, "x", ih, "->", round(pw, 1), "x", round(ph, 1))

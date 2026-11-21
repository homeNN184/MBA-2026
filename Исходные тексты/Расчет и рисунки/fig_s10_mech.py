# -*- coding: utf-8 -*-
"""Слайд 10. Механизм интеграции инновационного и инвестиционного процессов."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import matplotlib.image as mpimg
import icons_lib as I

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
PURPLE, FILL = "#8E44AD", "#EAF2FA"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")

TOP, BOT = YM - 0.9, 1.0

# ---------------- рисунок 16 без подписи легенды
img = mpimg.imread("/home/claude/work/fig/s10_mech_src.png")
if img.ndim == 3 and img.shape[2] == 4:
    img = img[:, :, :3]
import numpy as np
g = img if img.max() > 1.5 else img * 255.0
mask = (g.mean(axis=2) < 248)
rows = np.where(mask.any(axis=1))[0]
cols = np.where(mask.any(axis=0))[0]
img = img[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]
ih, iw = img.shape[0], img.shape[1]
PH = TOP - BOT
PW = PH * iw / ih
PX0 = 1.5
ax.imshow(img, extent=(PX0, PX0 + PW, BOT, TOP), zorder=3, aspect="auto")

# ---------------- пояснения
CX0, CX1 = PX0 + PW + 2.5, 98.5
ax.add_patch(FancyBboxPatch((CX0, BOT), CX1 - CX0, TOP - BOT,
                            boxstyle="round,pad=0,rounding_size=0.9",
                            fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
ax.add_patch(FancyBboxPatch((CX0, TOP - 0.75), CX1 - CX0, 0.75,
                            boxstyle="round,pad=0,rounding_size=0.35",
                            fc=NAVY, ec="none", zorder=3))
cx, cy = CX0 + 3.6, TOP - 3.6
ax.add_patch(Circle((cx, cy), 2.1, fc="none", ec=NAVY, lw=1.3, zorder=4))
I.gears(ax, cx, cy, 2.1, NAVY, 1.3)
ax.text(CX0 + 7.0, cy, "Механизм интеграции", ha="left", va="center",
        fontsize=8.0, color=NAVY, fontweight="bold")

ITEMS = [
    (TRN, "КТ-0 — задание на разработку, формируется из замысла\nи технических требований объекта"),
    (TRN, "Точка входа одна — начало разработки проектной\nдокументации: раздел технологических решений\nнельзя выполнить без характеристик оборудования"),
    (TRN, "Уровень на входе выбирается от TRL5 до TRL7,\nэто дает четыре сценария организации работ"),
    (PURPLE, "Уровни TRL6–TRL9 подтверждаются по окончании стадий\nрабочей документации, строительно-монтажных\nи пусконаладочных работ, комплексного опробования"),
    (NAVY, "Шесть контрольных точек интеграции, решение\nпринимается коллегиально, решает заказчик"),
]
y = TOP - 7.2
for col, it in ITEMS:
    ax.add_patch(Circle((CX0 + 2.6, y - 0.5), 0.38, fc=col, ec="none", zorder=5))
    ax.text(CX0 + 4.3, y, it, ha="left", va="top",
            fontsize=6.3, color=SUB, linespacing=1.4)
    y -= (it.count("\n") + 1) * 1.34 + 0.75

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s10_mech.png", dpi=660, facecolor="white")
print("ok, рисунок", round(PW, 1), "x", round(PH, 1), "| блок от", round(CX0, 1))

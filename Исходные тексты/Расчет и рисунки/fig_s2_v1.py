# -*- coding: utf-8 -*-
"""Слайд 2, вариант 1. Шевроны с пиктограммами, две схемы организации."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import icons_lib as I

NAVY, BLUE, GREEN, PURPLE, ORANGE, GREY = "#003366", "#0079C2", "#1B9E77", "#8E44AD", "#C4690E", "#595959"
plt.rcParams["font.family"] = "DejaVu Sans"
fig, ax = plt.subplots(figsize=(9.3, 4.15), dpi=660)
ax.set_xlim(0, 100); ax.set_ylim(0, 58); ax.axis("off")

W, H, TIP = 14.2, 10.5, 2.6


def chev(x, y, color, icon, title, sub=None, light=False):
    pts = [[x, y + H / 2], [x + W - TIP, y + H / 2], [x + W, y],
           [x + W - TIP, y - H / 2], [x, y - H / 2], [x + TIP, y]]
    ax.add_patch(Polygon(pts, closed=True, fc=color, ec="white", lw=1.4,
                         alpha=0.16 if light else 1.0, zorder=3))
    icon(ax, x + W / 2 - 0.4, y + 1.5, 4.6, color if light else "white", 1.7)
    ax.text(x + W / 2 - 0.4, y - 3.5, title, ha="center", va="center", fontsize=7.6,
            color=color if light else "white", zorder=5, linespacing=1.2)
    if sub:
        ax.text(x + W / 2 - 0.4, y - H / 2 - 2.2, sub, ha="center", va="top",
                fontsize=7.2, color=GREY, zorder=5)


def lane(y, t, c):
    ax.text(0.5, y, t, ha="left", va="center", fontsize=9.8, color=c, fontweight="bold")


# ---------------- верх, последовательная организация
lane(55.5, "Последовательная организация работ", NAVY)
X0, yA = 1.0, 45.0
seq = [(BLUE, I.lamp, "Идея\nTRL1"), (BLUE, I.flask, "Испытания\nTRL5"),
       (BLUE, I.gears, "Оборудование\nTRL9"), (PURPLE, I.doc, "Проектная\nдокументация"),
       (GREY, I.crane, "Строительство"), (NAVY, I.building, "Ввод\nобъекта")]
for k, (c, ic, t) in enumerate(seq):
    chev(X0 + k * (W + 1.2), yA, c, ic, t)
xEndA = X0 + 5 * (W + 1.2) + W

# ---------------- низ, параллельная организация
lane(32.5, "Параллельная организация работ", GREEN)
yB1, yB2 = 22.5, 6.0
for k, (c, ic, t) in enumerate(seq[:3]):
    chev(X0 + k * (W + 1.2), yB1, c, ic, t)
xEntry = X0 + 1 * (W + 1.2) + W / 2
par = [(PURPLE, I.doc, "Проектная\nдокументация"), (GREEN, I.crane, "Строительство"),
       (GREEN, I.building, "Ввод\nобъекта")]
for k, (c, ic, t) in enumerate(par):
    chev(X0 + (k + 1) * (W + 1.2), yB2, c, ic, t)
xEndB = X0 + 3 * (W + 1.2) + W

# точка входа
ax.annotate("", xy=(xEntry, yB2 + H / 2 + 0.3), xytext=(xEntry, yB1 - H / 2 - 0.3),
            arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=2.0,
                            shrinkA=0, shrinkB=0), zorder=8)
ax.text(xEntry + 1.8, (yB1 + yB2) / 2, "точка входа в инвестиционный процесс",
        ha="left", va="center", fontsize=7.8, color=ORANGE, fontweight="bold")

# выигрыш во времени
ax.plot([xEndA, xEndA], [yA - H / 2 - 0.5, 36.5], color=NAVY, lw=0.9, ls=":", zorder=2)
ax.plot([xEndB, xEndB], [yB2 + H / 2 + 0.5, 36.5], color=GREEN, lw=0.9, ls=":", zorder=2)
ax.annotate("", xy=(xEndB, 36.5), xytext=(xEndA, 36.5),
            arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=1.8), zorder=8)
ax.text((xEndA + xEndB) / 2, 37.9, "выигрыш во времени, ранний доход",
        ha="center", va="bottom", fontsize=8.4, color=ORANGE, fontweight="bold")

# риск
I.warn(ax, xEndB + 4.5, yB2 + 1.0, 4.6, ORANGE, 1.7)
ax.text(xEndB + 8.0, yB2 + 1.0, "риск переделок\nдокументации", ha="left", va="center",
        fontsize=7.8, color=ORANGE, linespacing=1.3)

fig.tight_layout(pad=0.15)
fig.savefig("/home/claude/work/fig/s2_v1.png", bbox_inches="tight", facecolor="white")
print("ok")

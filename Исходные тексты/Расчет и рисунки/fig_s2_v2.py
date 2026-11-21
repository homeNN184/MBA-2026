# -*- coding: utf-8 -*-
"""Слайд 2. Инновационная и инвестиционная деятельность, переход между ними."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import icons_lib as I

INN = "#0079C2"     # инновационная деятельность
INV = "#1B9E77"     # инвестиционная деятельность
TRN = "#C4690E"     # преимущество и риск
TRS = "#8E44AD"     # переход интеграции
SUB = "#3C4F66"     # заголовки полос
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.15
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
ax.set_xlim(0, 100); ax.set_ylim(0, 100 * H_IN / W_IN); ax.axis("off")
ax.set_aspect("equal")
R = 3.5


def node(x, y, c, icon, label, below=True):
    ax.add_patch(Circle((x, y), R, fc="white", ec=c, lw=2.0, zorder=6))
    icon(ax, x, y, R * 1.0, c, 1.6)
    dy, va = (-R - 1.3, "top") if below else (R + 1.3, "bottom")
    ax.text(x, y + dy, label, ha="center", va=va, fontsize=7.8, color=c,
            fontweight="bold", linespacing=1.25)


def link(x1, y1, x2, y2, c, lw=1.8, alpha=0.55, z=4, rad=None, head=0.22):
    kw = dict(arrowstyle="-|>,head_width=%.2f,head_length=%.2f" % (head, head * 2.3),
              color=c, lw=lw, alpha=alpha, shrinkA=0, shrinkB=0)
    if rad:
        kw["connectionstyle"] = rad
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=kw, zorder=z)


def chain(xs, y, c, gap=R + 0.6):
    for a, b in zip(xs[:-1], xs[1:]):
        link(a + gap, y, b - gap - 0.3, y, c)


# ======================= верхняя полоса
yA = 35.5
xa = [10, 24, 38, 52, 66, 80, 94]
ax.text(6.5, 43.6, "Последовательно", ha="left", va="center",
        fontsize=8.6, color=SUB, fontweight="bold")
ax.text((xa[0] + xa[2]) / 2, 40.2, "инновационная деятельность", ha="center", va="center",
        fontsize=8.0, color=INN, fontweight="bold")
ax.text((xa[3] + xa[6]) / 2, 40.2, "инвестиционная деятельность", ha="center", va="center",
        fontsize=8.0, color=INV, fontweight="bold")
chain(xa[:3], yA, INN)
chain(xa[3:], yA, INV)
node(xa[0], yA, INN, I.lamp, "Идея\nTRL1")
node(xa[1], yA, INN, I.flask, "Испытания\nTRL5")
node(xa[2], yA, INN, I.gears, "Оборудование\nTRL9")
node(xa[3], yA, INV, I.doc, "Проектная\nдокументация")
node(xa[4], yA, INV, I.draft, "Рабочая\nдокументация")
node(xa[5], yA, INV, I.crane, "Строительство")
node(xa[6], yA, INV, I.building, "Ввод объекта")
link(xa[2] + R + 0.5, yA, xa[3] - R - 0.5, yA, TRS, lw=3.4, alpha=1.0, z=8, head=0.42)
ax.text((xa[2] + xa[3]) / 2, yA + 1.5, "переход\nинтеграции", ha="center", va="bottom",
        fontsize=7.6, color=TRS, fontweight="bold", linespacing=1.25)

# ======================= нижняя полоса
yB1, yB2 = 19.0, 8.0
xb = [30, 43, 56, 69]
ax.text(6.5, 25.8, "Параллельно", ha="left", va="center",
        fontsize=8.6, color=SUB, fontweight="bold")
chain(xa[:3], yB1, INN)
node(xa[0], yB1, INN, I.lamp, "", below=False)
node(xa[1], yB1, INN, I.flask, "", below=False)
node(xa[2], yB1, INN, I.gears, "", below=False)
chain(xb, yB2, INV)
node(xb[0], yB2, INV, I.doc, "Проектная\nдокументация")
node(xb[1], yB2, INV, I.draft, "Рабочая\nдокументация")
node(xb[2], yB2, INV, I.crane, "Строительство")
node(xb[3], yB2, INV, I.building, "Ввод объекта")
link(xa[1] + 0.9, yB1 - R + 0.2, xb[0] - 1.6, yB2 + R + 0.6, TRS, lw=3.4, alpha=1.0, z=8,
     rad="angle3,angleA=-65,angleB=20", head=0.42)
ax.text(xa[1] + 5.4, 12.6, "переход интеграции,\nточка входа", ha="left", va="center",
        fontsize=7.6, color=TRS, fontweight="bold", linespacing=1.25)

# ======================= выигрыш и риск
yG = 14.3
ax.plot([xa[6], xa[6]], [yA - R - 3.0, yG], color=INV, lw=0.9, ls=":", alpha=0.7, zorder=2)
ax.plot([xb[3], xb[3]], [yB2 + R + 0.8, yG], color=INV, lw=0.9, ls=":", alpha=0.7, zorder=2)
ax.annotate("", xy=(xb[3], yG), xytext=(xa[6], yG),
            arrowprops=dict(arrowstyle="<->", color=TRN, lw=1.8), zorder=8)
ax.text((xa[6] + xb[3]) / 2, yG + 1.2, "преимущество",
        ha="center", va="bottom", fontsize=8.4, color=TRN, fontweight="bold")
I.warn(ax, 79.0, yB2 + 0.5, 4.6, TRN, 1.7)
ax.text(82.4, yB2 + 0.5, "риск переделок\nдокументации", ha="left", va="center",
        fontsize=7.8, color=TRN, linespacing=1.3)

fig.tight_layout(pad=0.15)
fig.savefig("/home/claude/work/fig/s2_v2.png", bbox_inches="tight", facecolor="white")
print("ok")

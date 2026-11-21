# -*- coding: utf-8 -*-
"""Слайд 3. Цель и задачи."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import icons_lib as I

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
FILL = "#EAF2FA"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
ax.set_xlim(0, 100); ax.set_ylim(0, 100 * H_IN / W_IN); ax.axis("off")
ax.set_aspect("equal")

# ---------------- цель
gy0, gy1 = 29.6, 42.6
ax.add_patch(FancyBboxPatch((2.0, gy0), 96.0, gy1 - gy0,
                            boxstyle="round,pad=0,rounding_size=1.2",
                            fc=FILL, ec="none", zorder=2))
ax.add_patch(FancyBboxPatch((2.0, gy0), 1.1, gy1 - gy0,
                            boxstyle="round,pad=0,rounding_size=0.5",
                            fc=NAVY, ec="none", zorder=3))
I.target(ax, 9.0, (gy0 + gy1) / 2, 7.6, NAVY, 1.9)
ax.text(15.5, (gy0 + gy1) / 2 + 3.9, "Цель работы", ha="left", va="center",
        fontsize=9.6, color=NAVY, fontweight="bold")
ax.text(15.5, (gy0 + gy1) / 2 - 1.5, "разработать модель управления инновационной деятельностью\n"
        "при реализации инвестиционных проектов", ha="left", va="center", fontsize=8.8,
        color=SUB, linespacing=1.45)

# ---------------- задачи
cards = [
    (INN, I.books, "Задача 1",
     "Проанализировать нормативную\nи методическую базу управления\nинновационной и инвестиционной\n"
     "деятельностью, российскую\nи зарубежную практику совмещения"),
    (INV, I.search, "Задача 2",
     "Проанализировать опыт\nразработки и внедрения\nинновационного оборудования\n"
     "при строительстве отраслевого\nметрологического центра\nрасходометрии ПАО «Газпром»"),
    (TRN, I.chartup, "Задача 3",
     "Разработать модель управления,\nвключающую механизм контрольных\nточек, моделирование сценарных\n"
     "условий, правило выбора\nи процесс принятия решения"),
]
x0, wc, gap = 2.0, 31.3, 1.6
cy0, cy1 = 1.5, 28.5
for k, (c, icon, head, body) in enumerate(cards):
    x = x0 + k * (wc + gap)
    ax.add_patch(FancyBboxPatch((x, cy0), wc, cy1 - cy0,
                                boxstyle="round,pad=0,rounding_size=1.2",
                                fc="white", ec="#D8DEE6", lw=1.2, zorder=2))
    ax.add_patch(FancyBboxPatch((x, cy1 - 0.9), wc, 0.9,
                                boxstyle="round,pad=0,rounding_size=0.5",
                                fc=c, ec="none", zorder=3))
    cx = x + wc / 2
    ax.add_patch(Circle((cx, cy1 - 6.4), 3.6, fc="white", ec=c, lw=2.0, zorder=6))
    icon(ax, cx, cy1 - 6.4, 3.6, c, 1.6)
    ax.text(cx, cy1 - 11.6, head, ha="center", va="center", fontsize=9.4,
            color=c, fontweight="bold")
    ax.text(cx, cy1 - 13.8, body, ha="center", va="top", fontsize=7.6,
            color=SUB, linespacing=1.5)

fig.tight_layout(pad=0.15)
fig.savefig("/home/claude/work/fig/s3_goal.png", bbox_inches="tight", facecolor="white")
print("ok")

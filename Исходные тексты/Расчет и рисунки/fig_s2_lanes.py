# -*- coding: utf-8 -*-
"""Слайд 2. Две схемы организации работ во времени."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon, Rectangle, FancyArrow

NAVY, BLUE, GREEN, PURPLE, ORANGE = "#003366", "#0079C2", "#1B9E77", "#8E44AD", "#C4690E"
GREY, LIGHT, INK = "#595959", "#E8F2FA", "#1A1A1A"
plt.rcParams["font.family"] = "DejaVu Sans"

fig, ax = plt.subplots(figsize=(9.3, 3.75), dpi=660)
ax.set_xlim(0, 100); ax.set_ylim(0, 38); ax.axis("off")

def bar(x, y, w, h, color, text, fs=8.6, tc="white", alpha=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.9",
                                fc=color, ec="none", alpha=alpha, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, zorder=4, linespacing=1.25)

def lane_label(y, t1, t2, color):
    ax.text(0.5, y, t1, ha="left", va="center", fontsize=9.6, color=color, fontweight="bold")
    if t2:
        ax.text(0.5, y - 2.7, t2, ha="left", va="center", fontsize=8.0, color=GREY)

def milestone(x, y, label, color):
    ax.add_patch(Polygon([[x, y + 2.6], [x + 1.5, y], [x, y - 2.6], [x - 1.5, y]],
                         closed=True, fc=color, ec="white", lw=1.1, zorder=6))
    ax.text(x, y + 4.3, label, ha="center", va="bottom", fontsize=8.4,
            color=color, fontweight="bold", zorder=6)

# ---------- пиктограммы
def ico_idea(x, y, c):
    ax.add_patch(Circle((x, y + 0.5), 1.25, fc="none", ec=c, lw=1.5, zorder=5))
    ax.plot([x - 0.6, x + 0.6], [y - 1.1, y - 1.1], color=c, lw=1.5, zorder=5)
    ax.plot([x - 0.4, x + 0.4], [y - 1.9, y - 1.9], color=c, lw=1.5, zorder=5)
    for a in (0.0, 0.5, 1.0):
        import math
        ax.plot([x + 1.9 * math.cos(math.pi * (0.25 + a * 0.5)),
                 x + 2.6 * math.cos(math.pi * (0.25 + a * 0.5))],
                [y + 0.5 + 1.9 * math.sin(math.pi * (0.25 + a * 0.5)),
                 y + 0.5 + 2.6 * math.sin(math.pi * (0.25 + a * 0.5))],
                color=c, lw=1.2, zorder=5)

def ico_doc(x, y, c):
    ax.add_patch(Rectangle((x - 1.1, y - 1.9), 2.2, 3.8, fc="none", ec=c, lw=1.5, zorder=5))
    for k in range(3):
        ax.plot([x - 0.6, x + 0.6], [y + 0.9 - k * 0.9] * 2, color=c, lw=1.1, zorder=5)

def ico_crane(x, y, c):
    ax.plot([x - 0.2, x - 0.2], [y - 2.0, y + 2.0], color=c, lw=1.6, zorder=5)
    ax.plot([x - 1.6, x + 2.1], [y + 2.0, y + 2.0], color=c, lw=1.6, zorder=5)
    ax.plot([x + 1.5, x + 1.5], [y + 2.0, y + 0.6], color=c, lw=1.2, zorder=5)
    ax.add_patch(Rectangle((x + 1.0, y - 0.4), 1.0, 1.0, fc="none", ec=c, lw=1.2, zorder=5))
    ax.plot([x - 1.6, x + 1.2], [y - 2.0, y - 2.0], color=c, lw=1.6, zorder=5)

def ico_warn(x, y, c):
    ax.add_patch(Polygon([[x, y + 1.7], [x + 1.7, y - 1.3], [x - 1.7, y - 1.3]],
                         closed=True, fc="none", ec=c, lw=1.5, zorder=5))
    ax.plot([x, x], [y + 0.8, y - 0.25], color=c, lw=1.5, zorder=5)
    ax.plot([x, x], [y - 0.7, y - 0.78], color=c, lw=1.8, zorder=5)

# ---------- верхняя полоса, последовательная организация
yA = 27.5
lane_label(yA + 9.0, "Последовательная организация", "разработка завершается, затем проектирование и стройка", NAVY)
ico_idea(5.5, yA, BLUE)
bar(9.5, yA - 2.6, 34, 5.2, BLUE, "Разработка и подтверждение\nхарактеристик оборудования")
ico_doc(47.0, yA, PURPLE)
bar(50.0, yA - 2.6, 17, 5.2, PURPLE, "Проектная\nдокументация")
ico_crane(70.0, yA, GREY)
bar(73.5, yA - 2.6, 16, 5.2, GREY, "Строительство")
milestone(90.5, yA, "Ввод объекта", NAVY)

# ---------- нижняя полоса, параллельная организация
yB = 11.0
lane_label(yB + 9.4, "Параллельная организация", "проектирование и стройка начинаются до конца разработки", GREEN)
ico_idea(5.5, yB + 2.25, BLUE)
bar(9.5, yB + 0.2, 34, 4.1, BLUE, "Разработка и подтверждение характеристик", fs=8.2)
ico_doc(13.0, yB - 4.95, PURPLE)
bar(16.5, yB - 7.0, 17, 4.1, PURPLE, "Проектная документация", fs=8.2)
ico_crane(37.0, yB - 4.95, GREEN)
bar(40.5, yB - 7.0, 16, 4.1, GREEN, "Строительство", fs=8.2)
milestone(58.0, yB - 2.4, "Ввод объекта", GREEN)

# ---------- выигрыш во времени
ax.annotate("", xy=(58.5, yB + 7.0), xytext=(90.0, yB + 7.0),
            arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=1.7), zorder=6)
ax.plot([90.5, 90.5], [yA - 3.2, yB + 7.0], color=NAVY, lw=0.9, ls=":", zorder=2)
ax.plot([58.0, 58.0], [yB + 7.0, yB - 2.4], color=GREEN, lw=0.9, ls=":", zorder=2)
ax.text(74.2, yB + 8.2, "выигрыш во времени", ha="center", va="bottom", fontsize=9.0,
        color=ORANGE, fontweight="bold")
ax.text(74.2, yB + 5.6, "ранний ввод объекта и начало дохода", ha="center", va="top",
        fontsize=8.2, color=GREY)

# ---------- риск
ico_warn(61.0, yB - 4.95, ORANGE)
ax.text(64.0, yB - 4.95, "риск переделок документации,\nхарактеристики еще не зафиксированы",
        ha="left", va="center", fontsize=8.2, color=ORANGE, linespacing=1.3)

# ---------- ось времени
ax.annotate("", xy=(97.5, 1.6), xytext=(2.0, 1.6),
            arrowprops=dict(arrowstyle="->", color="#B9B6AE", lw=1.2))
ax.text(97.5, 0.2, "время", ha="right", va="bottom", fontsize=8.0, color=GREY)

fig.tight_layout(pad=0.15)
fig.savefig("/home/claude/work/fig/s2_lanes.png", bbox_inches="tight", facecolor="white")
print("ok")

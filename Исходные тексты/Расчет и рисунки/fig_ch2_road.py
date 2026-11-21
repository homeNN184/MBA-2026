# -*- coding: utf-8 -*-
"""Рисунок 15 работы. Последовательность разработки СПУ ПГ-018 и стадий строительства."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 6.5, 2.95
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")

U = 100.0 / W_IN          # единиц графика в одном дюйме
PAD = 1.2                 # поле внутри блока, единиц


def fit(text, width, base=6.4, lo=4.4):
    """Подбор размера шрифта так, чтобы самая длинная строка влезла в блок."""
    n = max(len(s) for s in text.split("\n"))
    fs = base
    while fs > lo and n * 0.55 * fs / 72.0 * U > width - 2 * PAD:
        fs -= 0.1
    return fs


def band(items, y0, h, shades, fsbase=7.0):
    for (t, a, b), c in zip(items, shades):
        ax.add_patch(Rectangle((a, y0), b - a, h, fc=c, ec="white", lw=0.9, zorder=3))
        ax.text((a + b) / 2, y0 + h / 2, t, ha="center", va="center",
                fontsize=fit(t, b - a, fsbase), color=NAVY, zorder=4, linespacing=1.35)


# ---------------- инновационный процесс
INN_B = [("Техническое\nзадание", 0, 10.4), ("Конструкторская\nдокументация", 10.4, 29.6),
         ("Изготовление\nи комплектация", 29.6, 52.8), ("Заводские\nиспытания", 52.8, 65.6),
         ("Монтаж\nна объекте", 65.6, 80.0), ("Пусконаладочные\nработы, поверка", 80.0, 100.0)]
SH1 = ["#CFE4F5", "#A6CCEB", "#A6CCEB", "#CFE4F5", "#A6CCEB", "#CFE4F5"]
TOP_Y, BH = 29.5, 8.5
band(INN_B, TOP_Y, BH, SH1)
ax.text(100.0, TOP_Y + BH + 0.8, "Разработка и поставка СПУ ПГ-018", ha="right", va="bottom",
        fontsize=7.4, color=INN, fontweight="bold")
# короткая ось времени над дорожной картой
ax.add_patch(FancyArrowPatch((2.0, TOP_Y + BH + 4.2), (26.0, TOP_Y + BH + 4.2),
                             arrowstyle="-|>", mutation_scale=9, color=SUB, lw=1.0))
ax.text(27.6, TOP_Y + BH + 4.2, "Срок реализации Проекта", ha="left", va="center",
        fontsize=6.6, color=SUB)

# ---------------- инвестиционный процесс
INV_B = [("Задание на\nпроектирование", 0, 8.8), ("Инженерные\nизыскания", 8.8, 17.6),
         ("Проектная\nдокументация,\nэкспертиза", 17.6, 36.0), ("Рабочая\nдокументация", 36.0, 49.6),
         ("Строительно-монтажные работы", 49.6, 78.4), ("Пусконала-\nдочные работы", 78.4, 90.4),
         ("Ввод", 90.4, 100.0)]
SH2 = ["#DCF1E9", "#DCF1E9", "#A9DDC9", "#A9DDC9", "#86CEB2", "#C4E8DA", "#DCF1E9"]
BOT_Y = 5.0
band(INV_B, BOT_Y, BH, SH2)
ax.text(100.0, BOT_Y - 1.0, "Строительство третьего пускового комплекса", ha="right", va="top",
        fontsize=7.4, color=INV, fontweight="bold")

# ---------------- точки связи
LINKS = [(6.8, "Исходные данные\nдля конструирования", False, 0),
         (27.0, "Уточнение компоновки,\nнагрузок и мощности", True, 1),
         (46.5, "Согласование изменений\nс рабочей документацией", True, 0),
         (69.0, "Готовность объекта\nдля монтажа", False, 1),
         (86.0, "Подтверждение характеристик\nна построенном объекте", False, 0)]
LV = [25.0, 18.4]
for x, lab, down, lvl in LINKS:
    y1, y2 = (TOP_Y, BOT_Y + BH) if down else (BOT_Y + BH, TOP_Y)
    ax.add_patch(FancyArrowPatch((x, y1), (x, y2), arrowstyle="-|>", mutation_scale=8,
                                 color=TRN, lw=1.1, zorder=5))
    ax.text(x, LV[lvl], lab, ha="center", va="center", fontsize=5.2, color=TRN, zorder=6,
            linespacing=1.35,
            bbox=dict(boxstyle="round,pad=0.30", fc="white", ec=TRN, lw=0.7))

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/f2_road.png", dpi=300, bbox_inches="tight", facecolor="white")
print("ok")

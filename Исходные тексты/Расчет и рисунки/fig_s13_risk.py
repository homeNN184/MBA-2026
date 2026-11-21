# -*- coding: utf-8 -*-
"""Слайд 13. Риск-моделирование и имитационное моделирование."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import icons_lib as I

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
PURPLE, FILL = "#8E44AD", "#EAF2FA"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")

LM, GX = 2.0, 2.0
CW = (100 - 2 * LM - GX) / 2.0
TOP, BOT = YM - 0.9, 1.0

COLS = [
    (TRN, I.warn, "Риск доработок", [
        "Событие доработки: испытания изменили конструкцию,\nдокументацию или выполненные работы",
        "Каждое событие задано вероятностью, затратами\nи задержкой, вероятность растет при раннем входе",
        "События наступают после входа: при TRL5 — четыре,\nTRL6 — три, TRL7 — два",
        "Перебираются все исходы: вероятность, ожидаемый ЧДД\nи остаток преимущества",
    ]),
    (PURPLE, I.chartup, "Имитационное моделирование", [
        "Все параметры отклоняются одновременно и случайно,\nдоработки наступают с заданными вероятностями",
        "5 000 прогонов, в каждом выполняется полный расчет\nсценария",
        "Определяются медиана, диапазон P10–P90 и доля\nпрогонов с отрицательным ЧДД",
        "Начальное значение генератора фиксируется,\nрасчет воспроизводим",
    ]),
]

for k, (col, icon, head, items) in enumerate(COLS):
    x0 = LM + k * (CW + GX)
    ax.add_patch(FancyBboxPatch((x0, BOT), CW, TOP - BOT,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
    ax.add_patch(FancyBboxPatch((x0, TOP - 0.75), CW, 0.75,
                                boxstyle="round,pad=0,rounding_size=0.35",
                                fc=col, ec="none", zorder=3))
    cx, cy = x0 + 4.6, TOP - 4.6
    ax.add_patch(Circle((cx, cy), 2.9, fc="none", ec=col, lw=1.5, zorder=4))
    icon(ax, cx, cy, 2.9, col, 1.6)
    ax.text(x0 + 9.0, cy, head, ha="left", va="center",
            fontsize=9.6, color=NAVY, fontweight="bold")
    y = TOP - 10.6
    for it in items:
        ax.add_patch(Circle((x0 + 3.2, y - 0.8), 0.48, fc=col, ec="none", zorder=5))
        ax.text(x0 + 5.4, y, it, ha="left", va="top",
                fontsize=8.0, color=SUB, linespacing=1.45)
        y -= (it.count("\n") + 1) * 2.2 + 3.6


fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s13_risk.png", dpi=660, facecolor="white")
print("ok")

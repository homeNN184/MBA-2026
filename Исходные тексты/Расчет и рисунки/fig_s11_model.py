# -*- coding: utf-8 -*-
"""Слайд 11. Экономическая модель интеграции: сценарии и структура расчета."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import icons_lib as I

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
PURPLE, FILL = "#8E44AD", "#EAF2FA"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")

LM = 2.0
TOP = YM - 0.9

# ---------------- четыре сценария
SC = [(SUB, "Базовый", "TRL9", "создается", "8,00", "—"),
      (TRN, "Интеграция TRL7", "TRL7", "создается", "6,80", "−1,20"),
      (INN, "Интеграция TRL6", "TRL6", "не создается", "6,35", "−1,65"),
      (INV, "Интеграция TRL5", "TRL5", "не создается", "5,90", "−2,10")]
GAP = 1.6
CW = (100 - 2 * LM - 3 * GAP) / 4.0
SY1, SY0 = TOP, TOP - 17.4
for k, (col, name, trl, inf, term, delta) in enumerate(SC):
    x0 = LM + k * (CW + GAP)
    ax.add_patch(FancyBboxPatch((x0, SY0), CW, SY1 - SY0,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
    ax.add_patch(FancyBboxPatch((x0, SY1 - 0.75), CW, 0.75,
                                boxstyle="round,pad=0,rounding_size=0.35",
                                fc=col, ec="none", zorder=3))
    ax.text(x0 + CW / 2, SY1 - 2.6, name, ha="center", va="center",
            fontsize=7.6, color=NAVY, fontweight="bold")
    rows = [("Вход в проектирование", trl),
            ("Опытная инфраструктура", inf),
            ("Срок ввода, лет", term + ("" if delta == "—" else "   " + delta))]
    y = SY1 - 5.4
    for cap, val in rows:
        ax.text(x0 + CW / 2, y, cap, ha="center", va="center", fontsize=6.0, color=SUB)
        ax.text(x0 + CW / 2, y - 1.9, val, ha="center", va="center",
                fontsize=8.4, color=col, fontweight="bold")
        y -= 4.6
    ax.plot([x0 + 2.2, x0 + CW - 2.2], [SY1 - 3.9, SY1 - 3.9], color="#D6E3F0", lw=0.9, zorder=4)

# ---------------- структура расчета
BY1, BY0 = SY0 - 2.0, 1.0
BW = (100 - 2 * LM - 2 * 4.0) / 3.0
BLOCKS = [
    (INN, I.books, "Входные данные", [
        "Проект: бюджет, доля инновационных\nзатрат, ставка дисконтирования",
        "Сроки: восемь переходов TRL,\nвосемь стадий строительства",
        "Эксплуатация: выручка, загрузка,\nрасходы, ремонты",
        "Условия подтверждения: опытная\nинфраструктура, хранение",
    ]),
    (TRN, I.gears, "Расчет", [
        "Календарный план сценария\nпо срокам и долям этапов",
        "Денежные потоки по годам,\nкапитальные вложения",
        "Налоговый блок: база, перенос\nубытков, налог",
        "Дисконтирование к началу\nразработки",
    ]),
    (INV, I.chartup, "Результаты", [
        "Срок ввода объекта, ЧДД,\nиндекс доходности",
        "Внутренняя норма доходности,\nсроки окупаемости",
        "Преимущество над Базовым\nсценарием",
        "Потери от переделок и остаток\nпреимущества",
    ]),
]
for k, (col, icon, head, items) in enumerate(BLOCKS):
    x0 = LM + k * (BW + 4.0)
    ax.add_patch(FancyBboxPatch((x0, BY0), BW, BY1 - BY0,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc=FILL, ec="none", zorder=2))
    cx, cy = x0 + 3.4, BY1 - 3.0
    ax.add_patch(Circle((cx, cy), 1.9, fc="none", ec=col, lw=1.2, zorder=4))
    icon(ax, cx, cy, 1.9, col, 1.3)
    ax.text(x0 + 6.4, cy, head, ha="left", va="center",
            fontsize=7.6, color=NAVY, fontweight="bold")
    y = BY1 - 6.4
    for it in items:
        ax.add_patch(Circle((x0 + 2.4, y - 0.45), 0.34, fc=col, ec="none", zorder=5))
        ax.text(x0 + 3.9, y, it, ha="left", va="top",
                fontsize=6.2, color=SUB, linespacing=1.4)
        y -= 3.6
    if k:
        ax.add_patch(FancyArrowPatch((x0 - 3.2, (BY0 + BY1) / 2), (x0 - 0.9, (BY0 + BY1) / 2),
                                     arrowstyle="-|>", mutation_scale=10, color=TRN, lw=1.5, zorder=5))

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s11_model.png", dpi=660, facecolor="white")
print("ok")

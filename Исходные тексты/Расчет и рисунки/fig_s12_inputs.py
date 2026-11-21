# -*- coding: utf-8 -*-
"""Слайд 12. Экономическая модель: входные параметры."""
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

LM, GAP = 2.0, 1.8
CW = (100 - 2 * LM - 2 * GAP) / 3.0
BY0, BY1 = 0.3, 0.6
TOP = YM - 0.9
CY0 = BY1 + 1.6

COLS = [
    (INN, I.books, "Проект и сроки", [
        ("Бюджет проекта", "1 000 млн руб."),
        ("Доля инновационных\nи инвестиционных затрат", "35 % / 65 %"),
        ("Ставка дисконтирования, цены", "12 %, постоянные"),
        ("Срок разработки TRL1–TRL9", "3 года, восемь переходов"),
        ("Срок инвестиционного проекта", "5 лет, восемь стадий"),
    ]),
    (INV, I.building, "Эксплуатация и налоги", [
        ("Операционный период, загрузка", "30 лет; 20, 60, 100 %"),
        ("Выручка при полной загрузке", "350 млн руб. в год"),
        ("Эксплуатационные расходы", "19,14 млн руб. в год"),
        ("Обслуживание, текущий\nи капитальный ремонт", "1,2 / 2,5 / 5,0 млн руб."),
        ("Налог на прибыль, амортизация", "25 %, линейная, 20 лет"),
        ("Предел зачета убытков", "50 % базы до 2030 года"),
    ]),
    (TRN, I.flask, "Условия подтверждения", [
        ("Опытная инфраструктура", "10 % инновационных затрат"),
        ("Сценарии, где она создается", "Базовый и Интеграция TRL7"),
        ("Хранение и консервация\nв сценарии Интеграция TRL7", "1,5 % инновационных\nзатрат в год"),
    ]),
]

for k, (col, icon, head, rows) in enumerate(COLS):
    x0 = LM + k * (CW + GAP)
    ax.add_patch(FancyBboxPatch((x0, CY0), CW, TOP - CY0,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
    ax.add_patch(FancyBboxPatch((x0, TOP - 0.75), CW, 0.75,
                                boxstyle="round,pad=0,rounding_size=0.35",
                                fc=col, ec="none", zorder=3))
    cx, cy = x0 + 3.5, TOP - 3.4
    ax.add_patch(Circle((cx, cy), 2.0, fc="none", ec=col, lw=1.2, zorder=4))
    icon(ax, cx, cy, 2.0, col, 1.3)
    ax.text(x0 + 6.6, cy, head, ha="left", va="center",
            fontsize=7.6, color=NAVY, fontweight="bold")
    y = TOP - 7.2
    for cap, val in rows:
        nc = cap.count("\n") + 1
        ax.text(x0 + 2.0, y, cap, ha="left", va="top",
                fontsize=6.0, color=SUB, linespacing=1.35)
        ax.text(x0 + 2.0, y - nc * 1.35 - 0.35, val, ha="left", va="top",
                fontsize=7.2, color=col, fontweight="bold", linespacing=1.35)
        y -= nc * 1.35 + (val.count("\n") + 1) * 1.6 + 1.5


# ---------------- критерии принятия решения (третья колонка, нижняя часть)
x3 = LM + 2 * (CW + GAP)
ys = 15.8
ax.plot([x3 + 2.0, x3 + CW - 2.0], [ys + 2.6, ys + 2.6], color="#D6E3F0", lw=1.0, zorder=4)
ax.text(x3 + 2.0, ys + 0.9, "Критерии выбора сценария и их вес", ha="left", va="center",
        fontsize=7.0, color=NAVY, fontweight="bold")
CRIT = [("Чистый дисконтированный доход", "0,30"),
        ("Срок ввода объекта", "0,15"),
        ("Остаток в наихудшем исходе", "0,15"),
        ("Доказательность уровней TRL", "0,15"),
        ("Запас устойчивости", "0,15"),
        ("Ресурсная нагрузка", "0,10")]
y = ys - 1.6
for cap, w in CRIT:
    nc = cap.count("\n") + 1
    ax.add_patch(Circle((x3 + 2.5, y - 0.45), 0.34, fc=TRN, ec="none", zorder=5))
    ax.text(x3 + 3.8, y, cap, ha="left", va="top", fontsize=6.2, color=SUB, linespacing=1.3)
    ax.text(x3 + CW - 2.0, y, w, ha="right", va="top", fontsize=6.6, color=TRN, fontweight="bold")
    y -= 2.0


fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s12_inputs.png", dpi=660, facecolor="white")
print("ok")

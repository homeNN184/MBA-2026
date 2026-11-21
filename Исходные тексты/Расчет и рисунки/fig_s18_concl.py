# -*- coding: utf-8 -*-
"""Слайд 18. Выводы."""
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

Q = [
    (INV, I.chartup, "Источники выигрыша", [
        "Более раннее поступление выручки,\nобъект вводится раньше",
        "Отказ от временной опытной\nинфраструктуры в сценариях TRL6 и TRL5",
        "При нулевых затратах на нее преимущество\nсохраняется за счет срока ввода",
    ]),
    (INN, I.target, "Эффект интеграции", [
        "ЧДД выше Базового в 1,69–2,67 раза",
        "Прирост 19,8–48,1 % инновационных затрат,\n6,9–16,8 % бюджета проекта",
        "Срок ввода короче на 15,0–26,2 %,\nдисконтированная окупаемость на 16,1–30,7 %",
    ]),
    (TRN, I.warn, "Устойчивость вывода", [
        "Проверена по пяти параметрам, порядок\nсценариев не меняется ни в одной проверке",
        "При доработке на каждом уровне после входа\nсохраняется 10,1–47,0 % преимущества",
        "Запас по затратам и задержкам доработок\n1,12–1,94, наибольший у входа на TRL6",
    ]),
    (NAVY, I.check, "Применение", [
        "Пилотный проект, где разрабатываемое изделие\nявляется основным оборудованием объекта",
        "Расчет на предынвестиционной стадии\nи повторение в каждой контрольной точке",
        "По результатам — решение о распространении\nи об изменении форм документов планирования",
    ]),
]

LM, GX, GY = 2.0, 2.0, 1.2
CW = (100 - 2 * LM - GX) / 2.0
BY0, BY1 = 1.0, 6.4
TOP = YM - 0.9
RH = (TOP - BY1 - 1.6 - GY) / 2.0

for k, (col, icon, head, items) in enumerate(Q):
    r, c = divmod(k, 2)
    x0 = LM + c * (CW + GX)
    y1 = TOP - r * (RH + GY)
    y0 = y1 - RH
    ax.add_patch(FancyBboxPatch((x0, y0), CW, RH,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
    ax.add_patch(FancyBboxPatch((x0, y1 - 0.75), CW, 0.75,
                                boxstyle="round,pad=0,rounding_size=0.35",
                                fc=col, ec="none", zorder=3))
    cx, cy = x0 + 3.5, y1 - 3.4
    ax.add_patch(Circle((cx, cy), 2.0, fc="none", ec=col, lw=1.2, zorder=4))
    icon(ax, cx, cy, 2.0, col, 1.3)
    ax.text(x0 + 6.6, cy, head, ha="left", va="center",
            fontsize=7.8, color=NAVY, fontweight="bold")
    y = y1 - 6.4
    for it in items:
        ax.add_patch(Circle((x0 + 2.6, y - 0.45), 0.36, fc=col, ec="none", zorder=5))
        ax.text(x0 + 4.2, y, it, ha="left", va="top",
                fontsize=6.4, color=SUB, linespacing=1.3)
        y -= (it.count("\n") + 1) * 1.28 + 0.9

ax.add_patch(FancyBboxPatch((LM, BY0), 100 - 2 * LM, BY1 - BY0,
                            boxstyle="round,pad=0,rounding_size=0.9",
                            fc=FILL, ec="none", zorder=2))
ax.add_patch(FancyBboxPatch((LM, BY0), 0.9, BY1 - BY0,
                            boxstyle="round,pad=0,rounding_size=0.4",
                            fc=NAVY, ec="none", zorder=3))
ax.text(LM + 2.6, (BY0 + BY1) / 2 + 1.1, "Цель работы достигнута", ha="left", va="center",
        fontsize=7.2, color=NAVY, fontweight="bold")
ax.text(LM + 2.6, (BY0 + BY1) / 2 - 1.1,
        "разработана модель управления инновационной деятельностью при реализации инвестиционных проектов, "
        "работоспособность модели\nподтверждена расчетом на тестовых значениях исходных данных",
        ha="left", va="center", fontsize=6.6, color=SUB, linespacing=1.45)

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s18_concl.png", dpi=660, facecolor="white")
print("ok")

# -*- coding: utf-8 -*-
"""Слайд 5. Результат анализа нормативной и методической базы."""
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

LM, GAP = 2.0, 2.4
CW = (100 - 2 * LM - GAP) / 2.0
CY0, CY1 = 8.2, YM - 0.9

COLS = [
    (INV, I.check, "Предусмотрено действующими документами", [
        "Обязательные требования к созданию объекта\nи обоснованию применяемых решений",
        "Приоритеты технологического развития\nи энергетической безопасности",
        "Организационные связи инновационной\nи инвестиционной деятельности, участие\n"
        "профильных подразделений, согласование\nпрограммы внедрения",
        "Инновационный, патентный и экологический\nанализ решений на предынвестиционной стадии",
        "Шкала уровней готовности технологии",
    ]),
    (TRN, I.warn, "Требует проработки для параллельной работы", [
        "Разработка оборудования под конкретный\nстроительный проект и срок ввода объекта",
        "Общие контрольные точки двух процессов\nи состав подтверждающих материалов",
        "Разграничение технологической готовности,\nготовности проектной документации\n"
        "и достаточности исходных данных",
        "Порядок действий при неподтвержденной\nготовности и учет изменений",
        "Сведения об уровне готовности в формах\nдокументов планирования",
    ]),
]

for k, (col, icon, head, items) in enumerate(COLS):
    x0 = LM + k * (CW + GAP)
    ax.add_patch(FancyBboxPatch((x0, CY0), CW, CY1 - CY0,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
    ax.add_patch(FancyBboxPatch((x0, CY1 - 0.75), CW, 0.75,
                                boxstyle="round,pad=0,rounding_size=0.35",
                                fc=col, ec="none", zorder=3))
    cx, cy = x0 + 3.9, CY1 - 3.9
    ax.add_patch(Circle((cx, cy), 2.3, fc="none", ec=col, lw=1.3, zorder=4))
    icon(ax, cx, cy, 2.3, col, 1.4)
    ax.text(x0 + 7.6, cy, head, ha="left", va="center",
            fontsize=7.8, color=NAVY, fontweight="bold")
    y = CY1 - 8.2
    for it in items:
        n = it.count("\n") + 1
        ax.add_patch(Circle((x0 + 2.6, y - 0.55), 0.42, fc=col, ec="none", zorder=5))
        ax.text(x0 + 4.4, y, it, ha="left", va="top",
                fontsize=7.0, color=SUB, linespacing=1.42)
        y -= n * 1.52 + 1.45


by0, by1 = 0.3, 4.4
ax.add_patch(FancyBboxPatch((LM, by0), 100 - 2 * LM, by1 - by0,
                            boxstyle="round,pad=0,rounding_size=0.9",
                            fc=FILL, ec="none", zorder=2))
ax.add_patch(FancyBboxPatch((LM, by0), 0.9, by1 - by0,
                            boxstyle="round,pad=0,rounding_size=0.4",
                            fc=NAVY, ec="none", zorder=3))
ax.text(LM + 2.6, (by0 + by1) / 2,
        "Механизм, пригодный для прямого применения, в рассмотренных источниках не выявлен. "
        "Инструменты для его построения дают зарубежная\nи российская практика: оценка и планирование "
        "повышения готовности, поэтапные решения по пакетам работ, испытательная инфраструктура",
        ha="left", va="center", fontsize=7.0, color=SUB, linespacing=1.5)

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s5_res.png", dpi=660, facecolor="white")
print("ok")

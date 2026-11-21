# -*- coding: utf-8 -*-
"""Структура расчетной модели: входные данные, расчетное ядро, результаты."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
PURPLE, FILL = "#8E44AD", "#EAF2FA"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")

LM, GAP = 2.0, 3.4
CW = (100 - 2 * LM - 2 * GAP) / 3.0
TOP, BOT = YM - 0.9, 1.0

COLS = [(INN, "Входные данные",
         ["Бюджет проекта, доля инновационной\nчасти, ставка дисконтирования",
          "Сроки разработки и строительства,\nдоли времени переходов и стадий",
          "Выручка, загрузка, персонал,\nэксплуатационные расходы",
          "Налоги на прибыль и имущество,\nсрок амортизации, зачет убытка",
          "Стоимость опытной инфраструктуры",
          "События доработки: вероятность,\nпрямые затраты, задержка"]),
        (TRN, "Расчетное ядро",
         ["Календарь переходов уровней\nготовности и стадий строительства",
          "Годовые потоки затрат, выручки,\nналогов и дисконтирования",
          "Показатели эффективности:\nЧДД, ИД, ВНД, сроки окупаемости",
          "Полный перебор исходов событий\nдоработки и ожидаемые потери",
          "Имитационный расчет методом\nМонте-Карло на общем наборе отклонений",
          "Интегральная оценка по шести\nкритериям и правило выбора"]),
        (INV, "Результаты",
         ["Показатели по четырем сценариям\nи преимущество над базовым",
          "Календарный план и срок ввода\nобъекта по каждому сценарию",
          "Границы сохранения преимущества\nпо трем параметрам",
          "Медиана, доля убыточных прогонов,\nдоля лучших прогонов",
          "Профиль риска и остаток преимущества\nв наихудшем исходе",
          "Выбранный сценарий интеграции"])]

for k, (col, head, items) in enumerate(COLS):
    x0 = LM + k * (CW + GAP)
    ax.add_patch(FancyBboxPatch((x0, BOT), CW, TOP - BOT,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
    ax.add_patch(FancyBboxPatch((x0, TOP - 0.8), CW, 0.8,
                                boxstyle="round,pad=0,rounding_size=0.35",
                                fc=col, ec="none", zorder=3))
    ax.text(x0 + CW / 2, TOP - 2.6, head, ha="center", va="center",
            fontsize=8.0, color=NAVY, fontweight="bold")
    y = TOP - 5.0
    for it in items:
        n = it.count("\n") + 1
        h = n * 1.8 + 1.3
        ax.add_patch(FancyBboxPatch((x0 + 1.4, y - h), CW - 2.8, h,
                                    boxstyle="round,pad=0,rounding_size=0.6",
                                    fc=FILL, ec="none", zorder=3))
        ax.text(x0 + CW / 2, y - h / 2, it, ha="center", va="center",
                fontsize=5.9, color=SUB, linespacing=1.35, zorder=4)
        y -= h + 1.0

for k in (0, 1):
    x = LM + k * (CW + GAP) + CW
    ax.add_patch(FancyArrowPatch((x + 0.5, YM / 2), (x + GAP - 0.5, YM / 2),
                                 arrowstyle="-|>,head_width=0.34,head_length=0.8",
                                 color=NAVY, lw=2.0, alpha=0.75, zorder=5))

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/mod_struct.png", dpi=660, facecolor="white")
print("ok")

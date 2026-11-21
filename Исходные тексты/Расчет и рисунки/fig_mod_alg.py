# -*- coding: utf-8 -*-
"""Алгоритм моделирования: семь шагов расчета."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
PURPLE, FILL = "#8E44AD", "#EAF2FA"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")

LM, GAP = 2.0, 1.8
TOP = YM - 0.9

ST = [(INN, "Календарь", "Сроки переходов уровней\nготовности и стадий\nстроительства", "schedule( )"),
      (INN, "Годовые потоки", "Затраты, выручка, налоги,\nдисконтирование по годам\nрасчетного периода", "flows( )"),
      (INN, "Показатели", "ЧДД, индекс доходности,\nвнутренняя норма, простой\nи дисконтированный срок", "indicators( )"),
      (TRN, "Область событий", "Какие события доработки\nвозможны при данном\nуровне входа", "event_scope( )"),
      (TRN, "Перебор исходов", "Все сочетания событий,\nих вероятности, потери\nи ожидаемый доход", "outcomes( )"),
      (PURPLE, "Имитационный расчет", "Одновременное случайное\nотклонение параметров,\nодин набор на все сценарии", "monteCarlo( )"),
      (INV, "Правило выбора", "Отсев по наихудшему исходу,\nсравнение по ожидаемому\nдоходу и сроку ввода", "вкладка «Выбор сценария»"),
      (NAVY, "Интегральная оценка", "Шесть критериев с весами\nи проверка устойчивости\nвыбора к изменению весов", "расчетный модуль работы")]

CW = (100 - 2 * LM - 3 * GAP) / 4.0
RH = 15.6
ROWS = [(0, 4, TOP), (4, 8, TOP - RH - 3.4)]
pos = []
for a, b, ytop in ROWS:
    n = b - a
    for j, k in enumerate(range(a, b)):
        col, head, body, fn = ST[k]
        x0 = LM + j * (CW + GAP)
        ax.add_patch(FancyBboxPatch((x0, ytop - RH), CW, RH,
                                    boxstyle="round,pad=0,rounding_size=0.9",
                                    fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
        ax.add_patch(Circle((x0 + 3.0, ytop - 3.0), 1.5, fc=col, ec="none", zorder=4))
        ax.text(x0 + 3.0, ytop - 3.0, str(k + 1), ha="center", va="center",
                fontsize=7.0, color="white", fontweight="bold", zorder=5)
        ax.text(x0 + 5.6, ytop - 3.0, head, ha="left", va="center",
                fontsize=7.2, color=NAVY, fontweight="bold")
        ax.text(x0 + CW / 2, ytop - 8.6, body, ha="center", va="center",
                fontsize=5.9, color=SUB, linespacing=1.4)
        ax.add_patch(FancyBboxPatch((x0 + 2.0, ytop - RH + 1.2), CW - 4.0, 2.4,
                                    boxstyle="round,pad=0,rounding_size=0.5",
                                    fc=FILL, ec="none", zorder=3))
        mono = fn.endswith("( )")
        ax.text(x0 + CW / 2, ytop - RH + 2.4, fn, ha="center", va="center",
                fontsize=6.0 if mono else 5.6, color=col, zorder=4,
                family="DejaVu Sans Mono" if mono else "DejaVu Sans")
        pos.append((x0, ytop))
        if j < n - 1:
            ax.add_patch(FancyArrowPatch((x0 + CW + 0.25, ytop - RH / 2),
                                         (x0 + CW + GAP - 0.25, ytop - RH / 2),
                                         arrowstyle="-|>,head_width=0.28,head_length=0.7",
                                         color=NAVY, lw=1.6, alpha=0.7, zorder=5))

# переход со второго блока первого ряда во второй ряд
x_end = LM + 3 * (CW + GAP) + CW
y1 = TOP - RH
y2 = TOP - RH - 5.0 - RH / 2
ax.add_patch(FancyArrowPatch((x_end - CW / 2, y1 - 0.3), (LM + CW / 2, y2 + RH + 0.3),
                             connectionstyle="arc3,rad=-0.12",
                             arrowstyle="-|>,head_width=0.28,head_length=0.7",
                             color=NAVY, lw=1.6, alpha=0.5, zorder=1))


# итоговая полоса
BY0, BY1 = 0.6, 5.6
ax.add_patch(FancyBboxPatch((LM, BY0), 100 - 2 * LM, BY1 - BY0,
                            boxstyle="round,pad=0,rounding_size=0.9",
                            fc=FILL, ec="none", zorder=2))
ax.text(LM + 2.6, BY1 - 1.7, "Результат расчета", ha="left", va="center",
        fontsize=6.8, color=NAVY, fontweight="bold")
ax.text(LM + 2.6, BY1 - 3.7, "сценарий интеграции с входом на уровне TRL5, срок ввода объекта 5,90 года, "
        "ожидаемый чистый дисконтированный доход 260,0 млн руб., преимущество над базовым сценарием 168,5 млн руб.",
        ha="left", va="center", fontsize=6.0, color=SUB)

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/mod_alg.png", dpi=660, facecolor="white")
print("ok")

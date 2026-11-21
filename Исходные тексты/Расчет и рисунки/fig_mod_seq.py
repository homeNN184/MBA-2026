# -*- coding: utf-8 -*-
"""Последовательность определения сценария: условия отсева и выбор."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
PURPLE, FILL = "#8E44AD", "#EAF2FA"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")

TOP = YM - 1.2
BW, BH = 28.0, 6.4
DW, DH = 32.0, 9.0
RW = 13.0
COL = [(17.0, 35.0), (66.0, 84.0)]      # центр блока, левый край плашки отказа
GAP = 3.1


def act(cx, cy, title, body, col=INN, dark=False):
    fc = NAVY if dark else "#FFFFFF"
    ax.add_patch(FancyBboxPatch((cx - BW / 2, cy - BH / 2), BW, BH,
                                boxstyle="round,pad=0,rounding_size=0.8",
                                fc=fc, ec="none" if dark else "#D6E3F0",
                                lw=1.0, zorder=3))
    if not dark:
        ax.add_patch(FancyBboxPatch((cx - BW / 2, cy - BH / 2), 0.7, BH,
                                    boxstyle="round,pad=0,rounding_size=0.3",
                                    fc=col, ec="none", zorder=4))
    ax.text(cx, cy + 1.5, title, ha="center", va="center", fontsize=6.6,
            color="white" if dark else NAVY, fontweight="bold", zorder=5)
    ax.text(cx, cy - 1.5, body, ha="center", va="center", fontsize=5.4,
            color="#CFE3F5" if dark else SUB, linespacing=1.35, zorder=5)


def cond(cx, cy, text):
    ax.add_patch(Polygon([(cx, cy + DH / 2), (cx + DW / 2, cy),
                          (cx, cy - DH / 2), (cx - DW / 2, cy)],
                         closed=True, fc=FILL, ec=TRN, lw=1.1, zorder=3))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=5.0,
            color=NAVY, linespacing=1.35, zorder=5)


def arr(x1, y1, x2, y2, col=NAVY, al=0.7, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                 connectionstyle="arc3,rad=%.2f" % rad,
                                 arrowstyle="-|>,head_width=0.26,head_length=0.66",
                                 color=col, lw=1.4, alpha=al, zorder=2))


def reject(k, cy, text):
    x0 = COL[k][1]
    ax.add_patch(FancyBboxPatch((x0, cy - 3.0), RW, 6.0,
                                boxstyle="round,pad=0,rounding_size=0.7",
                                fc="#FBEFE4", ec="#E8C9A8", lw=1.0, zorder=3))
    ax.text(x0 + RW / 2, cy, text, ha="center", va="center", fontsize=5.2,
            color=TRN, linespacing=1.35, zorder=5)
    cx = COL[k][0]
    arr(cx + DW / 2, cy, x0 - 0.4, cy, col=TRN)
    ax.text((cx + DW / 2 + x0) / 2, cy + 1.6, "нет", ha="center", va="center",
            fontsize=5.2, color=TRN)


# ---------------- левая колонка
cx = COL[0][0]
y = TOP - BH / 2
act(cx, y, "Исходные данные проекта",
    "бюджет, сроки, ставка, выручка, налоги,\nпараметры событий доработки")
yp = y - BH / 2
y = yp - GAP - BH / 2
act(cx, y, "Расчет четырех сценариев",
    "базовый и три сценария интеграции\nс входом на уровнях TRL7, TRL6, TRL5")
arr(cx, yp, cx, y + BH / 2 + 0.3)
yp = y - BH / 2
y = yp - GAP - DH / 2
cond(cx, y, "Преимущество над базовым\nсохраняется в наихудшем исходе\nсобытий доработки?")
arr(cx, yp, cx, y + DH / 2 + 0.3)
reject(0, y, "Сценарий\nотклоняется")
yp = y - DH / 2
y = yp - GAP - BH / 2
act(cx, y, "Сравнение по ожидаемому доходу",
    "ожидаемый ЧДД по полному перебору\nисходов и срок ввода объекта", INV)
arr(cx, yp, cx, y + BH / 2 + 0.3)
ax.text(cx + 1.2, (yp + y + BH / 2) / 2, "да", ha="left", va="center",
        fontsize=5.2, color=INV)
y_last_left = y

# ---------------- переход во вторую колонку
xm = (COL[0][1] + RW + COL[1][0] - BW / 2) / 2.0
ax.plot([cx + BW / 2, xm], [y, y], color=NAVY, lw=1.4, alpha=0.5, zorder=1)
ax.plot([xm, xm], [y, TOP - BH / 2], color=NAVY, lw=1.4, alpha=0.5, zorder=1)
arr(xm, TOP - BH / 2, COL[1][0] - DW / 2 - 0.4, TOP - DH / 2, col=NAVY, al=0.5)

# ---------------- правая колонка
cx = COL[1][0]
y = TOP - DH / 2
cond(cx, y, "Преимущество устойчиво к ставке,\nстоимости опытной инфраструктуры\nи доле инновационных затрат?")
reject(1, y, "Уточнение\nисходных данных")
yp = y - DH / 2
y = yp - GAP - BH / 2
act(cx, y, "Имитационный расчет",
    "медиана, доля убыточных прогонов,\nдоля прогонов с лучшим результатом", PURPLE)
arr(cx, yp, cx, y + BH / 2 + 0.3)
ax.text(cx + 1.2, (yp + y + BH / 2) / 2, "да", ha="left", va="center",
        fontsize=5.2, color=INV)
yp = y - BH / 2
y = yp - GAP - BH / 2
act(cx, y, "Интегральная оценка",
    "шесть критериев с весами, проверка\nустойчивости выбора к изменению весов", INV)
arr(cx, yp, cx, y + BH / 2 + 0.3)
yp = y - BH / 2
y = yp - GAP - BH / 2
act(cx, y, "Решение о сценарии",
    "вход на уровне TRL5, срок ввода 5,90 года,\nожидаемый ЧДД 260,0 млн руб.", NAVY, dark=True)
arr(cx, yp, cx, y + BH / 2 + 0.3)

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/mod_seq.png", dpi=660, facecolor="white")
print("ok")

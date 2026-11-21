# -*- coding: utf-8 -*-
"""Слайд 16. Устойчивость результата: чувствительность и имитационный расчет."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
FILL = "#EAF2FA"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")

CL = {"BASE": SUB, "TRL7": TRN, "TRL6": INN, "TRL5": INV}
ORD = ["BASE", "TRL7", "TRL6", "TRL5"]
LB = {"BASE": "Базовый", "TRL7": "Интеграция TRL7",
      "TRL6": "Интеграция TRL6", "TRL5": "Интеграция TRL5"}

RATE = [10, 11, 12, 13, 14, 15, 16]
D_RATE = {"BASE": [327.9, 202.0, 100.8, 19.3, -46.5, -99.7, -142.6],
          "TRL7": [412.1, 278.6, 170.1, 81.6, 9.2, -50.1, -98.7],
          "TRL6": [500.8, 362.8, 249.8, 157.1, 80.7, 17.6, -34.7],
          "TRL5": [528.0, 386.0, 269.3, 172.9, 93.0, 26.7, -28.5]}
SHARE = [10, 20, 30, 35, 40, 50]
D_SHARE = {"BASE": [183.3, 150.5, 117.4, 100.8, 84.2, 51.0],
           "TRL7": [225.8, 204.0, 181.5, 170.1, 158.8, 136.1],
           "TRL6": [258.1, 254.8, 251.5, 249.8, 247.9, 243.8],
           "TRL5": [273.0, 272.0, 270.2, 269.3, 268.3, 266.5]}
PILOT = [0, 35, 70, 105, 140]
D_PILOT = {"BASE": [128.7, 100.8, 72.9, 45.0, 17.1],
           "TRL7": [198.0, 170.1, 142.2, 114.3, 86.4],
           "TRL6": [249.8, 249.8, 249.8, 249.8, 249.8],
           "TRL5": [269.3, 269.3, 269.3, 269.3, 269.3]}

PANELS = [(RATE, D_RATE, "Ставка дисконтирования, %", "Ставка дисконтирования 10–16 %"),
          (SHARE, D_SHARE, "Доля инновационных затрат, %", "Доля инновационных затрат 10–50 %"),
          (PILOT, D_PILOT, "Опытная инфраструктура, млн руб.", "Опытная инфраструктура 0–140 млн руб.")]

LM, GAP = 2.0, 2.2
PW = (100 - 2 * LM - 2 * GAP) / 3.0
TOP = YM - 0.9
BY0, BY1 = 1.0, 13.8
PY0 = BY1 + 1.8

for k, (xs, data, xlab, ttl) in enumerate(PANELS):
    x0 = LM + k * (PW + GAP)
    ax.add_patch(FancyBboxPatch((x0, PY0), PW, TOP - PY0,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
    ax.text(x0 + 2.0, TOP - 2.0, ttl, ha="left", va="center",
            fontsize=6.4, color=NAVY, fontweight="bold")
    a = fig.add_axes([(x0 + 6.0) / 100.0, (PY0 + 4.0) / YM,
                      (PW - 8.0) / 100.0, (TOP - PY0 - 8.0) / YM], zorder=6)
    a.set_facecolor("none")
    for s in ORD:
        a.plot(xs, data[s], color=CL[s], lw=1.4, marker="o", ms=1.8, zorder=4)
    a.axhline(0, color="#8A97A6", lw=0.9, zorder=3)
    a.set_xlim(min(xs), max(xs))
    a.tick_params(labelsize=5.4, length=2, width=0.7, colors=SUB, pad=1.5)
    a.set_xlabel(xlab, fontsize=5.6, color=SUB, labelpad=1.2)
    a.set_ylabel("ЧДД, млн руб.", fontsize=5.6, color=SUB, labelpad=1.2)
    a.grid(axis="y", color="#EDF2F7", lw=0.7)
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        a.spines[sp].set_color("#B9C6D6"); a.spines[sp].set_linewidth(0.8)

# ---------------- имитационный расчет
ax.add_patch(FancyBboxPatch((LM, BY0), 100 - 2 * LM, BY1 - BY0,
                            boxstyle="round,pad=0,rounding_size=0.9",
                            fc=FILL, ec="none", zorder=2))
ax.text(LM + 2.4, BY1 - 2.0, "Имитационный расчет (5 000 прогонов) и выбор сценария", ha="left", va="center",
        fontsize=6.8, color=NAVY, fontweight="bold")
COLS = [("Медиана ЧДД (P50), млн руб.", ["20,8", "81,2", "154,2", "164,4"]),
        ("Доля прогонов с ЧДД ниже нуля, %", ["45,4", "32,5", "19,0", "18,1"]),
        ("Доля прогонов, где сценарий лучший, %", ["0,0", "0,0", "17,1", "82,9"]),
        ("Интегральная оценка выбора, баллы", ["32,50", "39,92", "84,58", "72,98"])]
cx = [LM + 44.0, LM + 55.0, LM + 66.0, LM + 77.0]
for k, s in enumerate(ORD):
    ax.add_patch(Circle((cx[k] - 4.6, BY1 - 2.0), 0.38, fc=CL[s], ec="none", zorder=5))
    ax.text(cx[k] - 3.8, BY1 - 2.0, LB[s].replace("Интеграция ", ""), ha="left", va="center",
            fontsize=6.0, color=SUB, zorder=5)
y = BY1 - 4.4
for cap, vals in COLS:
    ax.text(LM + 2.4, y, cap, ha="left", va="center", fontsize=6.0, color=SUB, zorder=4)
    for k, v in enumerate(vals):
        ax.text(cx[k], y, v, ha="center", va="center", fontsize=6.4,
                color=CL[ORD[k]], fontweight="bold", zorder=4)
    y -= 2.6

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s16_sens.png", dpi=660, facecolor="white")
print("ok")

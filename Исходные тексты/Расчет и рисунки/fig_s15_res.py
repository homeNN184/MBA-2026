# -*- coding: utf-8 -*-
"""Слайд 15. Результаты моделирования: показатели и накопленный дисконтированный поток."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
from model import P, flows

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
HEAD = ["Базовый", "TRL7", "TRL6", "TRL5"]
ROWS = [
    ("Срок ввода, лет", ["8,00", "6,80", "6,35", "5,90"]),
    ("ЧДД, млн руб.", ["100,8", "170,1", "249,8", "269,3"]),
    ("Преимущество, млн руб.", ["—", "69,4", "149,1", "168,5"]),
    ("Преимущество, % инновационных затрат", ["—", "19,8", "42,6", "48,1"]),
    ("Индекс доходности", ["1,157", "1,250", "1,386", "1,400"]),
    ("Внутренняя норма доходности, %", ["13,27", "14,14", "15,32", "15,46"]),
    ("Дисконтированный срок окупаемости, лет", ["24,55", "20,60", "17,66", "17,01"]),
    ("Остаток преимущества при доработках, млн руб.", ["—", "7,0", "70,1", "48,1"]),
]

LM = 2.0
TOP, BOT = YM - 0.9, 1.0
TW = (100 - 2 * LM - 2.0) / 2.0   # ширина таблицы, равна ширине графика
ax.add_patch(FancyBboxPatch((LM, BOT), TW, TOP - BOT,
                            boxstyle="round,pad=0,rounding_size=0.9",
                            fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
CX = [LM + 26.8, LM + 31.9, LM + 37.0, LM + 42.1]
hy = TOP - 3.9
ax.text((CX[1] + CX[3]) / 2, TOP - 2.0, "Интеграция", ha="center", va="center",
        fontsize=5.8, color=SUB)
ax.plot([CX[1] - 2.2, CX[3] + 2.2], [TOP - 2.9, TOP - 2.9], color="#D6E3F0", lw=0.9, zorder=4)
for k, h in enumerate(HEAD):
    ax.text(CX[k], hy, h, ha="center", va="center", fontsize=6.6,
            color=CL[ORD[k]], fontweight="bold")
ax.plot([LM + 1.6, LM + TW - 1.6], [TOP - 5.6, TOP - 5.6], color="#D6E3F0", lw=0.9, zorder=4)

y = TOP - 7.6
for i, (cap, vals) in enumerate(ROWS):
    if i % 2 == 1:
        ax.add_patch(Rectangle((LM + 1.2, y - 1.5), TW - 2.4, 3.0,
                               fc=FILL, ec="none", zorder=3))
    ax.text(LM + 2.0, y, cap, ha="left", va="center", fontsize=5.9, color=SUB, zorder=4)
    for k, v in enumerate(vals):
        ax.text(CX[k], y, v, ha="center", va="center", fontsize=6.4,
                color=CL[ORD[k]] if i < 4 else NAVY,
                fontweight="bold" if i < 4 else "normal", zorder=4)
    y -= 4.2

# ---------------- накопленный дисконтированный поток
GX0, GX1 = LM + TW + 2.0, 98.0
ax.add_patch(FancyBboxPatch((GX0, BOT), GX1 - GX0, TOP - BOT,
                            boxstyle="round,pad=0,rounding_size=0.9",
                            fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
ax.text(GX0 + 2.2, TOP - 2.0, "Накопленный дисконтированный поток",
        ha="left", va="center", fontsize=6.8, color=NAVY, fontweight="bold")
lx = GX0 + 2.2
for s in ORD:
    ax.add_patch(Circle((lx, TOP - 4.4), 0.38, fc=CL[s], ec="none", zorder=5))
    lab = {"BASE": "Базовый", "TRL7": "TRL7", "TRL6": "TRL6", "TRL5": "TRL5"}[s]
    ax.text(lx + 1.0, TOP - 4.4, lab, ha="left", va="center", fontsize=6.0, color=SUB, zorder=5)
    lx += 1.0 + len(lab) * 0.47 + 1.8

a = fig.add_axes([(GX0 + 6.4) / 100.0, (BOT + 4.2) / YM,
                  (GX1 - GX0 - 8.6) / 100.0, (TOP - BOT - 10.4) / YM], zorder=6)
a.set_facecolor("none")
p = P()
for s in ORD:
    rows = flows(s, p)
    xs = [0] + [r["n"] for r in rows]
    ys = [0] + [r["cumd"] for r in rows]
    a.plot(xs, ys, color=CL[s], lw=1.5, zorder=4)
a.axhline(0, color="#8A97A6", lw=0.9, zorder=3)
a.set_xlim(0, 40); a.set_ylim(-700, 400)
a.set_xticks([0, 10, 20, 30, 40])
a.tick_params(labelsize=5.6, length=2, width=0.7, colors=SUB, pad=1.5)
a.set_xlabel("год от начала разработки", fontsize=5.8, color=SUB, labelpad=1.5)
a.set_ylabel("млн руб.", fontsize=5.8, color=SUB, labelpad=1.5)
a.grid(axis="y", color="#EDF2F7", lw=0.7)
for sp in ("top", "right"):
    a.spines[sp].set_visible(False)
for sp in ("left", "bottom"):
    a.spines[sp].set_color("#B9C6D6"); a.spines[sp].set_linewidth(0.8)

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s15_res.png", dpi=660, facecolor="white")
print("ok")

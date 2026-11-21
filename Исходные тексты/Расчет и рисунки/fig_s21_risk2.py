# -*- coding: utf-8 -*-
"""Слайд 18. Профиль риска доработок и распределение ЧДД по имитационному расчету."""
import sys, json
sys.path.insert(0, "/home/claude/work/model")
import numpy as np
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
ORD3 = ["TRL7", "TRL6", "TRL5"]
LB = {"BASE": "Базовый", "TRL7": "Интеграция TRL7",
      "TRL6": "Интеграция TRL6", "TRL5": "Интеграция TRL5"}
ru = lambda v, n=1: ("%.{0}f".format(n) % v).replace(".", ",")

R = json.load(open("/home/claude/work/model/results.json"))
MC = json.load(open("/home/claude/work/model/mc_full.json"))
V = {s: np.array(MC[s]) for s in ORD}

LM, GAP = 2.0, 2.2
PW = (100 - 2 * LM - GAP) / 2.0
TOP = YM - 0.9
BY0, BY1 = 1.0, 11.2
PY0 = BY1 + 1.8

TTL = ["Профиль риска доработок",
       "Распределение ЧДД, 5 000 прогонов"]
SUB2 = ["вероятность того, что потери дохода превысят значение по горизонтали",
        "штриховая линия отмечает медиану сценария"]


def card(k):
    x0 = LM + k * (PW + GAP)
    ax.add_patch(FancyBboxPatch((x0, PY0), PW, TOP - PY0,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
    ax.text(x0 + 2.4, TOP - 2.0, TTL[k], ha="left", va="center",
            fontsize=6.8, color=NAVY, fontweight="bold")
    ax.text(x0 + 2.4, TOP - 4.0, SUB2[k], ha="left", va="center",
            fontsize=5.8, color=SUB)
    a = fig.add_axes([(x0 + 7.0) / 100.0, (PY0 + 4.2) / YM,
                      (PW - 9.5) / 100.0, (TOP - PY0 - 10.4) / YM], zorder=6)
    a.set_facecolor("none")
    a.tick_params(labelsize=5.4, length=2, width=0.7, colors=SUB, pad=1.5)
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        a.spines[sp].set_color("#B9C6D6"); a.spines[sp].set_linewidth(0.8)
    return a

# ---------------- панель 1: профиль риска
a = card(0)
for s in ORD3:
    it = R["scn"][s]["out"]["items"]
    d = sorted(((x["loss"], x["prob"]) for x in it), reverse=True)
    xs, ys, acc = [], [], 0.0
    for L, p in d:
        acc += p
        xs.append(L); ys.append(acc * 100)
    a.step(xs, ys, where="post", color=CL[s], lw=1.6, zorder=4)
a.set_yscale("log")
a.set_ylim(0.05, 100); a.set_xlim(0, 100)
a.set_yticks([0.1, 1, 10, 100])
a.set_yticklabels(["0,1", "1", "10", "100"])
a.set_xlabel("потеря дохода, млн руб.", fontsize=5.8, color=SUB, labelpad=1.5)
a.set_ylabel("вероятность превышения, %", fontsize=5.8, color=SUB, labelpad=1.5)
a.grid(color="#EDF2F7", lw=0.7)

# ---------------- панель 2: распределение ЧДД
b = card(1)
edges = np.linspace(-400, 900, 46)
mid = (edges[:-1] + edges[1:]) / 2
for s in ORD:
    h, _ = np.histogram(V[s], bins=edges)
    b.plot(mid, h / h.sum() * 100, color=CL[s], lw=1.5, zorder=4)
    b.axvline(np.median(V[s]), color=CL[s], lw=0.9, ls=(0, (3, 2)), zorder=3)
b.axvline(0, color="#8A97A6", lw=0.9, zorder=3)
b.set_xlim(-400, 900)
b.set_xlabel("ЧДД в прогоне, млн руб.", fontsize=5.8, color=SUB, labelpad=1.5)
b.set_ylabel("доля прогонов, %", fontsize=5.8, color=SUB, labelpad=1.5)
b.grid(axis="y", color="#EDF2F7", lw=0.7)

# ---------------- нижняя полоса
ax.add_patch(FancyBboxPatch((LM, BY0), 100 - 2 * LM, BY1 - BY0,
                            boxstyle="round,pad=0,rounding_size=0.9",
                            fc=FILL, ec="none", zorder=2))
ax.text(LM + 2.4, BY1 - 2.0, "Риск доработок и результат 5 000 прогонов",
        ha="left", va="center", fontsize=6.8, color=NAVY, fontweight="bold")
cx = [LM + 44.0, LM + 55.0, LM + 66.0, LM + 77.0]
for k, s in enumerate(ORD):
    ax.add_patch(Circle((cx[k] - 4.6, BY1 - 2.0), 0.38, fc=CL[s], ec="none", zorder=5))
    ax.text(cx[k] - 3.8, BY1 - 2.0, LB[s].replace("Интеграция ", ""), ha="left",
            va="center", fontsize=6.0, color=SUB, zorder=5)


def pexc(s, thr):
    it = R["scn"][s]["out"]["items"]
    return sum(x["prob"] for x in it if x["loss"] >= thr) * 100


ROWS = [("Вероятность хотя бы одной доработки, %",
         ["—"] + [ru(pexc(s, 0.1)) for s in ORD3]),
        ("Вероятность потерь свыше 30 млн руб., %",
         ["—"] + [ru(pexc(s, 30.0)) for s in ORD3]),
        ("Медиана ЧДД (P50) и доля убыточных прогонов, %",
         ["20,8 · 45,4", "81,2 · 32,5", "154,2 · 19,0", "164,4 · 18,1"])]
y = BY1 - 4.4
for cap, vals in ROWS:
    ax.text(LM + 2.4, y, cap, ha="left", va="center", fontsize=6.0, color=SUB, zorder=4)
    for k, v in enumerate(vals):
        ax.text(cx[k], y, v, ha="center", va="center", fontsize=6.4,
                color=CL[ORD[k]], fontweight="bold", zorder=4)
    y -= 2.6

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s21_risk2.png", dpi=660, facecolor="white")
print("ok")

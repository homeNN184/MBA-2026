# -*- coding: utf-8 -*-
"""Все прогоны всех сценариев на одном рисунке."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = json.load(open("mc_full.json"))
N = len(R["BASE"])
rate = np.array(R["rate"]) * 100
V = {s: np.array(R[s]) for s in ("BASE", "TRL7", "TRL6", "TRL5")}

plt.rcParams.update({"font.family": "Liberation Serif", "font.size": 10})
GY = "#52514e"
CL = {"BASE": "#9aa5b1", "TRL7": "#8a3ffc", "TRL6": "#1baf7a", "TRL5": "#2a78d6"}
LB = {"BASE": "Базовый", "TRL7": "Интеграция TRL7", "TRL6": "Интеграция TRL6",
      "TRL5": "Интеграция TRL5"}
ru = lambda v, n: ("%%.%df" % n % v).replace(".", ",")
ORD = ["BASE", "TRL7", "TRL6", "TRL5"]

fig, axs = plt.subplots(1, 2, figsize=(11.5, 5.0))

# ---------- (а) все четыре облака: ставка дисконтирования и ЧДД
ax = axs[0]
for s in ORD:
    ax.scatter(rate, V[s], s=2.0, c=CL[s], alpha=0.22, linewidths=0, zorder=2)
edges = np.linspace(10, 16, 13)
mid = (edges[:-1] + edges[1:]) / 2
for s in ORD:
    med = [np.median(V[s][(rate >= edges[i]) & (rate < edges[i + 1])]) for i in range(12)]
    ax.plot(mid, med, color=CL[s], lw=2.6, zorder=5)
    ax.plot(mid, med, color="white", lw=4.2, zorder=4)
    ax.plot(mid, med, color=CL[s], lw=2.6, zorder=5,
            label="%s, медиана %s млн руб." % (LB[s], ru(np.median(V[s]), 0)))
ax.axhline(0, color=GY, lw=1.0)
ax.set_xlabel("ставка дисконтирования в прогоне, %", fontsize=10.5)
ax.set_ylabel("ЧДД, млн руб.", fontsize=10.5)
ax.set_xlim(9.8, 16.2)
ax.tick_params(labelsize=9.5); ax.grid(alpha=0.22)
ax.legend(fontsize=8.8, frameon=False, loc="upper right")
ax.set_title("а — все 20 000 точек, по 5 000 на сценарий.\nЛинии показывают медиану сценария",
             fontsize=10.5)

# ---------- (б) попарное сравнение с базовым сценарием
ax = axs[1]
lo = min(V[s].min() for s in ORD) - 20
hi = max(V[s].max() for s in ORD) + 20
ax.fill_between([lo, hi], [lo, hi], [hi, hi], color="#f1f5fa", zorder=0)
for s in ("TRL7", "TRL6", "TRL5"):
    sh = (V[s] > V["BASE"]).sum() / N * 100
    ax.scatter(V["BASE"], V[s], s=2.0, c=CL[s], alpha=0.16, linewidths=0, zorder=2,
               label="%s, выше линии %s %%" % (LB[s], ru(sh, 2)))
ax.plot([lo, hi], [lo, hi], color=GY, lw=1.2, zorder=4)
ax.axhline(0, color=GY, lw=0.6, ls=":"); ax.axvline(0, color=GY, lw=0.6, ls=":")
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xlabel("ЧДД базового сценария в том же прогоне, млн руб.", fontsize=10.5)
ax.set_ylabel("ЧДД сценария интеграции, млн руб.", fontsize=10.5)
ax.tick_params(labelsize=9.5); ax.grid(alpha=0.22)
lg = ax.legend(fontsize=8.8, frameon=False, loc="upper left", markerscale=6)
for h in lg.legend_handles:
    h.set_alpha(1.0)
ax.text(0.97, 0.05, "серая линия — равенство сценариев", transform=ax.transAxes,
        fontsize=9, ha="right", color=GY)
ax.set_title("б — те же прогоны попарно к базовому сценарию.\nТочка выше линии означает выигрыш интеграции",
             fontsize=10.5)

fig.tight_layout(pad=0.8)
fig.savefig("../fig/f_mc_all.png", dpi=450, bbox_inches="tight", facecolor="white")
plt.close(fig)
for s in ORD:
    print(LB[s], "медиана", ru(float(np.median(V[s])), 1),
          "| выше базового, %", ru(float((V[s] > V["BASE"]).sum() / N * 100), 2))

# -*- coding: utf-8 -*-
"""Облако прогонов для презентации: все точки всех сценариев."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = json.load(open("mc_full.json"))
N = len(R["BASE"])
rate = np.array(R["rate"]) * 100
V = {s: np.array(R[s]) for s in ("BASE", "TRL7", "TRL6", "TRL5")}
CL = {"BASE": "#2F6FC0", "TRL7": "#C4690E", "TRL6": "#8E44AD", "TRL5": "#1B9E77"}
LB = {"BASE": "Традиционная схема", "TRL7": "Интеграция TRL7",
      "TRL6": "Интеграция TRL6", "TRL5": "Интеграция TRL5"}
ORD = ["BASE", "TRL7", "TRL6", "TRL5"]
ru = lambda v, n: ("%%.%df" % n % v).replace(".", ",")
plt.rcParams["font.family"] = "DejaVu Sans"

fig, ax = plt.subplots(figsize=(7.6, 4.3), dpi=510)
for s in ORD:
    ax.scatter(rate, V[s], s=1.6, c=CL[s], alpha=0.16, linewidths=0, zorder=2)
edges = np.linspace(10, 16, 13); mid = (edges[:-1] + edges[1:]) / 2
for s in ORD:
    med = [np.median(V[s][(rate >= edges[i]) & (rate < edges[i + 1])]) for i in range(12)]
    ax.plot(mid, med, color="white", lw=5.0, zorder=4, solid_capstyle="round")
    ax.plot(mid, med, color=CL[s], lw=2.8, zorder=5, solid_capstyle="round",
            label="%s, медиана %s" % (LB[s], ru(np.median(V[s]), 0)))
ax.axhline(0, color="#52514e", lw=1.2, zorder=3)
ax.text(15.95, 14, "нулевой доход", fontsize=8.5, color="#52514e", ha="right", va="bottom")
ax.set_xlim(9.9, 16.1); ax.set_ylim(-420, 1050)
ax.set_xticks(range(10, 17))
ax.set_xticklabels(["%d %%" % v for v in range(10, 17)], fontsize=10)
ax.tick_params(labelsize=10)
ax.set_xlabel("ставка дисконтирования в прогоне", fontsize=11)
ax.set_ylabel("ЧДД, млн руб.", fontsize=11)
ax.grid(axis="y", color="#e8e6e0", lw=1)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"):
    ax.spines[sp].set_color("#b9b6ae")
lg = ax.legend(fontsize=9.5, frameon=False, loc="upper right", handlelength=1.6)
fig.tight_layout(pad=0.3)
fig.savefig("../fig/pres_mc.png", bbox_inches="tight", facecolor="white")
print("ok")

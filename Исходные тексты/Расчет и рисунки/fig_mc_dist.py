# -*- coding: utf-8 -*-
"""Рисунок: распределение ЧДД по сценариям при имитационном моделировании."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.family": "Liberation Serif", "font.size": 8})
CL = {"BASE": "#3C4F66", "TRL7": "#C4690E", "TRL6": "#0079C2", "TRL5": "#1B9E77"}
LB = {"BASE": "Базовый", "TRL7": "Интеграция TRL7",
      "TRL6": "Интеграция TRL6", "TRL5": "Интеграция TRL5"}
ORD = ["BASE", "TRL7", "TRL6", "TRL5"]
R = json.load(open("/home/claude/work/model/mc_full.json"))
V = {s: np.array(R[s]) for s in ORD}

fig, ax = plt.subplots(figsize=(6.5, 2.9), dpi=300)
edges = np.linspace(-400, 900, 40)
mid = (edges[:-1] + edges[1:]) / 2
for s in ORD:
    h, _ = np.histogram(V[s], bins=edges)
    ax.plot(mid, h / h.sum() * 100, color=CL[s], lw=1.3, label=LB[s], zorder=4)
    ax.axvline(np.median(V[s]), color=CL[s], lw=0.9, ls=(0, (3, 2)), zorder=3)
ax.axvline(0, color="#8A97A6", lw=0.9, zorder=2)
ax.set_xlim(-400, 900)
ax.set_xlabel("ЧДД в прогоне, млн руб.")
ax.set_ylabel("доля прогонов, %")
ax.grid(axis="y", color="#EDF2F7", lw=0.7)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"):
    ax.spines[sp].set_color("#B9C6D6")
ax.legend(frameon=False, fontsize=7, loc="upper right")
ax.text(0.01, 0.98, "штриховые линии — медианы (P50)", transform=ax.transAxes,
        fontsize=6.8, color="#3C4F66", va="top")
fig.tight_layout(pad=0.3)
fig.savefig("/home/claude/work/fig/f40_mcdist.png", dpi=300, bbox_inches="tight", facecolor="white")
print("ok", {s: round(float(np.median(V[s])), 1) for s in ORD})

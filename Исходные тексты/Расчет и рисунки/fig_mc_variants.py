# -*- coding: utf-8 -*-
"""Варианты визуализации результатов имитационного моделирования."""
import json, os, random, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from dataclasses import replace
from model import P, flows, npv, schedule, event_scope, ev_params, SCENARIOS

CACHE = "mc_full.json"
p0 = P()


def build():
    rnd = random.Random(20261107)
    out = {s: [] for s in SCENARIOS}
    out["rate"] = []; out["rev"] = []
    for _ in range(5000):
        ln = lambda s: math.exp(rnd.gauss(-s * s / 2, s))
        d = dict(td=ln(0.15), ti=ln(0.15), pe=ln(0.5), ce=ln(0.4),
                 rate=rnd.uniform(0.10, 0.16), rev=max(0.3, rnd.gauss(1, 0.15)),
                 u=[rnd.random() for _ in range(5)])
        pp = replace(p0, t_dev=p0.t_dev * d["td"], t_inv=p0.t_inv * d["ti"],
                     rate=d["rate"], revenue=p0.revenue * d["rev"])
        for s in SCENARIOS:
            if s == "BASE":
                out[s].append(npv(flows(s, pp))); continue
            sch = schedule(s, pp); delay = 0.0; extra = []
            for i, k in enumerate(range(5, 10)):
                aff, t, _ = event_scope(s, sch, k, pp)
                if not aff:
                    continue
                pr, c, dd = ev_params(pp, s, k, sch)
                if d["u"][i] < min(1.0, pr * d["pe"]):
                    delay += dd * d["ce"]; extra.append((t, c * d["ce"]))
            out[s].append(npv(flows(s, pp, delay_days=delay, extra=extra, sch=sch)))
        out["rate"].append(d["rate"]); out["rev"].append(d["rev"])
    json.dump(out, open(CACHE, "w"))
    return out


R = json.load(open(CACHE)) if os.path.exists(CACHE) else build()
N = len(R["BASE"])
base = np.array(R["BASE"]); t5 = np.array(R["TRL5"]); t6 = np.array(R["TRL6"]); t7 = np.array(R["TRL7"])
rate = np.array(R["rate"]) * 100; rev = np.array(R["rev"])
adv = t5 - base

plt.rcParams.update({"font.family": "Liberation Serif", "font.size": 10})
GY = "#52514e"
CL = {"BASE": "#9aa5b1", "TRL7": "#8a3ffc", "TRL6": "#1baf7a", "TRL5": "#2a78d6"}
LB = {"BASE": "Базовый", "TRL7": "Интеграция TRL7", "TRL6": "Интеграция TRL6", "TRL5": "Интеграция TRL5"}
ru = lambda v, n: ("%%.%df" % n % v).replace(".", ",")

fig = plt.figure(figsize=(11.5, 9.0))

# ---- A. трехмерное облако прогонов
ax = fig.add_subplot(2, 2, 1, projection="3d")
sc = ax.scatter(rate, rev, adv, c=adv, cmap="viridis", s=3.2, alpha=0.5, linewidths=0)
ax.set_xlabel("ставка дисконтирования, %", fontsize=9, labelpad=2)
ax.set_ylabel("множитель выручки", fontsize=9, labelpad=2)
ax.set_zlabel("преимущество ЧДД, млн руб.", fontsize=9, labelpad=2)
ax.tick_params(labelsize=8); ax.view_init(elev=20, azim=-58)
cb = fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.10); cb.ax.tick_params(labelsize=8)
ax.set_title("А. Трехмерное облако прогонов\n(преимущество «Интеграции TRL5» над базовым)",
             fontsize=10.5, pad=2)

# ---- B. поверхность преимущества
ax = fig.add_subplot(2, 2, 2, projection="3d")
rr = np.linspace(0.10, 0.16, 13); ss = np.linspace(0.10, 0.50, 13)
Z = np.zeros((len(ss), len(rr)))
for i, sh in enumerate(ss):
    for j, rt in enumerate(rr):
        q = P(rate=float(rt), share_inn=float(sh))
        Z[i, j] = npv(flows("TRL5", q)) - npv(flows("BASE", q))
X, Y = np.meshgrid(rr * 100, ss * 100)
su = ax.plot_surface(X, Y, Z, cmap=cm.viridis, linewidth=0.2, edgecolor="white", antialiased=True)
ax.contour(X, Y, Z, zdir="z", offset=float(Z.min()), levels=8, colors="#9aa5b1", linewidths=0.6)
ax.set_xlabel("ставка дисконтирования, %", fontsize=9, labelpad=2)
ax.set_ylabel("доля инноваций в бюджете, %", fontsize=9, labelpad=2)
ax.set_zlabel("преимущество ЧДД, млн руб.", fontsize=9, labelpad=2)
ax.tick_params(labelsize=8); ax.view_init(elev=22, azim=-130)
cb = fig.colorbar(su, ax=ax, shrink=0.6, pad=0.10); cb.ax.tick_params(labelsize=8)
ax.set_title("Б. Поверхность преимущества\n(расчет на сетке, без случайных отклонений)",
             fontsize=10.5, pad=2)

# ---- C. кумулятивные кривые
ax = fig.add_subplot(2, 2, 3)
for s, a in (("BASE", base), ("TRL7", t7), ("TRL6", t6), ("TRL5", t5)):
    xs = np.sort(a); ys = np.arange(1, N + 1) / N * 100
    ax.plot(xs, ys, color=CL[s], lw=1.8, label=LB[s])
    ax.plot([np.interp(50, ys, xs)], [50], marker="o", ms=5, color="white", mec=CL[s], mew=1.5, zorder=5)
ax.axvline(0, color=GY, lw=1.0)
ax.axhline(50, color=GY, lw=0.6, ls=":")
ax.text(0, 103, "ноль", fontsize=8.5, color=GY, ha="center")
ax.set_xlabel("ЧДД, млн руб.", fontsize=10)
ax.set_ylabel("доля прогонов не выше указанного ЧДД, %", fontsize=10)
ax.set_ylim(0, 108); ax.grid(alpha=0.25); ax.tick_params(labelsize=9)
ax.legend(fontsize=8.5, frameon=False, loc="lower right")
ax.set_title("В. Кумулятивные кривые распределения\n(кривая правее — сценарий лучше при любом пороге)",
             fontsize=10.5)

# ---- D. плотность облака
ax = fig.add_subplot(2, 2, 4)
hb = ax.hexbin(base, t5, gridsize=42, cmap="Blues", mincnt=1, linewidths=0)
lo = min(base.min(), t5.min()) - 20; hi = max(base.max(), t5.max()) + 20
ax.plot([lo, hi], [lo, hi], color=GY, lw=1.1)
ax.axhline(0, color=GY, lw=0.6, ls=":"); ax.axvline(0, color=GY, lw=0.6, ls=":")
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xlabel("ЧДД базового сценария, млн руб.", fontsize=10)
ax.set_ylabel("ЧДД «Интеграции TRL5», млн руб.", fontsize=10)
ax.tick_params(labelsize=9); ax.grid(alpha=0.2)
cb = fig.colorbar(hb, ax=ax, shrink=0.8, pad=0.02); cb.ax.tick_params(labelsize=8)
cb.set_label("прогонов в ячейке", fontsize=9)
ax.set_title("Г. Плотность облака вместо точек\n(читается при печати и при наложении точек)",
             fontsize=10.5)

fig.tight_layout(pad=0.8)
fig.savefig("../fig/f_mc_variants.png", dpi=450, bbox_inches="tight", facecolor="white")
plt.close(fig)
print("готово, преимущество на сетке от", round(float(Z.min()), 1), "до", round(float(Z.max()), 1))

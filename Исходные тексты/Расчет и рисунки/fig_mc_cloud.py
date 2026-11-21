# -*- coding: utf-8 -*-
"""Облако прогонов имитационного моделирования (тот же расчет, что в приложении 13)."""
import random, math, time, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dataclasses import replace
from model import P, flows, npv, schedule, event_scope, ev_params, SCENARIOS

p = P(); rnd = random.Random(20261107)


def draw():
    ln = lambda s: math.exp(rnd.gauss(-s * s / 2, s))
    return dict(td=ln(0.15), ti=ln(0.15), pe=ln(0.5), ce=ln(0.4),
                rate=rnd.uniform(0.10, 0.16), rev=max(0.3, rnd.gauss(1, 0.15)),
                u=[rnd.random() for _ in range(5)])


def run(s, d):
    pp = replace(p, t_dev=p.t_dev * d["td"], t_inv=p.t_inv * d["ti"],
                 rate=d["rate"], revenue=p.revenue * d["rev"])
    if s == "BASE":
        return npv(flows(s, pp))
    sch = schedule(s, pp); delay = 0.0; extra = []
    for i, k in enumerate(range(5, 10)):
        aff, t, _ = event_scope(s, sch, k, pp)
        if not aff:
            continue
        pr, c, dd = ev_params(pp, s, k, sch)
        if d["u"][i] < min(1.0, pr * d["pe"]):
            delay += dd * d["ce"]; extra.append((t, c * d["ce"]))
    return npv(flows(s, pp, delay_days=delay, extra=extra, sch=sch))


import os
if os.path.exists("mc_series.json"):
    res = json.load(open("mc_series.json")); N = len(res["BASE"])
    print("серии прочитаны из файла, прогонов", N)
else:
    t0 = time.time(); N = 5000
    res = {s: [] for s in SCENARIOS}
    for _ in range(N):
        d = draw()
        for s in SCENARIOS:
            res[s].append(run(s, d))
    print("прогоны, с:", round(time.time() - t0, 1))
    json.dump(res, open("mc_series.json", "w"))

plt.rcParams.update({"font.family": "Liberation Serif", "font.size": 8})
GY = "#52514e"
CL = {"BASE": "#9aa5b1", "TRL7": "#8a3ffc", "TRL6": "#1baf7a", "TRL5": "#2a78d6"}
LB = {"BASE": "Базовый", "TRL7": "Интеграция TRL7", "TRL6": "Интеграция TRL6", "TRL5": "Интеграция TRL5"}
q = lambda a, x: sorted(a)[int(x * (len(a) - 1))]
ru = lambda v, n: ("%%.%df" % n % v).replace(".", ",")

fig, axs = plt.subplots(1, 2, figsize=(6.5, 3.25))

# ---- (а) облако: Базовый против Интеграции TRL5
ax = axs[0]
x, y = res["BASE"], res["TRL5"]
lo = min(min(x), min(y)) - 20; hi = max(max(x), max(y)) + 20
ax.fill_between([lo, hi], [lo, hi], [hi, hi], color="#eaf1fb", zorder=0)
ax.scatter(x, y, s=2.2, c=CL["TRL5"], alpha=0.22, linewidths=0, zorder=2)
ax.plot([lo, hi], [lo, hi], color=GY, lw=1.0, zorder=3)
ax.axhline(0, color=GY, lw=0.6, ls=":", zorder=1)
ax.axvline(0, color=GY, lw=0.6, ls=":", zorder=1)
sh = sum(1 for i in range(N) if y[i] > x[i]) / N
ax.text(0.04, 0.95, "интеграция выгоднее\nв %s %% прогонов" % ru(sh * 100, 2),
        transform=ax.transAxes, fontsize=7, va="top", color=CL["TRL5"], fontweight="bold")
ax.text(0.04, 0.03, "каждая точка — один прогон", transform=ax.transAxes,
        fontsize=6.6, color=GY)
ax.text(0.97, 0.06, "линия равенства", transform=ax.transAxes, fontsize=6.6,
        ha="right", color=GY)
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xlabel("ЧДД базового сценария, млн руб.", fontsize=7)
ax.set_ylabel("ЧДД сценария «Интеграция TRL5», млн руб.", fontsize=7)
ax.tick_params(labelsize=6.8); ax.grid(alpha=0.2)
ax.set_title("а", fontsize=7.5, loc="left")

# ---- (б) распределение ЧДД по сценариям
ax = axs[1]
bins = 46
allv = [v for s in SCENARIOS for v in res[s]]
rng = (min(allv), max(allv))
for s in ("BASE", "TRL7", "TRL6", "TRL5"):
    ax.hist(res[s], bins=bins, range=rng, histtype="step", lw=1.3,
            color=CL[s], label="%s, убыточных %s %%" % (LB[s], ru(sum(1 for v in res[s] if v < 0) / N * 100, 1)))
ax.axvline(0, color=GY, lw=0.9)
ax.set_xlabel("ЧДД, млн руб.", fontsize=7)
ax.set_ylabel("число прогонов", fontsize=7)
ax.tick_params(labelsize=6.8); ax.grid(alpha=0.2, axis="y")
ax.legend(fontsize=6.0, frameon=False, loc="upper right")
ax.set_title("б", fontsize=7.5, loc="left")

fig.tight_layout(pad=0.4)
fig.savefig("../fig/f_mc_cloud.png", dpi=660, bbox_inches="tight", facecolor="white")
plt.close(fig)
for s in SCENARIOS:
    print(LB[s], "P10", round(q(res[s], .1), 1), "P50", round(q(res[s], .5), 1),
          "P90", round(q(res[s], .9), 1), "убыточных %", round(sum(1 for v in res[s] if v < 0) / N * 100, 1))
print("TRL5 > Базовый, %", round(sum(1 for i in range(N) if res["TRL5"][i] > res["BASE"][i]) / N * 100, 2))
print("TRL5 > TRL6, %", round(sum(1 for i in range(N) if res["TRL5"][i] > res["TRL6"][i]) / N * 100, 2))
print("готово")

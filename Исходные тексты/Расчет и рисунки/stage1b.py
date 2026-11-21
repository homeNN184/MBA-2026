# -*- coding: utf-8 -*-
import json, random
from dataclasses import replace
from model import *
from stage1 import solve, case, stats, OUT, p, b
# --- порог в терминах ожидаемого ущерба от доработки ПД/РД
n0_5 = npv(flows("TRL5", p))
q0 = replace(p, ev6_p_abs=0.0)
El5_other = outcomes("TRL5", q0)["E_loss"]
q1 = replace(p, ev6_p_abs=1.0, ev6_cost_abs=None)
# потеря NPV от одного события TRL6 (без других событий)
def single_loss(pp):
    sch = schedule("TRL5", pp); pr, c, d = ev_params(pp, "TRL5", 6, sch)
    rows = flows("TRL5", pp, delay_days=d, extra=[(sch["conf"][4], c)], sch=sch)
    return n0_5 - npv(rows), c, d
L6, c6, d6 = single_loss(p)
El6 = OUT["res"]["TRL6"]["E_loss"]; dN = OUT["thr56_rule"]["dNPV0"]
X = dN + El6 - El5_other
print("L6", round(L6,2), "cost", round(c6,2), "delay", round(d6), "E_loss5_other", round(El5_other,2), "X", round(X,2), "p6*L6 now", round(0.12*L6,2), "p6 break-even at L6:", round(X/L6,3))
# Проверка точности гиперболы
for pr in (0.1, 0.12, 0.2):
    f = lambda c: outcomes("TRL5", replace(p, ev6_p_abs=pr, ev6_cost_abs=c))["E_npv"] - outcomes("TRL6", p)["E_npv"]
    cc = solve(f, 0, 3000); pp_ = replace(p, ev6_p_abs=pr, ev6_cost_abs=cc); Ls, _, _ = single_loss(pp_)
    print(pr, round(cc,1), "L", round(Ls,1), "p*L", round(pr*Ls,2))
OUT["thr56_X"] = dict(X=X, L6=L6, c6=c6, d6=d6, El5_other=El5_other)
# --- многокритериальная оценка (К-3)
CRIT = ["ЧДД", "Срок ввода", "Остаток в наихудшем исходе", "Доказательность TRL", "Ресурсная нагрузка", "Устойчивость (m*)"]
W = [0.30, 0.15, 0.15, 0.15, 0.10, 0.15]
QUAL = {"Базовый": (3, 5), "TRL7": (5, 2), "TRL6": (4, 3), "TRL5": (3, 3)}
lab = {"BASE": "Базовый", "TRL7": "TRL7", "TRL6": "TRL6", "TRL5": "TRL5"}
def mm(v, lo, hi, inv=False):
    x = (v - lo) / (hi - lo) if hi > lo else 0.0
    return 1 - x if inv else x
res = OUT["res"]
rows = []
for s in SCENARIOS:
    sch = schedule(s, p)
    rows.append(dict(s=s, label=lab[s], npv=res[s]["npv0"], tv=sch["tv"], worst=res[s].get("worst", 0.0) if s != "BASE" else 0.0,
                     m=(res[s].get("mstar") or 0.0) if s != "BASE" else 0.0))
# для Базового сценария: остаток 0, m* неприменим -> максимальная устойчивость? (нет доработок): принять m*=максимум среди сценариев
mmax = max(r["m"] for r in rows)
rows[0]["m"] = mmax
npvs = [r["npv"] for r in rows]; tvs = [r["tv"] for r in rows]; ws = [r["worst"] for r in rows]; ms = [r["m"] for r in rows]
for r in rows:
    qe, qr = QUAL[r["label"]]
    r["score"] = [mm(r["npv"], min(npvs), max(npvs))*100, mm(r["tv"], min(tvs), max(tvs), True)*100, mm(r["worst"], min(ws), max(ws))*100,
                  (qe-1)/4*100, (qr-1)/4*100, mm(r["m"], min(ms), max(ms))*100]
    r["total"] = sum(a*b_ for a, b_ in zip(r["score"], W))
print([ (r["label"], [round(x,1) for x in r["score"]], round(r["total"],2)) for r in rows])
rnd = random.Random(20261107); wins = {r["label"]: 0 for r in rows}; N = 20000; samples = []
for _ in range(N):
    x = [rnd.expovariate(1) for _ in range(6)]; sm = sum(x); w = [v/sm for v in x]
    t = [sum(a*b_ for a, b_ in zip(r["score"], w)) for r in rows]; i = t.index(max(t)); wins[rows[i]["label"]] += 1
print({k: v/N for k, v in wins.items()})
OUT["mcw"] = {k: v/N for k, v in wins.items()}
# область весов, где выигрывает TRL6: вес устойчивости/остатка
for wt in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
    # распределяем остаток пропорционально базовым весам; устойчивость+остаток получают wt/2 каждый
    base = [0.30, 0.15, 0.15, 0.15, 0.10, 0.15]
    w = base[:]; w[2] = wt/2; w[5] = wt/2
    rest = 1 - wt; others = [base[0], base[1], base[3], base[4]]; so = sum(others)
    for k_, v in zip((0, 1, 3, 4), others): w[k_] = v/so*rest
    t = [sum(a*b_ for a, b_ in zip(r["score"], w)) for r in rows]
    print("w_robust", wt, rows[t.index(max(t))]["label"], [round(x,1) for x in t])
OUT["mc_rows"] = rows
json.dump(OUT, open("stage1.json", "w"), ensure_ascii=False, indent=1, default=float)

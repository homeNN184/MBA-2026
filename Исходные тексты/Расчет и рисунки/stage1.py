# -*- coding: utf-8 -*-
import json, random, math
from dataclasses import replace
from model import *
p = P(); b = npv(flows("BASE", p)); OUT = {}
def stats(pp, s):
    o = outcomes(s, pp); n0 = npv(flows(s, pp)); bb = npv(flows("BASE", pp))
    return dict(npv0=n0, R=n0 - bb, E_loss=o["E_loss"], E_npv=o["E_npv"], E_rem=o["E_npv"] - bb)
def case(pp): return replace(pp, mfix=True, p_ev=(pp.p_ev[0], 1, 1, 1, 1))
def solve(f, lo, hi, it=80):
    flo = f(lo); fhi = f(hi)
    if flo * fhi > 0: return None
    for _ in range(it):
        mid = (lo + hi) / 2; fm = f(mid)
        if flo * fm <= 0: hi = mid
        else: lo = mid; flo = fm
    return (lo + hi) / 2
# 1. параметры событий и результаты
OUT["events"] = {s: {k: ev_params(p, s, k) for k in range(5, 10)} for s in INTEG}
OUT["res"] = {}
for s in SCENARIOS:
    if s == "BASE": OUT["res"][s] = dict(npv0=b, R=0, E_loss=0, E_rem=0, worst=0); continue
    d = stats(p, s); oc = outcomes(s, case(p)); d["worst"] = min(i["npv"] for i in oc["items"]) - b
    # критический множитель m* затрат и задержек в расчётном случае
    def w(m): 
        pp = case(replace(p, ev_cost=tuple(c*m for c in p.ev_cost), ev_delay_d=tuple(x*m for x in p.ev_delay_d)))
        return min(i["npv"] for i in outcomes(s, pp)["items"]) - b
    d["mstar"] = solve(w, 1.0, 400.0)
    OUT["res"][s] = d
# 2. пороги TRL5/TRL6: ожидаемые потери
dN = OUT["res"]["TRL5"]["npv0"] - OUT["res"]["TRL6"]["npv0"]
OUT["thr56_rule"] = dict(dNPV0=dN, E_loss5=OUT["res"]["TRL5"]["E_loss"], E_loss6=OUT["res"]["TRL6"]["E_loss"])
# область предпочтения: (прямой ущерб TRL6-события, вероятность) при задержке d (сут.)
grid_p = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.70, 1.00]
OUT["thr56"] = {}
for dly in (104, 150, 200):
    row = []
    for pr in grid_p:
        def f(c):
            q = replace(p, ev6_cost_abs=c, ev6_delay_abs=dly, ev6_p_abs=pr)
            return outcomes("TRL5", q)["E_npv"] - outcomes("TRL6", p)["E_npv"]
        row.append((pr, solve(f, 0, 5000)))
    OUT["thr56"][dly] = row
# порог по задержке при фикс. стоимости 11,8 и разных вероятностях
OUT["thr56_delay"] = []
for pr in grid_p:
    def f(d):
        q = replace(p, ev6_delay_abs=d, ev6_p_abs=pr)
        return outcomes("TRL5", q)["E_npv"] - outcomes("TRL6", p)["E_npv"]
    OUT["thr56_delay"].append((pr, solve(f, 0, 3000)))
# порог TRL6/TRL7: стоимость опытной инфраструктуры (доля B_INN) и допстатьи
E6 = outcomes("TRL6", p)["E_npv"]
def f7(ps): return outcomes("TRL7", replace(p, pilot_share=ps))["E_npv"] - E6
OUT["thr67_pilot_share"] = solve(f7, -0.5, 0.5)
OUT["thr67_pilot_mln"] = OUT["thr67_pilot_share"] * p.b_inn if OUT["thr67_pilot_share"] is not None else None
def f7b(x): return outcomes("TRL7", replace(p, pilot_share=0.0, t7_store=p.t7_store*x, t7_remount=p.t7_remount*x, t7_warr_p=p.t7_warr_p*x))["E_npv"] - E6
OUT["thr67_extras_x0"] = solve(f7b, -5, 1.0)
OUT["E7_nopilot_noextras"] = outcomes("TRL7", replace(p, pilot_share=0.0, t7_store=0, t7_remount=0, t7_warr_p=0))["E_npv"]
# порог по вероятностям событий TRL6: во сколько раз надо умножить p и ущерб TRL6, чтобы TRL7 сравнялся
def f67(x):
    pp = replace(p, p_ev=tuple(v*x for v in p.p_ev), ev_cost=tuple(v*x for v in p.ev_cost), ev_delay_d=tuple(v*x for v in p.ev_delay_d), mfix=False)
    return outcomes("TRL7", pp)["E_npv"] - outcomes("TRL6", pp)["E_npv"]
OUT["thr67_scale"] = solve(f67, 1.0, 60.0)
# чувствительность опытной инфраструктуры 35-150
OUT["pilot_sens"] = []
for pm_ in (35, 50, 75, 100, 125, 150):
    q = replace(p, pilot_share=pm_ / p.b_inn); r = {s: npv(flows(s, q)) for s in SCENARIOS}
    OUT["pilot_sens"].append(dict(pilot=pm_, npv=r, R={s: r[s]-r["BASE"] for s in INTEG}))
json.dump(OUT, open("stage1.json", "w"), ensure_ascii=False, indent=1, default=float)
for k in ("events","res","thr56_rule","thr56","thr56_delay","thr67_pilot_mln","thr67_extras_x0","E7_nopilot_noextras","thr67_scale"):
    print(k, json.dumps(OUT[k], ensure_ascii=False, default=lambda x: round(x,3) if isinstance(x,float) else x)[:900])
for r in OUT["pilot_sens"]: print(r["pilot"], {k: round(v,1) for k,v in r["R"].items()})

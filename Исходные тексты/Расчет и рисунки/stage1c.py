# -*- coding: utf-8 -*-
import json, random, math, time
from dataclasses import replace
from model import *
OUT = json.load(open("stage1.json"))
p = P(); rnd = random.Random(20261107)
def draw():
    ln = lambda s: math.exp(rnd.gauss(-s*s/2, s))
    return dict(td=ln(0.15), ti=ln(0.15), pe=ln(0.5), ce=ln(0.4), rate=rnd.uniform(0.10, 0.16), rev=max(0.3, rnd.gauss(1, 0.15)), u=[rnd.random() for _ in range(5)])
def run(s, d):
    pp = replace(p, t_dev=p.t_dev*d["td"], t_inv=p.t_inv*d["ti"], rate=d["rate"], revenue=p.revenue*d["rev"])
    if s == "BASE": return npv(flows(s, pp))
    sch = schedule(s, pp); delay = 0.0; extra = []
    for i, k in enumerate(range(5, 10)):
        aff, t, _ = event_scope(s, sch, k, pp)
        if not aff: continue
        pr, c, dd = ev_params(pp, s, k, sch)
        if d["u"][i] < min(1.0, pr*d["pe"]): delay += dd*d["ce"]; extra.append((t, c*d["ce"]))
    return npv(flows(s, pp, delay_days=delay, extra=extra, sch=sch))
t0 = time.time(); N = 5000; res = {s: [] for s in SCENARIOS}
for _ in range(N):
    d = draw()
    for s in SCENARIOS: res[s].append(run(s, d))
print("time", round(time.time()-t0,1))
def q(a, x): a = sorted(a); return a[int(x*(len(a)-1))]
mc = {}
for s in SCENARIOS:
    a = res[s]; mc[s] = dict(p10=q(a,.1), p50=q(a,.5), p90=q(a,.9), mean=sum(a)/N, neg=sum(1 for v in a if v<0)/N,
                            adv_p10=q([x-y for x,y in zip(a,res["BASE"])],.1), adv_p50=q([x-y for x,y in zip(a,res["BASE"])],.5), adv_p90=q([x-y for x,y in zip(a,res["BASE"])],.9),
                            beat_base=sum(1 for x,y in zip(a,res["BASE"]) if x>y)/N)
best = {s: 0 for s in SCENARIOS}; best_int = {s: 0 for s in INTEG}
for i in range(N):
    v = {s: res[s][i] for s in SCENARIOS}; best[max(v, key=v.get)] += 1
    vi = {s: v[s] for s in INTEG}; best_int[max(vi, key=vi.get)] += 1
for s in SCENARIOS: mc[s]["best"] = best[s]/N
mc["best_int"] = {s: best_int[s]/N for s in INTEG}
# разность TRL5-TRL6
dif = [res["TRL5"][i]-res["TRL6"][i] for i in range(N)]
mc["d56"] = dict(p10=q(dif,.1), p50=q(dif,.5), p90=q(dif,.9), pos=sum(1 for x in dif if x>0)/N)
# loss tail P90 потерь от переделок (по MC, относительно NPV без событий) — для критерия устойчивости
print(json.dumps(mc, ensure_ascii=False, default=lambda x: round(x,3)))
# торнадо: влияние на преимущество TRL5 над TRL6 и на R каждого сценария, шаги 10-90% диапазона
def spec(key, lo, hi):
    out = {}
    for tag, v in (("lo", lo), ("hi", hi)):
        d = dict(td=1, ti=1, pe=1, ce=1, rate=0.12, rev=1.0, u=[0.0]*5)   # события наступают?? u=0 -> все события наступают с p>0
        d[key] = v
        out[tag] = d
    return out
# для торнадо ожидаемые значения: считаем E[NPV] через outcomes с параметрами
def enpv(s, **kw):
    q_ = p
    if "td" in kw: q_ = replace(q_, t_dev=p.t_dev*kw["td"])
    if "ti" in kw: q_ = replace(q_, t_inv=p.t_inv*kw["ti"])
    if "rate" in kw: q_ = replace(q_, rate=kw["rate"])
    if "rev" in kw: q_ = replace(q_, revenue=p.revenue*kw["rev"])
    if "pe" in kw: q_ = replace(q_, p_ev=tuple(min(1, v*kw["pe"]) for v in p.p_ev))
    if "ce" in kw: q_ = replace(q_, ev_cost=tuple(v*kw["ce"] for v in p.ev_cost), ev_delay_d=tuple(v*kw["ce"] for v in p.ev_delay_d))
    if "pilot" in kw: q_ = replace(q_, pilot_share=kw["pilot"])
    return outcomes(s, q_)["E_npv"] if s != "BASE" else npv(flows(s, q_))
T = []
for name, key, lo, hi in (("Ставка дисконтирования 10–16 %", "rate", 0.10, 0.16), ("Выручка ±20 %", "rev", 0.8, 1.2), ("Срок разработки ±25 %", "td", 0.75, 1.25),
                          ("Срок строительства ±15 %", "ti", 0.85, 1.15), ("Вероятности событий ×0,5…×2", "pe", 0.5, 2.0), ("Затраты и задержки событий ×0,5…×2", "ce", 0.5, 2.0), ("Опытная инфраструктура 35–150 млн", "pilot", 0.10, 150/350)):
    row = dict(name=name)
    for tag, v in (("lo", lo), ("hi", hi)):
        e = {s: enpv(s, **{key: v}) for s in SCENARIOS}
        row[tag] = dict(R5=e["TRL5"]-e["BASE"], R6=e["TRL6"]-e["BASE"], R7=e["TRL7"]-e["BASE"], d56=e["TRL5"]-e["TRL6"])
    T.append(row)
mc["tornado"] = T
for r in T: print(r["name"], {k: [round(r[t][k],1) for t in ("lo","hi")] for k in ("R5","R6","d56")})
OUT["mc"] = mc
json.dump(OUT, open("stage1.json", "w"), ensure_ascii=False, indent=1, default=float)

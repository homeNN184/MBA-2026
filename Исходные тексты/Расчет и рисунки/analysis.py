# -*- coding: utf-8 -*-
import json
from dataclasses import replace
from model import *

p = P()
R = {"params": {k: (list(v) if isinstance(v, tuple) else v) for k, v in p.__dict__.items()}}
R["derived"] = dict(b_inn=p.b_inn, b_inv=p.b_inv, opex=p.opex, to=p.to, tr=p.tr, kr=p.kr, pilot=p.pilot)
base_npv = npv(flows("BASE", p))
R["scn"] = {}
for s in SCENARIOS:
    sch = schedule(s, p)
    rows = flows(s, p)
    ind = indicators(rows, p.rate)
    R["scn"][s] = dict(sch=sch, rows=rows, ind=ind, npv0=npv(rows))
R["base_npv"] = base_npv
for s in INTEG:
    R["scn"][s]["R"] = R["scn"][s]["npv0"] - base_npv
    R["scn"][s]["R_rel"] = R["scn"][s]["R"] / p.b_inn * 100
    o = outcomes(s, p)
    for it in o["items"]:
        it["rem"] = it["npv"] - base_npv
        it["rem_pct_binn"] = it["rem"] / p.b_inn * 100
        it["rem_pct_R"] = it["rem"] / R["scn"][s]["R"] * 100
        it["tv_new"] = R["scn"][s]["sch"]["tv"] + it["delay"] / p.days
    o["E_npv"] = sum(i["prob"] * i["npv"] for i in o["items"])
    o["E_loss"] = o["npv0"] - o["E_npv"]
    o["E_rem"] = o["E_npv"] - base_npv
    o["worst"] = min(i["rem"] for i in o["items"])
    R["scn"][s]["out"] = o

# чувствительность: доля инновационных затрат
shares = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
R["sens_share"] = []
for sh in shares:
    q = replace(p, share_inn=sh)
    npvs = {s: npv(flows(s, q)) for s in SCENARIOS}
    ind = {s: indicators(flows(s, q), q.rate) for s in SCENARIOS}
    R["sens_share"].append(dict(share=sh, b_inn=q.b_inn, b_inv=q.b_inv, pilot=q.pilot, npv=npvs,
        R={s: npvs[s] - npvs["BASE"] for s in INTEG},
        Rrel={s: (npvs[s] - npvs["BASE"]) / q.b_inn * 100 for s in INTEG},
        irr={s: ind[s]["irr"] for s in SCENARIOS}))
# чувствительность: ставка дисконтирования 10..16
rates = [0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16]
R["sens_rate"] = []
for r in rates:
    q = replace(p, rate=r)
    npvs = {s: npv(flows(s, q)) for s in SCENARIOS}
    ind = {s: indicators(flows(s, q), r) for s in SCENARIOS}
    R["sens_rate"].append(dict(rate=r, npv=npvs,
        R={s: npvs[s] - npvs["BASE"] for s in INTEG},
        Rrel={s: (npvs[s] - npvs["BASE"]) / p.b_inn * 100 for s in INTEG},
        pi={s: ind[s]["pi"] for s in SCENARIOS}, dpp={s: ind[s]["dpp"] for s in SCENARIOS}))
# переключение знака: ставка, при которой NPV базового = 0 (ВНД базового) и R=0 (если есть)
def solve(f, lo, hi):
    flo = f(lo)
    if flo * f(hi) > 0: return None
    for _ in range(100):
        mid = (lo + hi) / 2
        if flo * f(mid) <= 0: hi = mid
        else: lo = mid; flo = f(mid)
    return (lo + hi) / 2
def first_root(f, lo=0.05, hi=3.0, step=0.005):
    x = lo; fx = f(x)
    while x + step <= hi:
        y = x + step; fy = f(y)
        if fx * fy <= 0: return solve(f, x, y)
        x, fx = y, fy
    return None
R["switch"] = {s: first_root(lambda r: npv(flows(s, replace(p, rate=r))) - npv(flows("BASE", replace(p, rate=r)))) for s in INTEG}
R["irr_base"] = R["scn"]["BASE"]["ind"]["irr"]

# меры управления рисками: эффект = снижение ожидаемых потерь − затраты меры (в ЧДД)
MEAS = [
 dict(id="М1", name="Проверка согласованности конструкторских и проектных решений до рабочей документации", dim="вероятность", ev=(6, 7), eff=(0.20, 0.35, 0.50), cost=0.40, n_pay=2),
 dict(id="М2", name="Фиксация конфигурации и разрешение изменений", dim="стоимость", ev=(6, 7, 8, 9), eff=(0.10, 0.20, 0.30), cost=0.50, n_pay=3),
 dict(id="М3", name="Поэтапная приемка строительной готовности", dim="длительность", ev=(7, 8, 9), eff=(0.10, 0.20, 0.30), cost=0.60, n_pay=4),
 dict(id="М4", name="Испытание связанных систем и комплексное опробование", dim="вероятность", ev=(8, 9), eff=(0.20, 0.35, 0.50), cost=0.80, n_pay=5),
]
def apply(pp, meas, e):
    pe, ec, dd = list(pp.p_ev), list(pp.ev_cost), list(pp.ev_delay_d)
    for m in meas:
        for k in m["ev"]:
            i = k - 5
            if m["dim"] == "вероятность": pe[i] *= (1 - e[m["id"]])
            elif m["dim"] == "стоимость": ec[i] *= (1 - e[m["id"]])
            else: dd[i] *= (1 - e[m["id"]])
    return replace(pp, p_ev=tuple(pe), ev_cost=tuple(ec), ev_delay_d=tuple(dd))
MEAS5 = dict(id="М5", name="Синхронизация календарного плана разработки с календарным планом строительства",
             dim="ожидание", ev=(), eff=(0.20, 0.35, 0.50), cost=0.50, n_pay=2)


def pv_store(s):
    """Приведенная стоимость хранения и консервации по окнам ожидания сценария."""
    sch = schedule(s, p); N = p.n_years
    wins = []
    a7, b7 = sch["conf"][5], sch["st"][4]
    if b7 - a7 > 1e-9: wins.append((a7, b7))
    for j in range(8):
        lag = sch["d_trl"][j] - sch["d_plan"][j]
        if lag > 1e-9: wins.append((sch["conf"][j] - lag, sch["conf"][j]))
    tot = 0.0
    for (a, b) in wins:
        for n_ in range(1, N + 1):
            tot += spread(a, b, p.t7_store * p.b_inn * (b - a), n_) * (1 + p.rate) ** (-n_)
    return tot


pm = replace(p, mfix=True, p_ev=(p.p_ev[0], 1.0, 1.0, 1.0, 1.0))   # расчетный случай: события доработки TRL6–TRL9 наступают
R["meas"] = {"list": MEAS + [MEAS5], "res": {}, "case": "events_occur"}
for s in INTEG:
    el0 = outcomes(s, pm)["E_loss"]
    res = {}
    for m in MEAS:
        row = []
        for j, lab in enumerate(("low", "mid", "high")):
            e = {m["id"]: m["eff"][j]}
            o = outcomes(s, apply(pm, [m], e))
            el1 = o["E_loss"]
            pvc = m["cost"] * (1 + p.rate) ** (-m["n_pay"])
            row.append(dict(eff=m["eff"][j], el=el1, dEL=el0 - el1, pvc=pvc, net=el0 - el1 - pvc))
        # безубыточная эффективность (линейный поиск по доле снижения)
        def f(x):
            return el0 - outcomes(s, apply(pm, [m], {m["id"]: x}))["E_loss"] - m["cost"] * (1 + p.rate) ** (-m["n_pay"])
        res[m["id"]] = dict(row=row, be=solve(f, 0.0, 0.99))
    # мера М5 сокращает длительность окон ожидания, поэтому ее эффект равен
    # сокращению приведенной стоимости хранения и консервации и не зависит от исходов доработок
    pvs = pv_store(s)
    pvc5 = MEAS5["cost"] * (1 + p.rate) ** (-MEAS5["n_pay"])
    row5 = [dict(eff=e_, el=el0, dEL=0.0, dNPV=e_ * pvs, pvc=pvc5, net=e_ * pvs - pvc5) for e_ in MEAS5["eff"]]
    res["М5"] = dict(row=row5, be=pvc5 / pvs if pvs > 0 else None, pv_store=pvs)
    # пакет из пяти мер
    row = []
    for j in range(3):
        e = {m["id"]: m["eff"][j] for m in MEAS}
        o = outcomes(s, apply(pm, MEAS, e))
        pvc = sum(m["cost"] * (1 + p.rate) ** (-m["n_pay"]) for m in MEAS) + pvc5
        d5 = MEAS5["eff"][j] * pvs
        row.append(dict(el=o["E_loss"], dEL=el0 - o["E_loss"], dNPV=d5, pvc=pvc,
                        net=el0 - o["E_loss"] + d5 - pvc,
                        worst=min(i["npv"] - base_npv for i in o["items"]) + d5))
    res["pack"] = row
    R["meas"]["res"][s] = res

# ===== сравнение точек входа =====
import random
OPT = [("BASE", "Базовый", False), ("TRL7", "TRL7", False), ("TRL6", "TRL6", False), ("TRL5", "TRL5", False)]
EP = {"opts": []}
for s, lab, pa in OPT:
    pp = p
    rows = flows(s, pp); ind = indicators(rows, pp.rate); sch = schedule(s, pp)
    d = dict(scn=s, label=lab, pilot=pa, npv=npv(rows), tv=sch["tv"], tv_inv=sch["tv"] - sch["f"],
             net9=sch["net_conf"][-1], pi=ind["pi"], irr=ind["irr"], pp=ind["pp"], dpp=ind["dpp"])
    if s == "BASE":
        d.update(R=0.0, worst=0.0, E_rem=0.0)
    else:
        o = outcomes(s, pp, sch=sch)
        d["worst"] = min(i["npv"] for i in o["items"]) - base_npv
        d["E_rem"] = o["E_npv"] - base_npv
        d["R"] = d["npv"] - base_npv
    EP["opts"].append(d)
tvb = EP["opts"][0]["tv"]
for d in EP["opts"]:
    d["dT"] = tvb - d["tv"]
    d["price"] = d["R"] / d["dT"] if d["dT"] > 1e-9 else None
# критический множитель затрат и задержек доработок (все события одновременно = наихудший исход)
def worst_rem(s, m, pa):
    pp = replace(p, ev_cost=tuple(c * m for c in p.ev_cost), ev_delay_d=tuple(x * m for x in p.ev_delay_d))
    o = outcomes(s, pp)
    return min(i["npv"] for i in o["items"]) - base_npv
EP["crit"] = {}
for s, lab, pa in OPT[1:]:
    m = solve(lambda x: worst_rem(s, x, pa), 1.0, 400.0)
    EP["crit"][lab] = dict(m=m, w1=worst_rem(s, 1.0, pa))
    if m:
        pp = replace(p, ev_cost=tuple(c * m for c in p.ev_cost), ev_delay_d=tuple(x * m for x in p.ev_delay_d))
        _ev = [e for e in outcomes(s, pp)["events"] if e["aff"]]      # только события, затрагивающие работы сценария
        EP["crit"][lab]["cost"] = sum(e["cost"] for e in _ev); EP["crit"][lab]["delay"] = sum(e["dd"] for e in _ev)
# многокритериальная матрица (шесть критериев, включая устойчивость m*)
CRIT = ["ЧДД", "Срок ввода", "Остаток в наихудшем исходе", "Доказательность TRL", "Ресурсная нагрузка", "Устойчивость (m*)"]
W = [0.30, 0.15, 0.15, 0.15, 0.10, 0.15]
QUAL = {"Базовый": (3, 5), "TRL7": (5, 2), "TRL6": (4, 3), "TRL5": (3, 3)}
def mm(v, lo, hi, inv=False):
    x = (v - lo) / (hi - lo) if hi > lo else 0.0
    return 1 - x if inv else x
for d in EP["opts"]:
    d["m"] = EP["crit"][d["label"]]["m"] if d["label"] in EP["crit"] else None
mmax = max(d["m"] for d in EP["opts"] if d["m"] is not None)
EP["opts"][0]["m"] = mmax      # в Базовом сценарии доработок нет: устойчивость принята наибольшей
npvs = [d["npv"] for d in EP["opts"]]; tvs = [d["tv"] for d in EP["opts"]]; ws = [d["worst"] for d in EP["opts"]]; ms_ = [d["m"] for d in EP["opts"]]
for d in EP["opts"]:
    qe, qr = QUAL[d["label"]]
    d["score"] = [mm(d["npv"], min(npvs), max(npvs)) * 100, mm(d["tv"], min(tvs), max(tvs), True) * 100,
                  mm(d["worst"], min(ws), max(ws)) * 100, (qe - 1) / 4 * 100, (qr - 1) / 4 * 100, mm(d["m"], min(ms_), max(ms_)) * 100]
    d["qual"] = [qe, qr]
def total(d, w): return sum(a * b for a, b in zip(d["score"], w))
for d in EP["opts"]: d["total"] = total(d, W)
EP["crit_names"] = CRIT; EP["weights"] = W
WS = {"Базовые веса": W, "Равные веса": [1/6] * 6, "Приоритет ЧДД": [0.45, 0.10, 0.10, 0.10, 0.10, 0.15],
      "Приоритет срока": [0.20, 0.35, 0.10, 0.10, 0.10, 0.15], "Приоритет надежности": [0.15, 0.05, 0.25, 0.15, 0.05, 0.35]}
EP["wsets"] = {}
for k, w in WS.items():
    t = [total(d, w) for d in EP["opts"]]
    EP["wsets"][k] = dict(w=w, tot=t, best=EP["opts"][t.index(max(t))]["label"])
rnd = random.Random(20261107); wins = {d["label"]: 0 for d in EP["opts"]}; N_MC = 10000
for _ in range(N_MC):
    x = [rnd.expovariate(1) for _ in range(6)]; sm = sum(x); w = [v / sm for v in x]
    t = [total(d, w) for d in EP["opts"]]
    wins[EP["opts"][t.index(max(t))]["label"]] += 1
EP["mc"] = dict(n=N_MC, wins={k: v / N_MC for k, v in wins.items()})
# область весов: суммарный вес критериев устойчивости (остаток + m*), остальные веса пропорциональны базовым
def w_rob(wt):
    base = W; w = base[:]; w[2] = wt / 2; w[5] = wt / 2
    others = [base[0], base[1], base[3], base[4]]; so = sum(others)
    for k_, v in zip((0, 1, 3, 4), others): w[k_] = v / so * (1 - wt)
    return w
def diff56(wt):
    w = w_rob(wt); t = {d["label"]: total(d, w) for d in EP["opts"]}
    return t["TRL5"] - t["TRL6"]
EP["w_switch"] = solve(diff56, 0.0, 0.6)
EP["w_rob_grid"] = [dict(wt=wt, best=max(EP["opts"], key=lambda d: total(d, w_rob(wt)))["label"], tot=[total(d, w_rob(wt)) for d in EP["opts"]]) for wt in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6)]

R["entry"] = EP

R["case"] = {}
for s_ in INTEG:
    o_ = outcomes(s_, replace(p, mfix=True, p_ev=(p.p_ev[0], 1.0, 1.0, 1.0, 1.0)))
    it = [i for i in o_["items"] if i["prob"] > 0.5][0]
    R["case"][s_] = dict(npv=it["npv"], rem=it["npv"] - base_npv, cost=it["cost"], delay=it["delay"], loss=R["scn"][s_]["npv0"] - it["npv"],
                         rem_pct_binn=(it["npv"] - base_npv) / p.b_inn * 100, rem_pct_R=(it["npv"] - base_npv) / R["scn"][s_]["R"] * 100,
                         tv=R["scn"][s_]["sch"]["tv"] + it["delay"] / p.days)

# для сравнения: эффект пакета мер при вероятностях исходных данных
R["meas_prob"] = {}
for s_ in INTEG:
    el0_ = R["scn"][s_]["out"]["E_loss"]
    row_ = []
    for j in range(3):
        e_ = {m["id"]: m["eff"][j] for m in MEAS}
        o_ = outcomes(s_, apply(p, MEAS, e_))
        pvc_ = sum(m["cost"] * (1 + p.rate) ** (-m["n_pay"]) for m in MEAS) + pvc5
        row_.append(el0_ - o_["E_loss"] + MEAS5["eff"][j] * pv_store(s_) - pvc_)
    R["meas_prob"][s_] = dict(net=row_, E_loss=el0_)

# дополнительные показатели для текста главы 3
q_ = replace(p, loss_limit_end=p.first_tax_year + p.n_years)
R["limit_check"] = {s_: npv(flows(s_, p)) - npv(flows(s_, q_)) for s_ in SCENARIOS}
R["limit_check"]["dR"] = {s_: (npv(flows(s_, p)) - base_npv) - (npv(flows(s_, q_)) - npv(flows("BASE", q_))) for s_ in INTEG}
R["extra"] = {}
for s_ in SCENARIOS:
    rows_ = R["scn"][s_]["rows"]
    mn_ = min(r["cumd"] for r in rows_)
    R["extra"][s_] = dict(min_cumd=mn_, min_n=[r["n"] for r in rows_ if r["cumd"] == mn_][0],
                          max_loss=max(r["loss_close"] for r in rows_), loss_free_n=min(r["n"] for r in rows_ if r["n"] > 1 and r["loss_close"] < 1e-9 and r["n"] > [x["n"] for x in rows_ if x["loss_close"] == max(y["loss_close"] for y in rows_)][0]),
                          tax_total=sum(r["tax"] for r in rows_))

def conv(o):
    if isinstance(o, dict): return {str(k): conv(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [conv(v) for v in o]
    return o
json.dump(conv(R), open("results.json", "w"), ensure_ascii=False, indent=1)
print("base", round(base_npv, 3))
for s in INTEG:
    o = R["scn"][s]["out"]
    print(s, "R=%.2f rel=%.1f%% E_loss=%.3f E_rem=%.2f worst=%.2f" % (R["scn"][s]["R"], R["scn"][s]["R_rel"], o["E_loss"], o["E_rem"], o["worst"]))
print("switch", R["switch"], "irr_base", R["irr_base"])
for r in R["sens_rate"]: print("rate", r["rate"], {k: round(v, 1) for k, v in r["npv"].items()}, {k: round(v, 1) for k, v in r["R"].items()})
for r in R["sens_share"]: print("share", r["share"], {k: round(v, 1) for k, v in r["npv"].items()}, {k: round(v, 1) for k, v in r["R"].items()})
for s in ("TRL5",):
    for k, v in R["meas"]["res"][s].items():
        if k == "pack": print("pack", [(round(x["dEL"], 2), round(x["net"], 2), round(x["worst"], 1)) for x in v])
        else: print(k, [(round(x["dEL"], 3), round(x["net"], 3)) for x in v["row"]], "be", v["be"])

for d in EP["opts"]: print(d["label"], round(d["npv"],1), round(d["tv"],2), round(d["R"],1), d["price"] and round(d["price"],1), round(d["worst"],1), round(d["total"],1))
print(EP["crit"]); print({k:v["best"] for k,v in EP["wsets"].items()}); print(EP["mc"])


print("case",R["case"])
for s_ in ("TRL5","TRL6"):
    for k,v in R["meas"]["res"][s_].items():
        if k=="pack": print("pack",[(round(x["dEL"],2),round(x["net"],2),round(x["worst"],1)) for x in v])
        else: print(k,[(round(x["dEL"],2),round(x["net"],2)) for x in v["row"]],"be",v["be"] and round(v["be"],3))

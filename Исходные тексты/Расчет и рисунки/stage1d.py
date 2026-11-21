# -*- coding: utf-8 -*-
import json
from dataclasses import replace
from model import *
OUT = json.load(open("stage1.json")); p = P()
def stress(kc, dy):
    bi = p.b_inn*kc; bv = p.b_inv; pp = replace(p, budget=bi+bv, share_inn=bi/(bi+bv), t_dev=p.t_dev+dy, pilot_share=p.pilot_share/kc*1.0)
    # опытная инфраструктура: сохраняем абсолютное значение 35 млн
    pp = replace(pp, pilot_share=p.pilot/pp.b_inn)
    r = {s: npv(flows(s, pp)) for s in SCENARIOS}
    return {s: r[s] for s in SCENARIOS}, {s: r[s]-r["BASE"] for s in INTEG}
ST = []
for kc, dy in ((1, 0), (1.5, 1.0), (1.5, 2.0), (2.0, 1.0), (2.0, 2.0)):
    n, R = stress(kc, dy); ST.append(dict(kc=kc, dy=dy, npv=n, R=R))
    print(kc, dy, {k: round(v,1) for k,v in n.items()}, {k: round(v,1) for k,v in R.items()})
OUT["stress"] = ST
OUT["t7x_npv"] = npv(flows("TRL7", replace(p, t7_store=0, t7_remount=0, t7_warr_p=0))) - npv(flows("TRL7", p))
OUT["wait_npv"] = {s_: npv(flows(s_, replace(p, t7_store=0, t7_remount=0, t7_warr_p=0))) - npv(flows(s_, p))
                   for s_ in ("TRL7", "TRL6", "TRL5")}
json.dump(OUT, open("stage1.json", "w"), ensure_ascii=False, indent=1, default=float)

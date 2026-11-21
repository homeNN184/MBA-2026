# -*- coding: utf-8 -*-
"""Влияние доли инновационного оборудования в бюджете на ЧДД сценариев."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"]="DejaVu Sans"
import sys; sys.path.insert(0,"/home/claude/work/model")
import model as M
SH=[0.10,0.20,0.30,0.40,0.50]
V={s:[] for s in M.SCENARIOS}
for sh in SH:
    q=M.P(share_inn=sh)
    for s in M.SCENARIOS: V[s].append(M.npv(M.flows(s,q)))
rel={s:[100.0*x/V[s][0] for x in V[s]] for s in M.SCENARIOS}
lab={"BASE":("Традиционная схема","#2F6FC0"),"TRL5":("Интеграция TRL5","#1B9E77"),
     "TRL6":("Интеграция TRL6","#8E44AD"),"TRL7":("Интеграция TRL7","#C4690E")}
fig,ax=plt.subplots(figsize=(7.0,3.3),dpi=300)
x=[s*100 for s in SH]
for s in ("BASE","TRL7","TRL6","TRL5"):
    n,c=lab[s]
    ax.plot(x,rel[s],color=c,lw=2.4,marker="o",ms=5,mfc="white",mew=1.6,label=n)
    dy={"TRL5":3.0,"TRL6":-3.0}.get(s,0.0)
    ax.text(x[-1]+1.2,rel[s][-1]+dy,"%.0f %%"%rel[s][-1],color=c,fontsize=9,fontweight="bold",va="center")
ax.set_xlim(8,57); ax.set_ylim(0,112)
ax.set_xticks(x); ax.set_xticklabels(["%d %%"%v for v in x],fontsize=9)
ax.set_yticks([0,25,50,75,100]); ax.set_yticklabels(["0","25","50","75","100"],fontsize=9)
ax.set_xlabel("доля инновационного оборудования в бюджете проекта",fontsize=9.5)
ax.set_ylabel("ЧДД, % к уровню при доле 10 %",fontsize=9.5)
ax.grid(axis="y",color="#e8e6e0",lw=1)
for s_ in ("top","right"): ax.spines[s_].set_visible(False)
for s_ in ("left","bottom"): ax.spines[s_].set_color("#b9b6ae")
ax.tick_params(colors="#555555",length=3)
ax.legend(loc="lower left",frameon=False,fontsize=9)
fig.tight_layout(pad=0.3)
fig.savefig("/home/claude/work/fig/pres_share.png",dpi=300,facecolor="white",bbox_inches="tight")
print("ЧДД, %% к уровню при доле 10 %%:")
for s in ("BASE","TRL5","TRL6","TRL7"):
    print(" ",lab[s][0], ["%.0f"%v for v in rel[s]])

# -*- coding: utf-8 -*-
"""Срок ввода по сценариям в относительных величинах к традиционной схеме."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"]="DejaVu Sans"
import sys; sys.path.insert(0,"/home/claude/work/model")
import model as M
p=M.P()
sc={s:M.schedule(s,p) for s in M.SCENARIOS}
base=sc["BASE"]["tv"]
rows=[("Традиционная схема","BASE","#2F6FC0"),("Интеграция TRL5","TRL5","#1B9E77"),
      ("Интеграция TRL6","TRL6","#8E44AD"),("Интеграция TRL7","TRL7","#C4690E")]
fig,ax=plt.subplots(figsize=(8.2,2.9),dpi=300)
for i,(lab,k,col) in enumerate(rows):
    y=len(rows)-1-i
    tv=sc[k]["tv"]/base*100
    en=sc[k]["st"][1]/base*100      # начало проектной документации
    ax.barh(y,en,height=0.52,color="#cfd6de",edgecolor="white")
    ax.barh(y,tv-en,left=en,height=0.52,color=col,edgecolor="white")
    ax.text(tv+1.5,y,"%.0f %%"%tv,va="center",fontsize=8.5,fontweight="bold",color=col)
    ax.text(-1.5,y,lab,va="center",ha="right",fontsize=8.5)
ax.set_xlim(-32,112); ax.set_ylim(-0.6,len(rows)-0.4)
ax.set_yticks([]); ax.set_xticks([0,25,50,75,100])
ax.set_xticklabels(["0","25","50","75","100"],fontsize=8)
ax.set_xlabel("срок от начала разработки, % к традиционной схеме",fontsize=8.5)
for s_ in ("top","right","left"): ax.spines[s_].set_visible(False)
ax.spines["bottom"].set_color("#b9b6ae")
ax.tick_params(axis="x",length=3,colors="#555555")
ax.text(0,len(rows)-0.25,"серым — подтверждение уровней до входа, цветом — проектирование и строительство",
        fontsize=8,color="#555555")
fig.tight_layout(pad=0.4)
fig.savefig("/home/claude/work/fig/pres_scen.png",dpi=300,facecolor="white",bbox_inches="tight")
print("ok")

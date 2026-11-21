# -*- coding: utf-8 -*-
"""Упрощенная схема механизма интеграции для презентации."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams["font.family"]="DejaVu Sans"
BL="#2F6FC0"; GR="#1B9E77"; OR="#C4690E"; PU="#8E44AD"
fig,ax=plt.subplots(figsize=(9.0,3.45),dpi=300); ax.axis("off")
ax.set_xlim(0,100.5); ax.set_ylim(-0.5,40)

def box(cx,y,w,h,t,fc,ec,fs=7.4,bold=False):
    ax.add_patch(FancyBboxPatch((cx-w/2,y),w,h,boxstyle="round,pad=0.25,rounding_size=0.7",
                                fc=fc,ec=ec,lw=1.0))
    ax.text(cx,y+h/2,t,ha="center",va="center",fontsize=fs,linespacing=1.2,
            fontweight="bold" if bold else "normal")

TOPY, TOPH = 29.0, 8.0
BOTY, BOTH = 2.5, 8.0
top=[("TRL1–TRL4\nисследования и\nкомпоненты",10.0,19.0),("TRL5\nкомпоненты в\nсоотв. среде",31.0,15.0),
     ("TRL6\nпрототип в\nсоотв. среде",49.0,15.0),("TRL7\nобразец в\nэкспл. среде",67.0,15.0),
     ("TRL8–TRL9\nсистема в\nэксплуатации",87.0,19.0)]
for t,cx,w in top: box(cx,TOPY,w,TOPH,t,"#eaf1fb",BL)
bot=[("Исходные\nданные",8.0,15.0),("Проектная\nдокументация,\nэкспертиза",26.0,18.0),
     ("Рабочая\nдокументация",44.0,15.0),("Строительно-\nмонтажные\nработы",62.0,16.0),
     ("Пусконаладочные\nработы",79.0,15.0),("Комплексное\nопробование",94.0,12.0)]
for t,cx,w in bot: box(cx,BOTY,w,BOTH,t,"#e7f6ef",GR)
ax.text(0.5,38.6,"Инновационный процесс",fontsize=8.6,fontweight="bold",color=BL,va="center")
ax.text(0.5,0.6,"Инвестиционный строительный процесс",fontsize=8.6,fontweight="bold",color=GR,va="center")

def link(x_from,x_to,lvl,col,lab,up):
    y1,y2=(TOPY,BOTY+BOTH) if not up else (BOTY+BOTH,TOPY)
    a=min(y1,y2); b=max(y1,y2)
    ax.plot([x_from,x_from],[b if not up else a, lvl],color=col,lw=2.0,solid_capstyle="butt")
    ax.plot([x_from,x_to],[lvl,lvl],color=col,lw=2.0,solid_capstyle="butt")
    tip=(x_to,a) if not up else (x_to,b)
    ax.plot([x_to,x_to],[lvl,tip[1]+(1.2 if not up else -1.2)],color=col,lw=2.0,solid_capstyle="butt")
    ax.add_patch(FancyArrowPatch((x_to,tip[1]+(2.2 if not up else -2.2)),tip,
                                 arrowstyle="-|>",mutation_scale=11,color=col,lw=2.0))
    ax.text((x_from+x_to)/2,lvl+0.9,lab,ha="center",va="bottom",fontsize=7.4,fontweight="bold",color=col,
            bbox=dict(boxstyle="round,pad=0.18",fc="white",ec="none"))

# вход: подтверждение TRL5/TRL6/TRL7 открывает проектную документацию
link(31.0,26.0,22.5,OR,"КТ-1  вход TRL5",False)
link(49.0,26.0,19.0,OR,"КТ-2  вход TRL6",False)
link(67.0,26.0,15.5,OR,"КТ-3  вход TRL7",False)
# подтверждение уровней на объекте
link(79.0,87.0,12.0,PU,"КТ-4  ПНР → TRL8",True)
link(94.0,91.0,24.5,PU,"КТ-5  КО → TRL9",True)
ax.text(0.5,24.0,"оранжевые связи —",fontsize=7.2,color=OR,va="center")
ax.text(0.5,21.6,"вход в инвестиционный процесс",fontsize=7.2,color=OR,va="center")
ax.text(0.5,18.0,"фиолетовые связи —",fontsize=7.2,color=PU,va="center")
ax.text(0.5,15.6,"подтверждение уровней на объекте",fontsize=7.2,color=PU,va="center")
fig.tight_layout(pad=0.2)
fig.savefig("/home/claude/work/fig/pres_mech.png",dpi=300,facecolor="white",bbox_inches="tight")
print("ok")

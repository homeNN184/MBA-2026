# -*- coding: utf-8 -*-
import re
src=open('charts2.py').read()
head=src.split("# ---------- Рисунок 3.1")[0]
exec(head)
import numpy as np
PU="#8a3ffc"
fig, ax = plt.subplots(figsize=(6.5, 5.0)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(1.5, 76)
ax.text(1, 73.3, "Инновационный процесс: уровни технологической зрелости инновационного продукта (TRL)", fontsize=7.6, fontweight="bold", color=BL, va="center")
top = ["Задание на\nразработку\nпродукта", "TRL1\nпринципы", "TRL2\nконцепция", "TRL3\nподтвержд.\nконцепции", "TRL4\nкомпоненты\nв лаборатории", "TRL5\nкомпоненты в\nсоотв. среде", "TRL6\nпрототип в\nсоотв. среде", "TRL7\nобразец в\nэксплуат. среде", "TRL8\nсистема\nквалифицир.", "TRL9\nподтверждена\nэксплуатацией"]
cxt = [5.2 + i * 9.9 for i in range(10)]
for i, t in enumerate(top):
    box(ax, cxt[i], 56, 8.6, 14, t, fc="#fff3e8" if i == 0 else "#eaf1fb", ec=OR if i == 0 else BL, fs=5.7)
    if i < 9: arrow(ax, (cxt[i] + 4.55, 63), (cxt[i + 1] - 4.55, 63), BL, lw=0.9)
ax.text(1, 10.8, "Инвестиционный строительный процесс: стадии создания инвестиционного объекта строительства", fontsize=7.6, fontweight="bold", color=GR, va="center")
bot = ["Замысел и\nтехнические\nтребования", "Задание на\nпроектирование", "Проектная\nдокументация,\nэкспертиза", "Рабочая\nдокументация", "Поставка\nМТР", "Строительно-\nмонтажные\nработы", "ПНР\nбез нагрузки", "ПНР\nпод нагрузкой", "Комплексное\nопробование,\nввод"]
cxb = [6.1 + j * 11.0 for j in range(9)]
for j, t in enumerate(bot):
    box(ax, cxb[j], 15, 10.0, 14, t, fc="#e7f6ef", ec=GR, fs=5.7)
    if j < 8: arrow(ax, (cxb[j] + 5.15, 22), (cxb[j + 1] - 5.15, 22), GR, lw=0.9)
YB, YT = 29.2, 56.0
LW=1.8
def line(xs,ys,col,**k): ax.plot(xs,ys,color=col,lw=LW,solid_capstyle="butt",solid_joinstyle="miter",**k)
def lab(x,y,t,col): ax.text(x,y,t,fontsize=6.4,fontweight="bold",color=col,ha="center",va="center",bbox=dict(boxstyle="round,pad=0.15",fc="white",ec="none"),zorder=5)
# КТ-0
x0=5.6; line([x0,x0],[YB,YT-1.2],OR); arrow(ax,(x0,YT-3),(x0,YT),OR,lw=LW,ms=14); lab(x0,42.5,"КТ-0",OR)
# оранжевая шина КТ-1..КТ-3 -> ПД
ob=47.0; xs=[cxt[5]-1.6, cxt[6]-1.6, cxt[7]-1.6]; xt2=cxb[2]
for x in xs: line([x,x],[YT,ob],OR)
line([xt2,xs[-1]],[ob,ob],OR)
line([xt2,xt2],[ob,YB+2.5],OR); arrow(ax,(xt2,YB+4.5),(xt2,YB),OR,lw=LW,ms=14)
for x,t in zip(xs,["КТ-1","КТ-2","КТ-3"]): lab(x,51.5,t,OR)
# фиолетовые линии: каждая отдельно, ломаная из вертикальных и горизонтальных отрезков
r=1.2; th=np.linspace(0,np.pi,30)
routes=[(cxb[3],cxt[6]+1.6,42.0,"КТ-2"),(cxb[5],cxt[7]+1.6,38.0,"КТ-3"),(cxb[6],cxt[8],34.0,"КТ-4"),(cxb[8],cxb[8],None,"КТ-5")]
for xs_,xt_,lv,t in routes:
    if lv is None:
        line([xs_,xs_],[YB,YT-2.2],PU); lab(xs_,33.4,t,PU)
    else:
        line([xs_,xs_],[YB,lv],PU); line([xs_,xt_],[lv,lv],PU); lab(xs_,(YB+lv)/2 if t!="КТ-4" else 30.6,t,PU) if False else None
        if xt_<=xs_+0: pass
        if ob-r>lv and abs(xt_-(cxt[6]+1.6))<1e-6:
            line([xt_,xt_],[lv,ob-r],PU); ax.plot(xt_+r*np.sin(th), ob-r+2*r*th/np.pi, color=PU, lw=LW); line([xt_,xt_],[ob+r,YT-2.2],PU)
        else:
            line([xt_,xt_],[lv,YT-2.2],PU)
    arrow(ax,(xt_,YT-4),(xt_,YT),PU,lw=LW,ms=14)
lab(cxb[3],35.5,"КТ-2",PU); lab(cxb[5],33.6,"КТ-3",PU); lab(cxb[6],31.6,"КТ-4",PU)
ax.text(1, 8.0, "оранжевые линии: КТ-0 — задание на разработку; КТ-1…КТ-3 — вход (начало ПД)", fontsize=6.4, color=OR, va="center")
ax.text(1, 6.0, "по подтверждению TRL5, TRL6 или TRL7 в зависимости от сценария", fontsize=6.4, color=OR, va="center")
ax.text(1, 4.0, "фиолетовые линии: подтверждение уровня по окончании стадии (РД, СМР, ПНР, КО)", fontsize=6.4, color=PU, va="center")
fig.tight_layout(pad=0.3); fig.savefig("/home/claude/work/fig15_draft.png", dpi=660, bbox_inches="tight", facecolor="white")

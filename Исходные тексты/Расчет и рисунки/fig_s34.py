# -*- coding: utf-8 -*-
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams["font.family"]="DejaVu Sans"
fig,ax=plt.subplots(figsize=(11,6.6),dpi=600); ax.set_xlim(0,100); ax.set_ylim(0,74); ax.axis("off")
stages=[("1. Замысел","КЦП","Расчет по прогнозным\nданным","Предварительное решение\nоб интеграции"),
        ("2. Начало\nразработки","Заявка на НИОКР,\nтехническое задание,\nпрограмма внедрения","—","Разработка адресно\nпод объект (КТ-0)"),
        ("3. Предынвестиционная\nстадия","Программа предынвести-\nционных исследований,\nпредпроектная документация","Расчет по уточненным\nданным (правило выбора)","Решение об интеграции\nи об уровне входа"),
        ("4. Активная фаза","Инвестиционная\nпрограмма,\nКТ-1 – КТ-5","Пересчет в каждой\nконтрольной точке","Запуск стадий\nстроительства"),
        ("5. Ввод и оценка","Акты ввода,\nотчет о внедрении","Уточнение\nпараметров","Параметры для\nследующих проектов")]
DATA = ["Проекты-аналоги,\nэкспертные оценки\nсроков и стоимости",
        "Техническое задание,\nуточненные оценки\nпо аналогам",
        "Результаты испытаний\nTRL4, предынвестиционные\nисследования",
        "Фактические данные\nконтрольных точек,\nпротоколы испытаний",
        "Фактические сроки\nи затраты, пополнение\nбазы аналогов"]
xs=[14,31,48,65,82]; w=16
rows=[("Стадия",62),("Документы",50),("Данные для\nмоделирования",38),("Модель",26),("Решение",14)]
for (lab,y) in rows:
    ax.text(12.0,y+4.25,lab,fontsize=8.5,fontweight="bold",color="#1e2761",ha="right",va="center",linespacing=1.3)
for i,(s,d,m,r) in enumerate(stages):
    x=xs[i]
    for (txt,y,fc) in ((s,62,"#1e2761"),(d,50,"#cadcfc"),(DATA[i],38,"#dfe9f6"),(m,26,"#e8eef9"),(r,14,"#ffffff")):
        ax.add_patch(FancyBboxPatch((x,y),w,8.5,boxstyle="round,pad=0.3,rounding_size=0.8",fc=fc,ec="#1e2761",lw=0.9))
        ax.text(x+w/2,y+4.25,txt,ha="center",va="center",fontsize=6.5 if y==38 else 7.4,color="white" if fc=="#1e2761" else "#111111",linespacing=1.3)
    if i<4:
        ax.add_patch(FancyArrowPatch((x+w+0.3,66.25),(xs[i+1]-0.3,66.25),arrowstyle="-|>",mutation_scale=10,color="#1e2761",lw=1.1))
# TRL line
ax.plot([14,98],[6,6],color="#1e2761",lw=1.2)
for x,t in ((14,"TRL1"),(39,"TRL4"),(56,"TRL5–TRL7"),(73,"TRL8"),(90,"TRL9")):
    ax.plot([x],[6],marker="D",color="#1e2761",ms=4); ax.text(x,2.2,t,ha="center",fontsize=7.5)
ax.text(12.0,6,"TRL",fontsize=8.5,fontweight="bold",color="#1e2761",ha="right",va="center")
ax.annotate("",xy=(39,11.4),xytext=(39,6.8),arrowprops=dict(arrowstyle="-|>",color="#b85042",lw=1))
ax.text(38.3,9.4,"инициирование стадии 3",fontsize=7,color="#b85042",ha="right",va="center")
ax.annotate("",xy=(56,11.4),xytext=(56,6.8),arrowprops=dict(arrowstyle="-|>",color="#b85042",lw=1))
ax.text(57.3,9.4,"вход в проектирование",fontsize=7,color="#b85042",ha="left",va="center")
plt.savefig("/home/claude/work/fig/f34_process.png",bbox_inches="tight",facecolor="white"); print("ok")

# -*- coding: utf-8 -*-
"""Слайд 9. SWOT-анализ организации разработки и поставки оборудования."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import icons_lib as I

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
PURPLE, FILL = "#8E44AD", "#EAF2FA"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")

Q = [
    (INV, I.check, "Сильные стороны", [
        "Требования закреплены в документации о закупке; частные задания\n"
        "на несерийные изделия согласованы экспертами ПАО «Газпром»,\n"
        "заказчика и эксплуатирующей организации",
        "Результаты заводских испытаний принимались до отгрузки оборудования",
        "Основание и ответственность закреплены Дорожной картой и Планом",
        "Компоновка и гидравлика обоснованы расчетами до изготовления",
        "Разработаны технические условия, зарегистрирован каталожный лист",
    ]),
    (PURPLE, I.minus, "Слабые стороны", [
        "Нет порядка, связывающего разработку со стадиями строительства",
        "Соответствие требованиям проверяется на построенном объекте",
        "Гарантийные обязательства могут закончиться до ввода объекта",
        "Нет прав на результаты интеллектуальной деятельности",
        "Неизвестна стоимость технического обслуживания и ремонта",
        "Изменения оборудования затрагивают строительные решения",
    ]),
    (INN, I.chartup, "Возможности", [
        "Совмещение процессов может сократить срок ввода объекта",
        "Договор позволяет ввести этапные приемки и испытания до поставки",
    ]),
    (TRN, I.warn, "Угрозы", [
        "Изготовитель ориентирован на срок поставки, а не на срок ввода",
        "Готовность изготовителя и соисполнителей не подтверждается заранее",
        "Отказ нестандартного изделия выявляется на объекте, аналогов нет",
        "Изменение характеристик приводит к доработкам документации",
    ]),
]

LM, GX, GY = 2.0, 2.0, 1.2
CW = (100 - 2 * LM - GX) / 2.0
BY0, BY1 = 0.3, 0.9                     # нижняя граница поля
TOP = YM - 0.9
AVAIL = TOP - (BY1 + 1.4) - GY
RH_TOP = AVAIL * 0.58
RH_BOT = AVAIL - RH_TOP

for k, (col, icon, head, items) in enumerate(Q):
    r, c = divmod(k, 2)
    x0 = LM + c * (CW + GX)
    RH = RH_TOP if r == 0 else RH_BOT
    y1 = TOP if r == 0 else TOP - RH_TOP - GY
    y0 = y1 - RH
    ax.add_patch(FancyBboxPatch((x0, y0), CW, RH,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
    ax.add_patch(FancyBboxPatch((x0, y1 - 0.75), CW, 0.75,
                                boxstyle="round,pad=0,rounding_size=0.35",
                                fc=col, ec="none", zorder=3))
    cx, cy = x0 + 3.6, y1 - 3.5
    ax.add_patch(Circle((cx, cy), 2.1, fc="none", ec=col, lw=1.3, zorder=4))
    icon(ax, cx, cy, 2.1, col, 1.4)
    ax.text(x0 + 7.0, cy, head, ha="left", va="center",
            fontsize=8.0, color=NAVY, fontweight="bold")
    y = y1 - 7.0
    for it in items:
        ax.add_patch(Circle((x0 + 2.6, y - 0.5), 0.38, fc=col, ec="none", zorder=5))
        ax.text(x0 + 4.3, y, it, ha="left", va="top",
                fontsize=6.3, color=SUB, linespacing=1.4)
        y -= (it.count("\n") + 1) * 1.34 + 0.65


fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s9_swot.png", dpi=660, facecolor="white")
print("ok, ряды", round(RH_TOP, 1), round(RH_BOT, 1))

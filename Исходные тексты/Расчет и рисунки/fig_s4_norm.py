# -*- coding: utf-8 -*-
"""Слайд 4. Рассмотренные группы источников."""
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

GR = [
    (NAVY, I.books, "Группа 1", "Федеральные нормативные правовые акты",
     "Градостроительный кодекс,\nстатьи 48, 49, 51, 53, 55\n"
     "№ 384-ФЗ, постановление № 87\n№ 223-ФЗ, № 488-ФЗ, № 127-ФЗ"),
    (NAVY, I.target, "Группа 2", "Государственные документы\nстратегического планирования",
     "Указы Президента № 145 и № 216\nЭнергетическая стратегия до 2050 года\n"
     "Концепция технологического развития\nдо 2030 года"),
    (INV, I.building, "Группа 3", "ПАО «Газпром», документы\nинвестиционной деятельности",
     "Постановление Правления № 5, планирование\n"
     "Приказ № 537, целевые программы развития\n"
     "Приказ № 548, инвестиционные программы\n"
     "Распоряжение № 95, исходные данные"),
    (INN, I.lamp, "Группа 4", "ПАО «Газпром», документы\nинновационной деятельности",
     "Приказ № 254, организация НИОКР\n"
     "Приказ № 102, внедрение инновационной\nпродукции\n"
     "ГОСТ Р 58048, уровни готовности технологии"),
    (PURPLE, I.search, "Группа 5", "Зарубежная практика",
     "DOE O 413.3B и DOE G 413.3-4A,\nоценка технологической готовности\n"
     "GAO-20-48G, качество оценки\nDNV-RP-A203, квалификация технологии"),
    (TRN, I.flask, "Группа 6", "Российская практика",
     "Госкорпорация «Росатом», уровни готовности\nПАО «Транснефть», испытания оборудования\n"
     "ПАО «НК «Роснефть», испытательная\nинфраструктура"),
]

LM, GAP = 2.0, 1.7
CW = (100 - 2 * LM - 2 * GAP) / 3.0
ROW_H = 18.2
ROWS = [(YM - 0.9 - ROW_H, YM - 0.9), (YM - 0.9 - 2 * ROW_H - 1.3, YM - 0.9 - ROW_H - 1.3)]

for n, (col, icon, num, name, body) in enumerate(GR):
    r, c = divmod(n, 3)
    x0 = LM + c * (CW + GAP)
    y0, y1 = ROWS[r]
    ax.add_patch(FancyBboxPatch((x0, y0), CW, y1 - y0,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
    ax.add_patch(FancyBboxPatch((x0, y1 - 0.75), CW, 0.75,
                                boxstyle="round,pad=0,rounding_size=0.35",
                                fc=col, ec="none", zorder=3))
    cx, cy = x0 + 3.9, y1 - 3.8
    ax.add_patch(Circle((cx, cy), 2.3, fc="none", ec=col, lw=1.3, zorder=4))
    icon(ax, cx, cy, 2.3 * 1.0, col, 1.4)
    ax.text(x0 + 7.4, cy, num, ha="left", va="center",
            fontsize=7.2, color=col, fontweight="bold")
    ax.text(x0 + 1.6, y1 - 7.2, name, ha="left", va="top",
            fontsize=7.4, color=NAVY, fontweight="bold", linespacing=1.32)
    ax.text(x0 + 1.6, y1 - 10.4, body, ha="left", va="top",
            fontsize=6.6, color=SUB, linespacing=1.42)

# нижняя полоса с признаками сопоставления
by0, by1 = 0.3, 3.3
ax.add_patch(FancyBboxPatch((LM, by0), 100 - 2 * LM, by1 - by0,
                            boxstyle="round,pad=0,rounding_size=0.8",
                            fc=FILL, ec="none", zorder=2))
ax.add_patch(FancyBboxPatch((LM, by0), 0.9, by1 - by0,
                            boxstyle="round,pad=0,rounding_size=0.4",
                            fc=NAVY, ec="none", zorder=3))
ax.text(LM + 2.4, (by0 + by1) / 2, "Признаки сопоставления", ha="left", va="center",
        fontsize=7.2, color=NAVY, fontweight="bold")
ax.text(LM + 22.5, (by0 + by1) / 2,
        "объект регулирования · участники и полномочия · этапы работ · "
        "критерии готовности · контрольные точки · порядок учета изменений",
        ha="left", va="center", fontsize=6.9, color=SUB)

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s4_norm.png", dpi=660, facecolor="white")
print("ok")

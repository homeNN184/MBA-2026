# -*- coding: utf-8 -*-
"""Рисунок 23 для слайда: стадии принятия решения об интеграции, палитра презентации."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
FILL, SOFT = "#EAF2FA", "#F4F8FC"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 11.0, 5.3
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=600)
ax.set_xlim(0, 100); ax.set_ylim(0, 100 * H_IN / W_IN); ax.axis("off")

U = 100.0 / W_IN          # единиц на дюйм
PAD = 1.9


def fit(text, width, base=7.4, lo=4.6):
    n = max(len(s) for s in text.split("\n"))
    fs = base
    while fs > lo and n * 0.70 * fs / 72.0 * U > width - 2 * PAD:
        fs -= 0.1
    return fs


stages = [
    ("1. Замысел", "КЦП", "Расчет\nпо прогнозным данным",
     "Предварительное решение\nоб интеграции"),
    ("2. Начало\nразработки", "Заявка на НИОКР,\nтехническое задание,\nпрограмма внедрения", "—",
     "Разработка адресно\nпод объект (КТ-0)"),
    ("3. Предынвестиционная\nстадия", "Программа\nпредынвестиционных\nисследований,\nпредпроектная\nдокументация",
     "Расчет по уточненным\nданным, правило выбора", "Решение об интеграции\nи об уровне входа"),
    ("4. Активная фаза", "Инвестиционная\nпрограмма,\nКТ-1 – КТ-5",
     "Пересчет в контрольных\nточках", "Запуск стадий\nстроительства"),
    ("5. Ввод и оценка", "Акты ввода,\nотчет о внедрении", "Уточнение\nпараметров",
     "Параметры\nдля следующих\nпроектов"),
]
xs = [14, 31, 48, 65, 82]
w, h = 16, 8.5
ROWS = [("Стадия", 38.0), ("Документы", 28.0), ("Модель", 18.0), ("Решение", 8.0)]
STY = [(NAVY, "white", NAVY), (FILL, NAVY, INN), (SOFT, NAVY, SUB), ("#FFFFFF", NAVY, NAVY)]

for lab, y in ROWS:
    ax.text(12.0, y + h / 2, lab, fontsize=8.0, fontweight="bold", color=NAVY,
            ha="right", va="center")
for i, texts in enumerate(stages):
    x = xs[i]
    for j, txt in enumerate(texts):
        y = ROWS[j][1]
        fc, tc, ec = STY[j]
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=0.7",
                                    fc=fc, ec=ec, lw=0.9))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center",
                fontsize=fit(txt, w), color=tc, linespacing=1.3)
    if i < 4:
        ax.add_patch(FancyArrowPatch((x + w + 0.3, ROWS[0][1] + h / 2),
                                     (xs[i + 1] - 0.3, ROWS[0][1] + h / 2),
                                     arrowstyle="-|>", mutation_scale=10, color=NAVY, lw=1.1))

ax.plot([14, 98], [2.6, 2.6], color=NAVY, lw=1.2)
for x, t in ((14, "TRL1"), (39, "TRL4"), (56, "TRL5–TRL7"), (73, "TRL8"), (90, "TRL9")):
    ax.plot([x], [2.6], marker="D", color=NAVY, ms=4)
    ax.text(x, 0.6, t, ha="center", fontsize=7.2, color=SUB)
ax.text(12.0, 2.6, "TRL", fontsize=8.0, fontweight="bold", color=NAVY, ha="right", va="center")
ax.annotate("", xy=(39, 7.2), xytext=(39, 3.3),
            arrowprops=dict(arrowstyle="-|>", color=TRN, lw=1.1))
ax.text(38.3, 5.6, "инициирование стадии 3", fontsize=7.0, color=TRN, ha="right", va="center")
ax.annotate("", xy=(56, 7.2), xytext=(56, 3.3),
            arrowprops=dict(arrowstyle="-|>", color=TRN, lw=1.1))
ax.text(57.3, 5.6, "вход в проектирование", fontsize=7.0, color=TRN, ha="left", va="center")

fig.savefig("/home/claude/work/fig/s17_src.png", bbox_inches="tight", facecolor="white")
print("ok")

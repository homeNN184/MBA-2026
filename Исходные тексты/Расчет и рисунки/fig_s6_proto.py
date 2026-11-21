# -*- coding: utf-8 -*-
"""Слайд 6. Прототип реализации механизма: почему выбран метрологический центр."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import matplotlib.image as mpimg
import icons_lib as I

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
PURPLE, FILL = "#8E44AD", "#EAF2FA"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")

# ---------------- фотография объекта
img = mpimg.imread("/home/claude/work/fig/ch2s/f01.jpg")
ih, iw = img.shape[0], img.shape[1]
PX0, PX1 = 2.0, 43.0
PY1 = YM - 0.9
PY0 = 7.4                      # низ совпадает с низом правого блока
pw, ph = PX1 - PX0, PY1 - PY0
need = int(round(ih * pw / ph))   # кадрирование по центру под нужную пропорцию
if need < iw:
    x0 = (iw - need) // 2
    img = img[:, x0:x0 + need]
else:
    need_h = int(round(iw * ph / pw))
    y0 = (ih - need_h) // 2
    img = img[y0:y0 + need_h, :]
ax.imshow(img, extent=(PX0, PX1, PY0, PY1), zorder=3, aspect="auto")
ax.add_patch(Rectangle((PX0, PY0), pw, ph, fc="none", ec="#D6E3F0", lw=1.0, zorder=5))
ax.add_patch(Rectangle((PX0, PY0), pw, 3.1, fc=NAVY, ec="none", alpha=0.72, zorder=4))
ax.text(PX0 + 1.6, PY0 + 1.55, "Третий пусковой комплекс, строительная площадка",
        ha="left", va="center", fontsize=7.0, color="#FFFFFF", zorder=6)

# ---------------- признаки выбора
CX0, CX1 = 46.0, 98.0
CY0, CY1 = 7.4, YM - 0.9
ax.add_patch(FancyBboxPatch((CX0, CY0), CX1 - CX0, CY1 - CY0,
                            boxstyle="round,pad=0,rounding_size=0.9",
                            fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
ax.add_patch(FancyBboxPatch((CX0, CY1 - 0.75), CX1 - CX0, 0.75,
                            boxstyle="round,pad=0,rounding_size=0.35",
                            fc=NAVY, ec="none", zorder=3))
cx, cy = CX0 + 3.9, CY1 - 3.9
ax.add_patch(Circle((cx, cy), 2.3, fc="none", ec=NAVY, lw=1.3, zorder=4))
I.search(ax, cx, cy, 2.3, NAVY, 1.4)
ax.text(CX0 + 7.6, cy, "Почему выбран этот проект", ha="left", va="center",
        fontsize=8.0, color=NAVY, fontweight="bold")

ITEMS = [
    (NAVY, "Дорожная карта 2019 года, подписанная Министром промышленности\n"
           "и торговли Российской Федерации Д.В. Мантуровым и Председателем\n"
           "Правления ПАО «Газпром» А.Б. Миллером"),
    (INV, "Системообразующий проект: крупный технологически\n"
          "неразделяемый объект, впервые применяемые решения"),
    (INN, "Основное технологическое оборудование разрабатывалось\n"
          "одновременно с проектированием и строительством"),
    (TRN, "Характеристики оборудования служили исходными данными\n"
          "для строительных решений и уточнялись по ходу разработки"),
    (PURPLE, "Требования к установке соответствуют уровню зарубежных\n"
             "центров, по расходу превышают наибольший из них"),
]
y = CY1 - 8.6
for col, it in ITEMS:
    n = it.count("\n") + 1
    ax.add_patch(Circle((CX0 + 2.6, y - 0.55), 0.42, fc=col, ec="none", zorder=5))
    ax.text(CX0 + 4.4, y, it, ha="left", va="top",
            fontsize=7.0, color=SUB, linespacing=1.45)
    y -= n * 1.52 + 1.7

# ---------------- показатели
by0, by1 = 0.3, 5.6
ax.add_patch(FancyBboxPatch((2.0, by0), 96.0, by1 - by0,
                            boxstyle="round,pad=0,rounding_size=0.9",
                            fc=FILL, ec="none", zorder=2))
STATS = [("DN 50–700", "номинальные диаметры\nповеряемых счетчиков газа", NAVY),
         ("0,1–10 МПа", "диапазон рабочего\nдавления", INN),
         ("5–40 000 м³/ч", "диапазон расхода\nприродного газа", INV),
         ("0,16 %", "расширенная\nнеопределенность, не более", TRN)]
w4 = 96.0 / 4
for k, (big, cap, col) in enumerate(STATS):
    xc = 2.0 + w4 * (k + 0.5)
    ax.text(xc, by1 - 1.7, big, ha="center", va="center",
            fontsize=10.2, color=col, fontweight="bold")
    ax.text(xc, by1 - 3.7, cap, ha="center", va="center",
            fontsize=6.6, color=SUB, linespacing=1.4)
    if k:
        ax.plot([2.0 + w4 * k, 2.0 + w4 * k], [by0 + 0.8, by1 - 0.8],
                color="#C9D8E8", lw=0.9, zorder=3)

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s6_proto.png", dpi=660, facecolor="white")
print("ok, фото", iw, "x", ih, "высота на схеме", round(ph, 1))

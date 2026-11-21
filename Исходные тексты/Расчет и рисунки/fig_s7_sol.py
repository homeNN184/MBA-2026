# -*- coding: utf-8 -*-
"""Слайд 7. Реализованные инновационные решения."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch
import matplotlib.image as mpimg
import icons_lib as I

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
PURPLE, FILL = "#8E44AD", "#EAF2FA"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, YM * 0 + 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")


def photo(path, x0, x1, y0, y1, fx=(0.0, 1.0), fy=(0.0, 1.0)):
    """Вставка фотографии с кадрированием под заданную область."""
    img = mpimg.imread(path)
    ih, iw = img.shape[0], img.shape[1]
    img = img[int(ih * fy[0]):int(ih * fy[1]), int(iw * fx[0]):int(iw * fx[1])]
    ih, iw = img.shape[0], img.shape[1]
    w, h = x1 - x0, y1 - y0
    need = int(round(ih * w / h))
    if need < iw:
        a = (iw - need) // 2
        img = img[:, a:a + need]
    else:
        nh = int(round(iw * h / w))
        a = (ih - nh) // 2
        img = img[a:a + nh, :]
    ax.imshow(img, extent=(x0, x1, y0, y1), zorder=3, aspect="auto")
    ax.add_patch(Rectangle((x0, y0), w, h, fc="none", ec="#D6E3F0", lw=0.9, zorder=5))


CARDS = [
    (INN, "/home/claude/work/fig/ch2s/f04.jpg", (0.0, 1.0), (0.0, 1.0),
     "Двухконтурная замкнутая схема",
     "Малый и большой кольцевые контуры\nработают независимо, циркуляция газа\n"
     "создается внутри установки\nРежимы поверки не зависят от режима\n"
     "магистрального газопровода\nПри замене счетчика около 99 % газа\n"
     "откачивается в буферную емкость"),
    (TRN, "/home/claude/work/fig/ch2s/f10.jpg", (0.5, 1.0), (0.0, 0.93),
     "Нестандартные соединительные\nдетали",
     "Детали DN 100–700 на давление 10 МПа:\nпереходы, раструбы, повороты\n"
     "Геометрия выбрана по результатам\nчисленного моделирования течения газа\n"
     "Разработаны технические условия,\nпродукция внесена в каталог\n«Продукция России»"),
    (INV, "/home/claude/work/fig/ch2s/f12.jpg", (0.01, 0.485), (0.0, 0.935),
     "Промышленные вентиляторы\nвысокого давления",
     "Пять агрегатов мощностью 1250 и 500 кВт\nЭлектродвигатель размещен в герметичном\n"
     "корпусе и работает в среде природного газа\nРабочее колесо установлено на валу ротора,\n"
     "уплотнение вала не требуется, попадание\nмасла в трубопроводы исключено"),
]

LM, GAP = 2.0, 1.8
CW = (100 - 2 * LM - 2 * GAP) / 3.0
CY0, CY1 = 7.4, YM - 0.9
PH = 16.4                                  # высота фотографии

for k, (col, path, fx, fy, head, body) in enumerate(CARDS):
    x0 = LM + k * (CW + GAP)
    ax.add_patch(FancyBboxPatch((x0, CY0), CW, CY1 - CY0,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
    photo(path, x0, x0 + CW, CY1 - PH, CY1, fx, fy)
    ax.add_patch(Rectangle((x0, CY1 - PH - 0.7), CW, 0.7, fc=col, ec="none", zorder=4))
    ax.text(x0 + 1.6, CY1 - PH - 2.3, head, ha="left", va="top",
            fontsize=7.4, color=NAVY, fontweight="bold", linespacing=1.3)
    ax.text(x0 + 1.6, CY1 - PH - 6.5, body, ha="left", va="top",
            fontsize=6.6, color=SUB, linespacing=1.46)

# ---------------- цепочка зависимости
by0, by1 = 0.3, 6.1
ax.add_patch(FancyBboxPatch((LM, by0), 100 - 2 * LM, by1 - by0,
                            boxstyle="round,pad=0,rounding_size=0.9",
                            fc=FILL, ec="none", zorder=2))
CH = ["Расчетная\nмодель", "Конструкция\nтрубопроводов", "Нестандартные\nдетали",
      "Параметры\nПВВД", "Исходные данные\nдля рабочей\nдокументации"]
n = len(CH)
x_start, x_end = LM + 8.5, 100 - LM - 9.0
step = (x_end - x_start) / (n - 1)
for i, c in enumerate(CH):
    xc = x_start + i * step
    ax.text(xc, (by0 + by1) / 2, c, ha="center", va="center",
            fontsize=6.8, color=NAVY if i == n - 1 else SUB,
            fontweight="bold" if i == n - 1 else "normal", linespacing=1.4)
    if i:
        ax.add_patch(FancyArrowPatch((xc - step + 7.6, (by0 + by1) / 2),
                                     (xc - 7.6, (by0 + by1) / 2),
                                     arrowstyle="-|>", mutation_scale=9,
                                     color=TRN, lw=1.3, zorder=5))

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s7_sol.png", dpi=660, facecolor="white")
print("ok")

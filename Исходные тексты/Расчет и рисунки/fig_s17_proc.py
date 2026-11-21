# -*- coding: utf-8 -*-
"""Слайд 17. Процесс принятия решения об интеграции."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import matplotlib.image as mpimg
import numpy as np
import icons_lib as I

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
PURPLE, FILL = "#8E44AD", "#EAF2FA"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")

LM = 2.0
TOP = YM - 0.9
BY0, BY1 = 1.0, 9.6
PY0 = BY1 + 1.8

# ---------------- рисунок 23
img = mpimg.imread("/home/claude/work/fig/s17_src.png")
if img.ndim == 3 and img.shape[2] == 4:
    img = img[:, :, :3]
g = img if img.max() > 1.5 else img * 255.0
mask = (g.mean(axis=2) < 248)
rows = np.where(mask.any(axis=1))[0]
cols = np.where(mask.any(axis=0))[0]
img = img[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]
ih, iw = img.shape[0], img.shape[1]
PH = TOP - PY0
PW = PH * iw / ih
ax.imshow(img, extent=(LM, LM + PW, PY0, TOP), zorder=3, aspect="auto")

# ---------------- условия и ограничения
CX0, CX1 = LM + PW + 2.2, 98.0
ax.add_patch(FancyBboxPatch((CX0, PY0), CX1 - CX0, TOP - PY0,
                            boxstyle="round,pad=0,rounding_size=0.9",
                            fc="#FFFFFF", ec="#D6E3F0", lw=1.0, zorder=2))
ax.add_patch(FancyBboxPatch((CX0, TOP - 0.75), CX1 - CX0, 0.75,
                            boxstyle="round,pad=0,rounding_size=0.35",
                            fc=NAVY, ec="none", zorder=3))
cx, cy = CX0 + 3.4, TOP - 3.4
ax.add_patch(Circle((cx, cy), 2.0, fc="none", ec=NAVY, lw=1.2, zorder=4))
I.check(ax, cx, cy, 2.0, NAVY, 1.4)
ax.text(CX0 + 6.4, cy, "Условия и ограничения", ha="left", va="center",
        fontsize=7.4, color=NAVY, fontweight="bold")

ITEMS = [
    (INV, "Сведения об уровне готовности и контрольных\nточках включаются в целевую программу\nи обоснование инвестиций"),
    (INV, "Объект строительства указывается в программе\nвнедрения, контрольные точки входят\nв ее план-график"),
    (INV, "Передача исходных данных к каждой точке\nзакрепляется в техническом задании"),
    (TRN, "Параметры модели нормированы\nи уточняются данными проекта"),
    (TRN, "Порядок предлагается для одного\nпилотного проекта"),
    (TRN, "Порядок применяется решением\nфункционального заказчика"),
]
y = TOP - 7.0
for col, it in ITEMS:
    ax.add_patch(Circle((CX0 + 2.4, y - 0.45), 0.34, fc=col, ec="none", zorder=5))
    ax.text(CX0 + 3.9, y, it, ha="left", va="top",
            fontsize=5.9, color=SUB, linespacing=1.32)
    y -= (it.count("\n") + 1) * 1.24 + 1.0

# ---------------- защитное свойство
ax.add_patch(FancyBboxPatch((LM, BY0), 100 - 2 * LM, BY1 - BY0,
                            boxstyle="round,pad=0,rounding_size=0.9",
                            fc=FILL, ec="none", zorder=2))
ax.add_patch(FancyBboxPatch((LM, BY0), 0.9, BY1 - BY0,
                            boxstyle="round,pad=0,rounding_size=0.4",
                            fc=TRN, ec="none", zorder=3))
ax.text(LM + 2.6, BY1 - 2.2, "Защитное свойство процесса", ha="left", va="center",
        fontsize=7.2, color=NAVY, fontweight="bold")
ax.text(LM + 2.6, BY1 - 5.2,
        "до начала проектирования расчет выполняется дважды: на стадии замысла по прогнозным данным и на предынвестиционной "
        "стадии по уточненным.\nЕсли уточненный расчет не подтверждает преимущество интеграции, проект возвращается "
        "к последовательной организации работ без потерь.\nПосле входа модель пересчитывается в контрольных точках "
        "и служит уже не выбору сценария, а оценке последствий изменений",
        ha="left", va="center", fontsize=6.6, color=SUB, linespacing=1.5)

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s17_proc.png", dpi=660, facecolor="white")
print("ok, рисунок", round(PW, 1), "x", round(PH, 1))

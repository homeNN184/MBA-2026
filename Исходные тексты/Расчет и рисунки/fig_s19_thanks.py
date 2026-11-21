# -*- coding: utf-8 -*-
"""Слайд 19. Завершение доклада."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import icons_lib as I

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
FILL = "#EAF2FA"
plt.rcParams["font.family"] = "DejaVu Sans"
W_IN, H_IN = 9.3, 4.0
fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=660)
YM = 100 * H_IN / W_IN
ax.set_xlim(0, 100); ax.set_ylim(0, YM); ax.axis("off")
ax.set_aspect("equal")

LM = 2.0
TOP = YM - 0.9

# тема работы
ax.add_patch(FancyBboxPatch((LM, 20.0), 96.0, 18.0,
                            boxstyle="round,pad=0,rounding_size=1.0",
                            fc=FILL, ec="none", zorder=2))
ax.add_patch(FancyBboxPatch((LM, 20.0), 1.0, 18.0,
                            boxstyle="round,pad=0,rounding_size=0.45",
                            fc=NAVY, ec="none", zorder=3))
I.target(ax, 9.0, 29.0, 7.0, NAVY, 1.8)
ax.text(15.5, 32.6, "Тема дипломного проекта", ha="left", va="center",
        fontsize=7.6, color=NAVY, fontweight="bold")
ax.text(15.5, 27.6,
        "Разработка модели управления инновационной деятельностью\n"
        "при реализации инвестиционных проектов",
        ha="left", va="center", fontsize=8.4, color=SUB, linespacing=1.6)

# слушатель
ax.text(LM + 2.6, 14.0, "Постаутов Константин Владимирович", ha="left", va="center",
        fontsize=8.6, color=NAVY, fontweight="bold")
ax.text(LM + 2.6, 10.0,
        "заместитель главного инженера по автоматизации\nи метрологическому обеспечению "
        "ООО «Газпром трансгаз Екатеринбург»",
        ha="left", va="center", fontsize=7.4, color=SUB, linespacing=1.55)

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("/home/claude/work/fig/s19_thanks.png", dpi=660, facecolor="white")
print("ok")

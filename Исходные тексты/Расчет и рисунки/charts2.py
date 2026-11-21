# -*- coding: utf-8 -*-
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
R = json.load(open("results.json"))
plt.rcParams.update({"font.family": "Liberation Serif", "font.size": 8})
OUT = "../fig/"
BL, OR, GR, GY = "#0079C2", "#C4690E", "#1B9E77", "#3C4F66"

def box(ax, cx, y, w, h, t, fc="#eaf1fb", ec=BL, fs=6.6, bold=False):
    ax.add_patch(FancyBboxPatch((cx - w / 2, y), w, h, boxstyle="round,pad=0.25,rounding_size=0.8", fc=fc, ec=ec, lw=0.9))
    ax.text(cx, y + h / 2, t, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", linespacing=1.15)

def arrow(ax, p, q, col=GY, ls="-", lw=1.0, style="-|>", ms=7):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=ms, color=col, lw=lw, ls=ls, shrinkA=0, shrinkB=0))

# ---------- Рисунок 3.1: два процесса и их интеграция
fig, ax = plt.subplots(figsize=(6.5, 5.0)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 78)
ax.text(1, 76, "Инновационный процесс: уровни готовности технологии (TRL)", fontsize=7.6, fontweight="bold", color=BL, va="center")
top = ["Задание на\nразработку\nпродукта", "TRL1\nпринципы", "TRL2\nконцепция", "TRL3\nподтвержд.\nконцепции", "TRL4\nкомпоненты\nв лаборатории", "TRL5\nкомпоненты в\nсоотв. среде", "TRL6\nпрототип в\nсоотв. среде", "TRL7\nобразец в\nэксплуат. среде", "TRL8\nсистема\nквалифицир.", "TRL9\nподтверждена\nэксплуатацией"]
cxt = [5.2 + i * 9.9 for i in range(10)]
for i, t in enumerate(top):
    box(ax, cxt[i], 56, 8.6, 14, t, fc="#fff3e8" if i == 0 else "#eaf1fb", ec=OR if i == 0 else BL, fs=5.7)
    if i < 9: arrow(ax, (cxt[i] + 4.55, 63), (cxt[i + 1] - 4.55, 63), BL, lw=0.9)
ax.text(1, 12.6, "Инвестиционный строительный процесс: стадии создания инвестиционного объекта строительства", fontsize=7.6, fontweight="bold", color=GR, va="center")
bot = ["Замысел и\nтехнические\nтребования", "Задание на\nпроектирование", "Проектная\nдокументация,\nэкспертиза", "Рабочая\nдокументация", "Поставка\nМТР", "Строительно-\nмонтажные\nработы", "ПНР\nбез нагрузки", "ПНР\nпод нагрузкой", "Комплексное\nопробование,\nввод"]
cxb = [6.1 + j * 11.0 for j in range(9)]
for j, t in enumerate(bot):
    box(ax, cxb[j], 15, 10.0, 14, t, fc="#e7f6ef", ec=GR, fs=5.7)
    if j < 8: arrow(ax, (cxb[j] + 5.15, 22), (cxb[j + 1] - 5.15, 22), GR, lw=0.9)
# связи (контрольные точки)
links = [(0, 0, "КТ-0", "", "u"), (5, 2, "КТ-1", "", "d"), (6, 2, "КТ-2", "", "d"), (7, 2, "КТ-3", "", "d"), (6, 3, "КТ-2", "", "u"), (7, 5, "КТ-3", "", "u"), (8, 6, "КТ-4", "", "u"), (9, 8, "КТ-5", "", "u")]
for ti, bj, lab, txt, dr in links:
    xt, xb = cxt[ti], cxb[bj]
    if dr == "d":   # решение о запуске стадии принимается по подтвержденному уровню: сверху вниз
        arrow(ax, (xt, 56), (xb, 29.2), OR, lw=2.2, ms=24)
        # метка
    else:           # результаты испытаний на объекте: снизу вверх
        arrow(ax, (xb, 29.2), (xt, 56), OR if ti == 0 else "#8E44AD", lw=2.2, ms=24)
    fr = 0.30 if dr == "d" else 0.25
    xm = xt + (xb - xt) * fr if dr == "d" else xb + (xt - xb) * fr
    ym = 56 - 26.8 * fr if dr == "d" else 29.2 + 26.8 * fr
    ax.text(xm, ym, lab, fontsize=6.4, fontweight="bold", color=OR if (dr == "d" or ti == 0) else "#8E44AD", ha="center", va="center", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
ax.text(1, 10.4, "оранжевые стрелки: КТ-0 — задание на разработку; КТ-1…КТ-3 — вход (начало ПД)", fontsize=6.4, color=OR, va="center")
ax.text(1, 8.6, "по подтверждению TRL5, TRL6 или TRL7 в зависимости от сценария", fontsize=6.4, color=OR, va="center")
ax.text(1, 6.8, "фиолетовые стрелки: подтверждение уровня по окончании стадии (РД, СМР, ПНР, КО)", fontsize=6.4, color="#8E44AD", va="center")
box(ax, 50, 0.4, 96, 5.2, "Совет по изменениям: реестр изменений, базовая линия конфигурации; расчетная модель оценки эффекта и рисков в каждой контрольной точке", fc="#f3f2ee", ec=GY, fs=6.4)
plt.close(fig)   # рисунок механизма строится скриптом fig_mech_work.py (ортогональная разводка)

# ---------- Рисунок 3.2: дорожная карта интеграции (точка входа TRL5–ПД)
sc = R["scn"]["TRL5"]["sch"]
fig, ax = plt.subplots(figsize=(6.5, 3.9))
ax.set_xlim(0, 6.9); ax.set_ylim(0, 21); ax.set_yticks([]); ax.grid(False)
for sp in ("left", "top", "right"): ax.spines[sp].set_visible(False)
ax.set_xlabel("Время от начала разработки инновационного продукта, лет", fontsize=7)
ax.tick_params(labelsize=7)
names = ["TRL1→2", "TRL2→3", "TRL3→4", "TRL4→5", "TRL5→6", "TRL6→7", "TRL7→8", "TRL8→9"]
cols = ["#cfe0f7"] * 4 + ["#9dc2ef"] * 2 + ["#e0cdfa"] * 2
y0 = 15
for k in range(8):
    a_, b_ = sc["trl_start"][k], sc["conf"][k]
    ax.add_patch(Rectangle((a_, y0), b_ - a_, 3.2, fc=cols[k], ec="white", lw=0.8))
    narrow = b_ - a_ < 0.45
    ax.text((a_ + b_) / 2, y0 + 1.6, names[k][3:] if narrow else names[k], ha="center", va="center", fontsize=5.4 if narrow else 6.2, rotation=90 if narrow else 0)
g0, g1 = sc["conf"][4], sc["trl_start"][5]
ax.add_patch(Rectangle((g0, y0 + 0.2), g1 - g0, 2.8, fc="#f1f1f1", ec="none"))
ax.text(0.02, 19.4, "серый интервал — изготовление и поставка оборудования", fontsize=6.4, va="center", color=GY)
ax.text(-0.05, y0 + 1.6, "Инновационный\nпроцесс", ha="right", va="center", fontsize=7, color=BL, fontweight="bold")
stg = ["Задание", "ПД", "РД", "Поставка\nМТР", "Строительно-монтажные работы", "ПНР", "ПНР под\nнагрузкой", "КО"]
fc2 = ["#d9efe5", "#9fd8bf", "#9fd8bf", "#d9efe5", "#7cc8a8", "#d9efe5", "#c1e6d5", "#d9efe5"]
for k in range(8):
    a_, b_ = sc["st"][k], sc["en"][k]
    ax.add_patch(Rectangle((a_, 8.2), b_ - a_, 3.2, fc=fc2[k], ec="white", lw=0.8))
    if b_ - a_ > 0.3: ax.text((a_ + b_) / 2, 9.8, stg[k], ha="center", va="center", fontsize=5.6 if b_ - a_ < 0.8 else 6.6)
    else: ax.text((a_ + b_) / 2, 9.8, stg[k], ha="center", va="center", fontsize=5.4, rotation=90)
ax.text(-0.05, 9.8, "Инвестиционный\nпроцесс", ha="right", va="center", fontsize=7, color=GR, fontweight="bold")
kt = [(sc["conf"][3], "КТ-1: TRL5 подтвержден,\nначало проектной документации", OR, 5.2),
      (sc["conf"][4], "КТ-2: TRL6 подтвержден,\nзавершена РД", OR, 2.2),
      (sc["conf"][5], "КТ-3: СМР завершены,\nTRL7 подтвержден", "#8E44AD", 5.2),
      (sc["conf"][6], "КТ-4: ПНР завершены,\nTRL8 подтвержден", "#8E44AD", 2.2),
      (sc["conf"][7], "КТ-5: КО завершено,\nTRL9 подтвержден", "#8E44AD", 5.2)]
for x, lab, col, yy in kt:
    ax.plot([x, x], [yy + 1.6, 18.2], color=col, lw=1.1, ls="--")
    ax.plot([x], [18.4], marker="v", ms=6, color=col)
    ax.text(min(x, 6.05) if x > 5.5 else x, yy, lab, ha="center", va="center", fontsize=6.0, color=col, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=col, lw=0.6))
ax.text(0.02, 20.3, "КТ-0: задание на разработку формируется по результатам планирования на уровне замысла", fontsize=6.4, va="center", color=OR)
fig.tight_layout(pad=0.3); fig.savefig(OUT + "f310_roadmap.png", dpi=660, bbox_inches="tight", facecolor="white"); plt.close(fig)
print("ok")

# ---------- Новые рисунки: область предпочтения TRL5/TRL6 и риск (Монте-Карло, торнадо)
import numpy as np
S1 = json.load(open("stage1.json")); X = S1["thr56_X"]
fig, ax = plt.subplots(figsize=(6.5, 3.2))
L_ = np.linspace(0.5, 160, 600); pc = np.minimum(1.0, X["X"] / L_)
ax.fill_between(L_, 0, pc, color="#cfe0f7", alpha=0.9, label="TRL5 лучше TRL6")
ax.fill_between(L_, pc, 1.0, color="#fbe3d6", alpha=0.9, label="TRL6 лучше TRL5")
ax.plot(L_, pc, color=GY, lw=1.2)
p6 = S1["events"]["TRL5"]["6"][0]
ax.plot([X["L6"]], [p6], marker="o", ms=6, color=OR, zorder=5)
ax.annotate(("расчетная точка\n(%.1f млн руб.; %.2f)" % (X["L6"], p6)).replace(".", ","), (X["L6"], p6), xytext=(X["L6"] + 12, p6 - 0.085), fontsize=6.6, arrowprops=dict(arrowstyle="-", color=OR, lw=0.7))
ax.text(105, X["X"] / 105 + 0.04, ("p × L = %.1f млн руб." % X["X"]).replace(".", ","), fontsize=6.6, color=GY)
ax.set_xlim(0, 160); ax.set_ylim(0, 0.6)
ax.set_xlabel("Ущерб от события TRL6 при входе на TRL5 (потеря ЧДД), млн руб.", fontsize=7); ax.set_ylabel("Вероятность события TRL6", fontsize=7)
ax.tick_params(labelsize=7); ax.legend(fontsize=6.6, loc="upper right", frameon=False); ax.grid(alpha=0.25)
fig.tight_layout(pad=0.4); fig.savefig(OUT + "f38_threshold.png", dpi=660, bbox_inches="tight", facecolor="white"); plt.close(fig)

fig, axs = plt.subplots(1, 2, figsize=(6.5, 3.0), gridspec_kw=dict(width_ratios=[1, 1.25]))
ax = axs[0]; mc = S1["mc"]; labs = ["Базовый", "TRL7", "TRL6", "TRL5"]; cl = ["#3C4F66", "#C4690E", "#0079C2", "#1B9E77"]
for i, s in enumerate(["BASE", "TRL7", "TRL6", "TRL5"]):
    m = mc[s]; ax.plot([i, i], [m["p10"], m["p90"]], color=cl[i], lw=3.2, solid_capstyle="round"); ax.plot([i], [m["p50"]], marker="o", ms=5, color="white", mec=cl[i], mew=1.4, zorder=5)
ax.axhline(0, color=GY, lw=0.7); ax.set_xticks(range(4)); ax.set_xticklabels(labs, fontsize=6.8); ax.tick_params(labelsize=7)
ax.set_ylabel("ЧДД, млн руб. (P10–P90, точка — P50)", fontsize=6.8); ax.grid(alpha=0.25, axis="y"); ax.set_title("а", fontsize=7.5, loc="left")
ax = axs[1]; T = S1["mc"]["tornado"]; T = sorted([t for t in T if abs(t["hi"]["d56"] - t["lo"]["d56"]) > 0.05], key=lambda t: -abs(t["hi"]["d56"] - t["lo"]["d56"]))
for i, t in enumerate(T):
    lo, hi = t["lo"]["d56"], t["hi"]["d56"]
    ax.barh(i, hi - lo, left=lo, color=BL, height=0.55)
ax.axvline(0, color=GY, lw=0.8); ax.set_yticks(range(len(T))); ax.set_yticklabels([t["name"] for t in T], fontsize=6.0); ax.invert_yaxis()
ax.set_xlabel("ЧДД TRL5 − ЧДД TRL6, млн руб.", fontsize=6.8); ax.tick_params(labelsize=6.5); ax.grid(alpha=0.25, axis="x"); ax.set_title("б", fontsize=7.5, loc="left")
fig.tight_layout(pad=0.4); fig.savefig(OUT + "f39_risk.png", dpi=660, bbox_inches="tight", facecolor="white"); plt.close(fig)
print("ok2")

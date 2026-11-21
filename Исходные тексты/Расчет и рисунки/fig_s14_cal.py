# -*- coding: utf-8 -*-
"""Слайд 14. Календарный план четырех сценариев в палитре презентации."""
import sys
sys.path.insert(0, "/home/claude/work/model")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle as Rc
from model import P, schedule

NAVY, INN, INV, TRN, SUB = "#003366", "#0079C2", "#1B9E77", "#C4690E", "#3C4F66"
PURPLE = "#8E44AD"
plt.rcParams["font.family"] = "DejaVu Sans"

ST = ["ИД", "ПД", "РД", "МТР", "СМР", "ПНР хх", "ПНР нагр.", "КО"]
TRL_C = ["#CFE4F5", "#B9D7EF", "#A2CAE9", "#7FB6DF", "#4C98CF", "#2080BE", "#0067A3", "#00538A"]
ST_C = ["#DCF1E9", "#C2E7DA", "#A9DDC9", "#7FCDB2", "#4FBA96", "#2AA87F", "#17906A", "#0F7556"]
INF_C = ["#F2DFC2", "#DFC18A"]
TTL = {"BASE": "Базовый: разработка TRL1–TRL9 на опытной инфраструктуре, затем строительство",
       "TRL7": "Интеграция TRL7: вход после подтверждения TRL7 на опытной инфраструктуре",
       "TRL6": "Интеграция TRL6: вход после подтверждения TRL6, TRL7 — к концу СМР",
       "TRL5": "Интеграция TRL5: вход после TRL5, TRL6 — к концу РД, TRL7 — к концу СМР"}
S4 = ["BASE", "TRL7", "TRL6", "TRL5"]

p = P()
fig, axs = plt.subplots(4, 1, figsize=(9.3, 4.0), sharex=True, dpi=660,
                        gridspec_kw=dict(height_ratios=[1.42, 1.42, 1, 1], hspace=0.62))
for ax, s_ in zip(axs, S4):
    sch = schedule(s_, p)
    has = s_ in ("BASE", "TRL7")
    yp, yc, yd = (.1, 1.2, 2.5) if has else (None, .1, 1.4)
    top = 3.7 if has else 2.6
    if has:
        end_t = 3.0 if s_ == "BASE" else sch["conf"][5]
        for i, (a, b, l) in enumerate(((sch["trl_start"][4], sch["conf"][4], "созд."),
                                       (sch["conf"][4], end_t, "испытания"))):
            ax.add_patch(Rc((a, yp), b - a, .7, fc=INF_C[i], ec="white", lw=.8))
            if b - a > .35:
                ax.text((a + b) / 2, yp + .35, l, ha="center", va="center",
                        fontsize=5.2 if b - a < .9 else 5.8, color="#5A4714")
    for j in range(8):
        a, b = sch["trl_start"][j], sch["conf"][j]
        k = j + 2
        ax.add_patch(Rc((a, yd), b - a, .7, fc=TRL_C[j], ec="white", lw=.8))
        if b - a > .33:
            ax.text((a + b) / 2, yd + .35, "TRL%d" % k, ha="center", va="center",
                    fontsize=5.4, color="white" if j >= 4 else NAVY)
        ax.plot([b], [yd + .7], marker="D", ms=2.2, color=NAVY, zorder=5)
    ext = {"TRL7": (5, sch["conf"][5], sch["st"][5]),
           "TRL6": (4, sch["conf"][4], sch["st"][4]),
           "TRL5": (4, sch["conf"][4], sch["st"][4])}.get(s_)
    if ext:
        k, a, b = ext
        ax.add_patch(Rc((a, yd), b - a, .7, fc=TRL_C[k], alpha=.3, ec=TRL_C[k], lw=1.0,
                        ls="-.", hatch="//"))
    for i_, (a, b) in enumerate(zip(sch["st"], sch["en"])):
        ax.add_patch(Rc((a, yc), b - a, .7, fc=ST_C[i_], ec="white", lw=.8))
        if b - a > .33:
            ax.text((a + b) / 2, yc + .35, ST[i_], ha="center", va="center",
                    fontsize=5.4, color="white" if i_ >= 4 else NAVY)
    tv, ent = sch["tv"], sch["st"][1]
    ax.axvline(tv, color=NAVY, ls="--", lw=.9)
    lab = ("ввод %.2f" % tv).replace(".", ",")
    if tv > 7.4:
        ax.text(tv - .08, top - .05, lab, fontsize=5.8, va="top", ha="right",
                color=NAVY, fontweight="bold")
    else:
        ax.text(tv + .08, top - .05, lab, fontsize=5.8, va="top", ha="left",
                color=NAVY, fontweight="bold")
    ax.axvline(ent, color=TRN, ls=":", lw=1.2)
    if tv > 7 or ent > 3:
        ax.text(ent + .06, top - .05, "вход", fontsize=5.8, color=TRN, va="top", ha="left")
    else:
        ax.text(ent - .06, top - .05, "вход", fontsize=5.8, color=TRN, va="top", ha="right")
    ax.set_ylim(0, top)
    ax.set_yticks([yc + .35, yd + .35] + ([yp + .35] if has else []))
    ax.set_yticklabels(["Строительство", "Разработка"] + (["Опытная\nинфраструктура"] if has else []),
                       fontsize=5.6, color=SUB)
    ax.set_title(TTL[s_], loc="left", fontsize=6.6, fontweight="bold", color=NAVY, pad=2.0)
    ax.set_xlim(0, 8.4)
    ax.set_xticks(range(0, 9))
    ax.tick_params(labelsize=5.8, length=2, width=.7, colors=SUB)
    ax.grid(axis="x", color="#EDF2F7", lw=.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color("#B9C6D6")
axs[-1].set_xlabel("Время от начала разработки, лет", fontsize=6.4, color=SUB, labelpad=1.5)
fig.subplots_adjust(left=0.085, right=0.995, top=0.945, bottom=0.095)
fig.savefig("/home/claude/work/fig/s14_cal.png", dpi=660, facecolor="white")
print("ok")

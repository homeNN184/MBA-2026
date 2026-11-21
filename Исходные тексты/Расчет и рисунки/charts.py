# -*- coding: utf-8 -*-
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
from matplotlib import font_manager as fm
R = json.load(open("results.json"))
plt.rcParams.update({"font.family": "Liberation Serif", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#3C4F66", "axes.linewidth": 0.8, "axes.grid": True, "grid.color": "#e3e2dc", "grid.linewidth": 0.6,
    "axes.axisbelow": True, "legend.frameon": False, "figure.dpi": 100, "savefig.dpi": 660, "text.color": "#0b0b0b",
    "axes.labelcolor": "#0b0b0b", "xtick.color": "#0b0b0b", "ytick.color": "#0b0b0b"})
COL = {"BASE": "#3C4F66", "TRL7": "#C4690E", "TRL6": "#0079C2", "TRL5": "#1B9E77"}
LS = {"BASE": "-", "TRL7": ":", "TRL6": "-.", "TRL5": "--"}
MK = {"BASE": "o", "TRL7": "D", "TRL6": "^", "TRL5": "s"}
NAME = {"BASE": "Базовый", "TRL7": "Интеграция TRL7", "TRL6": "Интеграция TRL6", "TRL5": "Интеграция TRL5"}
S4 = ("BASE", "TRL7", "TRL6", "TRL5"); S3 = ("TRL7", "TRL6", "TRL5")
OUT = "../fig/"
W = 6.3
def save(fig, n):
    fig.savefig(OUT + n, bbox_inches="tight", facecolor="white"); plt.close(fig)

# 3.1 схема механизма контрольных точек
fig, ax = plt.subplots(figsize=(W, 3.9)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 62)
ax.grid(False)
def box(x, y, w, h, t, fc="#eaf1fb", ec="#0079C2", fs=8.2, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=fc, ec=ec, lw=1.0))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", linespacing=1.2)
box(1, 44, 26, 15, "Технологический контур\nуровни TRL 5–9,\nподтверждение\nготовности", fc="#fdeee7", ec="#C4690E")
box(37, 44, 26, 15, "Контрольные точки\nКТ-1 … КТ-4:\nкритерии, полномочия,\nварианты решения", bold=True)
box(73, 44, 26, 15, "Строительный контур\nПД, РД, закупка,\nСМР, наладка,\nввод", fc="#e3f5ee", ec="#1B9E77")
for x0, x1 in ((27.8, 36.2), (72.2, 63.8)):
    ax.add_patch(FancyArrowPatch((x0, 51.5), (x1, 51.5), arrowstyle="<->", mutation_scale=10, lw=1.0, color="#3C4F66"))
box(37, 25, 26, 11, "Совет по изменениям:\nреестр, базовая линия", fc="#f4f3ef", ec="#3C4F66")
ax.add_patch(FancyArrowPatch((50, 43.5), (50, 36.5), arrowstyle="<->", mutation_scale=10, lw=1.0, color="#3C4F66"))
box(1, 3, 30, 13, "Модель оценки (ТЗ 0.82):\nЧДД, преимущество R_s,\nисходы переделок", fc="#f4f3ef", ec="#3C4F66")
box(35, 3, 30, 13, "Меры управления\nрисками М1–М4:\nвладелец, срок, критерий", fc="#f4f3ef", ec="#3C4F66")
box(69, 3, 30, 13, "Обеспечение внедрения:\nсоциально-психологическое,\nпрофессиональное, ресурсное", fc="#f4f3ef", ec="#3C4F66", fs=7.6)
for x in (16, 50, 84):
    ax.add_patch(FancyArrowPatch((x, 16.6), (50, 24.4), arrowstyle="->", mutation_scale=9, lw=0.9, color="#3C4F66"))
plt.close(fig)   # рисунок механизма строится скриптом fig_mech_work.py (ортогональная разводка)

# 3.2 календарь сценариев (единая точка входа — начало ПД)
from matplotlib.patches import Rectangle as Rc
with plt.rc_context({"font.family": "DejaVu Sans"}):
    ST = ["ИД", "ПД", "РД", "МТР", "СМР", "ПНР хх", "ПНР нагр.", "КО"]
    SCc = ["#3C4F66", "#0079C2", "#1B9E77", "#d9a21b", "#3C4F66", "#C4690E", "#c2453d", "#7a3fa0"]
    TCc = {2: "#cfd8e3", 3: "#b7c4d6", 4: "#9fb0c8", 5: "#0079C2", 6: "#1B9E77", 7: "#8E44AD", 8: "#C4690E", 9: "#c2453d"}
    TTL = {"BASE": "1. Базовый: разработка TRL1–TRL9 на опытной инфраструктуре, затем строительство",
           "TRL7": "2. Интеграция TRL7: вход после подтверждения TRL7 на опытной инфраструктуре",
           "TRL6": "3. Интеграция TRL6: вход после подтверждения TRL6; TRL7 — к концу СМР",
           "TRL5": "4. Интеграция TRL5: вход после подтверждения TRL5; TRL6 — к концу РД, TRL7 — к концу СМР"}
    fig, axs = plt.subplots(4, 1, figsize=(8.4, 7.7), sharex=True, gridspec_kw=dict(height_ratios=[1.5, 1.5, 1, 1]))
    for ax, s_ in zip(axs, S4):
        sch = R["scn"][s_]["sch"]; has = s_ in ("BASE", "TRL7")
        yp, yc, yd = (.1, 1.2, 2.5) if has else (None, .1, 1.4)
        top = 3.7 if has else 2.6
        if has:
            end_t = 3.0 if s_ == "BASE" else sch["conf"][5]
            for a, b, l in ((sch["trl_start"][4], sch["conf"][4], "создание"), (sch["conf"][4], end_t, "испытания")):
                ax.add_patch(Rc((a, yp), b - a, .7, fc="#e8d9b0" if "созд" in l else "#d2b86a", ec="white", lw=1))
                ax.text((a + b) / 2, yp + .35, (l if b - a > .6 else ("созд." if "созд" in l else "испыт.")), ha="center", va="center", fontsize=7 if b - a > .6 else 5.8, color="#3b2f10")
        for j in range(8):
            a, b = sch["trl_start"][j], sch["conf"][j]; k = j + 2
            ax.add_patch(Rc((a, yd), b - a, .7, fc=TCc[k], ec="white", lw=1))
            ax.text((a + b) / 2, yd + .35, ("TRL%d" % k) if b - a > .3 else "%d" % k, ha="center", va="center", fontsize=7, color="white" if k >= 5 else "#2b3440")
            ax.plot([b], [yd + .7], marker="D", ms=3.5, color="#222", zorder=5)
        ext = None
        if s_ == "TRL7": ext = (7, sch["conf"][5], sch["st"][5], "▲ подтверждение TRL7 продолжается: демонтаж, монтаж на объекте\nстроительства, подключение к действующей инфраструктуре")
        if s_ == "TRL6": ext = (6, sch["conf"][4], sch["st"][4], "▲ подтверждение TRL6 продолжается:\nизготовление, поставка оборудования")
        if s_ == "TRL5": ext = (6, sch["conf"][4], sch["st"][4], "▲ подтверждение TRL6 продолжается:\nизготовление, поставка оборудования")
        if ext:
            k, a, b, note = ext
            ax.add_patch(Rc((a, yd), b - a, .7, fc=TCc[k], alpha=.28, ec=TCc[k], lw=1.4, ls="-.", hatch="//"))
            ax.text(a, yd - .1, note, ha="left", va="top", fontsize=6.6, color="#222", style="italic")
        for i_, (a, b) in enumerate(zip(sch["st"], sch["en"])):
            ax.add_patch(Rc((a, yc), b - a, .7, fc=SCc[i_], ec="white", lw=1))
            if b - a > .3: ax.text((a + b) / 2, yc + .35, ST[i_], ha="center", va="center", fontsize=7, color="white")
            else: ax.text((a + b) / 2, yc + .35, ST[i_], ha="center", va="center", fontsize=5.2, color="white", rotation=90)
        tv = sch["tv"]; ent = sch["st"][1]
        ax.axvline(tv, color="#222", ls="--", lw=1); ax.text(tv + .05, top - .05, ("ввод %.2f" % tv).replace(".", ","), fontsize=7.5, va="top")
        ax.axvline(ent, color="#b42318", ls=":", lw=1.5)
        if tv > 7 or ent > 3: ax.text(ent + .05, top - .05, "вход: начало ПД", fontsize=7.5, color="#b42318", va="top", ha="left")
        else: ax.text(ent - .05, top - .05, "вход: начало ПД", fontsize=7.5, color="#b42318", va="top", ha="right")
        ax.set_ylim(0, top)
        ax.set_yticks([yc + .35, yd + .35] + ([yp + .35] if has else []))
        ax.set_yticklabels(["Строительство", "Разработка (TRL)"] + (["Опытная\nинфраструктура"] if has else []), fontsize=7.5)
        ax.set_title(TTL[s_], loc="left", fontsize=8.6, fontweight="bold")
        ax.set_xlim(0, 8.4); ax.set_xticks(range(0, 9)); ax.tick_params(labelsize=7.5); ax.grid(axis="x", color="#e3e7ec", lw=.6); ax.grid(axis="y", visible=False); ax.set_axisbelow(True)
    axs[-1].set_xlabel("Время от начала разработки, лет", fontsize=8)
    fig.tight_layout(); save(fig, "f32_calendar.png")

# 3.3 накопленный ЧДП и годовой ЧДП
fig, axs = plt.subplots(1, 2, figsize=(W, 3.1))
for s in S4:
    rows = R["scn"][s]["rows"]; n = [r["n"] for r in rows]
    axs[0].plot(n, [r["cf"] for r in rows], color=COL[s], ls=LS[s], lw=1.6, label=NAME[s])
    axs[1].plot(n, [r["cum"] for r in rows], color=COL[s], ls=LS[s], lw=1.6, label=NAME[s])
axs[0].set_title("Чистый денежный поток по годам", loc="left", fontsize=10); axs[1].set_title("Накопленный денежный поток", loc="left", fontsize=10)
for a in axs: a.set_xlabel("Расчетный год n"); a.axhline(0, color="#3C4F66", lw=0.8)
axs[0].set_ylabel("млн руб."); axs[0].legend(fontsize=8, loc="upper left")
fig.tight_layout(); save(fig, "f33_cashflow.png")

# 3.4 накопленный дисконтированный ЧДП
fig, ax = plt.subplots(figsize=(W, 3.2))
for s in S4:
    rows = R["scn"][s]["rows"]; n = [0] + [r["n"] for r in rows]; y = [0] + [r["cumd"] for r in rows]
    ax.plot(n, y, color=COL[s], ls=LS[s], lw=1.8, label="%s: ЧДД %.1f" % (NAME[s], R["scn"][s]["ind"]["npv"]))
    d = R["scn"][s]["ind"]["dpp"]
    ax.plot([d], [0], marker=MK[s], color=COL[s], ms=7, mec="white", mew=1.2)
    off = {"BASE": (22, -26), "TRL7": (30, -45), "TRL6": (30, -62), "TRL5": (30, -79)}[s]
    ax.annotate("DPP = %.1f" % d, (d, 0), textcoords="offset points", xytext=off, ha="left", fontsize=8, arrowprops=dict(arrowstyle="-", color=COL[s], lw=0.8))
ax.axhline(0, color="#3C4F66", lw=0.8); ax.set_xlabel("Расчетный год n"); ax.set_ylabel("млн руб. (r = 12 %)")
ax.legend(fontsize=8, loc="upper left")
fig.tight_layout(); save(fig, "f34_cumdisc.png")

# 3.5 чувствительность к ставке
fig, axs = plt.subplots(1, 2, figsize=(W, 3.2))
rt = [d["rate"] * 100 for d in R["sens_rate"]]
for s in S4:
    axs[0].plot(rt, [d["npv"][s] for d in R["sens_rate"]], color=COL[s], ls=LS[s], marker=MK[s], ms=4.5, lw=1.6, mec="white", label=NAME[s])
for s in S3:
    axs[1].plot(rt, [d["R"][s] for d in R["sens_rate"]], color=COL[s], ls=LS[s], marker=MK[s], ms=4.5, lw=1.6, mec="white", label=NAME[s])
axs[0].axhline(0, color="#3C4F66", lw=0.8); axs[0].set_title("ЧДД", loc="left", fontsize=10); axs[1].set_title("Преимущество R_s", loc="left", fontsize=10)
for a in axs: a.set_xlabel("Ставка дисконтирования, %")
axs[0].set_ylabel("млн руб."); axs[0].legend(fontsize=7.5, loc="upper right"); axs[1].legend(fontsize=7.5, loc="upper right")
axs[1].set_ylim(0, 205)
fig.tight_layout(); save(fig, "f35_rate.png")

# 3.6 чувствительность к доле
fig, axs = plt.subplots(1, 2, figsize=(W, 3.2))
sh = [d["share"] * 100 for d in R["sens_share"]]
for s in S4:
    axs[0].plot(sh, [d["npv"][s] for d in R["sens_share"]], color=COL[s], ls=LS[s], marker=MK[s], ms=4.5, lw=1.6, mec="white", label=NAME[s])
for s in S3:
    axs[1].plot(sh, [d["R"][s] for d in R["sens_share"]], color=COL[s], ls=LS[s], marker=MK[s], ms=4.5, lw=1.6, mec="white", label=NAME[s])
axs[0].set_title("ЧДД", loc="left", fontsize=10); axs[1].set_title("Преимущество R_s", loc="left", fontsize=10)
for a in axs: a.set_xlabel("Доля инновационных затрат, %"); a.axvline(35, color="#8b8a83", lw=0.8, ls=":")
axs[0].set_ylabel("млн руб."); axs[0].legend(fontsize=7.5, loc="lower left"); axs[1].legend(fontsize=7.5, loc="upper left")
fig.tight_layout(); save(fig, "f36_share.png")

# 3.7 остатки преимущества по исходам
fig, ax = plt.subplots(figsize=(W, 3.5))
it5 = sorted(R["scn"]["TRL5"]["out"]["items"], key=lambda i: -i["rem"])
def num(i): c = i["combo"]; return 1 + 8 * c[0] + 4 * c[1] + 2 * c[2] + c[3]
order = [num(i) for i in it5]
# общая нумерация исходов — по сценарию TRL5 (события TRL6–TRL9); в TRL6 не наступает событие TRL6, в TRL7 — TRL6 и TRL7
d5 = {num(i): i for i in R["scn"]["TRL5"]["out"]["items"]}
d6 = {1 + 4 * i["combo"][0] + 2 * i["combo"][1] + i["combo"][2]: i for i in R["scn"]["TRL6"]["out"]["items"]}
d7 = {1 + 2 * i["combo"][0] + i["combo"][1]: i for i in R["scn"]["TRL7"]["out"]["items"]}
ax.bar(range(16), [d5[o]["rem"] for o in order], width=0.26, color=COL["TRL5"], label=NAME["TRL5"] + " (16 исходов)", edgecolor="white", lw=0.8)
xs6 = [x for x, o in enumerate(order) if o in d6]
ax.bar([x + 0.27 for x in xs6], [d6[order[x]]["rem"] for x in xs6], width=0.26, color=COL["TRL6"], label=NAME["TRL6"] + " (8 исходов)", edgecolor="white", lw=0.8)
xs7 = [x for x, o in enumerate(order) if o in d7]
ax.bar([x - 0.27 for x in xs7], [d7[order[x]]["rem"] for x in xs7], width=0.26, color=COL["TRL7"], label=NAME["TRL7"] + " (4 исхода)", edgecolor="white", lw=0.8)
for s_ in S3: ax.axhline(R["scn"][s_]["R"], color=COL[s_], lw=0.9, ls=":")
ax.text(-0.4, 203, "пунктир: R_s без переделок (цвет — сценарий)", ha="left", fontsize=8)
ax.set_xlabel("№ исхода по приложению 8 (по убыванию остатка сценария TRL5)"); ax.set_ylabel("Остаток преимущества, млн руб."); ax.set_xticks(range(16)); ax.set_xticklabels(order, fontsize=8)
ax.legend(fontsize=7.5, loc="upper right"); ax.set_ylim(0, 215)
fig.tight_layout(); save(fig, "f37_outcomes.png")

# 3.8 налог и баланс убытка (Интеграция TRL5)
rows = R["scn"]["TRL5"]["rows"][:20]
fig, ax = plt.subplots(figsize=(W, 3.1)); n = [r["n"] for r in rows]
ax.bar(n, [r["tax"] for r in rows], color="#C4690E", width=0.6, label="Налог на прибыль", edgecolor="white")
ax.plot(n, [r["loss_close"] for r in rows], color="#0079C2", lw=1.8, marker="o", ms=4, mec="white", label="Неиспользованный убыток на конец года")
ax.set_xticks(range(1,21)); ax.set_xlabel("Расчетный год n (n = 1 — 2026 г.)"); ax.set_ylabel("млн руб."); ax.legend(fontsize=8, loc="upper right"); ax.axvline(5.5, color="#8b8a83", lw=0.8, ls=":")
ax.text(10, 260, "пунктир: 2030 г. — окончание действия\nпредела зачета убытка в 50 %", fontsize=8, va="top")
fig.tight_layout(); save(fig, "f38_tax.png")

# 3.9 эффект мер
fig, ax = plt.subplots(figsize=(W, 3.0))
ids = ["М1", "М2", "М3", "М4", "М5", "pack"]; lab = ["М1", "М2", "М3", "М4", "М5", "Пакет\nМ1–М5"]
res = R["meas"]["res"]["TRL5"]
import numpy as np
x = np.arange(len(ids))
for j, (nm, c) in enumerate((("низкая", "#c6d7ee"), ("средняя", "#6f9ed6"), ("высокая", "#0079C2"))):
    vals = [(res[i]["row"][j]["net"] if i != "pack" else res[i][j]["net"]) for i in ids]
    ax.bar(x + (j - 1) * 0.26, vals, width=0.24, color=c, label="эффективность " + nm, edgecolor="white")
ax.axhline(0, color="#3C4F66", lw=0.8); ax.set_xticks(x); ax.set_xticklabels(lab); ax.set_ylabel("Эффект, млн руб.")
ax.legend(fontsize=8, loc="upper left"); fig.tight_layout(); save(fig, "f39_measures.png")

# 3.10 дорожная карта (диаграмма Ганта по месяцам)
RM = [("1.1 Положение о контрольных точках и критериях готовности", 1, 3), ("1.2 Совет по изменениям и порядок решений", 1, 2),
      ("2.1 Паспорт контрольной точки, матрица исходных данных", 3, 5), ("2.2 Реестр изменений, конфигурационный учет", 4, 8),
      ("2.3 Модель оценки: ввод в порядок расчета", 5, 9), ("3.1 Профессиональное обучение", 6, 10),
      ("3.2 Социально-психологическое сопровождение", 3, 14), ("4.1 Пилотное применение на проекте", 10, 18),
      ("4.2 Поэтапная приемка строительной готовности", 12, 18), ("5.1 Корректировка регламентов по итогам пилота", 18, 21),
      ("5.2 Предложения по включению в корпоративные документы", 21, 24)]
json.dump(RM, open("roadmap.json", "w"), ensure_ascii=False)
fig, ax = plt.subplots(figsize=(W, 3.7))
ecol = {"1": "#0079C2", "2": "#6250d6", "3": "#1B9E77", "4": "#C4690E", "5": "#3C4F66"}
for i, (t, a, b) in enumerate(RM):
    ax.barh(i, b - a + 1, left=a - 1, height=0.55, color=ecol[t[0]], edgecolor="white")
ax.set_yticks(range(len(RM))); ax.set_yticklabels([t for t, _, _ in RM], fontsize=7.8); ax.invert_yaxis()
ax.set_xlim(0, 24); ax.set_xticks(range(0, 25, 3)); ax.set_xlabel("Месяцы от утверждения решения (допущение)"); ax.grid(axis="y", visible=False)
fig.tight_layout(); save(fig, "f310_plan_unused.png")
print("ok")

# 3.5+3.6 объединенный рисунок чувствительности (2×2)
fig, axs = plt.subplots(2, 2, figsize=(W, 5.0))
rt = [d["rate"] * 100 for d in R["sens_rate"]]; sh = [d["share"] * 100 for d in R["sens_share"]]
for s in S4:
    axs[0][0].plot(rt, [d["npv"][s] for d in R["sens_rate"]], color=COL[s], ls=LS[s], marker=MK[s], ms=4, lw=1.5, mec="white", label=NAME[s])
    axs[1][0].plot(sh, [d["npv"][s] for d in R["sens_share"]], color=COL[s], ls=LS[s], marker=MK[s], ms=4, lw=1.5, mec="white", label=NAME[s])
for s in S3:
    axs[0][1].plot(rt, [d["R"][s] for d in R["sens_rate"]], color=COL[s], ls=LS[s], marker=MK[s], ms=4, lw=1.5, mec="white", label=NAME[s])
    axs[1][1].plot(sh, [d["R"][s] for d in R["sens_share"]], color=COL[s], ls=LS[s], marker=MK[s], ms=4, lw=1.5, mec="white", label=NAME[s])
axs[0][0].axhline(0, color="#3C4F66", lw=0.8); axs[0][1].set_ylim(0, 205)
for a, t in zip((axs[0][0], axs[0][1], axs[1][0], axs[1][1]), ("а) ЧДД, ставка", "б) преимущество R_s, ставка", "в) ЧДД, доля", "г) преимущество R_s, доля")):
    a.set_title(t, loc="left", fontsize=9)
for a in axs[0]: a.set_xlabel("Ставка дисконтирования, %", fontsize=8.5)
for a in axs[1]: a.set_xlabel("Доля инновационных затрат, %", fontsize=8.5); a.axvline(35, color="#8b8a83", lw=0.8, ls=":")
for a in axs[:, 0]: a.set_ylabel("млн руб.", fontsize=8.5)
axs[0][0].legend(fontsize=7, loc="upper right"); axs[1][0].legend(fontsize=7, loc="lower left")
fig.tight_layout(); save(fig, "f35_sens.png")

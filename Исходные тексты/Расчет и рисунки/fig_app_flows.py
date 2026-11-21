# -*- coding: utf-8 -*-
"""Графики денежных потоков по сценариям для приложений.

Заменяют печатные годовые таблицы: затраты года показаны вниз с разделением
на инновационные и инвестиционные, поступления после налога вверх, накопленный
дисконтированный поток линией.
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = json.load(open("/home/claude/work/model/results.json", encoding="utf-8"))
SC = ["BASE", "TRL7", "TRL6", "TRL5"]
SCL = {"BASE": "Базовый", "TRL7": "Интеграция TRL7", "TRL6": "Интеграция TRL6",
       "TRL5": "Интеграция TRL5"}
INN, INV, OP, CUM = "#8E44AD", "#1B9E77", "#9fb8cf", "#003366"
plt.rcParams["font.family"] = "DejaVu Sans"


def one(key):
    rows = R["scn"][key]["rows"]
    yrs = [r["year"] for r in rows]
    inn = [r["inn"] + r["pilot"] + r["rework"] + r.get("t7x", 0.0) for r in rows]
    inv = [r["inv"] for r in rows]
    op = [max(0.0, r["cf_op"]) for r in rows]
    cum = [r["cumd"] for r in rows]

    fig, ax = plt.subplots(figsize=(10.2, 4.3), dpi=600)
    ax.axhline(0, color="#b9b6ae", lw=0.8)
    ax.bar(yrs, op, width=0.72, color=OP, label="Поступления от эксплуатации после налога")
    ax.bar(yrs, [-v for v in inv], width=0.72, color=INV, label="Инвестиционные затраты")
    ax.bar(yrs, [-v for v in inn], width=0.72, bottom=[-v for v in inv], color=INN,
           label="Инновационные затраты")
    ax.plot(yrs, cum, color=CUM, lw=1.8, label="Накопленный дисконтированный поток")
    ax.set_xlabel("Календарный год расчетного периода", fontsize=8.5)
    ax.set_ylabel("Млн руб.", fontsize=8.5)
    ax.tick_params(labelsize=8)
    ax.grid(axis="y", color="#eceae4", lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(fontsize=7.6, loc="lower right", frameon=False, ncol=2)
    ax.set_title("Денежный поток по годам. %s" % SCL[key], fontsize=10, loc="left")
    fig.tight_layout()
    out = "/home/claude/work/fig/app_flow_%s.png" % key
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print(out)


for k in SC:
    one(k)

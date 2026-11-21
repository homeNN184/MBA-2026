# -*- coding: utf-8 -*-
"""Пересборка листов legacy_tables.xlsx из результатов модели.

Лист содержит расчеты, не включенные в рабочую книгу: чувствительность к доле
инновационных затрат, меры управления рисками, пороги безразличия, стресс-сценарии
и имитационное моделирование. Структура строк сохранена, поскольку сборщик
приложений ищет блоки по тексту заголовков.
"""
import copy, json
import openpyxl

SRC = "/home/claude/work/ch3/legacy_tables.xlsx"
R = json.load(open("results.json", encoding="utf-8"))
S = json.load(open("stage1.json", encoding="utf-8"))
wb = openpyxl.load_workbook(SRC)
SC4 = ("BASE", "TRL7", "TRL6", "TRL5")
IN3 = ("TRL7", "TRL6", "TRL5")
TT = {"BASE": "Базовый", "TRL7": "Интеграция TRL7", "TRL6": "Интеграция TRL6", "TRL5": "Интеграция TRL5"}


def put(ws, r, vals, c0=1, style_row=None):
    for i, v in enumerate(vals):
        cell = ws.cell(r, c0 + i)
        if style_row is not None:
            cell._style = copy.copy(ws.cell(style_row, c0 + i)._style)
        cell.value = v


# ---------- Чувств_доля ----------
ws = wb["Чувств_доля"]
for i, d in enumerate(R["sens_share"]):
    r = 5 + i
    put(ws, r, [d["share"], d["b_inn"], d["b_inv"], d["pilot"]]
        + [d["npv"][s] for s in SC4] + [d["npv"][s] - d["npv"]["BASE"] for s in IN3], style_row=5)

# ---------- Меры ----------
ws = wb["Меры"]
M = R["meas"]; L = M["list"]
DIM = {"вероятность": "вероятность", "стоимость": "стоимость",
       "длительность": "длительность", "ожидание": "длительность ожидания"}
LVL = ["низкая", "средняя", "высокая"]
ws.cell(1, 1).value = ("Меры управления рисками: эффект = снижение потерь от доработок или затрат ожидания "
                       "в расчетном случае − приведенные затраты меры. Эффективность задана диапазоном (предпосылки)")
ws.cell(3, 5).value = "Снижение потерь от доработок или затрат ожидания (расчетный случай), млн руб."
r = 4
for key in IN3:
    res = M["res"][key]
    for m in L:
        rr = res[m["id"]]
        for j in range(3):
            x = rr["row"][j]
            d = x.get("dEL", 0.0) + x.get("dNPV", 0.0)
            be = rr["be"]
            put(ws, r, [m["id"], TT[key], DIM[m["dim"]], "%s: %d %%" % (LVL[j], round(m["eff"][j] * 100)),
                        d, x["pvc"], d - x["pvc"],
                        ("не применима" if (be is None or d <= 0) else be)], style_row=4)
            r += 1
    for j in range(3):
        x = res["pack"][j]
        d = x.get("dEL", 0.0) + x.get("dNPV", 0.0)
        put(ws, r, ["Пакет М1–М5", TT[key], "комплексное", LVL[j], d, x["pvc"], d - x["pvc"], "—"], style_row=4)
        r += 1
for q in range(r, ws.max_row + 1):
    for c in range(1, 9):
        ws.cell(q, c).value = None

# ---------- Пороги ----------
ws = wb["Пороги"]
X = S["thr56_X"]; ev5 = S["events"]["TRL5"]["6"]
ws.cell(3, 2).value = S["thr56_rule"]["dNPV0"]
ws.cell(4, 2).value = S["thr56_rule"]["E_loss6"]
ws.cell(5, 2).value = X["El5_other"]
ws.cell(6, 2).value = X["X"]
ws.cell(7, 2).value = X["L6"]
ws.cell(8, 2).value = X["c6"]
ws.cell(9, 2).value = X["d6"]
ws.cell(10, 2).value = ev5[0]
ws.cell(11, 2).value = ev5[0] * X["L6"]
ws.cell(12, 2).value = X["X"] / X["L6"]
ws.cell(13, 2).value = S["thr67_scale"]
ws.cell(14, 2).value = S["E7_nopilot_noextras"]
ws.cell(18, 1).value = "Вероятность p"
NOB = "TRL6 лучше при любых затратах"
keys = ["104", "150", "200"]
ws.cell(17, 1).value = "Безразличный прямой ущерб события TRL6 (млн руб.) при задержке d (сут.) и вероятности p"
for i in range(3):
    ws.cell(18, 2 + i).value = "Задержка %s сут." % keys[i]
ws.cell(18, 5).value = "Безразличная задержка при затратах %s млн руб., сут." % ("%.1f" % X["c6"]).replace(".", ".")
for i, (pq, _) in enumerate(S["thr56"][keys[0]]):
    r = 19 + i
    row = [pq]
    for k in keys:
        v = dict(S["thr56"][k]).get(pq)
        row.append(NOB if v is None else v)
    dd = dict(S["thr56_delay"]).get(pq)
    row.append(NOB if dd is None else dd)
    put(ws, r, row, style_row=19)
ws.cell(29, 1).value = "Чувствительность к стоимости опытной инфраструктуры (млн руб.): ЧДД сценариев"
for i, d in enumerate(S["pilot_sens"]):
    put(ws, 31 + i, [d["pilot"]] + [d["npv"][s] for s in SC4], style_row=31)

# ---------- Точки входа ----------
ws = wb["Точки входа"]
EP = R["entry"]
for i, s in enumerate(SC4):
    d = [o for o in EP["opts"] if o["scn"] == s][0]
    put(ws, 4 + i, [TT[s].replace("Интеграция ", ""), d["npv"], d["tv"],
                    d.get("R", 0.0), d.get("dT", 0.0),
                    "—" if d.get("price") is None else d.get("price", "—"),
                    d.get("worst", 0.0)], style_row=4)
mcw = EP["mc"]["wins"]
ws.cell(21, 1).value = ("Доля случайных наборов весов (%d испытаний, равномерное распределение на симплексе), "
                        "при которых вариант лучший" % EP["mc"]["n"])
put(ws, 23, ["Доля побед"] + [mcw.get(TT[s].replace("Интеграция ", ""), mcw.get(TT[s], 0.0)) for s in SC4], style_row=23)
ws.cell(25, 1).value = ("Область весов: суммарный вес критериев «остаток» и «устойчивость» (поровну), остальные веса "
                        "пропорциональны базовым. Выбор TRL5 → TRL6 меняется при весе %.3f" % EP["w_switch"])
for i, g in enumerate(EP["w_rob_grid"]):
    put(ws, 27 + i, [g["wt"]] + list(g["tot"]) + [g["best"]], style_row=27)
ws.cell(35, 1).value = "Критический множитель затрат и задержек доработок (остаток Q в расчетном случае = 0)"
for i, s in enumerate(IN3):
    c = EP["crit"][s]
    put(ws, 37 + i, [s, c["m"], c["cost"], c["delay"], c["w1"]], style_row=37)

# ---------- Риск_стресс ----------
ws = wb["Риск_стресс"]
mc = S["mc"]
N_SIM = "5 000"
ws.cell(1, 1).value = ("Стресс-сценарии удорожания инновационной части и имитационное моделирование (%s прогонов). "
                       "Значения модели Python." % N_SIM)
ws.cell(3, 1).value = "Стресс: удорожание инновационной части и задержка разработки (без событий доработки), ЧДД, млн руб."
for i, d in enumerate(S["stress"]):
    put(ws, 5 + i, [d["kc"], d["dy"]] + [d["npv"][s] for s in SC4] + [d["R"][s] for s in IN3], style_row=5)
for i, s in enumerate(SC4):
    m = mc[s]
    put(ws, 14 + i, [TT[s], m["p10"], m["p50"], m["p90"], m["mean"], m["neg"],
                     m["adv_p10"], m["adv_p50"], m["adv_p90"], m["beat_base"], m["best"]], style_row=14)
d56 = mc["d56"]
put(ws, 19, ["Разность ЧДД TRL5 − TRL6: P10 / P50 / P90, вероятность TRL5 лучше",
             d56["p10"], d56["p50"], d56["p90"], d56["pos"]], style_row=19)
for i, t in enumerate(mc["tornado"]):
    put(ws, 23 + i, [t["name"], t["lo"]["R5"], t["hi"]["R5"], t["lo"]["R6"], t["hi"]["R6"],
                     t["lo"]["d56"], t["hi"]["d56"]], style_row=23)

# ---------- замена термина и буквы е ----------
RULES = [("Переделать", "Доработать"), ("Переделок", "Доработок"), ("Переделк", "Доработк"),
         ("переделать", "доработать"), ("переделок", "доработок"), ("переделк", "доработк"),
         ("ё", "е"), ("Ё", "Е")]
for sh in wb.sheetnames:
    w_ = wb[sh]
    for row in w_.iter_rows():
        for cell in row:
            v = cell.value
            if isinstance(v, str) and not v.startswith("="):
                nv = v
                for a, bq in RULES:
                    nv = nv.replace(a, bq)
                if nv != v:
                    cell.value = nv

wb.save(SRC)
print("legacy_tables.xlsx пересобран")

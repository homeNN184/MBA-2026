# -*- coding: utf-8 -*-
import json
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter as L

R = json.load(open("results.json"))
P = R["params"]; D = R["derived"]
wb = Workbook()
F_IN = Font(name="Times New Roman", size=11, color="0000FF")
F_N = Font(name="Times New Roman", size=11)
F_B = Font(name="Times New Roman", size=11, bold=True)
F_H = Font(name="Times New Roman", size=11, bold=True)
F_T = Font(name="Times New Roman", size=14, bold=True)
F_ST = Font(name="Times New Roman", size=11, color="7F7F7F")
FILL_H = PatternFill("solid", fgColor="DCE6F1")
FILL_IN = PatternFill("solid", fgColor="FFF2CC")
FILL_ST = PatternFill("solid", fgColor="EDEDED")
FILL_OK = PatternFill("solid", fgColor="E2EFDA")
thin = Side(style="thin", color="999999")
BRD = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="center", horizontal="center")
LEFT = Alignment(wrap_text=True, vertical="center", horizontal="left")

def put(ws, ref, v, font=F_N, fmt=None, fill=None, align=None, border=True):
    c = ws[ref]; c.value = v; c.font = font
    if fmt: c.number_format = fmt
    if fill: c.fill = fill
    if align: c.alignment = align
    if border: c.border = BRD
    return c

def name(n, ws, ref):
    wb.defined_names[n] = DefinedName(n, attr_text="'%s'!%s" % (ws.title, ref))

def header(ws, row, heads, widths=None, height=60):
    for i, h in enumerate(heads, 1):
        put(ws, "%s%d" % (L(i), row), h, F_H, fill=FILL_H, align=WRAP)
    ws.row_dimensions[row].height = height
    if widths:
        for i, w in enumerate(widths, 1): ws.column_dimensions[L(i)].width = w

# ---------------------------------------------------------------- Входы
wsI = wb.active; wsI.title = "Входы"
put(wsI, "A1", "Входные данные модели. Суммы — млн руб. в постоянных ценах. Ввод — ячейки на желтом фоне.", F_T, border=False)
heads = ["Параметр", "Значение", "Единица", "Основание / пояснение", "Имя"]
header(wsI, 3, heads, [52, 14, 14, 70, 14], 30)
rows_in = [
 ("Бюджет инвестиционно-инновационного проекта", P["budget"], "млн руб.", "исходное условие", "B_total", "0.00", True),
 ("Доля инновационных затрат s_INN", P["share_inn"], "доля", "диапазон 10–50 %", "s_INN", "0.00%", True),
 ("Инновационные затраты B_INN = B·s_INN", "=B_total*s_INN", "млн руб.", "(350 млн руб. при 35 %)", "B_INN", "0.00", False),
 ("Прочая инвестиционная часть B_INV = B − B_INN", "=B_total-B_INN", "млн руб.", "(650 млн руб. при 35 %)", "B_INV", "0.00", False),
 ("Ставка дисконтирования r", P["rate"], "доля", "диапазон 10–16 %", "r_disc", "0.00%", True),
 ("Длительность разработки до TRL9 (исходный план)", P["t_dev"], "лет", "исходное условие", "T_dev", "0.00", True),
 ("Длительность инвестиционного проекта", P["t_inv"], "лет", "исходное условие", "T_inv", "0.00", True),
 ("Срок эксплуатации от ввода", P["op_years"], "лет", "исходное условие", "Op_N", "0", True),
 ("Выручка при полной загрузке", P["revenue"], "млн руб./год", "исходное условие", "Rev_full", "0.00", True),
 ("Загрузка: первый год эксплуатации", P["load"][0], "доля", "исходное условие", "Load_1", "0.00", True),
 ("Загрузка: второй год эксплуатации", P["load"][1], "доля", "третий и далее — 100 %", "Load_2", "0.00", True),
 ("Численность работников", P["staff"], "чел.", "исходное условие", "Staff", "0", True),
 ("Заработная плата", P["salary_k"], "тыс. руб./мес", "исходное условие", "Salary", "0.00", True),
 ("Надбавки (начисляются на зарплату)", P["markup"], "доля", "исходное условие", "Markup", "0.00%", True),
 ("Административные расходы (начисляются на зарплату)", P["admin"], "доля", "исходное условие", "Admin", "0.00%", True),
 ("Годовые операционные затраты Opex", "=Staff*Salary*12/1000*(1+Markup+Admin)", "млн руб./год", "(19,14 млн руб.)", "Opex", "0.00", False),
 ("Доля ТО от бюджета", P["to_rate"], "доля", "исходное условие", "To_rate", "0.00%", True),
 ("ТО, ежегодно", "=B_total*To_rate", "млн руб.", "(1,20 млн руб.)", "TO_amt", "0.00", False),
 ("Доля ТР от бюджета", P["tr_rate"], "доля", "исходное условие", "Tr_rate", "0.00%", True),
 ("ТР, в годы эксплуатации 3, 6, …, 30", "=B_total*Tr_rate", "млн руб.", "(2,50 млн руб.)", "TR_amt", "0.00", False),
 ("Доля КР от бюджета", P["kr_rate"], "доля", "исходное условие", "Kr_rate", "0.00%", True),
 ("КР, в годы эксплуатации 5, 10, …, 30", "=B_total*Kr_rate", "млн руб.", "(5 млн руб.)", "KR_amt", "0.00", False),
 ("Ставка налога на прибыль", P["tax"], "доля", "исходное условие", "Tax_rate", "0.00%", True),
 ("Срок линейной амортизации прочих инвестиций", P["amort_years"], "лет", "(согласованное расчетное допущение)", "Amort_N", "0", True),
 ("Предел зачета убытка по налоговой базе", P["loss_limit"], "доля", "до 2030 г. включительно 50 %, далее ограничения нет", "Loss_lim", "0.00%", True),
 ("Последний календарный год ограничения зачета убытка", P["loss_limit_end"], "год", "исходное условие", "Loss_lim_end", "0", True),
 ("Первый налоговый год (n = 1)", P["first_tax_year"], "год", "исходное условие", "Year_1", "0", True),
 ("Доля опытной инфраструктуры от B_INN (только Базовый и Интеграция TRL7)", P["pilot_share"], "доля", "исходное условие", "Pilot_share", "0.00%", True),
 ("Опытная инфраструктура", "=Pilot_share*B_INN", "млн руб.", "(35 млн руб. при 35 %)", "Pilot", "0.00", False),
 ("Дней в году", P["days"], "дн.", "перевод задержек ввода из дней в годы", "Days", "0", True),
 ("Доля незафиксированных интерфейсных параметров на входе TRL5", P["phi_s"][0], "доля", "параметр эволюции исходных данных; нормированное значение", "Phi5", "0.00", True),
 ("Доля незафиксированных интерфейсных параметров на входе TRL6", P["phi_s"][1], "доля", "опорный уровень (вероятности событий таблицы ниже заданы для него)", "Phi6", "0.00", True),
 ("Доля незафиксированных интерфейсных параметров на входе TRL7", P["phi_s"][2], "доля", "нормированное значение", "Phi7", "0.00", True),
 ("Доля марок документации, зависящих от параметра (чувствительность)", P["sigma"], "доля", "нормированное значение", "Sigma_m", "0.00", True),
 ("Проектные работы (ПД и РД), доля B_INV", P["pir_share"], "доля", "нормированное значение", "PIR_share", "0.00%", True),
 ("Доля ПД в проектных работах", P["pd_part"], "доля", "нормированное значение", "PD_part", "0.00", True),
 ("Повторная экспертиза, доля стоимости ПД", P["exp_share"], "доля", "нормированное значение", "Exp_share", "0.00%", True),
 ("Срок повторной экспертизы", P["exp_days"], "дн.", "нормированное значение", "Exp_days", "0", True),
 ("Хранение и консервация оборудования (Интеграция TRL7), доля B_INN в год", P["t7_store"], "доля", "интервал от подтверждения TRL7 до начала СМР", "T7_store", "0.00%", True),
 ("Демонтаж, транспортировка, монтаж и повторная верификация (Интеграция TRL7), доля B_INN", P["t7_remount"], "доля", "в момент начала СМР", "T7_remount", "0.00%", True),
 ("Вероятность окончания гарантии до ввода (Интеграция TRL7)", P["t7_warr_p"], "доля", "нормированное значение", "T7_warr_p", "0.00", True),
 ("Затраты продления гарантии, доля B_INN (Интеграция TRL7)", P["t7_warr_cost"], "доля", "учитываются как ожидаемое значение в момент ввода", "T7_warr_cost", "0.00%", True),
]
r0 = 4
for i, (lab, val, unit, src, nm, fmt, is_in) in enumerate(rows_in):
    r = r0 + i
    put(wsI, "A%d" % r, lab, align=LEFT)
    put(wsI, "B%d" % r, val, F_IN if is_in else F_N, fmt, FILL_IN if is_in else None)
    put(wsI, "C%d" % r, unit); put(wsI, "D%d" % r, src, align=LEFT); put(wsI, "E%d" % r, nm)
    name(nm, wsI, "$B$%d" % r)
rT = r0 + len(rows_in) + 2
put(wsI, "A%d" % rT, "Таблица переходов TRL: массив временных долей и массив налогового признания хранятся раздельно", F_B, border=False)
hdr = rT + 1
for i, h in enumerate(["Переход", "Доля времени, %", "Доля налогового признания / затрат, %", "Затраты этапа, млн руб.", ""], 1):
    put(wsI, "%s%d" % (L(i), hdr), h, F_H, fill=FILL_H, align=WRAP)
wsI.row_dimensions[hdr].height = 45
TRL = ["TRL1→2", "TRL2→3", "TRL3→4", "TRL4→5", "TRL5→6", "TRL6→7", "TRL7→8", "TRL8→9"]
TR0 = hdr + 1
for k in range(8):
    r = TR0 + k
    put(wsI, "A%d" % r, TRL[k])
    put(wsI, "B%d" % r, P["w_time"][k], F_IN, "0.00", FILL_IN)
    put(wsI, "C%d" % r, P["w_tax"][k], F_IN, "0.00", FILL_IN)
    put(wsI, "D%d" % r, "=B_INN*C%d/100" % r, F_N, "0.00")
put(wsI, "A%d" % (TR0 + 8), "Сумма", F_B)
put(wsI, "B%d" % (TR0 + 8), "=SUM(B%d:B%d)" % (TR0, TR0 + 7), F_B, "0.00")
put(wsI, "C%d" % (TR0 + 8), "=SUM(C%d:C%d)" % (TR0, TR0 + 7), F_B, "0.00")
put(wsI, "D%d" % (TR0 + 8), "=SUM(D%d:D%d)" % (TR0, TR0 + 7), F_B, "0.00")
W_TIME = "Входы!$B$%d:$B$%d" % (TR0, TR0 + 7); W_TAX = "Входы!$C$%d:$C$%d" % (TR0, TR0 + 7)
rS = TR0 + 11
put(wsI, "A%d" % rS, "Стадии строительства: доли времени инвестиционного проекта (не являются стоимостными)", F_B, border=False)
for i, h in enumerate(["Стадия", "Доля времени, %", "Длительность, лет", "", ""], 1):
    put(wsI, "%s%d" % (L(i), rS + 1), h, F_H, fill=FILL_H, align=WRAP)
STG = ["Исходные данные и общие решения", "Проектная документация, экспертиза и корректировка", "Рабочая документация", "Поставка МТР",
       "Строительно-монтажные работы", "ПНР без нагрузки", "ПНР под нагрузкой", "Комплексное опробование"]
ST0 = rS + 2
for k in range(8):
    r = ST0 + k
    put(wsI, "A%d" % r, STG[k], align=LEFT)
    put(wsI, "B%d" % r, P["stage_share"][k], F_IN, "0.00", FILL_IN)
    put(wsI, "C%d" % r, "=B%d/100*T_inv" % r, F_N, "0.00")
put(wsI, "A%d" % (ST0 + 8), "Сумма", F_B)
put(wsI, "B%d" % (ST0 + 8), "=SUM(B%d:B%d)" % (ST0, ST0 + 7), F_B, "0.00")
put(wsI, "C%d" % (ST0 + 8), "=SUM(C%d:C%d)" % (ST0, ST0 + 7), F_B, "0.00")
rE = ST0 + 11
put(wsI, "A%d" % rE, "События доработки: вероятности TRL1–TRL9; затраты и задержки TRL5–TRL9", F_B, border=False)
for i, h in enumerate(["Уровень", "Вероятность, %", "Совокупные затраты, млн руб.", "Задержка ввода, сут.", "Доля бюджета, %"], 1):
    put(wsI, "%s%d" % (L(i), rE + 1), h, F_H, fill=FILL_H, align=WRAP)
wsI.row_dimensions[rE + 1].height = 45
EV0 = rE + 2
pall = [30, 20, 14, 12, 9, 6, 4, 3, 2]
for k in range(9):
    r = EV0 + k
    put(wsI, "A%d" % r, "TRL%d" % (k + 1))
    put(wsI, "B%d" % r, pall[k], F_IN, "0.00", FILL_IN)
    if k >= 4:
        put(wsI, "C%d" % r, P["ev_cost"][k - 4], F_IN, "0.00", FILL_IN)
        put(wsI, "D%d" % r, P["ev_delay_d"][k - 4], F_IN, "0", FILL_IN)
        put(wsI, "E%d" % r, "=C%d/B_total*100" % r, F_N, "0.00")
    else:
        for c in "CDE": put(wsI, "%s%d" % (c, r), "—")
wsI.freeze_panes = "A4"
EVR = {k: EV0 + k - 1 for k in range(1, 10)}      # строка уровня TRLk

# ---------------------------------------------------------------- Эксплуатация
wsO = wb.create_sheet("Эксплуатация")
put(wsO, "A1", "Годы эксплуатации от даты ввода (не календарные): плановые потоки по годам эксплуатации j", F_T, border=False)
header(wsO, 3, ["Год экспл. j", "Загрузка", "Выручка, млн руб.", "Опер. затраты, млн руб.", "ТО, млн руб.", "ТР, млн руб.", "КР, млн руб.", "Амортизация, млн руб.", "ТОиР всего, млн руб."],
       [12, 12, 16, 16, 14, 14, 14, 18, 16], 45)
O0 = 4
for j in range(1, 31):
    r = O0 + j - 1
    put(wsO, "A%d" % r, j, fmt="0")
    put(wsO, "B%d" % r, "=IF(A%d=1,Load_1,IF(A%d=2,Load_2,1))" % (r, r), fmt="0.00")
    put(wsO, "C%d" % r, "=Rev_full*B%d" % r, fmt="0.00")
    put(wsO, "D%d" % r, "=Opex", fmt="0.00")
    put(wsO, "E%d" % r, "=TO_amt", fmt="0.00")
    put(wsO, "F%d" % r, "=IF(MOD(A%d,3)=0,TR_amt,0)" % r, fmt="0.00")
    put(wsO, "G%d" % r, "=IF(MOD(A%d,5)=0,KR_amt,0)" % r, fmt="0.00")
    put(wsO, "H%d" % r, "=IF(A%d<=Amort_N,B_INV/Amort_N,0)" % r, fmt="0.00")
    put(wsO, "I%d" % r, "=E%d+F%d+G%d" % (r, r, r), fmt="0.00")
put(wsO, "A%d" % (O0 + 30), "Итого", F_B)
for c in "CDEFGHI":
    put(wsO, "%s%d" % (c, O0 + 30), "=SUM(%s%d:%s%d)" % (c, O0, c, O0 + 29), F_B, "0.00")
OC = {k: "Эксплуатация!$%s$%d:$%s$%d" % (c, O0, c, O0 + 29) for k, c in zip(["load", "rev", "opex", "to", "tr", "kr", "am", "toir"], "BCDEFGHI")}

# ---------------------------------------------------------------- Сети
wsN = wb.create_sheet("Сети")
put(wsN, "A1", "Календарь и сетевые зависимости (время в годах от начала разработки, t = 0)", F_T, border=False)
put(wsN, "A3", "Календарь переходов TRL (плановые длительности; общий для четырех сценариев)", F_B, border=False)
header(wsN, 4, ["Переход", "Длительность, лет", "Начало, t", "Подтверждение (конец), t", "Налоговый год признания", "Затраты этапа, млн руб."], [46, 16, 14, 18, 16, 16], 45)
N0 = 5
for k in range(8):
    r = N0 + k
    put(wsN, "A%d" % r, TRL[k])
    put(wsN, "B%d" % r, "=Входы!B%d/100*T_dev" % (TR0 + k), fmt="0.000")
    put(wsN, "C%d" % r, 0 if k == 0 else "=D%d" % (r - 1), fmt="0.000")
    put(wsN, "D%d" % r, "=C%d+B%d" % (r, r), fmt="0.000")
    put(wsN, "E%d" % r, "=ROUNDUP(ROUND(D%d,6),0)" % r, fmt="0")
    put(wsN, "F%d" % r, "=Входы!D%d" % (TR0 + k), fmt="0.00")
NC = {k: N0 + k for k in range(8)}   # строки переходов
SCN4 = ("BASE", "TRL7", "TRL6", "TRL5")
INTEG = ("TRL7", "TRL6", "TRL5")
LVL = {"TRL5": 5, "TRL6": 6, "TRL7": 7}
scn_code = {"BASE": "БАЗ", "TRL7": "И7", "TRL6": "И6", "TRL5": "И5"}
scn_title = {"BASE": "Базовый", "TRL7": "Интеграция TRL7", "TRL6": "Интеграция TRL6", "TRL5": "Интеграция TRL5"}
S_ROW = {}     # строки блока сценария
TC = {}        # строки календаря переходов TRL сценария
r = N0 + 10
NST = 8
for s in SCN4:
    put(wsN, "A%d" % r, "Сценарий: " + scn_title[s], F_B, border=False)
    hdr = r + 1
    for i, h in enumerate(["Стадия строительства", "Длительность, лет", "Начало, t", "Окончание, t", "Примечание"], 1):
        put(wsN, "%s%d" % (L(i), hdr), h, F_H, fill=FILL_H, align=WRAP)
    s0 = hdr + 1
    for k in range(NST):
        rr = s0 + k
        put(wsN, "A%d" % rr, STG[k], align=LEFT)
        put(wsN, "B%d" % rr, "=Входы!C%d" % (ST0 + k), fmt="0.000")
        if k == 0:
            f = "=D%d" % NC[7] if s == "BASE" else "=D%d-B%d" % (NC[LVL[s] - 2], rr)
            put(wsN, "C%d" % rr, f, fmt="0.000")
        else:
            put(wsN, "C%d" % rr, "=D%d" % (rr - 1), fmt="0.000")
        put(wsN, "D%d" % rr, "=C%d+B%d" % (rr, rr), fmt="0.000")
        note = ""
        if s == "BASE":
            if k == 0: note = "Финансирование после подтверждения TRL9"
        else:
            lv = LVL[s]
            if k == 0: note = "Непосредственно перед ПД; ПД начинается при плановом подтверждении TRL%d" % lv
            if k == 1: note = "Начало ПД = подтвержденный TRL%d (единая точка входа)" % lv
            if k == 2 and lv < 6: note = "Конец РД = подтверждение TRL6"
            if k == 4 and lv < 7: note = "Конец СМР = подтверждение TRL7"
            if k == 5: note = "Конец ПНР без нагрузки = подтверждение TRL8"
            if k == 7: note = "Конец комплексного опробования = подтверждение TRL9"
        put(wsN, "E%d" % rr, note, align=LEFT)
    put(wsN, "A%d" % (s0 + 8), "Начало финансирования f", F_B); put(wsN, "B%d" % (s0 + 8), "=C%d" % s0, F_B, "0.000")
    put(wsN, "A%d" % (s0 + 9), "Плановый ввод в эксплуатацию T_v", F_B); put(wsN, "B%d" % (s0 + 9), "=D%d" % (s0 + 7), F_B, "0.000")
    put(wsN, "A%d" % (s0 + 10), "Срок инвестиционного проекта, лет", F_B); put(wsN, "B%d" % (s0 + 10), "=B%d-B%d" % (s0 + 9, s0 + 8), F_B, "0.000")
    S_ROW[s] = dict(s0=s0, f="Сети!$B$%d" % (s0 + 8), tv="Сети!$B$%d" % (s0 + 9), st=s0)
    # календарь переходов TRL сценария
    t0 = s0 + 12
    put(wsN, "A%d" % (t0 - 1), "Календарь переходов TRL сценария (до входа — плановый календарь разработки; после входа — подтверждение по этапам строительства)", F_B, border=False)
    for i, h in enumerate(["Переход", "Длительность, лет", "Начало, t", "Подтверждение (конец), t", "Налоговый год признания", "Затраты этапа, млн руб."], 1):
        put(wsN, "%s%d" % (L(i), t0), h, F_H, fill=FILL_H, align=WRAP)
    wsN.row_dimensions[t0].height = 45
    TC[s] = {}
    st_r = lambda k: s0 + k
    for k in range(8):
        rr = t0 + 1 + k; TC[s][k] = rr
        put(wsN, "A%d" % rr, TRL[k])
        plan_c = "C%d" % NC[k]; plan_d = "D%d" % NC[k]
        c_f = "=" + plan_c; d_f = "=" + plan_d
        if s != "BASE":
            lv = LVL[s]
            if k == 4 and lv < 6: c_f = "=C%d" % st_r(1); d_f = "=D%d" % st_r(2)
            if k == 5 and lv < 7: c_f = "=C%d" % st_r(4); d_f = "=D%d" % st_r(4)
            if k == 6: c_f = "=C%d" % st_r(5); d_f = "=D%d" % st_r(5)
            if k == 7: c_f = "=C%d" % st_r(6); d_f = "=D%d" % st_r(7)
        put(wsN, "C%d" % rr, c_f, fmt="0.000"); put(wsN, "D%d" % rr, d_f, fmt="0.000")
        put(wsN, "B%d" % rr, "=D%d-C%d" % (rr, rr), fmt="0.000")
        put(wsN, "E%d" % rr, "=ROUNDUP(ROUND(D%d,6),0)" % rr, fmt="0")
        put(wsN, "F%d" % rr, "=Входы!D%d" % (TR0 + k), fmt="0.00")
    r = t0 + 11
wsN.column_dimensions["E"].width = 55

# ---------------------------------------------------------------- Расп_ и Год_
NY = P["n_years"]
Y0 = 17               # первая строка данных годовой таблицы
YL = Y0 + NY - 1
ind_cells = {}
for s in SCN4:
    c = scn_code[s]
    wsR = wb.create_sheet("Расп_" + c)
    put(wsR, "A1", "Распределение капитальных затрат по календарным годам — " + scn_title[s], F_T, border=False)
    put(wsR, "A2", "Затраты распределены равномерно по длительности этапа; доля года = пересечение этапа с годом (n−1, n] / длительность этапа.", F_ST, border=False)
    heads = ["n", "Год"] + ["Инновации: " + t for t in TRL] + ["Опытная инфраструктура", "Прочие инвестиции", "Прямые затраты доработок (ввод)", "Затраты ожидания (окна календарного плана)"]
    header(wsR, 4, heads, [6, 8] + [13] * 12, 75)
    put(wsR, "A5", "начало этапа", F_ST, border=False); put(wsR, "A6", "конец этапа", F_ST, border=False); put(wsR, "A7", "сумма, млн руб.", F_ST, border=False)
    for k in range(8):
        col = L(3 + k)
        put(wsR, "%s5" % col, "=Сети!C%d" % TC[s][k], fmt="0.000"); put(wsR, "%s6" % col, "=Сети!D%d" % TC[s][k], fmt="0.000"); put(wsR, "%s7" % col, "=Сети!F%d" % TC[s][k], fmt="0.00")
    # опытная инфраструктура: окно перехода TRL5→6 (только Базовый и Интеграция TRL7)
    put(wsR, "K5", "=Сети!C%d" % NC[4], fmt="0.000"); put(wsR, "K6", "=Сети!D%d" % NC[4], fmt="0.000")
    put(wsR, "K7", "=Pilot" if s in ("BASE", "TRL7") else 0, fmt="0.00")
    put(wsR, "L5", "=" + S_ROW[s]["f"], fmt="0.000"); put(wsR, "L6", "=" + S_ROW[s]["tv"], fmt="0.000"); put(wsR, "L7", "=B_INV", fmt="0.00")
    put(wsR, "M5", "—"); put(wsR, "M6", "—"); put(wsR, "M7", "вводится вручную", F_ST)
    if s == "BASE":
        put(wsR, "N5", "—"); put(wsR, "N6", "—"); put(wsR, "N7", "нет", F_ST)
    else:
        put(wsR, "N5", "окна", F_ST); put(wsR, "N6", "см. блок ниже", F_ST); put(wsR, "N7", "формулы", F_ST)
    # блок окон ожидания: длительность окна определяется календарным планом сценария
    W0 = 7 + NY + 4
    W_ROW = {i: W0 + 2 + i for i in range(7)}
    put(wsR, "A%d" % W0, "Окна ожидания при совмещении процессов", F_B, border=False)
    put(wsR, "A%d" % (W0 + 1), "Окно ожидания разработчика возникает, если подтверждение уровня готовности привязано к стадии строительства и наступает позже планового окончания перехода. Окно простоя оборудования возникает, если изделие готово раньше начала монтажа. Если окна нет, его длительность равна нулю и затрат нет.", F_ST, border=False)
    header(wsR, W0 + 1, ["Окно", "Начало, t", "Конец, t", "Длительность, лет", "Разовая сумма, млн руб."], None, 45)
    wnames = ["Ожидание разработчика: " + TRL[4], "Ожидание разработчика: " + TRL[5],
              "Ожидание разработчика: " + TRL[6], "Ожидание разработчика: " + TRL[7],
              "Простой готового оборудования до монтажа",
              "Демонтаж, перевозка, монтаж и верификация (разовая)",
              "Продление гарантии или ремонт (разовая)"]
    for i in range(7):
        put(wsR, "A%d" % W_ROW[i], wnames[i], align=LEFT)
    if s == "BASE":
        for i in range(7):
            for cc in ("B", "C", "D", "E"):
                put(wsR, "%s%d" % (cc, W_ROW[i]), 0, fmt="0.000")
    else:
        for j in range(4, 8):
            rr = W_ROW[j - 4]
            lag = "MAX(0,(Сети!D%d-Сети!C%d)-Сети!B%d)" % (TC[s][j], TC[s][j], NC[j])
            put(wsR, "D%d" % rr, "=" + lag, fmt="0.000")
            put(wsR, "C%d" % rr, "=Сети!D%d" % TC[s][j], fmt="0.000")
            put(wsR, "B%d" % rr, "=C%d-D%d" % (rr, rr), fmt="0.000")
            put(wsR, "E%d" % rr, 0, fmt="0.000")
        ri = W_ROW[4]
        put(wsR, "B%d" % ri, "=Сети!D%d" % TC[s][5], fmt="0.000")
        put(wsR, "C%d" % ri, "=MAX(B%d,Сети!C%d)" % (ri, S_ROW[s]["s0"] + 4), fmt="0.000")
        put(wsR, "D%d" % ri, "=C%d-B%d" % (ri, ri), fmt="0.000")
        put(wsR, "E%d" % ri, 0, fmt="0.000")
        rm = W_ROW[5]
        put(wsR, "B%d" % rm, "=C%d" % ri, fmt="0.000"); put(wsR, "C%d" % rm, "=C%d" % ri, fmt="0.000")
        put(wsR, "D%d" % rm, 0, fmt="0.000")
        put(wsR, "E%d" % rm, "=IF(D%d>0,T7_remount*B_INN,0)" % ri, fmt="0.000")
        rg = W_ROW[6]
        put(wsR, "B%d" % rg, "=" + S_ROW[s]["tv"], fmt="0.000"); put(wsR, "C%d" % rg, "=" + S_ROW[s]["tv"], fmt="0.000")
        put(wsR, "D%d" % rg, 0, fmt="0.000")
        put(wsR, "E%d" % rg, "=T7_warr_p*T7_warr_cost*B_INN", fmt="0.000")
    put(wsR, "A%d" % (W_ROW[6] + 2), "Затраты ожидания за период = T7_store · B_INN · сумма длительностей окон + разовые суммы.", F_ST, border=False)
    for n in range(1, NY + 1):
        r = 7 + n
        put(wsR, "A%d" % r, n, fmt="0"); put(wsR, "B%d" % r, "=Year_1+A%d-1" % r, fmt="0")
        for k in range(9):
            col = L(3 + k)
            put(wsR, "%s%d" % (col, r), "=IF(%s$6>%s$5,%s$7*MAX(0,MIN(%s$6,$A%d)-MAX(%s$5,$A%d-1))/(%s$6-%s$5),0)" % (col, col, col, col, r, col, r, col, col), fmt="0.000")
        # столбец L (прочие инвестиции) — индекс 12: колонки C..K это 9 (8 TRL + опыт), L — инвестиции
        put(wsR, "L%d" % r, "=IF(L$6>L$5,L$7*MAX(0,MIN(L$6,$A%d)-MAX(L$5,$A%d-1))/(L$6-L$5),0)" % (r, r), fmt="0.000")
        put(wsR, "M%d" % r, 0, F_IN, "0.000", FILL_IN)
        if s == "BASE":
            put(wsR, "N%d" % r, 0, fmt="0.000")
        else:
            ov = "+".join("MAX(0,MIN($C$%d,$A%d)-MAX($B$%d,$A%d-1))" % (W_ROW[w], r, W_ROW[w], r)
                          for w in range(5))
            put(wsR, "N%d" % r, "=T7_store*B_INN*(%s)+IF(ROUNDUP(ROUND($C$%d,9),0)=$A%d,$E$%d,0)+IF(ROUNDUP(ROUND(%s,9),0)=$A%d,$E$%d,0)"
                % (ov, W_ROW[4], r, W_ROW[5], S_ROW[s]["tv"], r, W_ROW[6]), fmt="0.000")
    # итог
    rt = 7 + NY + 1
    put(wsR, "A%d" % rt, "Итого", F_B)
    for k in range(3, 15):
        col = L(k)
        put(wsR, "%s%d" % (col, rt), "=SUM(%s8:%s%d)" % (col, col, 7 + NY), F_B, "0.00")
    wsR.freeze_panes = "C8"

    wsY = wb.create_sheet("Год_" + c)
    put(wsY, "A1", "Годовая таблица после налога — " + scn_title[s] + " (млн руб., постоянные цены, оплата в конце года)", F_T, border=False)
    meta = [("Плановый ввод T_v, t", "=" + S_ROW[s]["tv"], "0.000"), ("Задержка ввода Δ, сут. (ввод вручную; для исходов доработок)", 0, "0"),
            ("Ввод с учетом задержки, t", "=B3+B4/Days", "0.0000"), ("Целая часть m = ⌊T_v⌋", "=INT(ROUND(B5,9))", "0"),
            ("Дробная часть φ = T_v − m", "=ROUND(B5-B6,9)", "0.0000")]
    for i, (lab, v, fmt) in enumerate(meta):
        put(wsY, "A%d" % (3 + i), lab, F_B, align=LEFT)
        put(wsY, "B%d" % (3 + i), v, F_IN if i == 1 else F_N, fmt, FILL_IN if i == 1 else None)
    put(wsY, "A8", "Показатели эффективности (после налога)", F_B, border=False)
    wsY.column_dimensions["A"].width = 44
    # заголовки таблицы
    heads = ["n", "Год", "Инновационные затраты", "Опытная инфраструктура", "Прочие инвестиции", "Прямые затраты доработок и дополнительные затраты сценария", "Капитальные затраты всего",
             "Выручка", "Операционные затраты", "ТО", "ТР", "КР", "ТОиР всего", "EBITDA (выручка − Opex − ТОиР)",
             "Амортизация (налоговая)", "НИОКР, признаваемые для налога", "Налоговая база до зачета убытка",
             "Убыток на начало года", "Прирост убытка", "Предел зачета", "Использовано убытка", "Убыток на конец года",
             "Налогооблагаемая прибыль", "Налог на прибыль", "Операционный поток после налога", "Чистый денежный поток (ЧДП)", "ЧДП накопленный",
             "Коэффициент дисконтирования", "Дисконтированный ЧДП", "ДЧДП накопленный", "ПВ капитальных затрат", "ПВ операц. потока после налога",
             "Признак окупаемости PP", "Признак окупаемости DPP"]
    header(wsY, 16, heads, None, 75)
    for i in range(3, len(heads) + 1): wsY.column_dimensions[L(i)].width = 14
    wsY.column_dimensions["B"].width = 10
    def opf(key, r):
        col = OC[key]
        return "=(1-$B$7)*IF(AND($A%d-$B$6>=1,$A%d-$B$6<=Op_N),INDEX(%s,$A%d-$B$6),0)+$B$7*IF(AND($A%d-$B$6-1>=1,$A%d-$B$6-1<=Op_N),INDEX(%s,$A%d-$B$6-1),0)" % (r, r, col, r, r, r, col, r)
    for n in range(1, NY + 1):
        r = Y0 + n - 1; q = 7 + n   # строка в Расп_
        put(wsY, "A%d" % r, n, fmt="0"); put(wsY, "B%d" % r, "=Year_1+A%d-1" % r, fmt="0")
        put(wsY, "C%d" % r, "=SUM(Расп_%s!C%d:J%d)" % (c, q, q), fmt="0.00")
        put(wsY, "D%d" % r, "=Расп_%s!K%d" % (c, q), fmt="0.00")
        put(wsY, "E%d" % r, "=Расп_%s!L%d" % (c, q), fmt="0.00")
        put(wsY, "F%d" % r, "=Расп_%s!M%d+Расп_%s!N%d" % (c, q, c, q), fmt="0.00")
        put(wsY, "G%d" % r, "=SUM(C%d:F%d)" % (r, r), fmt="0.00")
        put(wsY, "H%d" % r, opf("rev", r), fmt="0.00"); put(wsY, "I%d" % r, opf("opex", r), fmt="0.00")
        put(wsY, "J%d" % r, opf("to", r), fmt="0.00"); put(wsY, "K%d" % r, opf("tr", r), fmt="0.00"); put(wsY, "L%d" % r, opf("kr", r), fmt="0.00")
        put(wsY, "M%d" % r, "=SUM(J%d:L%d)" % (r, r), fmt="0.00")
        put(wsY, "N%d" % r, "=H%d-I%d-M%d" % (r, r, r), fmt="0.00")
        put(wsY, "O%d" % r, opf("am", r), fmt="0.00")
        put(wsY, "P%d" % r, "=SUMPRODUCT((Сети!$E$%d:$E$%d=A%d)*Сети!$F$%d:$F$%d)" % (TC[s][0], TC[s][7], r, TC[s][0], TC[s][7]), fmt="0.00")
        put(wsY, "Q%d" % r, "=N%d-O%d-P%d" % (r, r, r), fmt="0.00")
        put(wsY, "R%d" % r, 0 if n == 1 else "=V%d" % (r - 1), fmt="0.00")
        put(wsY, "S%d" % r, "=MAX(-Q%d,0)" % r, fmt="0.00")
        put(wsY, "T%d" % r, "=IF(B%d<=Loss_lim_end,Loss_lim,1)" % r, fmt="0%")
        put(wsY, "U%d" % r, "=IF(Q%d>0,MIN(R%d,T%d*Q%d),0)" % (r, r, r, r), fmt="0.00")
        put(wsY, "V%d" % r, "=R%d+S%d-U%d" % (r, r, r), fmt="0.00")
        put(wsY, "W%d" % r, "=MAX(Q%d,0)-U%d" % (r, r), fmt="0.00")
        put(wsY, "X%d" % r, "=Tax_rate*W%d" % r, fmt="0.00")
        put(wsY, "Y%d" % r, "=N%d-X%d" % (r, r), fmt="0.00")
        put(wsY, "Z%d" % r, "=Y%d-G%d" % (r, r), fmt="0.00")
        put(wsY, "AA%d" % r, "=Z%d" % r if n == 1 else "=AA%d+Z%d" % (r - 1, r), fmt="0.00")
        put(wsY, "AB%d" % r, "=(1+r_disc)^(-A%d)" % r, fmt="0.0000")
        put(wsY, "AC%d" % r, "=Z%d*AB%d" % (r, r), fmt="0.00")
        put(wsY, "AD%d" % r, "=AC%d" % r if n == 1 else "=AD%d+AC%d" % (r - 1, r), fmt="0.00")
        put(wsY, "AE%d" % r, "=G%d*AB%d" % (r, r), fmt="0.00")
        put(wsY, "AF%d" % r, "=Y%d*AB%d" % (r, r), fmt="0.00")
        if n == 1:
            put(wsY, "AG%d" % r, '=""'); put(wsY, "AH%d" % r, '=""')
        else:
            put(wsY, "AG%d" % r, '=IF(AND(AA%d<0,AA%d>=0),A%d-1+(-AA%d)/Z%d,"")' % (r - 1, r, r, r - 1, r), fmt="0.000")
            put(wsY, "AH%d" % r, '=IF(AND(AD%d<0,AD%d>=0),A%d-1+(-AD%d)/AC%d,"")' % (r - 1, r, r, r - 1, r), fmt="0.000")
    rt = Y0 + NY
    put(wsY, "A%d" % rt, "Итого", F_B)
    for k in list(range(3, 16)) + [16, 19, 21, 23, 24, 25, 26, 29, 31, 32]:
        col = L(k)
        put(wsY, "%s%d" % (col, rt), "=SUM(%s%d:%s%d)" % (col, Y0, col, YL), F_B, "0.00")
    # показатели
    ind = [("ЧДД (NPV), млн руб.", "=SUM(AC%d:AC%d)" % (Y0, YL), "0.00"),
           ("Индекс доходности PI = ПВ операц. потока / ПВ капитальных затрат", "=AF%d/AE%d" % (rt, rt), "0.0000"),
           ("Срок окупаемости PP, лет от t = 0", '=IF(COUNT(AG%d:AG%d)=0,"не достигается",MIN(AG%d:AG%d))' % (Y0, YL, Y0, YL), "0.00"),
           ("Дисконтированный срок окупаемости DPP, лет от t = 0", '=IF(COUNT(AH%d:AH%d)=0,"не достигается",MIN(AH%d:AH%d))' % (Y0, YL, Y0, YL), "0.00"),
           ("Внутренняя норма доходности IRR", "=IRR(Z%d:Z%d,0.1)" % (Y0, YL), "0.00%"),
           ("Проверка: сумма признанных НИОКР = B_INN", '=IF(ABS(P%d-B_INN)<0.000001,"верно","ОШИБКА")' % rt, None),
           ("Проверка: амортизация = B_INV (без повторной амортизации инноваций)", '=IF(ABS(O%d-B_INV)<0.000001,"верно","ОШИБКА")' % rt, None),
           ("Проверка: убыток на конец горизонта = 0", '=IF(ABS(V%d)<0.000001,"верно","убыток не использован")' % YL, None)]
    # показатели размещаем справа от меты (D3:...): строки 3–10, столбец D-E
    for i, (lab, f, fmt) in enumerate(ind):
        put(wsY, "D%d" % (3 + i), lab, F_B, align=LEFT)
        wsY.merge_cells("D%d:I%d" % (3 + i, 3 + i))
        put(wsY, "J%d" % (3 + i), f, F_B, fmt, FILL_OK)
    ind_cells[s] = dict(npv="'Год_%s'!$J$3" % c, pi="'Год_%s'!$J$4" % c, pp="'Год_%s'!$J$5" % c, dpp="'Год_%s'!$J$6" % c, irr="'Год_%s'!$J$7" % c,
                        z="'Год_%s'!$Z$%d:$Z$%d" % (c, Y0, YL), a="'Год_%s'!$A$%d:$A$%d" % (c, Y0, YL), y="'Год_%s'!$Y$%d:$Y$%d" % (c, Y0, YL), g="'Год_%s'!$G$%d:$G$%d" % (c, Y0, YL))
    wsY.freeze_panes = "C17"

# ---------------------------------------------------------------- Итоги
wsT = wb.create_sheet("Итоги", 1)
put(wsT, "A1", "Итоги расчета: ЧДД после налогообложения при r = 12 %, млн руб.", F_T, border=False)
header(wsT, 3, ["Показатель", "Базовый", "Интеграция TRL7", "Интеграция TRL6", "Интеграция TRL5", "Пояснение"], [52, 18, 20, 20, 20, 70], 40)
rows_t = [("ЧДД (NPV_s,0), млн руб.", "npv", "0.00", "Без событий доработки"),
          ("Индекс доходности PI", "pi", "0.000", "ПВ операционного потока после налога / ПВ капитальных затрат"),
          ("Срок окупаемости PP, лет от начала разработки", "pp", "0.00", "Накопленный ЧДП ≥ 0, линейная интерполяция внутри года"),
          ("Дисконтированный срок окупаемости DPP, лет", "dpp", "0.00", "Накопленный дисконтированный ЧДП ≥ 0"),
          ("Внутренняя норма доходности IRR", "irr", "0.00%", "ЧДД при IRR равен нулю")]
for i, (lab, key, fmt, note) in enumerate(rows_t):
    r = 4 + i
    put(wsT, "A%d" % r, lab, align=LEFT)
    for j, s in enumerate(SCN4):
        put(wsT, "%s%d" % (L(2 + j), r), "=" + ind_cells[s][key], fmt=fmt)
    put(wsT, "F%d" % r, note, align=LEFT)
put(wsT, "A9", "Преимущество R_s = NPV_s,0 − NPV_BASE, млн руб.", F_B, align=LEFT)
put(wsT, "B9", "—")
for j in range(1, 4): put(wsT, "%s9" % L(2 + j), "=%s4-$B$4" % L(2 + j), F_B, "0.00")
put(wsT, "F9", "исходное условие", align=LEFT)
put(wsT, "A10", "Относительное преимущество R_s / B_INN × 100 %", F_B, align=LEFT)
put(wsT, "B10", "—")
for j in range(1, 4): put(wsT, "%s10" % L(2 + j), "=%s9/B_INN*100" % L(2 + j), F_B, "0.0")
put(wsT, "F10", "Знаменатель B_INN без опытной инфраструктуры", align=LEFT)
put(wsT, "A11", "Базовая точка: ЧДД Базового сценария", F_B, align=LEFT)
put(wsT, "B11", '=IF(B4>0,"положителен","ДЕФИЦИТ "&TEXT(B4,"0.00"))', F_B, fill=FILL_OK)
for j in range(1, 4): put(wsT, "%s11" % L(2 + j), "—")
put(wsT, "F11", "При дефиците расчет останавливается для согласования входов", align=LEFT)
put(wsT, "A12", "Начало финансирования f, t", align=LEFT)
put(wsT, "A13", "Плановый ввод T_v, t", align=LEFT)
put(wsT, "A14", "Подтверждение TRL9 (Базовый — опытная инфраструктура; интеграция — конец комплексного опробования), t", align=LEFT)
put(wsT, "A15", "Срок инвестиционного проекта, лет (план — 5 лет)", align=LEFT)
for j, s_ in enumerate(SCN4):
    c_ = L(2 + j)
    put(wsT, "%s12" % c_, "=" + S_ROW[s_]["f"], fmt="0.00")
    put(wsT, "%s13" % c_, "=" + S_ROW[s_]["tv"], fmt="0.00")
    put(wsT, "%s14" % c_, "=Сети!D%d" % TC[s_][7], fmt="0.00")
    put(wsT, "%s15" % c_, "=Сети!B%d" % (S_ROW[s_]["s0"] + 10), fmt="0.00")
put(wsT, "A16", "Подтверждение TRL7, t", align=LEFT)
for j, s_ in enumerate(SCN4): put(wsT, "%s16" % L(2 + j), "=Сети!D%d" % TC[s_][5], fmt="0.00")
for c_ in "CDE": wsT.column_dimensions[c_].width = 24
NPVB = "Итоги!$B$4"

# ---------------------------------------------------------------- Чувствительность к ставке (формулы)
wsC = wb.create_sheet("Чувств_ставка")
put(wsC, "A1", "Чувствительность к ставке дисконтирования 10–16 %: изменяется только коэффициент дисконтирования", F_T, border=False)
header(wsC, 3, ["Ставка r", "ЧДД Базовый", "ЧДД TRL7", "ЧДД TRL6", "ЧДД TRL5", "R_s TRL7", "R_s TRL6", "R_s TRL5",
                "R_s / B_INN TRL7, %", "R_s / B_INN TRL6, %", "R_s / B_INN TRL5, %",
                "PI Базовый", "PI TRL7", "PI TRL6", "PI TRL5", "Базовая точка (ЧДД Базового > 0)"], [10, 14, 14, 14, 14, 14, 14, 14, 16, 16, 16, 12, 12, 12, 12, 24], 60)
for i, rate in enumerate([0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16]):
    r = 4 + i
    put(wsC, "A%d" % r, rate, F_IN, "0%", FILL_IN)
    for j, s in enumerate(SCN4):
        put(wsC, "%s%d" % (L(2 + j), r), "=SUMPRODUCT(%s/(1+$A%d)^%s)" % (ind_cells[s]["z"], r, ind_cells[s]["a"]), fmt="0.00")
        put(wsC, "%s%d" % (L(12 + j), r), "=SUMPRODUCT(%s/(1+$A%d)^%s)/SUMPRODUCT(%s/(1+$A%d)^%s)" % (ind_cells[s]["y"], r, ind_cells[s]["a"], ind_cells[s]["g"], r, ind_cells[s]["a"]), fmt="0.000")
    for j in range(3):
        put(wsC, "%s%d" % (L(6 + j), r), "=%s%d-B%d" % (L(3 + j), r, r), fmt="0.00")
        put(wsC, "%s%d" % (L(9 + j), r), "=%s%d/B_INN*100" % (L(6 + j), r), fmt="0.0")
    put(wsC, "P%d" % r, '=IF(B%d>0,"положителен","ДЕФИЦИТ "&TEXT(B%d,"0.0"))' % (r, r))
put(wsC, "A12", "Контроль: значения при r = 12 % совпадают с листом «Итоги»", F_B, border=False)
put(wsC, "A13", "Разность ЧДД", F_N)
for j in range(4): put(wsC, "%s13" % L(2 + j), "=%s6-Итоги!%s4" % (L(2 + j), L(2 + j)), fmt="0.000000")
put(wsC, "A15", "Ставка, при которой R_s обращается в ноль (IRR разности потоков сценария и Базового; вне диапазона 10–16 %):", F_B, border=False)
put(wsC, "A16", "TRL7", F_N); put(wsC, "B16", "=IRR(B23:B62,0.3)", F_B, "0.00%")
put(wsC, "A17", "TRL6", F_N); put(wsC, "B17", "=IRR(C23:C62,0.3)", F_B, "0.00%")
put(wsC, "A18", "TRL5", F_N); put(wsC, "B18", "=IRR(D23:D62,0.3)", F_B, "0.00%")
put(wsC, "A21", "Разность чистых денежных потоков сценария и Базового по годам (для расчета ставки переключения)", F_B, border=False)
for j_, h_ in enumerate(["n", "TRL7 − Базовый", "TRL6 − Базовый", "TRL5 − Базовый"]): put(wsC, "%s22" % L(1 + j_), h_, F_H, fill=FILL_H, align=WRAP)
for n_ in range(1, NY + 1):
    rr_ = 22 + n_
    put(wsC, "A%d" % rr_, n_, fmt="0")
    for j_, c_ in enumerate(("И7", "И6", "И5")):
        put(wsC, "%s%d" % (L(2 + j_), rr_), "='Год_%s'!Z%d-'Год_БАЗ'!Z%d" % (c_, Y0 + n_ - 1, Y0 + n_ - 1), fmt="0.00")
put(wsC, "A19", "Внутренняя норма доходности Базового сценария", F_N); wsC.merge_cells("A19:C19"); put(wsC, "D19", "=" + ind_cells["BASE"]["irr"], F_B, "0.00%")


# ---------------------------------------------------------------- Блок расчета исхода (формулы)
BSTRIDE = 50
def make_block(ws, top, s_, title, bit_refs, evs, mult_f):
    c_ = scn_code[s_]; tv_ = S_ROW[s_]["tv"]
    put(ws, "A%d" % top, title, F_B, border=False)
    put(ws, "A%d" % (top + 1), "Множитель затрат и задержек m", align=LEFT); put(ws, "B%d" % (top + 1), mult_f, fmt="0.0000")
    dl = "+".join("%s*%s*$B$%d" % (b_, e_["delay"], top + 1) for b_, e_ in zip(bit_refs, evs))
    put(ws, "A%d" % (top + 2), "Задержка ввода Δ, сут.", align=LEFT); put(ws, "B%d" % (top + 2), "=" + dl, fmt="0.00")
    put(ws, "A%d" % (top + 3), "Ввод с учетом задержки, t", align=LEFT); put(ws, "B%d" % (top + 3), "=%s+B%d/Days" % (tv_, top + 2), fmt="0.0000")
    put(ws, "A%d" % (top + 4), "Целая часть m и дробная часть φ ввода", align=LEFT)
    put(ws, "B%d" % (top + 4), "=INT(ROUND(B%d,9))" % (top + 3), fmt="0"); put(ws, "C%d" % (top + 4), "=ROUND(B%d-B%d,9)" % (top + 3, top + 4), fmt="0.0000")
    r0_ = top + 7; rl_ = r0_ + NY - 1
    put(ws, "A%d" % (top + 5), "ЧДД исхода, млн руб.", F_B, align=LEFT); put(ws, "B%d" % (top + 5), "=SUM(R%d:R%d)" % (r0_, rl_), F_B, "0.00", FILL_OK)
    put(ws, "C%d" % (top + 5), "Остаток над Базовым", F_B, align=LEFT); put(ws, "D%d" % (top + 5), "=B%d-%s" % (top + 5, NPVB), F_B, "0.00", FILL_OK)
    for j_, h_ in enumerate(["n", "Плановые капитальные затраты", "Прямые затраты доработок", "Выручка", "Опер. затраты", "ТОиР", "Амортизация", "НИОКР, признаваемые для налога",
                             "EBITDA", "Налоговая база до зачета", "Убыток на начало", "Прирост убытка", "Предел зачета", "Использовано убытка", "Убыток на конец", "Налог", "ЧДП", "Дисконтированный ЧДП"]):
        put(ws, "%s%d" % (L(1 + j_), top + 6), h_, F_H, fill=FILL_H, align=WRAP)
    ws.row_dimensions[top + 6].height = 45
    mm_ = "$B$%d" % (top + 4); ph_ = "$C$%d" % (top + 4)
    def opf_(rng, r):
        return ("=(1-%s)*IF(AND($A%d-%s>=1,$A%d-%s<=Op_N),INDEX(%s,$A%d-%s),0)+%s*IF(AND($A%d-%s-1>=1,$A%d-%s-1<=Op_N),INDEX(%s,$A%d-%s-1),0)"
                % (ph_, r, mm_, r, mm_, rng, r, mm_, ph_, r, mm_, r, mm_, rng, r, mm_))
    for n_ in range(1, NY + 1):
        r = r0_ + n_ - 1; yr = Y0 + n_ - 1
        put(ws, "A%d" % r, n_, fmt="0")
        put(ws, "B%d" % r, "='Год_%s'!G%d" % (c_, yr), fmt="0.00")
        ex = "+".join("%s*%s*$B$%d*(ROUNDUP(ROUND(%s,9),0)=$A%d)" % (b_, e_["cost"], top + 1, e_["t"], r) for b_, e_ in zip(bit_refs, evs))
        put(ws, "C%d" % r, "=" + ex, fmt="0.00")
        put(ws, "D%d" % r, opf_(OC["rev"], r), fmt="0.00"); put(ws, "E%d" % r, opf_(OC["opex"], r), fmt="0.00")
        put(ws, "F%d" % r, opf_(OC["toir"], r), fmt="0.00"); put(ws, "G%d" % r, opf_(OC["am"], r), fmt="0.00")
        put(ws, "H%d" % r, "='Год_%s'!P%d" % (c_, yr), fmt="0.00")
        put(ws, "I%d" % r, "=D%d-E%d-F%d" % (r, r, r), fmt="0.00")
        put(ws, "J%d" % r, "=I%d-G%d-H%d" % (r, r, r), fmt="0.00")
        put(ws, "K%d" % r, 0 if n_ == 1 else "=O%d" % (r - 1), fmt="0.00")
        put(ws, "L%d" % r, "=MAX(-J%d,0)" % r, fmt="0.00")
        put(ws, "M%d" % r, "='Год_%s'!T%d" % (c_, yr), fmt="0%")
        put(ws, "N%d" % r, "=IF(J%d>0,MIN(K%d,M%d*J%d),0)" % (r, r, r, r), fmt="0.00")
        put(ws, "O%d" % r, "=K%d+L%d-N%d" % (r, r, r), fmt="0.00")
        put(ws, "P%d" % r, "=Tax_rate*(MAX(J%d,0)-N%d)" % (r, r), fmt="0.00")
        put(ws, "Q%d" % r, "=I%d-P%d-B%d-C%d" % (r, r, r, r), fmt="0.00")
        put(ws, "R%d" % r, "=Q%d*'Год_%s'!AB%d" % (r, c_, yr), fmt="0.00")
    return "'%s'!$B$%d" % (ws.title, top + 5)
def setup_block_sheet(ws, title):
    put(ws, "A1", title, F_T, border=False)
    ws.column_dimensions["A"].width = 44
    for i_ in range(2, 19): ws.column_dimensions[L(i_)].width = 14

# ---------------------------------------------------------------- События
wsV = wb.create_sheet("События")
put(wsV, "A1", "Исходы событий доработки TRL6–TRL9. Параметры событий зависят от точки входа (доля незафиксированных параметров φ). Вероятности, суммы и годовые расчеты ЧДД исходов (листы «Исходы_…») — формулы", F_T, border=False)
put(wsV, "A2", "Модель суммирования: события независимы; прямые затраты суммируются (совокупные затраты каждого события уже включают все его составляющие, повторно не добавляются); задержки ввода суммируются, так как все события лежат на одной критической цепи без запаса времени.", F_ST, border=False)
row = 4
EVT = {}
for s in INTEG:
    o = R["scn"][s]["out"]
    wsB = wb.create_sheet("Исходы_" + scn_code[s])
    setup_block_sheet(wsB, "Годовые расчеты исходов доработок — " + scn_title[s] + " (формулы; события и их параметры берутся с листа «События»)")
    put(wsV, "A%d" % row, "Сценарий: " + scn_title[s], F_B, border=False)
    row += 1
    for i, h in enumerate(["Событие", "Момент, t", "Вероятность", "Затраты, млн руб.", "Задержка, сут.", "Затронутые работы"], 1):
        put(wsV, "%s%d" % (L(i), row), h, F_H, fill=FILL_H, align=WRAP)
    ev0 = row + 1
    for e in o["events"]:
        row += 1
        k = e["k"]
        put(wsV, "A%d" % row, "TRL%d" % k)
        put(wsV, "B%d" % row, "=Сети!D%d" % TC[s][k - 2], fmt="0.00")
        ph = {"TRL5": "Phi5", "TRL6": "Phi6", "TRL7": "Phi7"}[s]
        put(wsV, "C%d" % row, "=MIN(1,Входы!B%d/100*%s/Phi6)" % (EVR[k], ph), fmt="0.00%")
        if k == 6 and s == "TRL5":
            cf = "=(Phi5*Sigma_m+Exp_share*PD_part)*PIR_share*B_INV"
            df = "=Phi5*Sigma_m*(Входы!C%d+Входы!C%d)*Days+Exp_days" % (ST0 + 1, ST0 + 2)
        else:
            cf = "=Входы!C%d" % EVR[k]; df = "=Входы!D%d" % EVR[k]
        put(wsV, "D%d" % row, cf if e["aff"] else 0, fmt="0.00")
        put(wsV, "E%d" % row, df if e["aff"] else 0, fmt="0")
        put(wsV, "F%d" % row, e["desc"], align=LEFT)
    row += 2
    active = [e for e in o["events"] if e["aff"]]
    na = len(active)
    hd = ["№ исхода"] + ["TRL%d" % e["k"] for e in active] + ["Вероятность исхода", "Прямые затраты, млн руб.", "Задержка ввода, сут.", "Новый ввод, t", "ЧДД исхода, млн руб.", "Ущерб = NPV_s,0 − ЧДД исхода", "Остаток R_ост = ЧДД исхода − NPV_BASE", "R_ост / B_INN, %", "R_ост / R_s, %"]
    for i, h in enumerate(hd, 1): put(wsV, "%s%d" % (L(i), row), h, F_H, fill=FILL_H, align=WRAP)
    wsV.row_dimensions[row].height = 60
    hdr = row
    # события для связи: строки ev0..ev0+4 (TRL5..9) — активные начинаются с TRL6
    ev_rows = {e["k"]: ev0 + (e["k"] - 5) for e in o["events"]}
    items = sorted(o["items"], key=lambda it: it["combo"])
    pc = L(2 + na)
    for idx, it in enumerate(items):
        row += 1
        put(wsV, "A%d" % row, idx + 1, fmt="0")
        for j, e in enumerate(active):
            put(wsV, "%s%d" % (L(2 + j), row), it["combo"][j], F_IN, "0", FILL_IN)
        # вероятность
        terms = []
        for j, e in enumerate(active):
            c = "%s%d" % (L(2 + j), row); pr = "$C$%d" % ev_rows[e["k"]]
            terms.append("IF(%s=1,%s,1-%s)" % (c, pr, pr))
        put(wsV, "%s%d" % (pc, row), "=" + "*".join(terms), fmt="0.000000")
        cs = "+".join("%s%d*$D$%d" % (L(2 + j), row, ev_rows[e["k"]]) for j, e in enumerate(active))
        ds = "+".join("%s%d*$E$%d" % (L(2 + j), row, ev_rows[e["k"]]) for j, e in enumerate(active))
        cc = L(3 + na); dc = L(4 + na); tc = L(5 + na); nc = L(6 + na); lc = L(7 + na); rc = L(8 + na); r1 = L(9 + na); r2 = L(10 + na)
        put(wsV, "%s%d" % (cc, row), "=" + cs, fmt="0.00"); put(wsV, "%s%d" % (dc, row), "=" + ds, fmt="0")
        put(wsV, "%s%d" % (tc, row), "=%s+%s%d/Days" % (S_ROW[s]["tv"], dc, row), fmt="0.000")
        evs_ = [dict(t="События!$B$%d" % ev_rows[e["k"]], cost="События!$D$%d" % ev_rows[e["k"]], delay="События!$E$%d" % ev_rows[e["k"]]) for e in active]
        bits_ = ["События!$%s$%d" % (L(2 + j), row) for j in range(na)]
        npv_ref = make_block(wsB, 3 + idx * BSTRIDE, s, "Исход № %d сценария %s" % (idx + 1, scn_title[s]), bits_, evs_, 1)
        put(wsV, "%s%d" % (nc, row), "=" + npv_ref, fmt="0.00")
        put(wsV, "%s%d" % (lc, row), "=%s-%s%d" % (ind_cells[s]["npv"], nc, row), fmt="0.00")
        put(wsV, "%s%d" % (rc, row), "=%s%d-%s" % (nc, row, NPVB), fmt="0.00")
        put(wsV, "%s%d" % (r1, row), "=%s%d/B_INN*100" % (rc, row), fmt="0.0")
        put(wsV, "%s%d" % (r2, row), "=%s%d/(%s-%s)*100" % (rc, row, ind_cells[s]["npv"], NPVB), fmt="0.0")
    first, last = hdr + 1, row
    row += 1
    put(wsV, "A%d" % row, "Итого / ожидание", F_B)
    put(wsV, "%s%d" % (pc, row), "=SUM(%s%d:%s%d)" % (pc, first, pc, last), F_B, "0.000000")
    put(wsV, "%s%d" % (nc, row), "=SUMPRODUCT(%s%d:%s%d,%s%d:%s%d)" % (pc, first, pc, last, nc, first, nc, last), F_B, "0.00")
    put(wsV, "%s%d" % (lc, row), "=SUMPRODUCT(%s%d:%s%d,%s%d:%s%d)" % (pc, first, pc, last, lc, first, lc, last), F_B, "0.00")
    put(wsV, "%s%d" % (rc, row), "=SUMPRODUCT(%s%d:%s%d,%s%d:%s%d)" % (pc, first, pc, last, rc, first, rc, last), F_B, "0.00")
    put(wsV, "%s%d" % (r1, row), "=%s%d/B_INN*100" % (rc, row), F_B, "0.0")
    EVT[s] = dict(first=first, last=last, tot=row, cols=dict(p=pc, c=cc, d=dc, t=tc, n=nc, l=lc, r=rc, r1=r1, r2=r2), na=na, ev_rows=ev_rows,
                  active=[e["k"] for e in active])
    row += 1
    put(wsV, "A%d" % row, "Наименьший остаток по исходам", F_B)
    put(wsV, "%s%d" % (rc, row), "=MIN(%s%d:%s%d)" % (rc, first, rc, last), F_B, "0.00")
    row += 3
wsV.column_dimensions["A"].width = 12
for i in range(2, 16): wsV.column_dimensions[L(i)].width = 15

# ---------------------------------------------------------------- Пояснения и порядок листов
wsX = wb.create_sheet("Пояснения", 0)
put(wsX, "A1", "Модель интеграции инновационного и инвестиционного проектов. Листы и условные обозначения", F_T, border=False)
lines = [
 ("Входы", "Все входные данные; желтые ячейки можно изменять."),
 ("Итоги", "ЧДД, PI, PP, DPP, IRR четырех сценариев; преимущество R_s; базовая точка; место и срок подтверждения TRL9."),
 ("Сети", "Плановый календарь TRL; стадии строительства (8 стадий) и календарь подтверждения TRL для четырех сценариев; вход — начало проектной документации."),
 ("Эксплуатация", "Плановые потоки по годам эксплуатации (выручка, затраты, ТОиР, амортизация)."),
 ("Расп_БАЗ, Расп_И7, Расп_И6, Расп_И5", "Распределение капитальных затрат по календарным годам."),
 ("Год_БАЗ, Год_И7, Год_И6, Год_И5", "Годовые таблицы после налога: капитальные затраты, EBITDA, налоговая база, перенос убытка, налог, потоки, дисконтирование. Ячейка «Задержка ввода» и столбец «Прямые затраты доработок» позволяют воспроизвести любой исход."),
 ("Чувств_ставка", "ЧДД и преимущество при ставке 10–16 %, ставка переключения (IRR разности потоков); формулы."),
 ("События, Исходы_И5, Исходы_И6, Исходы_И7", "Исходы доработок TRL6–TRL9: вероятности, затраты, задержки; полный годовой расчет каждого исхода; остатки преимущества."),
 ("Точки входа, Устойчивость", "Сравнение четырех вариантов: цена ускорения, критический множитель m* (метод секущих, годовые расчеты), многокритериальная оценка по шести критериям, чувствительность к весам."),
 ("Пороги", "Порог безразличия TRL5/TRL6: допустимый ожидаемый ущерб от доработки ПД и РД."),
 ("Обозначения", "INN — инновационный проект; INV — прочая инвестиционная часть; BASE — Базовый сценарий; NPV — чистый дисконтированный доход (ЧДД); PI — индекс доходности; PP/DPP — простой/дисконтированный срок окупаемости; IRR — внутренняя норма доходности."),
 ("Цвета", "Синий шрифт на желтом фоне — ввод; черный — формула. Все остальные значения вычисляются формулами и пересчитываются при изменении входных данных."),
]
for i, (a, b) in enumerate(lines):
    put(wsX, "A%d" % (3 + i), a, F_B, align=LEFT); put(wsX, "B%d" % (3 + i), b, align=LEFT)
wsX.column_dimensions["A"].width = 30; wsX.column_dimensions["B"].width = 120


# ---------------------------------------------------------------- Устойчивость: критический множитель m* (метод секущих)
wsU = wb.create_sheet("Устойчивость")
setup_block_sheet(wsU, "Критический множитель m* затрат и задержек доработок (все события наступают; остаток над Базовым = 0). Метод секущих: каждая итерация — полный годовой расчет")
NIT = 8
UB = {}
U0 = 14
for si, s_ in enumerate(INTEG):
    e_ = EVT[s_]
    evs_ = [dict(t="События!$B$%d" % e_["ev_rows"][k], cost="События!$D$%d" % e_["ev_rows"][k], delay="События!$E$%d" % e_["ev_rows"][k]) for k in e_["active"]]
    UB[s_] = []
    for it_ in range(NIT):
        top = U0 + (si * NIT + it_) * BSTRIDE
        if it_ == 0: mf = 1
        elif it_ == 1: mf = 2
        else:
            p1, p2 = UB[s_][it_ - 1], UB[s_][it_ - 2]
            mf = "=IF(ABS(D%d-D%d)<0.000000000001,B%d,B%d-D%d*(B%d-B%d)/(D%d-D%d))" % (p1 + 5, p2 + 5, p1 + 1, p1 + 1, p1 + 5, p1 + 1, p2 + 1, p1 + 5, p2 + 5)
        make_block(wsU, top, s_, "%s: итерация %d" % (scn_title[s_], it_ + 1), ["1"] * len(evs_), evs_, mf)
        UB[s_].append(top)
header(wsU, 3, ["Сценарий", "Множитель m*", "Остаток при m* (контроль → 0), млн руб.", "Остаток при m = 1, млн руб.", "Суммарные затраты при m*, млн руб.", "Суммарная задержка при m*, сут."], None, 60)
for si, s_ in enumerate(INTEG):
    r = 4 + si; tl = UB[s_][-1]; t0 = UB[s_][0]
    put(wsU, "A%d" % r, scn_title[s_], align=LEFT)
    put(wsU, "B%d" % r, "=B%d" % (tl + 1), F_B, "0.0000", FILL_OK)
    put(wsU, "C%d" % r, "=D%d" % (tl + 5), fmt="0.000000"); put(wsU, "D%d" % r, "=D%d" % (t0 + 5), fmt="0.00")
    put(wsU, "E%d" % r, "=SUM(C%d:C%d)" % (tl + 7, tl + 6 + NY) , fmt="0.0"); put(wsU, "F%d" % r, "=B%d" % (tl + 2), fmt="0")
wsU.freeze_panes = "B4"

# ---------------------------------------------------------------- Точки входа
EP = R["entry"]; S1 = json.load(open("stage1.json"))
wsE = wb.create_sheet("Точки входа")
put(wsE, "A1", "Сравнение точек входа инновационного проекта в инвестиционный (раздел 3.4.5). Вводятся только веса и балльные оценки (желтый фон).", F_T, border=False)
heads = ["Вариант", "ЧДД, млн руб.", "Ввод T_v, лет", "Преимущество R, млн руб.", "Сокращение срока ΔT, лет", "Цена ускорения R/ΔT, млн руб./год", "Остаток Q в наихудшем исходе, млн руб.", "Критический множитель m*",
         "Балл: ЧДД", "Балл: срок", "Балл: остаток", "Балл: устойчивость", "Доказательность TRL (1–5)", "Ресурсная нагрузка (1–5)", "Балл: доказательность", "Балл: нагрузка", "Интегральная оценка"]
header(wsE, 3, heads, [24, 13, 12, 15, 14, 17, 18, 13, 11, 11, 11, 13, 15, 15, 13, 13, 14], 75)
n = len(EP["opts"]); r1 = 4; rn = r1 + n - 1
nm = lambda col, r: "(%s%d-MIN($%s$%d:$%s$%d))/(MAX($%s$%d:$%s$%d)-MIN($%s$%d:$%s$%d))*100" % (col, r, col, r1, col, rn, col, r1, col, rn, col, r1, col, rn)
rw = rn + 2
ITOG_COL = {"BASE": "B", "TRL7": "C", "TRL6": "D", "TRL5": "E"}
for i, d in enumerate(EP["opts"]):
    r = r1 + i; s_ = SCN4[i]
    put(wsE, "A%d" % r, d["label"], align=LEFT)
    put(wsE, "B%d" % r, "=Итоги!%s4" % ITOG_COL[s_], fmt="0.00"); put(wsE, "C%d" % r, "=" + S_ROW[s_]["tv"], fmt="0.00")
    put(wsE, "D%d" % r, "=B%d-$B$%d" % (r, r1), fmt="0.00"); put(wsE, "E%d" % r, "=$C$%d-C%d" % (r1, r), fmt="0.00")
    put(wsE, "F%d" % r, '=IF(E%d>0,D%d/E%d,"—")' % (r, r, r), fmt="0.0")
    if s_ == "BASE":
        put(wsE, "G%d" % r, 0, fmt="0.00"); put(wsE, "H%d" % r, "=MAX(H%d:H%d)" % (r1 + 1, rn), fmt="0.000")
    else:
        ee = EVT[s_]
        put(wsE, "G%d" % r, "=События!%s%d" % (ee["cols"]["r"], ee["tot"] + 1), fmt="0.00")
        put(wsE, "H%d" % r, "=Устойчивость!B%d" % (4 + INTEG.index(s_)), fmt="0.000")
    put(wsE, "I%d" % r, "=" + nm("B", r), fmt="0.0")
    put(wsE, "J%d" % r, "=100-(" + nm("C", r) + ")", fmt="0.0")
    put(wsE, "K%d" % r, "=" + nm("G", r), fmt="0.0"); put(wsE, "L%d" % r, "=" + nm("H", r), fmt="0.0")
    put(wsE, "M%d" % r, d["qual"][0], F_IN, "0", FILL_IN); put(wsE, "N%d" % r, d["qual"][1], F_IN, "0", FILL_IN)
    put(wsE, "O%d" % r, "=(M%d-1)/4*100" % r, fmt="0.0"); put(wsE, "P%d" % r, "=(N%d-1)/4*100" % r, fmt="0.0")
    put(wsE, "Q%d" % r, "=I%d*$B$%d+J%d*$C$%d+K%d*$D$%d+O%d*$E$%d+P%d*$F$%d+L%d*$G$%d" % (r, rw + 2, r, rw + 2, r, rw + 2, r, rw + 2, r, rw + 2, r, rw + 2), F_B, "0.00")
put(wsE, "A%d" % rw, "Веса критериев (сумма 1)", F_B, border=False)
for j, h in enumerate(["ЧДД", "Срок ввода", "Остаток", "Доказательность", "Нагрузка", "Устойчивость", "Сумма"]):
    put(wsE, "%s%d" % (L(2 + j), rw + 1), h, F_H, fill=FILL_H, align=WRAP)
put(wsE, "A%d" % (rw + 2), "Вес w", align=LEFT)
for j, w in enumerate(EP["weights"]): put(wsE, "%s%d" % (L(2 + j), rw + 2), w, F_IN, "0.00", FILL_IN)
put(wsE, "H%d" % (rw + 2), "=SUM(B%d:G%d)" % (rw + 2, rw + 2), F_B, "0.00")
rs = rw + 4
put(wsE, "A%d" % rs, "Чувствительность к весам", F_B, border=False)
put(wsE, "A%d" % (rs + 1), "Набор весов", F_H, fill=FILL_H, align=WRAP)
for j in range(6): put(wsE, "%s%d" % (L(2 + j), rs + 1), EP["crit_names"][j], F_H, fill=FILL_H, align=WRAP)
for j, d in enumerate(EP["opts"]): put(wsE, "%s%d" % (L(8 + j), rs + 1), "Оценка: " + d["label"], F_H, fill=FILL_H, align=WRAP)
put(wsE, "%s%d" % (L(8 + len(EP["opts"])), rs + 1), "Лучший вариант", F_H, fill=FILL_H, align=WRAP)
wsE.row_dimensions[rs + 1].height = 45
for i, (k, v) in enumerate(EP["wsets"].items()):
    r = rs + 2 + i
    put(wsE, "A%d" % r, k, align=LEFT)
    for j, w in enumerate(v["w"]): put(wsE, "%s%d" % (L(2 + j), r), w, F_IN, "0.00", FILL_IN)
    for j in range(n):
        ro = r1 + j
        put(wsE, "%s%d" % (L(8 + j), r), "=$I$%d*$B%d+$J$%d*$C%d+$K$%d*$D%d+$O$%d*$E%d+$P$%d*$F%d+$L$%d*$G%d" % (ro, r, ro, r, ro, r, ro, r, ro, r, ro, r), fmt="0.0")
    put(wsE, "%s%d" % (L(8 + n), r), "=INDEX($A$%d:$A$%d,MATCH(MAX(H%d:K%d),H%d:K%d,0))" % (r1, rn, r, r, r, r))
rg = rs + 2 + len(EP["wsets"]) + 1
put(wsE, "A%d" % rg, "Область весов: суммарный вес критериев «остаток» и «устойчивость» (поровну), остальные веса пропорциональны базовым", F_B, border=False)
for j, h in enumerate(["Суммарный вес"] + ["Оценка: " + d["label"] for d in EP["opts"]] + ["Лучший вариант"]):
    put(wsE, "%s%d" % (L(1 + j), rg + 1), h, F_H, fill=FILL_H, align=WRAP)
W_ = rw + 2
so = "($B$%d+$C$%d+$E$%d+$F$%d)" % (W_, W_, W_, W_)
for i, g in enumerate(EP["w_rob_grid"]):
    r = rg + 2 + i
    put(wsE, "A%d" % r, g["wt"], F_IN, "0.00", FILL_IN)
    for j in range(n):
        ro = r1 + j
        f = "=$I$%d*(1-$A%d)*$B$%d/%s+$J$%d*(1-$A%d)*$C$%d/%s+$K$%d*$A%d/2+$O$%d*(1-$A%d)*$E$%d/%s+$P$%d*(1-$A%d)*$F$%d/%s+$L$%d*$A%d/2" % (
            ro, r, W_, so, ro, r, W_, so, ro, r, ro, r, W_, so, ro, r, W_, so, ro, r)
        put(wsE, "%s%d" % (L(2 + j), r), f, fmt="0.0")
    put(wsE, "%s%d" % (L(2 + n), r), "=INDEX($B$%d:$E$%d,1,MATCH(MAX(B%d:E%d),B%d:E%d,0))" % (rg + 1, rg + 1, r, r, r, r))
rgl = rg + 1 + len(EP["w_rob_grid"]); rgf = rg + 2
put(wsE, "A%d" % (rgl + 1), "Вес устойчивости, при котором выбор TRL5 → TRL6 меняется", F_B, align=LEFT)
put(wsE, "B%d" % (rgl + 1), "=A%d+(0-(E%d-D%d))*(A%d-A%d)/((E%d-D%d)-(E%d-D%d))" % (rgf, rgf, rgf, rgl, rgf, rgl, rgl, rgf, rgf), F_B, "0.000", FILL_OK)
rc = rgl + 3
put(wsE, "A%d" % rc, "Критический множитель затрат и задержек доработок (остаток Q в наихудшем исходе = 0)", F_B, border=False)
for j, h in enumerate(["Вариант", "Множитель m*", "Суммарные затраты при m*, млн руб.", "Суммарная задержка при m*, дней", "Остаток при m = 1, млн руб."]):
    put(wsE, "%s%d" % (L(1 + j), rc + 1), h, F_H, fill=FILL_H, align=WRAP)
wsE.row_dimensions[rc + 1].height = 60
for i, s_ in enumerate(INTEG):
    r = rc + 2 + i
    put(wsE, "A%d" % r, scn_title[s_], align=LEFT)
    for j, col in enumerate("BEFD"):
        put(wsE, "%s%d" % (L(2 + j), r), "=Устойчивость!%s%d" % (col, 4 + i), fmt=["0.000", "0.0", "0", "0.00"][j])
put(wsE, "A%d" % (rc + 6), "Балльные оценки доказательности (K) и ресурсной нагрузки (L) заданы по шкалам 1–5 (5 — наилучшее).", F_N, border=False)
wsE.freeze_panes = "B4"
ENTRY_POS = dict(rw=rw, rs=rs, rg=rg, rc=rc, rgl=rgl)

# ---------------------------------------------------------------- Пороги
wsP = wb.create_sheet("Пороги")
put(wsP, "A1", "Порог безразличия между точками входа TRL5 и TRL6 (раздел 3.4.5).", F_T, border=False)
e5 = EVT["TRL5"]; e6 = EVT["TRL6"]; k6 = e5["ev_rows"][6]
bc = [L(2 + j) for j in range(e5["na"])]
rng = lambda c: "События!$%s$%d:$%s$%d" % (c, e5["first"], c, e5["last"])
pc5, lc5 = e5["cols"]["p"], e5["cols"]["l"]
rows_p = [("Разность ЧДД без событий TRL5 − TRL6, млн руб.", "=Итоги!E4-Итоги!D4", "0.00"),
          ("Ожидаемые потери TRL6 от доработок, млн руб.", "=События!%s%d" % (e6["cols"]["l"], e6["tot"]), "0.00"),
          ("Ожидаемые потери TRL5 без события TRL6, млн руб.", "=SUMPRODUCT((%s=0)*%s*%s)/(1-События!$C$%d)" % (rng(bc[0]), rng(pc5), rng(lc5), k6), "0.00"),
          ("Порог X: TRL5 лучше TRL6, пока вероятность × ущерб от события TRL6 меньше, млн руб.", "=B3+B4-B5", "0.00"),
          ("Ущерб от события TRL6 при входе TRL5 (потеря ЧДД), млн руб.", "=SUMPRODUCT((%s=1)*(%s=0)*(%s=0)*(%s=0)*%s)" % (rng(bc[0]), rng(bc[1]), rng(bc[2]), rng(bc[3]), rng(lc5)), "0.00"),
          ("в том числе прямые затраты, млн руб.", "=События!$D$%d" % k6, "0.00"), ("в том числе задержка, сут.", "=События!$E$%d" % k6, "0"),
          ("Расчетная вероятность события TRL6 при входе TRL5", "=События!$C$%d" % k6, "0.00"),
          ("Расчетный ожидаемый ущерб, млн руб.", "=B10*B7", "0.00"),
          ("Безразличная вероятность при расчетном ущербе", "=B6/B7", "0.00")]
for i, (a, v, f) in enumerate(rows_p):
    put(wsP, "A%d" % (3 + i), a, align=LEFT); put(wsP, "B%d" % (3 + i), v, F_B, f, FILL_OK)
wsP.column_dimensions["A"].width = 78
for c_ in "BCDEF": wsP.column_dimensions[c_].width = 18

# ---------------------------------------------------------------- Пояснения (обновление списка листов)
order = ["Пояснения", "Итоги", "Входы", "Сети", "Эксплуатация", "Расп_БАЗ", "Год_БАЗ", "Расп_И5", "Год_И5", "Расп_И6", "Год_И6", "Расп_И7", "Год_И7", "Чувств_ставка", "События", "Исходы_И7", "Исходы_И6", "Исходы_И5", "Устойчивость", "Точки входа", "Пороги"]
wb._sheets = [wb[n] for n in order]
for ws in wb.worksheets:
    ws.sheet_view.zoomScale = 90
    ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
wb.save("TRL_model.xlsx")
json.dump(dict(EVT={k:{kk:vv for kk,vv in v.items() if kk not in ('ev_rows',)} for k,v in EVT.items()}, EPOS=ENTRY_POS, Y0=Y0, YL=YL, NY=NY, NC=NC, S_ROW=S_ROW, TC=TC), open("xl_layout.json", "w"))
print("saved")

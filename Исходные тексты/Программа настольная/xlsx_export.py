# -*- coding: utf-8 -*-
# Автор и разработчик: Postautov_K_V
"""Выгрузка расчета в книгу Excel с действующими формулами.

Книга пересчитывается средствами Excel: изменение значения на листе «Входы» меняет
календарный план, годовые потоки, показатели эффективности и чувствительность.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName

import model_core as M
import calc as CA

SC = CA.SC
SCL = CA.SCL
CODE = CA.CODE

F_T = Font(name="Times New Roman", size=12, bold=True)
F_H = Font(name="Times New Roman", size=10, bold=True, color="FFFFFF")
F_N = Font(name="Times New Roman", size=10)
F_B = Font(name="Times New Roman", size=10, bold=True)
FILL_H = PatternFill("solid", fgColor="1D3A5C")
FILL_IN = PatternFill("solid", fgColor="FFF4D6")
FILL_OK = PatternFill("solid", fgColor="EAF3EA")
FILL_G = PatternFill("solid", fgColor="F2F2EE")
THIN = Side(style="thin", color="C9C7C1")
BRD = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
LEFT = Alignment(horizontal="left", vertical="top", wrap_text=True)
CTR = Alignment(horizontal="center", vertical="center", wrap_text=True)


def put(ws, ref, v, font=F_N, fmt=None, fill=None, align=None):
    c = ws[ref]
    c.value = v
    c.font = font
    c.border = BRD
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    c.alignment = align or Alignment(vertical="center")
    return c


def header(ws, row, heads, widths=None, height=42):
    for i, h in enumerate(heads):
        c = ws.cell(row=row, column=i + 1, value=h)
        c.font = F_H
        c.fill = FILL_H
        c.border = BRD
        c.alignment = CTR
    ws.row_dimensions[row].height = height
    if widths:
        for i, w in enumerate(widths):
            ws.column_dimensions[L(i + 1)].width = w


# ------------------------------------------------------------------ выражения
def ov(a, b, n):
    """Пересечение отрезка [a;b] с годом (n-1;n] поэлементно (без функций MIN и MAX)."""
    hi = "((%s+%s-ABS(%s-%s))/2)" % (b, n, b, n)
    lo = "((%s+(%s-1)+ABS(%s-(%s-1)))/2)" % (a, n, a, n)
    d = "(%s-%s)" % (hi, lo)
    return "((%s+ABS(%s))/2)" % (d, d)


def build(state, R, path):
    wb = Workbook()
    nm = {}

    def defname(name, sheet, ref):
        nm[name] = "'%s'!%s" % (sheet, ref)
        wb.defined_names.add(DefinedName(name, attr_text=nm[name]))

    # ------------------------------------------------------------ Входы
    ws = wb.active
    ws.title = "Входы"
    put(ws, "A1", "Входные данные модели", F_T)
    ws["A1"].border = Border()
    header(ws, 2, ["Параметр", "Значение", "Обозначение"], [62, 16, 18], 20)
    scal = [
        ("budget", "BUDGET", "Бюджет проекта, млн руб.", "0"),
        ("share_inn", "SHARE_INN", "Доля инновационной части в бюджете, %", "0.0%"),
        ("rate", "RATE", "Ставка дисконтирования, % годовых", "0.0%"),
        ("t_dev", "T_DEV", "Срок разработки от TRL1 до TRL9, лет", "0.00"),
        ("t_inv", "T_INV", "Срок строительства, лет", "0.00"),
        ("n_years", "N_YEARS", "Расчетный период, лет от начала разработки", "0"),
        ("first_tax_year", "FIRST_YEAR", "Первый расчетный год", "0"),
        ("op_years", "OP_YEARS", "Срок эксплуатации объекта, лет от ввода", "0"),
        ("revenue", "REVENUE", "Выручка при полной загрузке, млн руб. в год", "0.0"),
        ("staff", "STAFF", "Численность персонала, человек", "0"),
        ("salary_k", "SALARY", "Средняя заработная плата одного работника, тыс. руб. в месяц", "0.0"),
        ("markup", "MARKUP", "Начисления на заработную плату, % фонда оплаты труда", "0.0%"),
        ("admin", "ADMIN", "Административные расходы, % фонда оплаты труда", "0.0%"),
        ("to_rate", "TO_RATE", "Техническое обслуживание, % бюджета проекта в год", "0.00%"),
        ("tr_rate", "TR_RATE", "Текущий ремонт, % бюджета проекта за один ремонт", "0.00%"),
        ("kr_rate", "KR_RATE", "Капитальный ремонт, % бюджета проекта за один ремонт", "0.00%"),
        ("tax", "TAX", "Ставка налога на прибыль, %", "0.0%"),
        ("amort_years", "AMORT_YEARS", "Срок амортизации инвестиционной части, лет", "0"),
        ("loss_limit", "LOSS_LIMIT", "Предел зачета убытка, % налоговой базы", "0.0%"),
        ("loss_limit_last_n", "LOSS_N", "Предел зачета убытка действует в первые N лет расчетного периода", "0"),
        ("pilot_share", "PILOT_SHARE", "Опытная инфраструктура, % инновационной части", "0.0%"),
        ("t7_store", "T7_STORE", "Хранение и консервация, % инновационной части в год", "0.00%"),
        ("t7_remount", "T7_REMOUNT", "Демонтаж, перевозка, монтаж и верификация, % инновационной части", "0.00%"),
        ("t7_warr_p", "T7_WARR_P", "Вероятность окончания гарантии до ввода, %", "0.0%"),
        ("t7_warr_cost", "T7_WARR_COST", "Продление гарантии или ремонт, % инновационной части", "0.00%"),
    ]
    r = 3
    for key, name, title, fmt in scal:
        put(ws, "A%d" % r, title, align=LEFT)
        put(ws, "B%d" % r, state[key], F_B, fmt, FILL_IN)
        put(ws, "C%d" % r, name, F_N, align=CTR)
        defname(name, "Входы", "$B$%d" % r)
        r += 1
    # векторы
    r += 1
    vec_start = r
    put(ws, "A%d" % r, "Векторные параметры", F_T)
    r += 1
    header(ws, r, ["Номер", "Доли времени переходов TRL, %", "Доли инновационных затрат по переходам, %",
                   "Доли времени стадий строительства, %"], [62, 16, 18, 22], 44)
    vr = r + 1
    for j in range(8):
        put(ws, "A%d" % (vr + j), M.TRL_NAMES[j] + " / " + M.STAGE_NAMES[j], align=LEFT)
        put(ws, "B%d" % (vr + j), state["w_time"][j], F_B, "0.0", FILL_IN)
        put(ws, "C%d" % (vr + j), state["w_tax"][j], F_B, "0.0", FILL_IN)
        put(ws, "D%d" % (vr + j), state["stage_share"][j], F_B, "0.0", FILL_IN)
    defname("W_TIME", "Входы", "$B$%d:$B$%d" % (vr, vr + 7))
    defname("W_TAX", "Входы", "$C$%d:$C$%d" % (vr, vr + 7))
    defname("STAGE_SHARE", "Входы", "$D$%d:$D$%d" % (vr, vr + 7))
    r = vr + 9

    def vec_block(title, key, name, fmt="0.000"):
        nonlocal r
        put(ws, "A%d" % r, title, F_B, align=LEFT)
        v = state[key]
        for j, x in enumerate(v):
            put(ws, "%s%d" % (L(2 + j), r), x, F_B, fmt, FILL_IN)
        defname(name, "Входы", "$B$%d:$%s$%d" % (r, L(1 + len(v)), r))
        r += 1

    vec_block("Загрузка по годам эксплуатации, %", "load", "LOAD", "0%")
    vec_block("Годы текущего ремонта", "tr_years", "TR_YEARS", "0")
    vec_block("Годы капитального ремонта", "kr_years", "KR_YEARS", "0")
    r += 1
    put(ws, "A%d" % r, "Производные величины (формулы)", F_T)
    r += 1
    der = [("B_INN", "Инновационная часть бюджета, млн руб.", "=BUDGET*SHARE_INN", "0.00"),
           ("B_INV", "Инвестиционная часть бюджета, млн руб.", "=BUDGET-B_INN", "0.00"),
           ("OPEX", "Операционные расходы, млн руб. в год", "=STAFF*SALARY*12/1000*(1+MARKUP+ADMIN)", "0.00"),
           ("TO_", "Техническое обслуживание, млн руб. в год", "=BUDGET*TO_RATE", "0.00"),
           ("TR_", "Текущий ремонт, млн руб.", "=BUDGET*TR_RATE", "0.00"),
           ("KR_", "Капитальный ремонт, млн руб.", "=BUDGET*KR_RATE", "0.00"),
           ("PILOT", "Опытная инфраструктура, млн руб.", "=PILOT_SHARE*B_INN", "0.00")]
    for name, title, fml, fmt in der:
        put(ws, "A%d" % r, title, align=LEFT)
        put(ws, "B%d" % r, fml, F_B, fmt, FILL_OK)
        put(ws, "C%d" % r, name, F_N, align=CTR)
        defname(name, "Входы", "$B$%d" % r)
        r += 1
    ws.freeze_panes = "A3"

    # ------------------------------------------------------------ Календарь
    wc = wb.create_sheet("Календарь")
    put(wc, "A1", "Календарный план по сценариям, лет от начала разработки", F_T)
    wc["A1"].border = Border()
    row = 3
    CAL = {}
    LVL = {"TRL5": 5, "TRL6": 6, "TRL7": 7}
    for s in SC:
        put(wc, "A%d" % row, SCL[s], F_T)
        wc["A%d" % row].border = Border()
        hr = row + 1
        header(wc, hr, ["Номер", "Переход уровня готовности", "Длительность перехода, лет",
                        "Плановое подтверждение, лет", "Стадия строительства", "Длительность стадии, лет",
                        "Начало стадии, лет", "Окончание стадии, лет",
                        "Начало работ по уровню, лет", "Подтверждение уровня, лет", "Длительность, лет",
                        "Доля уровня в сроке реализации", "Доля стадии в сроке реализации"],
               [8, 26, 14, 14, 34, 14, 13, 13, 14, 14, 13, 15, 15], 46)
        d0 = hr + 1
        for j in range(8):
            rr = d0 + j
            put(wc, "A%d" % rr, j + 1, F_N, "0", align=CTR)
            put(wc, "B%d" % rr, M.TRL_NAMES[j], align=LEFT)
            put(wc, "C%d" % rr, "=INDEX(W_TIME,%d)/100*T_DEV" % (j + 1), F_N, "0.000")
            put(wc, "D%d" % rr, "=SUM($C$%d:C%d)" % (d0, rr), F_N, "0.000")
            put(wc, "E%d" % rr, M.STAGE_NAMES[j], align=LEFT)
            put(wc, "F%d" % rr, "=INDEX(STAGE_SHARE,%d)/100*T_INV" % (j + 1), F_N, "0.000")
        # f и tv
        fr = d0 + 8
        if s == "BASE":
            f_f = "=D%d" % (d0 + 7)
        else:
            f_f = "=D%d-F%d" % (d0 + LVL[s] - 2, d0)
        put(wc, "E%d" % fr, "Начало стадии 1 (строительство), лет", F_B, align=LEFT)
        put(wc, "F%d" % fr, f_f, F_B, "0.000", FILL_OK)
        put(wc, "E%d" % (fr + 1), "Ввод в эксплуатацию, лет", F_B, align=LEFT)
        put(wc, "F%d" % (fr + 1), "=H%d" % (d0 + 7), F_B, "0.000", FILL_OK)
        put(wc, "E%d" % (fr + 2), "Целая часть срока ввода", F_B, align=LEFT)
        put(wc, "F%d" % (fr + 2), "=INT(ROUND(F%d,9))" % (fr + 1), F_B, "0")
        put(wc, "E%d" % (fr + 3), "Дробная часть срока ввода", F_B, align=LEFT)
        put(wc, "F%d" % (fr + 3), "=ROUND(F%d,9)-F%d" % (fr + 1, fr + 2), F_B, "0.000")
        for j in range(8):
            rr = d0 + j
            put(wc, "G%d" % rr, "=F%d" % fr if j == 0 else "=H%d" % (rr - 1), F_N, "0.000")
            put(wc, "H%d" % rr, "=G%d+F%d" % (rr, rr), F_N, "0.000")
        # начало и подтверждение уровней с учетом точки входа
        st_f = {j: "=G%d" % (d0 + j) for j in range(8)}
        en_f = {j: "=H%d" % (d0 + j) for j in range(8)}
        start_s = {0: "=0"}
        conf_s = {}
        for j in range(8):
            conf_s[j] = "=D%d" % (d0 + j)
            if j > 0:
                start_s[j] = "=D%d" % (d0 + j - 1)
        if s != "BASE":
            k = LVL[s]
            if k < 6:
                conf_s[4] = en_f[2]
                start_s[4] = st_f[1]
            if k < 7:
                conf_s[5] = en_f[4]
                start_s[5] = st_f[4]
            conf_s[6] = en_f[5]
            start_s[6] = st_f[5]
            conf_s[7] = en_f[7]
            start_s[7] = st_f[6]
        for j in range(8):
            rr = d0 + j
            put(wc, "I%d" % rr, start_s[j], F_N, "0.000", FILL_G)
            put(wc, "J%d" % rr, conf_s[j], F_N, "0.000", FILL_G)
            put(wc, "K%d" % rr, "=J%d-I%d" % (rr, rr), F_N, "0.000")
            put(wc, "L%d" % rr, "=K%d/$F$%d" % (rr, fr + 1), F_N, "0.0%")
            put(wc, "M%d" % rr, "=F%d/$F$%d" % (rr, fr + 1), F_N, "0.0%")
        put(wc, "E%d" % (fr + 4), "Совмещение разработки и строительства, лет", F_B, align=LEFT)
        put(wc, "F%d" % (fr + 4), "=MAX(0,D%d-F%d)" % (d0 + 7, fr), F_B, "0.000")
        put(wc, "E%d" % (fr + 5), "Доля совмещения в сроке реализации", F_B, align=LEFT)
        put(wc, "F%d" % (fr + 5), "=F%d/F%d" % (fr + 4, fr + 1), F_B, "0.0%")
        c = CODE[s]
        defname(c + "_START", "Календарь", "$I$%d:$I$%d" % (d0, d0 + 7))
        defname(c + "_CONF", "Календарь", "$J$%d:$J$%d" % (d0, d0 + 7))
        defname(c + "_DUR", "Календарь", "$K$%d:$K$%d" % (d0, d0 + 7))
        defname(c + "_F", "Календарь", "$F$%d" % fr)
        defname(c + "_TV", "Календарь", "$F$%d" % (fr + 1))
        defname(c + "_M", "Календарь", "$F$%d" % (fr + 2))
        defname(c + "_PHI", "Календарь", "$F$%d" % (fr + 3))
        CAL[s] = dict(d0=d0, fr=fr, code=c,
                      conf6="$J$%d" % (d0 + 5), st5="$G$%d" % (d0 + 4))
        row = fr + 7
    wc.freeze_panes = "A3"

    # ------------------------------------------------------------ потоки
    COLS = ["Год расчета", "Календарный год", "Инновационная часть", "Опытная инфраструктура",
            "Инвестиционная часть", "Доработки (ввод вручную)", "Дополнительные статьи TRL7",
            "Капитальные затраты", "Выручка", "Операционные расходы", "Обслуживание и ремонт",
            "Амортизация", "Признание расходов на разработку", "EBITDA", "Налоговая база до переноса",
            "Предел переноса убытка", "Убыток на начало года", "Прирост убытка", "Использование убытка",
            "Убыток на конец года", "Налогооблагаемая база", "Налог на прибыль",
            "Поток от операционной деятельности", "Чистый поток", "Коэффициент дисконтирования",
            "Дисконтированный поток", "Дисконтированный операционный поток",
            "Дисконтированные капитальные затраты", "Накопленный поток",
            "Накопленный дисконтированный поток", "Поток для расчета ВНД",
            "Срок окупаемости (расчет)", "Дисконтированный срок (расчет)"]
    N = int(state["n_years"])
    SHN = {}
    for s in SC:
        c = CODE[s]
        name = "Поток " + {"BASE": "Базовый", "TRL7": "И7", "TRL6": "И6", "TRL5": "И5"}[s]
        SHN[s] = name
        wf = wb.create_sheet(name)
        header(wf, 1, COLS, [10, 12] + [13] * (len(COLS) - 2), 70)
        for i in range(N):
            n = i + 1
            rr = i + 2
            A = "$A%d" % rr
            put(wf, "A%d" % rr, n, F_B, "0", align=CTR)
            put(wf, "B%d" % rr, "=FIRST_YEAR+%s-1" % A, F_N, "0", align=CTR)
            # инновационная часть
            put(wf, "C%d" % rr, "=SUMPRODUCT(%s/(%s_DUR+(%s_DUR=0))*(W_TAX/100*B_INN))"
                % (ov(c + "_START", c + "_CONF", A), c, c), F_N, "0.000")
            # опытная инфраструктура
            if s in ("BASE", "TRL7"):
                a = "INDEX(%s_START,5)" % c
                b = "INDEX(%s_CONF,5)" % c
                put(wf, "D%d" % rr, "=PILOT*%s/(%s-%s)" % (ov(a, b, A), b, a), F_N, "0.000")
            else:
                put(wf, "D%d" % rr, 0, F_N, "0.000")
            # инвестиционная часть
            put(wf, "E%d" % rr, "=B_INV*%s/(%s_TV-%s_F)" % (ov(c + "_F", c + "_TV", A), c, c), F_N, "0.000")
            put(wf, "F%d" % rr, 0, F_N, "0.000", FILL_IN)
            if s == "TRL7":
                a7 = "INDEX(%s_CONF,6)" % c
                b7 = "INDEX(%s_ST_5,1)" % c if False else "Календарь!%s" % CAL[s]["st5"]
                put(wf, "G%d" % rr, "=T7_STORE*B_INN*%s+IF(%s=CEILING(ROUND(%s,9),1),T7_REMOUNT*B_INN,0)"
                                    "+IF(%s=CEILING(ROUND(%s_TV,9),1),T7_WARR_P*T7_WARR_COST*B_INN,0)"
                    % (ov(a7, b7, A), A, b7, A, c), F_N, "0.000")
            else:
                put(wf, "G%d" % rr, 0, F_N, "0.000")
            put(wf, "H%d" % rr, "=C%d+D%d+E%d+F%d+G%d" % (rr, rr, rr, rr, rr), F_B, "0.000")

            def cal(expr):
                """(1-phi)*f(j) + phi*f(j-1), где j = n - m."""
                j1 = "(%s-%s_M)" % (A, c)
                j2 = "(%s-%s_M-1)" % (A, c)
                return "=(1-%s_PHI)*%s+%s_PHI*%s" % (c, expr.replace("@", j1), c, expr.replace("@", j2))

            put(wf, "I%d" % rr, cal("IF(OR(@<1,@>OP_YEARS),0,REVENUE*IF(@<=COUNT(LOAD),INDEX(LOAD,MAX(@,1)),1))"),
                F_N, "0.000")
            put(wf, "J%d" % rr, cal("IF(OR(@<1,@>OP_YEARS),0,OPEX)"), F_N, "0.000")
            put(wf, "K%d" % rr, cal("IF(OR(@<1,@>OP_YEARS),0,TO_+IF(COUNTIF(TR_YEARS,@)>0,TR_,0)"
                                    "+IF(COUNTIF(KR_YEARS,@)>0,KR_,0))"), F_N, "0.000")
            put(wf, "L%d" % rr, cal("IF(OR(@<1,@>OP_YEARS,@>AMORT_YEARS),0,B_INV/AMORT_YEARS)"), F_N, "0.000")
            put(wf, "M%d" % rr, "=SUMPRODUCT((CEILING(ROUND(%s_CONF,9),1)=%s)*(W_TAX/100*B_INN))" % (c, A),
                F_N, "0.000")
            put(wf, "N%d" % rr, "=I%d-J%d-K%d" % (rr, rr, rr), F_B, "0.000")
            put(wf, "O%d" % rr, "=N%d-L%d-M%d" % (rr, rr, rr), F_N, "0.000")
            put(wf, "P%d" % rr, "=IF(%s<=LOSS_N,LOSS_LIMIT,1)" % A, F_N, "0.00")
            put(wf, "Q%d" % rr, 0 if i == 0 else "=T%d" % (rr - 1), F_N, "0.000")
            put(wf, "R%d" % rr, "=IF(O%d<0,-O%d,0)" % (rr, rr), F_N, "0.000")
            put(wf, "S%d" % rr, "=IF(O%d<0,0,MIN(Q%d,P%d*O%d))" % (rr, rr, rr, rr), F_N, "0.000")
            put(wf, "T%d" % rr, "=Q%d+R%d-S%d" % (rr, rr, rr), F_N, "0.000")
            put(wf, "U%d" % rr, "=MAX(O%d,0)-S%d" % (rr, rr), F_N, "0.000")
            put(wf, "V%d" % rr, "=TAX*U%d" % rr, F_N, "0.000")
            put(wf, "W%d" % rr, "=N%d-V%d" % (rr, rr), F_N, "0.000")
            put(wf, "X%d" % rr, "=W%d-H%d" % (rr, rr), F_B, "0.000")
            put(wf, "Y%d" % rr, "=(1+RATE)^-%s" % A, F_N, "0.0000")
            put(wf, "Z%d" % rr, "=X%d*Y%d" % (rr, rr), F_B, "0.000")
            put(wf, "AA%d" % rr, "=W%d*Y%d" % (rr, rr), F_N, "0.000")
            put(wf, "AB%d" % rr, "=H%d*Y%d" % (rr, rr), F_N, "0.000")
            put(wf, "AC%d" % rr, "=X%d" % rr if i == 0 else "=AC%d+X%d" % (rr - 1, rr), F_N, "0.000")
            put(wf, "AD%d" % rr, "=Z%d" % rr if i == 0 else "=AD%d+Z%d" % (rr - 1, rr), F_N, "0.000")
            put(wf, "AE%d" % rr, "=X%d" % rr, F_N, "0.000")
            pc = "0" if i == 0 else "AC%d" % (rr - 1)
            put(wf, "AF%d" % rr, '=IF(AND(AC%s>=0,%s<0),%s-1+(-%s)/(AC%s-%s),"")' % (rr, pc, A, pc, rr, pc),
                F_N, "0.000")
            pd = "0" if i == 0 else "AD%d" % (rr - 1)
            put(wf, "AG%d" % rr, '=IF(AND(AD%s>=0,%s<0),%s-1+(-%s)/(AD%s-%s),"")' % (rr, pd, A, pd, rr, pd),
                F_N, "0.000")
        put(wf, "AE1", 0, F_B, "0.000")
        wf["AE1"].fill = FILL_OK
        last = N + 1
        defname(c + "_CF", SHN[s], "$X$2:$X$%d" % last)
        defname(c + "_NN", SHN[s], "$A$2:$A$%d" % last)
        defname(c + "_PVOP", SHN[s], "$AA$2:$AA$%d" % last)
        defname(c + "_PVCX", SHN[s], "$AB$2:$AB$%d" % last)
        defname(c + "_IRRCF", SHN[s], "$AE$1:$AE$%d" % last)
        defname(c + "_PP", SHN[s], "$AF$2:$AF$%d" % last)
        defname(c + "_DPP", SHN[s], "$AG$2:$AG$%d" % last)
        wf.freeze_panes = "C2"

    # ------------------------------------------------------------ Итоги
    wi = wb.create_sheet("Итоги")
    put(wi, "A1", "Показатели эффективности сценариев", F_T)
    wi["A1"].border = Border()
    header(wi, 2, ["Показатель"] + [SCL[s] for s in SC] + ["Контроль расчетного ядра", "Расхождение"],
           [46, 18, 18, 18, 18, 24, 16], 44)
    lines = [
        ("Чистый дисконтированный доход, млн руб.", lambda c: "=SUM(%s_PVOP)-SUM(%s_PVCX)" % (c, c), "0.00", "npv"),
        ("Индекс доходности", lambda c: "=SUM(%s_PVOP)/SUM(%s_PVCX)" % (c, c), "0.0000", "pi"),
        ("Внутренняя норма доходности", lambda c: "=IRR(%s_IRRCF)" % c, "0.0000", "irr"),
        ("Срок окупаемости, лет", lambda c: "=MIN(%s_PP)" % c, "0.000", "pp"),
        ("Дисконтированный срок окупаемости, лет", lambda c: "=MIN(%s_DPP)" % c, "0.000", "dpp"),
        ("Срок ввода в эксплуатацию, лет", lambda c: "=%s_TV" % c, "0.000", "tv"),
        ("Капитальные затраты, млн руб.", lambda c: "=SUM('%s'!$H$2:$H$%d)" % (SHN["BASE"], N + 1), "0.00", None),
    ]
    rr = 3
    for title, fml, fmt, key in lines:
        put(wi, "A%d" % rr, title, F_B, align=LEFT)
        for i, s in enumerate(SC):
            c = CODE[s]
            v = fml(c) if key != "capex" else fml(c)
            if title.startswith("Капитальные"):
                v = "=SUM('%s'!$H$2:$H$%d)" % (SHN[s], N + 1)
            put(wi, "%s%d" % (L(2 + i), rr), v, F_B, fmt, FILL_OK)
        if key:
            ind = R["scn"]["BASE"]["ind"]
            ctrl = ind.get(key) if key != "tv" else R["scn"]["BASE"]["sch"]["tv"]
            put(wi, "F%d" % rr, ctrl, F_N, fmt)
            put(wi, "G%d" % rr, "=B%d-F%d" % (rr, rr), F_N, "0.000000")
        rr += 1
    put(wi, "A%d" % rr, "Преимущество к базовому сценарию, млн руб.", F_B, align=LEFT)
    put(wi, "B%d" % rr, "—", F_N, align=CTR)
    for i, s in enumerate(SC[1:], start=1):
        put(wi, "%s%d" % (L(2 + i), rr), "=%s3-$B$3" % L(2 + i), F_B, "0.00", FILL_OK)
    rr += 2
    put(wi, "A%d" % rr, "Столбец «Контроль расчетного ядра» содержит значения базового сценария, "
                        "полученные программой при выгрузке. Расхождение показывает отличие формул книги "
                        "от расчетного ядра и при неизменных входных данных равно нулю.", F_N, align=LEFT)
    wi["A%d" % rr].border = Border()
    wi.merge_cells("A%d:G%d" % (rr, rr))
    wi.row_dimensions[rr].height = 44

    # ------------------------------------------------------------ Чувствительность
    wv = wb.create_sheet("Чувствительность")
    put(wv, "A1", "Чувствительность чистого дисконтированного дохода к ставке дисконтирования", F_T)
    wv["A1"].border = Border()
    header(wv, 2, ["Ставка дисконтирования"] + [SCL[s] for s in SC] +
           ["Преимущество TRL7", "Преимущество TRL6", "Преимущество TRL5"],
           [24, 16, 16, 16, 16, 18, 18, 18], 44)
    for i in range(7):
        rr = 3 + i
        put(wv, "A%d" % rr, 0.10 + 0.01 * i, F_B, "0.00", FILL_IN)
        for j, s in enumerate(SC):
            c = CODE[s]
            put(wv, "%s%d" % (L(2 + j), rr), "=SUMPRODUCT(%s_CF,(1+$A%d)^-%s_NN)" % (c, rr, c), F_N, "0.00")
        for j, s in enumerate(SC[1:]):
            put(wv, "%s%d" % (L(6 + j), rr), "=%s%d-$B%d" % (L(3 + j), rr, rr), F_N, "0.00")
    put(wv, "A11", "Чувствительность к остальным параметрам выполняется изменением значения на листе «Входы»: "
                   "книга пересчитывается полностью.", F_N, align=LEFT)
    wv["A11"].border = Border()
    wv.merge_cells("A11:H11")
    wv.row_dimensions[11].height = 30

    # ------------------------------------------------------------ Пояснения
    wp = wb.create_sheet("Пояснения")
    put(wp, "A1", "Пояснения к книге", F_T)
    wp["A1"].border = Border()
    txt = [
        ("Назначение", "Книга повторяет расчет программы и пересчитывается средствами Excel. "
                       "Изменяются только ячейки с желтой заливкой на листе «Входы»."),
        ("Единицы", "Суммы в млн руб. в постоянных ценах. Время в годах от начала разработки, t = 0. "
                    "Календарный год n охватывает интервал (n-1; n], оплата отнесена на конец года, "
                    "дисконтирование по множителю (1 + ставка) в степени минус n."),
        ("Сценарии", "Базовый: строительство начинается после подтверждения TRL9. Интеграция TRLk: "
                     "разработка проектной документации начинается в момент планового подтверждения TRLk, "
                     "последующие уровни подтверждаются при строительстве."),
        ("Лист «Календарь»", "Доли уровней и стадий приведены к сроку реализации сценария. Длительности переходов уровней и стадий строительства, даты начала и окончания "
                             "стадий, моменты подтверждения уровней с учетом точки входа."),
        ("Листы потоков", "Годовая таблица затрат, выручки, налога и потоков. Столбец «Доработки» заполняется "
                          "вручную для проверки влияния событий доработки."),
        ("Лист «Итоги»", "Показатели эффективности в виде формул и контрольные значения расчетного ядра."),
        ("Лист «Чувствительность»", "Чистый дисконтированный доход при ставках от 10 до 16 процентов."),
        ("Ограничение", "Длительность каждой стадии и каждого перехода должна быть больше нуля."),
    ]
    wp.column_dimensions["A"].width = 26
    wp.column_dimensions["B"].width = 110
    for i, (a, b) in enumerate(txt):
        put(wp, "A%d" % (3 + i), a, F_B, align=LEFT)
        put(wp, "B%d" % (3 + i), b, F_N, align=LEFT)
        wp.row_dimensions[3 + i].height = 44
    order = ["Пояснения", "Входы", "Календарь"] + [SHN[s] for s in SC] + ["Итоги", "Чувствительность"]
    wb._sheets = [wb[n] for n in order]
    for w in wb.worksheets:
        w.sheet_view.zoomScale = 90
        w.page_setup.orientation = "landscape"
        w.page_setup.fitToWidth = 1
        w.page_setup.fitToHeight = 0
        w.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(path)
    return path

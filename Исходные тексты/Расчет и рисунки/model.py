# -*- coding: utf-8 -*-
"""Расчетное ядро по ТЗ ред. 0.82 (модель интеграции инновационного и инвестиционного проектов).
Все суммы в млн руб. в постоянных ценах; время в годах от начала разработки (t=0);
календарный год n охватывает (n-1, n], оплата в конце года, дисконтирование (1+r)^-n.
"""
from dataclasses import dataclass, field, replace
import math

TRL_NAMES = ["TRL1→2", "TRL2→3", "TRL3→4", "TRL4→5", "TRL5→6", "TRL6→7", "TRL7→8", "TRL8→9"]
STAGE_NAMES = ["Исходные данные и общие решения", "Проектная документация, экспертиза и корректировка",
               "Рабочая документация", "Поставка МТР", "Строительно-монтажные работы",
               "ПНР без нагрузки", "ПНР под нагрузкой", "Комплексное опробование"]
SCENARIOS = ["BASE", "TRL7", "TRL6", "TRL5"]
INTEG = ["TRL7", "TRL6", "TRL5"]
SCN_TITLE = {"BASE": "Базовый", "TRL7": "Интеграция TRL7", "TRL6": "Интеграция TRL6", "TRL5": "Интеграция TRL5"}


@dataclass
class P:
    budget: float = 1000.0
    share_inn: float = 0.35
    rate: float = 0.12
    t_dev: float = 3.0
    t_inv: float = 5.0
    w_time: tuple = (5, 7, 10, 13, 15, 15, 15, 20)            # доли времени переходов TRL, %
    w_tax: tuple = (5, 7, 10, 13, 15, 15, 15, 20)             # доли налогового признания, %
    stage_share: tuple = (3, 8, 9, 8, 42, 12, 15, 3)          # доли времени стадий строительства, % (8 стадий; «Поставка МТР» = закупка + поставка)
    smr_lead: float = 2.0 / 3.0                               # TRL6→7 начинается через эту долю длительности СМР
    op_years: int = 30
    load: tuple = (0.2, 0.6)                                  # далее 1.0
    revenue: float = 350.0
    staff: int = 11
    salary_k: float = 100.0                                   # тыс. руб./мес
    markup: float = 0.35
    admin: float = 0.10
    to_rate: float = 0.0012
    tr_rate: float = 0.0025
    tr_years: tuple = (3, 6, 9, 12, 15, 18, 21, 24, 27, 30)
    kr_rate: float = 0.005
    kr_years: tuple = (5, 10, 15, 20, 25, 30)
    tax: float = 0.25
    amort_years: int = 20
    loss_limit: float = 0.5
    loss_limit_end: int = 2030                                # последний календарный год ограничения зачета убытков
    first_tax_year: int = 2026
    pilot_all: bool = False                                   # опытная инфраструктура также в сценариях интеграции (вариант «+ОИ»)
    pilot_share: float = 0.10                                 # доля опытной инфраструктуры от B_INN (только Базовый)
    # события доработки TRL5..TRL9
    p_ev: tuple = (0.09, 0.06, 0.04, 0.03, 0.02)
    ev_cost: tuple = (2.0, 5.0, 10.0, 20.0, 30.0)
    ev_delay_d: tuple = (30, 30, 30, 60, 90)
    days: float = 365.0
    # зависимость параметров событий от точки входа (К-1): доля незафиксированных интерфейсных параметров на входе
    phi_s: tuple = (0.40, 0.20, 0.10)                         # TRL5, TRL6, TRL7
    mfix: bool = False                                        # True: вероятности не масштабируются по точке входа (расчетный случай)
    sigma: float = 0.60                                       # доля марок, зависящих от незафиксированного параметра (чувствительность)
    pir_share: float = 0.07                                   # проектные работы (ПД+РД), доля от инвестиционной части
    pd_part: float = 0.40                                     # доля ПД в проектных работах
    exp_share: float = 0.05                                   # повторная экспертиза, доля стоимости ПД
    exp_days: float = 30.0                                    # срок повторной экспертизы, сут.
    ev6_cost_abs: float = None                                # переопределение для поиска порогов (событие TRL6 при входе TRL5)
    ev6_delay_abs: float = None
    ev6_p_abs: float = None
    # дополнительные статьи сценария «Интеграция TRL7» (К-4)
    t7_store: float = 0.015                                   # хранение и консервация, доля B_INN в год
    t7_remount: float = 0.06                                  # демонтаж, транспортировка, монтаж, повторная верификация, доля B_INN
    t7_warr_p: float = 0.25                                   # вероятность окончания гарантии до ввода
    t7_warr_cost: float = 0.05                                # затраты продления гарантии/ремонта, доля B_INN
    n_years: int = 40                                         # длина таблицы (календарных лет)

    @property
    def b_inn(self): return self.budget * self.share_inn
    @property
    def b_inv(self): return self.budget - self.b_inn
    @property
    def opex(self): return self.staff * self.salary_k * 12 / 1000.0 * (1 + self.markup + self.admin)
    @property
    def to(self): return self.budget * self.to_rate
    @property
    def tr(self): return self.budget * self.tr_rate
    @property
    def kr(self): return self.budget * self.kr_rate
    @property
    def pilot(self): return self.pilot_share * self.b_inn

    def load_j(self, j):
        return self.load[j - 1] if j <= len(self.load) else 1.0


def overlap(a, b, n):
    """Длина пересечения [a,b] с календарным годом (n-1,n]."""
    return max(0.0, min(b, n) - max(a, n - 1))


def spread(a, b, amount, n):
    """Равномерное распределение amount по [a,b] на календарный год n."""
    if b - a <= 1e-12:
        return amount if (n - 1 < a <= n + 1e-12) else 0.0
    return amount * overlap(a, b, n) / (b - a)


def schedule(scn, p: P):
    """Календарь: переходы TRL (плановые), стадии строительства, ключевые даты."""
    d_trl = [w / 100.0 * p.t_dev for w in p.w_time]
    conf = []
    t = 0.0
    for d in d_trl:
        t += d
        conf.append(t)                       # конец TRLk→k+1 (подтверждение TRL k+1)
    trl_start = [0.0] + conf[:-1]
    d_st = [w / 100.0 * p.t_inv for w in p.stage_share]
    # Точка входа в инвестиционный объект одна — начало проектной документации (ПД). В сценарии «Интеграция TRLk»
    # ПД начинается в момент планового подтверждения TRLk; этап «Исходные данные» выполняется непосредственно перед ПД.
    # Базовый: строительство начинается после подтверждения TRL9.
    LVL = {"TRL5": 5, "TRL6": 6, "TRL7": 7}
    if scn == "BASE":
        f = conf[-1]
    else:
        entry = conf[LVL[scn] - 2]           # плановое подтверждение TRLk = начало ПД
        f = entry - d_st[0]
    st, en = [], []
    t = f
    for d in d_st:
        st.append(t); t += d; en.append(t)
    tv = en[-1]
    # календарь переходов TRL. Индекс j соответствует достижению уровня TRL(j+2): конец перехода TRL(j+1)→(j+2).
    # До входа (уровни не выше k) — плановый календарь разработки. После входа подтверждение уровней идет при строительстве:
    # TRL6 — конец РД; TRL7 — конец СМР; TRL8 — конец ПНР без нагрузки; TRL9 — конец комплексного опробования.
    conf_s = list(conf); start_s = [0.0] + conf[:-1]
    if scn != "BASE":
        k = LVL[scn]
        if k < 6:
            conf_s[4] = en[2]; start_s[4] = st[1]
        if k < 7:
            conf_s[5] = en[4]; start_s[5] = st[4]
        conf_s[6] = en[5]; start_s[6] = st[5]
        conf_s[7] = en[7]; start_s[7] = st[6]
    d_s = [conf_s[j] - start_s[j] for j in range(8)]
    return dict(d_trl=d_s, d_plan=d_trl, conf=conf_s, trl_start=start_s, conf_plan=conf, d_st=d_st, st=st, en=en, f=f, tv=tv,
                net_conf=conf_s, scn=scn)


def pilot_window(sch):
    # опытная инфраструктура создается в окне перехода TRL5→6 (инфраструктура для очередного испытания — первой)
    return sch["trl_start"][4], sch["conf"][4]


def year_of(t):
    return int(math.ceil(round(t, 9)))


def flows(scn, p: P, delay_days=0.0, extra=(), sch=None):
    """Годовая таблица после налога. extra: [(время, сумма)] — прямые затраты доработок (без налогового эффекта)."""
    sch = sch or schedule(scn, p)
    N = p.n_years
    tv = sch["tv"] + delay_days / p.days
    m = int(math.floor(round(tv, 9)))
    phi = round(tv - m, 9)
    rows = []
    # плановые затраты
    inn_cash = [[spread(sch["trl_start"][k], sch["conf"][k], w / 100.0 * p.b_inn, n) for k, w in enumerate(p.w_tax)] for n in range(1, N + 1)]
    # налоговое признание инновационных расходов по завершении этапов
    rec = [0.0] * N
    for k, w in enumerate(p.w_tax):
        y = year_of(sch["conf"][k])
        if y <= N: rec[y - 1] += w / 100.0 * p.b_inn
    pilot = [0.0] * N
    if scn in ("BASE", "TRL7"):
        a, b = pilot_window(sch)
        for n in range(1, N + 1): pilot[n - 1] = spread(a, b, p.pilot, n)
    inv = [spread(sch["f"], sch["tv"], p.b_inv, n) for n in range(1, N + 1)]
    exc = [0.0] * N
    for (t, c) in extra:
        exc[year_of(t) - 1] += c
    t7x = [0.0] * N
    # Затраты ожидания определяются по календарному плану. Окно простоя оборудования
    # возникает, если изделие готово раньше начала монтажа. Окно ожидания разработчика
    # возникает, если подтверждение уровня готовности привязано к стадии строительства
    # и наступает позже планового окончания перехода. Если окна нет, затрат нет.
    if scn != "BASE":
        a7, b7 = sch["conf"][5], sch["st"][4]                  # простой оборудования до монтажа
        if b7 - a7 > 1e-9:
            for n in range(1, N + 1):
                t7x[n - 1] += spread(a7, b7, p.t7_store * p.b_inn * (b7 - a7), n)
            t7x[year_of(b7) - 1] += p.t7_remount * p.b_inn
        for j in range(8):                                     # ожидание разработчика на переходах
            lag = sch["d_trl"][j] - sch["d_plan"][j]
            if lag > 1e-9:
                a, b = sch["conf"][j] - lag, sch["conf"][j]
                for n in range(1, N + 1):
                    t7x[n - 1] += spread(a, b, p.t7_store * p.b_inn * lag, n)
        t7x[year_of(sch["tv"]) - 1] += p.t7_warr_p * p.t7_warr_cost * p.b_inn
    # эксплуатация: по годам эксплуатации j
    def opj(j, kind):
        if j < 1 or j > p.op_years: return 0.0
        if kind == "rev": return p.revenue * p.load_j(j)
        if kind == "opex": return p.opex
        if kind == "to": return p.to
        if kind == "tr": return p.tr if j in p.tr_years else 0.0
        if kind == "kr": return p.kr if j in p.kr_years else 0.0
        if kind == "am": return p.b_inv / p.amort_years if j <= p.amort_years else 0.0
    def cal(n, kind):
        j = n - m
        return (1 - phi) * opj(j, kind) + phi * opj(j - 1, kind)
    loss = 0.0
    cum = 0.0
    cumd = 0.0
    out = []
    for n in range(1, N + 1):
        r = dict(n=n, year=p.first_tax_year + n - 1)
        r["inn"] = sum(inn_cash[n - 1])
        r["pilot"] = pilot[n - 1]
        r["inv"] = inv[n - 1]
        r["rework"] = exc[n - 1]
        r["t7x"] = t7x[n - 1]
        r["capex"] = r["inn"] + r["pilot"] + r["inv"] + r["rework"] + r["t7x"]
        r["rev"] = cal(n, "rev"); r["opex"] = cal(n, "opex")
        r["to"] = cal(n, "to"); r["tr"] = cal(n, "tr"); r["kr"] = cal(n, "kr")
        r["toir"] = r["to"] + r["tr"] + r["kr"]
        r["am"] = cal(n, "am")
        r["rnd"] = rec[n - 1]
        r["ebitda"] = r["rev"] - r["opex"] - r["toir"]
        r["base"] = r["ebitda"] - r["am"] - r["rnd"]
        lim = p.loss_limit if r["year"] <= p.loss_limit_end else 1.0
        r["loss_open"] = loss
        if r["base"] < 0:
            r["loss_add"] = -r["base"]; r["loss_use"] = 0.0
        else:
            r["loss_add"] = 0.0; r["loss_use"] = min(loss, lim * r["base"])
        loss = loss + r["loss_add"] - r["loss_use"]
        r["loss_close"] = loss
        r["limit"] = lim
        r["taxable"] = max(r["base"], 0.0) - r["loss_use"]
        r["tax"] = p.tax * r["taxable"]
        r["cf_op"] = r["ebitda"] - r["tax"]
        r["cf"] = r["cf_op"] - r["capex"]
        r["df"] = (1 + p.rate) ** (-n)
        r["pv"] = r["cf"] * r["df"]
        r["pv_op"] = r["cf_op"] * r["df"]
        r["pv_capex"] = r["capex"] * r["df"]
        cum += r["cf"]; cumd += r["pv"]
        r["cum"] = cum; r["cumd"] = cumd
        out.append(r)
    return out


def npv(rows): return sum(r["pv"] for r in rows)


def npv_at(rows, rate): return sum(r["cf"] * (1 + rate) ** (-r["n"]) for r in rows)


def irr(rows, lo=-0.5, hi=2.0):
    f = lambda x: npv_at(rows, x)
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0: return None
    for _ in range(200):
        mid = (lo + hi) / 2
        fm = f(mid)
        if flo * fm <= 0: hi, fhi = mid, fm
        else: lo, flo = mid, fm
    return (lo + hi) / 2


def payback(rows, key):
    """Срок окупаемости: первое n, когда накопленный итог >= 0 (линейная интерполяция внутри года); годы от t=0."""
    prev = 0.0
    prev_c = 0.0
    c = 0.0
    seen_neg = False
    for r in rows:
        c += r[key]
        if c < 0: seen_neg = True
        if seen_neg and c >= 0:
            frac = (0 - prev_c) / (c - prev_c) if c != prev_c else 0
            return (r["n"] - 1) + frac
        prev_c = c
    return None


def indicators(rows, rate):
    pv_ic = sum(r["pv_capex"] for r in rows)
    pv_cf = sum(r["pv_op"] for r in rows)
    return dict(npv=pv_cf - pv_ic, pi=pv_cf / pv_ic, pv_ic=pv_ic, pv_cf=pv_cf,
                pp=payback(rows, "cf"),
                dpp=payback(rows, "pv"),
                irr=irr(rows), sum_capex=sum(r["capex"] for r in rows))


def event_scope(scn, sch, k, p: P):
    """k = 5..9 (уровень TRL). Возвращает (затронуты ли работы, время события, описание) по плановому календарю TRL.
    Событие происходит в момент подтверждения TRLk; затронуты начатые работы (документация, СМР и пр.)."""
    t = sch["conf"][k - 2]
    if scn == "BASE":
        return False, t, "нет (изолированный анализ)"
    st, en = sch["st"], sch["en"]
    eps = 1e-9
    started = [s < t - eps for s in st]    # стадия начата строго до момента события
    if k == 5:
        aff = started[1]                    # ПД начата до подтверждения TRL5?
        return aff, t, "ПД и экспертиза" if aff else "нет: уровень подтвержден до начала ПД"
    if k == 6:
        aff = en[1] <= t + eps or started[1]   # ПД выпущена/в работе
        return aff, t, "ПД, РД и выполненные работы" if aff else "нет: уровень подтвержден до начала ПД"
    # TRL7–9: проектная и рабочая документация, КД, конструкция, инфраструктура, повторные испытания
    aff = any(started[1:])
    return aff, t, "документация, конструкция, инфраструктура, испытания" if aff else "нет: уровень подтвержден до начала ПД"


EV_COST0 = (2.0, 5.0, 10.0, 20.0, 30.0)
EV_DELAY0 = (30, 30, 30, 60, 90)


def ev_params(p: P, scn, k, sch=None):
    """Вероятность, затраты (млн руб.) и задержка (сут.) события доработки уровня TRLk для сценария.
    Эволюция исходных данных: вероятность пропорциональна доле незафиксированных параметров на входе (phi);
    чувствительность: ущерб события TRL6 при входе TRL5 — стоимость повторной разработки ПД и РД, доли изменяемых марок и повторной экспертизы."""
    i = k - 5
    LV = {"TRL5": 0, "TRL6": 1, "TRL7": 2}
    phi = p.phi_s[LV[scn]] if scn in LV else p.phi_s[1]
    m = 1.0 if p.mfix else phi / p.phi_s[1]
    pr = min(1.0, p.p_ev[i] * m)
    cost, dd = p.ev_cost[i], p.ev_delay_d[i]
    if k == 6 and scn == "TRL5":
        ch = phi * p.sigma
        cpir = p.pir_share * p.b_inv
        sch = sch or schedule(scn, p)
        days = (sch["d_st"][1] + sch["d_st"][2]) * p.days
        cost = (ch * cpir + p.exp_share * p.pd_part * cpir) * (p.ev_cost[1] / EV_COST0[1])
        dd = (ch * days + p.exp_days) * (p.ev_delay_d[1] / EV_DELAY0[1])
        if p.ev6_cost_abs is not None: cost = p.ev6_cost_abs
        if p.ev6_delay_abs is not None: dd = p.ev6_delay_abs
        if p.ev6_p_abs is not None: pr = p.ev6_p_abs
    return pr, cost, dd


def outcomes(scn, p: P, sch=None):
    """Исходы событий доработки TRL5..TRL9: (подмножества) -> ущерб и ЧДД."""
    sch = sch or schedule(scn, p)
    base_rows = flows(scn, p, sch=sch)
    n0 = npv(base_rows)
    active = []
    for i, k in enumerate(range(5, 10)):
        aff, t, desc = event_scope(scn, sch, k, p)
        pr_, c_, d_ = ev_params(p, scn, k, sch)
        active.append(dict(k=k, aff=aff, t=t, desc=desc, p=pr_, cost=c_, dd=d_))
    ev_list = [a for a in active if a["aff"]]
    res = []
    from itertools import product
    for combo in product([0, 1], repeat=len(ev_list)):
        prob = 1.0
        cost = 0.0; dd = 0.0; extra = []
        names = []
        for a, c in zip(ev_list, combo):
            prob *= a["p"] if c else (1 - a["p"])
            if c:
                cost += a["cost"]; dd += a["dd"]; extra.append((a["t"], a["cost"])); names.append("TRL%d" % a["k"])
        rows = flows(scn, p, delay_days=dd, extra=extra, sch=sch)
        res.append(dict(combo=combo, names=names, prob=prob, cost=cost, delay=dd, npv=npv(rows), loss=n0 - npv(rows)))
    E = sum(i["prob"] * i["npv"] for i in res)
    return dict(events=active, items=res, npv0=n0, E_npv=E, E_loss=n0 - E)

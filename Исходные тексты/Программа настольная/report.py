# -*- coding: utf-8 -*-
# Автор и разработчик: Postautov_K_V
"""Сборка отчета по результатам расчета в формате PDF.

Состав отчета задается пользователем в окне выбора. Крупные таблицы заменяются
графиками и итоговой таблицей, подробные таблицы выводятся только при выборе
полной глубины детализации.
"""
import datetime

import calc as CA
import model_core as M
import pdf_core as PC

SC = CA.SC
SCL = CA.SCL
COL = {"BASE": "#3C4F66", "TRL7": "#C4690E", "TRL6": "#8E44AD", "TRL5": "#1B9E77"}
NAVY = "#003366"
INK = "#1c1c1a"
MUT = "#5b5a55"
LINE = "#d7d5cf"
FILL = "#EAF2FA"

SECTIONS = [
    ("inputs", "Входные данные"),
    ("check", "Проверка данных и тождеств расчета"),
    ("summary", "Показатели эффективности сценариев"),
    ("calendar", "Календарный план"),
    ("flows", "Денежные потоки"),
    ("sens", "Чувствительность"),
    ("mc", "Имитационное моделирование"),
    ("ev", "События доработки"),
    ("tax", "Налоговые расчеты"),
    ("pick", "Выбор сценария"),
]

DEPTHS = [
    ("short", "Кратко. Только графики и итоговые таблицы"),
    ("std", "Стандартно. Графики и основные таблицы"),
    ("full", "Подробно. Все таблицы расчета"),
]


class Doc(object):
    """Потоковая верстка отчета на листах формата A4."""

    def __init__(self, title):
        self.p = PC.PDF(size=PC.A4L, margin=36.0)
        self.title = title
        self.n = 0
        self.toc = []
        self._new_page(first=True)

    # ------------------------------------------------------------- страницы
    def _new_page(self, first=False):
        self.p.page()
        self.n += 1
        w, h = self.p.W, self.p.H
        if not first:
            self.p.line(36, h - 44, w - 36, h - 44, col=LINE, lw=0.6)
            self.p.text(36, h - 38, self.title, 8.5, col=MUT)
            self.p.text(w - 36, h - 38, "Страница %d" % self.n, 8.5, col=MUT, align="r")
        self.y = h - (66 if not first else 36)

    def need(self, h):
        if self.y - h < 46:
            self._new_page()
            return True
        return False

    def space(self, h):
        self.y -= h

    @property
    def wide(self):
        return self.p.W - 72

    # ------------------------------------------------------------- текст
    def h1(self, s):
        self.need(46)
        self.y -= 6
        self.p.rect(36, self.y - 4, self.wide, 20, fill=NAVY)
        self.p.text(44, self.y + 1, s, 12.5, col="#ffffff", bold=True)
        self.y -= 22
        self.toc.append((s, self.n))

    def h2(self, s, keep=140):
        self.need(keep)
        self.y -= 4
        self.p.text(36, self.y, s, 11.0, col=NAVY, bold=True)
        self.y -= 14

    def para(self, s, size=10.0, col=MUT):
        for ln in self.p.wrap(s, self.wide, size):
            self.need(size + 4)
            self.p.text(36, self.y, ln, size, col=col)
            self.y -= size + 3.2
        self.y -= 3

    def note(self, s):
        lines = self.p.wrap(s, self.wide - 16, 10.0)
        h = len(lines) * 13 + 10
        self.need(h + 6)
        self.p.rect(36, self.y - h + 10, self.wide, h, fill=FILL)
        self.p.line(36, self.y - h + 10, 36, self.y + 10, col="#0079C2", lw=2.0)
        yy = self.y
        for ln in lines:
            self.p.text(46, yy, ln, 10.0, col=INK)
            yy -= 13
        self.y -= h + 4

    # ------------------------------------------------------------- таблица
    def table(self, head, rows, widths=None, size=10.0, align=None, max_rows=None):
        cols = len(head)
        if widths is None:
            widths = [self.wide / cols] * cols
        sc = self.wide / float(sum(widths))
        widths = [w * sc for w in widths]
        if align is None:
            align = ["l"] + ["r"] * (cols - 1)
        # кегль уменьшается, если самое длинное слово не помещается в колонку
        for _ in range(12):
            over = False
            for i in range(cols):
                lim = widths[i] - 9
                words = [str(head[i])] + [str(r[i]) for r in rows]
                for wd in words:
                    for part in wd.split():
                        if self.p.text_width(part, size, True) > lim:
                            over = True
                            break
                    if over:
                        break
                if over:
                    break
            if not over or size <= 10.0:
                break
            size -= 0.3
        hl = [self.p.wrap(h, widths[i] - 8, size, True) for i, h in enumerate(head)]
        hh = max(len(x) for x in hl) * (size + 2) + 6

        def head_row():
            self.p.rect(36, self.y - hh + size + 2, self.wide, hh, fill="#f0efea")
            x = 42.0
            for i, parts in enumerate(hl):
                yy = self.y
                for ln in parts:
                    ax = x + 4 if align[i] == "l" else x + widths[i] - 4
                    self.p.text(ax, yy, ln, size, col=INK, bold=True,
                                align="l" if align[i] == "l" else "r")
                    yy -= size + 2
                x += widths[i]
            self.y -= hh

        self.need(hh + 30)
        head_row()
        shown = rows if max_rows is None else rows[:max_rows]
        for k, r in enumerate(shown):
            cells = [self.p.wrap(str(c), widths[i] - 8, size) for i, c in enumerate(r)]
            rh = max(len(c) for c in cells) * (size + 2) + 4
            if self.need(rh + 4):
                head_row()
            if k % 2:
                self.p.rect(36, self.y - rh + size + 2, self.wide, rh, fill="#fbfaf7")
            x = 42.0
            for i, parts in enumerate(cells):
                yy = self.y
                for ln in parts:
                    ax = x + 4 if align[i] == "l" else x + widths[i] - 4
                    self.p.text(ax, yy, ln, size, col=INK,
                                align="l" if align[i] == "l" else "r")
                    yy -= size + 2
                x += widths[i]
            self.p.line(36, self.y - rh + size + 1, 42 + self.wide, self.y - rh + size + 1,
                        col=LINE, lw=0.4)
            self.y -= rh
        if max_rows is not None and len(rows) > max_rows:
            self.y -= 2
            self.p.text(36, self.y, "Показаны первые %d строк из %d" % (max_rows, len(rows)),
                        7.0, col=MUT)
            self.y -= 12
        self.y -= 8

    # ------------------------------------------------------------- графики
    def _frame(self, h, lo, hi, left=58, right=14, top=10, bottom=26, ylab=""):
        self.need(h + 16)
        x0, x1 = 42.0 + left, 42.0 + self.wide - right
        y1, y0 = self.y - top, self.y - h + bottom
        if hi == lo:
            hi = lo + 1.0
        yp = lambda v: y0 + (v - lo) / float(hi - lo) * (y1 - y0)
        for i in range(5):
            v = lo + (hi - lo) * i / 4.0
            self.p.line(x0, yp(v), x1, yp(v), col="#eceae4", lw=0.5)
            self.p.text(x0 - 6, yp(v) - 2.5, CA.f(v, 0), 7.0, col=MUT, align="r")
        if lo < 0 < hi:
            self.p.line(x0, yp(0), x1, yp(0), col="#b9b6ae", lw=0.7)
        if ylab:
            self.p.text(36, self.y - 2, ylab, 7.2, col=MUT)
        return x0, x1, y0, y1, yp

    @staticmethod
    def _bounds(vals, zero=True):
        hi, lo = max(vals), min(vals)
        if zero:
            hi, lo = max(hi, 0.0), min(lo, 0.0)
        pad = (hi - lo) * 0.14 or 1.0
        return lo - (pad if lo < 0 else 0.0), hi + pad

    def vbars(self, items, h=150, ylab="", dec=1):
        """items: [(подпись, значение, цвет)]"""
        lo, hi = self._bounds([v for _, v, _ in items])
        x0, x1, y0, y1, yp = self._frame(h, lo, hi, ylab=ylab)
        bw = (x1 - x0) / float(len(items))
        for i, (k, v, c) in enumerate(items):
            x = x0 + i * bw + bw * 0.22
            w = bw * 0.56
            a, b = yp(0), yp(v)
            self.p.rect(x, min(a, b), w, abs(b - a), fill=c)
            self.p.text(x + w / 2, b + (4 if v >= 0 else -9), CA.f(v, dec), 7.4, col=INK,
                        bold=True, align="c")
            for j, ln in enumerate(self.p.wrap(k, bw, 7.0)):
                self.p.text(x + w / 2, y0 - 10 - j * 8, ln, 7.0, col=MUT, align="c")
        self.y -= h + 10

    def hbars(self, items, h=None, lab_w=120, dec=2, unit=""):
        """Горизонтальные полосы: [(подпись, значение, цвет)]"""
        n = len(items)
        h = h or (n * 22 + 20)
        self.need(h + 10)
        x0 = 42.0 + lab_w
        x1 = 42.0 + self.wide - 46
        hi = max(v for _, v, _ in items) * 1.08 or 1.0
        for i, (k, v, c) in enumerate(items):
            y = self.y - 14 - i * 22
            self.p.text(36, y, k, 7.6, col=INK)
            w = (x1 - x0) * v / hi
            self.p.rect(x0, y - 3, w, 12, fill=c)
            self.p.text(x0 + w + 5, y, CA.f(v, dec) + unit, 7.4, col=INK, bold=True)
        self.y -= h

    def flowbars(self, rows, h=180, ylab="Млн руб."):
        """Денежный поток по годам: затраты вниз, поступления вверх."""
        inn = [r["inn"] + r["pilot"] + r["rework"] + r["t7x"] for r in rows]
        inv = [r["inv"] for r in rows]
        op = [r["cf_op"] for r in rows]
        cum = [r["cumd"] for r in rows]
        hi = max([0.0] + op + cum)
        lo = min([0.0] + [-(inn[i] + inv[i]) for i in range(len(rows))] + cum)
        pad = (hi - lo) * 0.1 or 1.0
        x0, x1, y0, y1, yp = self._frame(h, lo - pad, hi + pad, ylab=ylab)
        bw = (x1 - x0) / float(len(rows))
        step = max(1, int(round(len(rows) / 12.0)))
        for i, r in enumerate(rows):
            x = x0 + i * bw + bw * 0.12
            w = max(1.2, bw * 0.76)
            if op[i] > 0:
                self.p.rect(x, yp(0), w, yp(op[i]) - yp(0), fill="#9fb8cf")
            base = 0.0
            if inv[i] > 0:
                self.p.rect(x, yp(-inv[i]), w, yp(0) - yp(-inv[i]), fill="#1B9E77")
                base = inv[i]
            if inn[i] > 0:
                self.p.rect(x, yp(-base - inn[i]), w, yp(-base) - yp(-base - inn[i]), fill="#8E44AD")
            if i % step == 0:
                self.p.text(x + w / 2, y0 - 11, "%d" % int(r["year"]), 7.6, col=MUT, align="c")
        self.p.poly([(x0 + i * bw + bw * 0.5, yp(v)) for i, v in enumerate(cum)],
                    col="#003366", lw=1.3)
        self.p.text((x0 + x1) / 2, y0 - 22, "Год расчетного периода", 8.0, col=MUT, align="c")
        self.y -= h + 6
        self.legend([("Инновационные затраты", "#8E44AD"), ("Инвестиционные затраты", "#1B9E77"),
                     ("Поступления от эксплуатации", "#9fb8cf"),
                     ("Накопленный дисконтированный поток", "#003366")])

    def lines(self, xs, series, h=160, ylab="", xlab="", xdec=0, xfmt=None):
        """series: [(подпись, цвет, [значения])]"""
        allv = [v for _, _, vs in series for v in vs]
        lo, hi = self._bounds(allv, zero=False)
        x0, x1, y0, y1, yp = self._frame(h, lo, hi, ylab=ylab)
        n = len(xs)
        xp = lambda i: x0 + (x1 - x0) * (i / float(n - 1) if n > 1 else 0.5)
        for i in range(n):
            if n <= 12 or i % max(1, n // 10) == 0:
                lab = xfmt(xs[i]) if xfmt else CA.f(xs[i], xdec)
                self.p.text(xp(i), y0 - 11, lab, 6.8, col=MUT, align="c")
        for k, c, vs in series:
            self.p.poly([(xp(i), yp(v)) for i, v in enumerate(vs)], col=c, lw=1.2)
        if xlab:
            self.p.text((x0 + x1) / 2, y0 - 22, xlab, 7.0, col=MUT, align="c")
        self.y -= h + 6
        self.legend([(k, c) for k, c, _ in series])

    def legend(self, items):
        self.need(16)
        x = 42.0
        for k, c in items:
            self.p.rect(x, self.y, 8, 8, fill=c)
            self.p.text(x + 12, self.y + 1, k, 7.2, col=INK)
            x += 16 + self.p.text_width(k, 7.2)
        self.y -= 16

    def ranges(self, items, h=None, lab_w=120):
        """Диапазоны: [(подпись, p10, p50, p90, цвет)]"""
        n = len(items)
        h = h or (n * 24 + 26)
        self.need(h + 10)
        x0, x1 = 42.0 + lab_w, 42.0 + self.wide - 20
        lo = min(i[1] for i in items)
        hi = max(i[3] for i in items)
        pad = (hi - lo) * 0.12 or 1.0
        lo, hi = lo - pad, hi + pad
        xp = lambda v: x0 + (x1 - x0) * (v - lo) / float(hi - lo)
        if lo < 0 < hi:
            self.p.line(xp(0), self.y - h + 20, xp(0), self.y, col="#b9b6ae", lw=0.6)
        for i, (k, a, m, b, c) in enumerate(items):
            y = self.y - 14 - i * 24
            self.p.text(36, y, k, 7.6, col=INK)
            self.p.rect(xp(a), y - 3, xp(b) - xp(a), 11, fill=c)
            self.p.line(xp(m), y - 6, xp(m), y + 11, col="#ffffff", lw=1.6)
            self.p.text(xp(a) - 4, y, CA.f(a, 0), 6.8, col=MUT, align="r")
            self.p.text(xp(b) + 4, y, CA.f(b, 0), 6.8, col=MUT)
        self.p.text((x0 + x1) / 2, self.y - h + 8, "Границы столбца соответствуют P10 и P90, "
                    "светлая черта соответствует медиане", 6.8, col=MUT, align="c")
        self.y -= h

    def hist(self, series, h=170, bins=36, ylab="Число прогонов"):
        """Гистограмма распределения: [(подпись, цвет, значения)]"""
        allv = [v for _, _, vs in series for v in vs]
        lo, hi = min(allv), max(allv)
        if hi == lo:
            hi = lo + 1.0
        step = (hi - lo) / float(bins)
        hs = []
        for k, c, vs in series:
            cnt = [0] * bins
            for v in vs:
                j = int((v - lo) / step)
                cnt[min(max(j, 0), bins - 1)] += 1
            hs.append((k, c, cnt))
        top = max(max(c) for _, _, c in hs)
        x0, x1, y0, y1, yp = self._frame(h, 0, top, ylab=ylab)
        bw = (x1 - x0) / float(bins)
        for k, c, cnt in hs:
            pts = []
            for j, v in enumerate(cnt):
                pts.append((x0 + j * bw, yp(v)))
                pts.append((x0 + (j + 1) * bw, yp(v)))
            self.p.poly(pts, col=c, lw=1.0)
        for i in range(5):
            v = lo + (hi - lo) * i / 4.0
            self.p.text(x0 + (x1 - x0) * i / 4.0, y0 - 11, CA.f(v, 0), 6.8, col=MUT, align="c")
        self.p.text((x0 + x1) / 2, y0 - 22, "Чистый дисконтированный доход, млн руб.",
                    7.0, col=MUT, align="c")
        self.y -= h + 6
        self.legend([(k, c) for k, c, _ in series])

    def save(self, path):
        return self.p.save(path)


# ---------------------------------------------------------------- содержание
def _inputs_rows(state):
    rows = []
    for group, items in CA.FIELDS:
        rows.append([group.upper(), ""])
        for it in items:
            key, lab = it[0], it[1]
            pct = it[3] if len(it) > 3 else 0
            v = state.get(key)
            if isinstance(v, bool):
                v = "да" if v else "нет"
            elif isinstance(v, (list, tuple)):
                v = "; ".join(CA.f(x, 2) for x in v)
            elif isinstance(v, float):
                x = v * 100 if pct else v
                v = CA.f(x, 0 if abs(x - round(x)) < 1e-9 else 2)
            rows.append([lab, str(v)])
    return rows


def build(R, mc, state, opts, path):
    """Сборка отчета. opts: dict(depth=..., sections=set(...), scn=...)"""
    depth = opts.get("depth", "std")
    want = opts.get("sections", set(k for k, _ in SECTIONS))
    full = depth == "full"
    std = depth in ("std", "full")
    p = R["p"]
    d = Doc("Отчет по расчету модели управления инновационной деятельностью")

    # ---------------------------------------------------------- титул
    d.p.rect(36, d.p.H - 156, d.wide, 98, fill=NAVY)
    d.p.text(58, d.p.H - 88, "Отчет по расчету", 20, col="#ffffff", bold=True)
    yy = d.p.H - 110
    for ln in d.p.wrap("Модель управления инновационной деятельностью при реализации "
                       "инвестиционного проекта. Расчет сценарных условий интеграции",
                       d.wide - 32, 10):
        d.p.text(58, yy, ln, 10, col="#c9d8ea")
        yy -= 14
    d.y = d.p.H - 186
    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    d.table(["Показатель", "Значение"], [
        ["Дата формирования отчета", now],
        ["Автор и разработчик программы", "Postautov_K_V"],
        ["Бюджет проекта, млн руб.", CA.f(p.budget, 1)],
        ["Доля инновационной части, %", CA.f(p.share_inn * 100, 1)],
        ["Ставка дисконтирования, % годовых", CA.f(p.rate * 100, 1)],
        ["Расчетный период, лет", str(p.n_years)],
        ["Глубина детализации", dict(DEPTHS)[depth].split(".")[0]],
    ], widths=[62, 38], align=["l", "r"])
    d.note("Расчет выполнен программой модели по введенным значениям. Суммы приведены "
           "в млн руб. в постоянных ценах, время указано в годах от начала разработки. "
           "Значения показателей зависят от исходных данных и подлежат уточнению "
           "по мере выполнения стадий проекта.")

    # ---------------------------------------------------------- входные данные
    if "inputs" in want:
        d.h1("1. Входные данные")
        d.table(["Параметр", "Значение"], _inputs_rows(state), widths=[72, 28], align=["l", "r"])
        h, rows = CA.t_derived(R)
        d.h2("Производные величины")
        d.table(h, rows, widths=[72, 28], align=["l", "r"])

    # ---------------------------------------------------------- проверка
    if "check" in want:
        d.h1("2. Проверка данных и тождеств расчета")
        h1, r1, ok1 = CA.t_inputs(R)
        h2, r2, ok2 = CA.t_identities(R)
        d.table(["Блок проверки", "Строк", "Результат"], [
            ["Проверка введенных данных", str(len(r1)),
             "все условия выполнены" if ok1 else "есть нарушения"],
            ["Проверка тождеств расчета", str(len(r2)),
             "все тождества выполнены" if ok2 else "есть нарушения"],
        ], widths=[60, 15, 25], align=["l", "r", "r"])
        if not ok1 or not ok2 or full:
            if not ok1 or full:
                d.h2("Проверка введенных данных")
                d.table(h1, r1, widths=[56, 26, 18], align=["l", "r", "r"])
            if not ok2 or full:
                d.h2("Проверка тождеств расчета")
                d.table(h2, r2, widths=[56, 26, 18], align=["l", "r", "r"])

    # ---------------------------------------------------------- показатели
    if "summary" in want:
        d.h1("3. Показатели эффективности сценариев")
        d.vbars([(SCL[s], R["scn"][s]["ind"]["npv"], COL[s]) for s in SC],
                ylab="Чистый дисконтированный доход, млн руб.")
        h, rows = CA.t_summary(R)
        d.table(h, rows, widths=[16, 11, 6, 8, 13, 17, 12, 17])
        d.h2("Накопленный дисконтированный поток")
        yrs = [r["year"] for r in R["scn"]["BASE"]["rows"]]
        d.lines(yrs, [(SCL[s], COL[s], [r["cumd"] for r in R["scn"][s]["rows"]]) for s in SC],
                ylab="Млн руб.", xlab="Год расчетного периода", xfmt=lambda v: "%d" % int(v))

    # ---------------------------------------------------------- календарь
    if "calendar" in want:
        d.h1("4. Календарный план")
        d.hbars([(SCL[s], R["scn"][s]["sch"]["tv"], COL[s]) for s in SC], unit=" лет")
        h, rows = CA.t_cal_summary(R)
        d.table(h, rows, widths=[14, 12, 9, 11, 13, 11, 12, 9, 9])
        if full:
            for s in SC:
                (h1, r1), (h2, r2) = CA.t_calendar(R, s)
                d.h2("%s. Переходы уровней готовности" % SCL[s])
                d.table(h1, r1, widths=[22, 20, 22, 20, 16])
                d.h2("%s. Стадии строительства" % SCL[s])
                d.table(h2, r2, widths=[32, 17, 17, 18, 16])

    # ---------------------------------------------------------- потоки
    if "flows" in want:
        d.h1("5. Денежные потоки")
        d.para("Годовые потоки показаны графически. Итоговая таблица содержит приведенные "
               "величины, из которых складывается чистый дисконтированный доход.")
        sel = opts.get("scn") or "TRL5"
        rows = R["scn"][sel]["rows"]
        d.h2("%s. Денежный поток по годам" % SCL[sel], keep=230)
        d.flowbars(rows)
        d.para("Столбцы вниз показывают затраты года, причем инновационные затраты включают "
               "опытную инфраструктуру, затраты на доработки и затраты на хранение и повторную "
               "верификацию оборудования. Столбцы вверх показывают поступления от эксплуатации "
               "за вычетом налога.")
        head = ["Сценарий", "Приведенные поступления", "Приведенные инновационные затраты",
                "Приведенные инвестиционные затраты", "Приведенный налог", "ЧДД, млн руб."]
        rr = []
        for s in SC:
            rw = R["scn"][s]["rows"]
            i = R["scn"][s]["ind"]
            pv_inn = sum((r["inn"] + r["pilot"] + r["rework"] + r["t7x"]) * r["df"] for r in rw)
            pv_inv = sum(r["inv"] * r["df"] for r in rw)
            rr.append([SCL[s], CA.f(i["pv_cf"], 1), CA.f(pv_inn, 1), CA.f(pv_inv, 1),
                       CA.f(sum(r["tax"] * r["df"] for r in rw), 1), CA.f(i["npv"], 1)])
        d.h2("Итоговая таблица приведенных величин")
        d.table(head, rr, widths=[18, 17, 18, 18, 15, 14])
        if full:
            for s in SC:
                h, rows2 = CA.t_flows(R, s)
                d.h2("%s. Годовая таблица" % SCL[s])
                d.table(h, rows2, size=10.0, widths=[5] + [5.6] * (len(h) - 1))

    # ---------------------------------------------------------- чувствительность
    if "sens" in want:
        d.h1("6. Чувствительность")
        d.h2("Зависимость от ставки дисконтирования")
        xs = [r["rate"] * 100 for r in R["rates"]]
        d.lines(xs, [(SCL[s], COL[s], [r[s] for r in R["rates"]]) for s in SC],
                ylab="ЧДД, млн руб.", xlab="Ставка дисконтирования, % годовых")
        d.h2("Зависимость от доли инновационной части")
        xs = [r["share"] * 100 for r in R["shares"]]
        d.lines(xs, [(SCL[s], COL[s], [r[s] for r in R["shares"]]) for s in SC],
                ylab="ЧДД, млн руб.", xlab="Доля инновационной части, %")
        d.h2("Зависимость от стоимости опытной инфраструктуры")
        xs = [r["cost"] for r in R["pilot"]]
        d.lines(xs, [(SCL[s], COL[s], [r[s] for r in R["pilot"]]) for s in SC],
                ylab="ЧДД, млн руб.", xlab="Стоимость опытной инфраструктуры, млн руб.")
        if std:
            h, rows = CA.t_rates(R)
            d.h2("Итоговая таблица по ставке дисконтирования")
            d.table(h, rows, widths=[16, 21, 21, 21, 21])
        if full:
            h, rows = CA.t_shares(R)
            d.h2("Доля инновационной части")
            d.table(h, rows, widths=[16, 21, 21, 21, 21])
            h, rows = CA.t_pilot(R)
            d.h2("Стоимость опытной инфраструктуры")
            d.table(h, rows, widths=[16, 14, 14, 14, 14, 14, 14])

    # ---------------------------------------------------------- имитация
    if "mc" in want:
        d.h1("7. Имитационное моделирование")
        if not mc:
            d.para("Прогоны не выполнялись. Для включения раздела выполните расчет "
                   "на вкладке «Имитационное моделирование».")
        else:
            d.para("Выполнено %d прогонов, начальное значение генератора %d. При каждом прогоне "
                   "одновременно отклоняются бюджет, сроки, ставка, выручка и параметры доработок."
                   % (mc["N"], mc["seed"]))
            d.h2("Распределение чистого дисконтированного дохода")
            d.hist([(SCL[s], COL[s], mc["series"][s]) for s in SC])
            d.h2("Диапазон от P10 до P90")
            d.ranges([(SCL[s], mc["scn"][s]["p10"], mc["scn"][s]["p50"],
                       mc["scn"][s]["p90"], COL[s]) for s in SC])
            h, rows = CA.t_mc(mc)
            d.table(h, rows, widths=[16, 11, 12, 11, 12, 14, 12, 12])
            if std:
                h, rows = CA.t_mc_adv(mc)
                d.h2("Преимущество над базовым сценарием")
                d.table(h, rows, widths=[26, 18, 18, 18, 20])
            if full:
                h, rows = CA.t_mc_d56(mc)
                d.h2("Сравнение сценариев TRL5 и TRL6")
                d.table(h, rows, widths=[72, 28], align=["l", "r"])

    # ---------------------------------------------------------- доработки
    if "ev" in want:
        d.h1("8. События доработки")
        prof = CA.risk_profile(R)
        d.h2("Преимущество и ожидаемые потери")
        items = []
        for x in prof:
            items.append((x["label"], x["adv"], COL[x["key"]]))
        d.vbars(items, ylab="Преимущество над базовым сценарием, млн руб.")
        d.table(["Сценарий", "Преимущество, млн руб.", "Ожидаемая потеря, млн руб.",
                 "Преимущество за вычетом потерь, млн руб."],
                [[x["label"], CA.f(x["adv"], 1), CA.f(x["eloss"], 2),
                  CA.f(x["adv"] - x["eloss"], 1)] for x in prof],
                widths=[22, 26, 26, 26])
        d.h2("Итог по исходам событий")
        rr = []
        for s in ("TRL7", "TRL6", "TRL5"):
            o = R["scn"][s]["out"]
            worst = min(i["npv"] for i in o["items"])
            rr.append([SCL[s], CA.f(o["npv0"], 1), CA.f(o["E_npv"], 1), CA.f(o["E_loss"], 2),
                       CA.f(worst, 1), CA.f(worst - R["base"], 1), str(len(o["items"]))])
        d.table(["Сценарий", "ЧДД без событий", "Ожидаемый ЧДД", "Ожидаемая потеря",
                 "Наихудший ЧДД", "Преимущество в наихудшем исходе", "Исходов"],
                rr, widths=[17, 13, 13, 13, 13, 19, 12])
        if std:
            for s in ("TRL7", "TRL6", "TRL5"):
                (h1, r1), (h2, r2), note = CA.t_events(R, s)
                d.h2("%s. Перечень событий" % SCL[s])
                d.table(h1, r1, widths=[22, 32, 13, 18, 15])
                if full:
                    d.h2("%s. Перебор исходов" % SCL[s])
                    d.table(h2, r2, size=10.0, widths=[32, 12, 13, 12, 15, 16])
                d.para(note)

    # ---------------------------------------------------------- налоги
    if "tax" in want:
        d.h1("9. Налоговые расчеты")
        h1, r1, n1, h2, r2, n2, txt, data = CA.t_tax(R)
        d.h2("Разложение чистого дисконтированного дохода")
        d.table(h1, r1, widths=[20, 20, 16, 20, 12, 12])
        d.note(n1)
        d.h2("Сравнение порядков признания инновационных затрат")
        d.vbars([(SCL[s], data[s]["npvB"] - data[s]["npvA"], COL[s]) for s in SC],
                ylab="Изменение ЧДД при переходе на амортизацию, млн руб.", h=130)
        if std:
            d.table(h2, r2, size=10.0, widths=[15, 11, 11, 11, 13, 13, 13, 11, 10])
        d.note(n2)
        d.para(txt)

    # ---------------------------------------------------------- выбор
    if "pick" in want:
        d.h1("10. Выбор сценария")
        h, rows, txt = CA.t_pick(R)
        d.table(h, rows, size=10.0, widths=[14, 10, 12, 12, 11, 11, 14, 9, 11])
        d.note(txt)
        if R["p"].use_crit:
            ok = [s for s in ("TRL7", "TRL6", "TRL5")
                  if min(i["npv"] for i in R["scn"][s]["out"]["items"]) - R["base"] > 0]
            if ok:
                h1, r1, h2, r2 = CA.t_crit(R, ok)
                d.h2("Шестикритериальная оценка")
                d.table(h1, r1, size=10.0, widths=[16, 13, 10, 13, 14, 12, 11])
                d.note("Исходные величины оценки. Остаток базового варианта принят равным нулю, "
                       "запас устойчивости базового варианта принят наибольшим среди вариантов, "
                       "поскольку доработок в нем нет.")
                d.table(h2, r2, size=10.0, widths=[16] + [11] * (len(h2) - 2) + [10])
                d.note("Количественные критерии нормированы линейно по наилучшему и наихудшему "
                       "значению среди вариантов, для срока ввода нормировка обращена. Экспертные "
                       "оценки переведены в баллы по формуле, в которой из оценки вычитается "
                       "единица и результат делится на четыре. Оценка S является взвешенной "
                       "суммой баллов.")

    d.para("Отчет сформирован программой модели. Автор и разработчик Postautov_K_V.", 7.4)
    return d.save(path)

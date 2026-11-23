# -*- coding: utf-8 -*-
# Автор и разработчик: Postautov_K_V
"""Настольная программа расчета модели интеграции инновационного и инвестиционного процессов.

Расчетное ядро: модуль model_core (тот же, что применен в дипломном проекте).
Запуск: python app.py
"""
import os
import sys
import math
import random
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import calc as CA
import report as RP

TITLE = ("Модель управления инновационной деятельностью при реализации "
         "инвестиционного проекта. Расчет сценариев интеграции")
VERSION = "1.7 от 23.11.2026"
SIGN = "Дипломный проект, версия программы " + VERSION + "\nАвтор Постаутов К.В."
BG = "#fcfcfb"
INK = "#1c1c1a"
MUT = "#7a7a74"
LINE = "#dedcd6"
ACC = "#2F6FC0"
HEAD = "#1d3a5c"


# ------------------------------------------------------------------ таблица
class Table(ttk.Frame):
    def __init__(self, master, head, rows, widths=None, height=12, marks=None,
                 extra_tags=None, row_tags=None):
        """marks — номера строк, которые выделяются цветом.
        extra_tags — словарь имя тега и цвет фона, row_tags — тег для каждой строки."""
        ttk.Frame.__init__(self, master)
        cols = ["c%d" % i for i in range(len(head))]
        self.tv = ttk.Treeview(self, columns=cols, show="headings", height=height)
        self.tv.tag_configure("mark", background="#dff3e6")
        self.tv.tag_configure("warn", background="#fbe3e3")
        for nm, cl in (extra_tags or {}).items():
            self.tv.tag_configure(nm, background=cl)
        marks = set(marks or ())
        for i, h in enumerate(head):
            self.tv.heading(cols[i], text=h)
            w = widths[i] if widths else (240 if i == 0 else 120)
            self.tv.column(cols[i], width=w, anchor="w" if i == 0 else "e", stretch=(i == 0))
        for j, r in enumerate(rows):
            tags = ("mark",) if j in marks else (
                ("warn",) if any(str(x) == "НАРУШЕНО" for x in r) else ())
            if not tags and row_tags and j < len(row_tags) and row_tags[j]:
                tags = (row_tags[j],)
            self.tv.insert("", "end", values=[str(x) for x in r], tags=tags)
        vs = ttk.Scrollbar(self, orient="vertical", command=self.tv.yview)
        hs = ttk.Scrollbar(self, orient="horizontal", command=self.tv.xview)
        self.tv.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.tv.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


# ------------------------------------------------------------------ графики
class Chart(tk.Canvas):
    def __init__(self, master, width=820, height=300):
        tk.Canvas.__init__(self, master, width=width, height=height, bg="white",
                           highlightthickness=1, highlightbackground=LINE)
        self.W, self.H = width, height
        self.job = None

    @staticmethod
    def ticks(lo, hi, k=4):
        return [lo + (hi - lo) * i / float(k) for i in range(k + 1)]

    def frame(self, lo, hi, left=86, right=24, top=18, bottom=46, ylab=""):
        self.delete("all")
        self.L, self.R, self.T, self.B = left, self.W - right, top, self.H - bottom
        self.lo, self.hi = lo, hi
        for v in self.ticks(lo, hi):
            y = self.ypix(v)
            self.create_line(self.L, y, self.R, y, fill="#e8e6e0")
            self.create_text(self.L - 8, y, text=CA.f(v, 0), anchor="e", fill=MUT, font=("Segoe UI", 8))
        if lo < 0 < hi:
            self.create_line(self.L, self.ypix(0), self.R, self.ypix(0), fill="#b9b6ae")
        if ylab:
            self.create_text(4, 9, text=ylab, anchor="w", fill=MUT, font=("Segoe UI", 8))

    def ypix(self, v):
        if self.hi == self.lo:
            return (self.T + self.B) / 2.0
        return self.T + (self.hi - v) / float(self.hi - self.lo) * (self.B - self.T)

    @staticmethod
    def bounds(vals, zero=True):
        hi, lo = max(vals), min(vals)
        if zero:
            hi, lo = max(hi, 0.0), min(lo, 0.0)
        pad = (hi - lo) * 0.12 or 1.0
        return lo - (pad if lo < 0 else 0.0), hi + pad

    def bars(self, items, ylab=""):
        lo, hi = self.bounds([v for _, v, _ in items])
        self.frame(lo, hi, ylab=ylab)
        bw = (self.R - self.L) / float(len(items))
        for i, (k, v, col) in enumerate(items):
            x = self.L + i * bw + bw * 0.2
            w = bw * 0.6
            y0, y1 = self.ypix(0), self.ypix(v)
            self.create_rectangle(x, min(y0, y1), x + w, max(y0, y1), fill=col, outline=col)
            self.create_text(x + w / 2, y1 - 9 if v >= 0 else y1 + 9, text=CA.f(v, 1),
                             fill=INK, font=("Segoe UI", 9, "bold"))
            self.create_text(x + w / 2, self.B + 16, text=k, fill=MUT, font=("Segoe UI", 8))

    def flow_bars(self, rows, ylab="млн руб."):
        """Денежный поток по годам: затраты вниз, поступления вверх,
        инновационные и инвестиционные затраты показаны отдельно."""
        inn = [r["inn"] + r["pilot"] + r["rework"] + r["t7x"] for r in rows]
        inv = [r["inv"] for r in rows]
        op = [r["cf_op"] for r in rows]
        cum = [r["cumd"] for r in rows]
        hi = max([0.0] + op + cum)
        lo = min([0.0] + [-(inn[i] + inv[i]) for i in range(len(rows))] + cum)
        pad = (hi - lo) * 0.1 or 1.0
        self.frame(lo - pad, hi + pad, ylab=ylab)
        bw = (self.R - self.L) / float(len(rows))
        step = max(1, int(round(len(rows) / 12.0)))
        for i, r in enumerate(rows):
            x = self.L + i * bw + bw * 0.12
            w = max(2.0, bw * 0.76)
            y0 = self.ypix(0)
            if op[i] > 0:
                self.create_rectangle(x, self.ypix(op[i]), x + w, y0,
                                      fill="#9fb8cf", outline="#9fb8cf")
            base = 0.0
            if inv[i] > 0:
                self.create_rectangle(x, y0, x + w, self.ypix(-inv[i]),
                                      fill="#1B9E77", outline="#1B9E77")
                base = inv[i]
            if inn[i] > 0:
                self.create_rectangle(x, self.ypix(-base), x + w, self.ypix(-base - inn[i]),
                                      fill="#8E44AD", outline="#8E44AD")
            if i % step == 0:
                self.create_text(x + w / 2, self.B + 16, text=str(r["year"]),
                                 fill=MUT, font=("Segoe UI", 8))
        pts = []
        for i, v in enumerate(cum):
            pts += [self.L + i * bw + bw * 0.5, self.ypix(v)]
        if len(pts) >= 4:
            self.create_line(*pts, fill="#003366", width=2, smooth=False)

    CAL_ST = ["ИД", "ПД", "РД", "МТР", "СМР", "ПНР хх", "ПНР нагр.", "КО"]
    CAL_SC = ["#3C4F66", "#0079C2", "#1B9E77", "#d9a21b", "#3C4F66", "#C4690E", "#c2453d", "#7a3fa0"]
    CAL_TC = {2: "#cfd8e3", 3: "#b7c4d6", 4: "#9fb0c8", 5: "#0079C2", 6: "#1B9E77",
              7: "#8E44AD", 8: "#C4690E", 9: "#c2453d"}

    def calendar_panel(self, key, sch, maxT):
        """Календарный план сценария: разработка, строительство, опытная инфраструктура."""
        has = key in ("BASE", "TRL7")
        L, Rr, T, Bm = 150, 26, 44, 26
        rowH, gap = 24, 20
        W = int(self["width"])
        xp = lambda t: L + t / maxT * (W - L - Rr)
        yr = lambda i: T + i * (rowH + gap)
        for g in range(int(maxT) + 1):
            self.create_line(xp(g), T - 6, xp(g), yr(3 if has else 2) - gap,
                             fill="#e9eef5")
            self.create_text(xp(g), yr(3 if has else 2) - gap + 12, text=str(g),
                             fill=MUT, font=("Segoe UI", 8))
        names = ["Разработка (TRL)", "Строительство"] + (["Опытная инфраструктура"] if has else [])
        for i, t in enumerate(names):
            self.create_text(L - 10, yr(i) + rowH / 2, text=t, fill=MUT,
                             anchor="e", font=("Segoe UI", 8))
        yd = yr(0)
        for j in range(8):
            a, b = sch["trl_start"][j], sch["conf"][j]
            k = j + 2
            self.create_rectangle(xp(a), yd, xp(b), yd + rowH, fill=self.CAL_TC[k], outline="white")
            if xp(b) - xp(a) > 26:
                self.create_text((xp(a) + xp(b)) / 2, yd + rowH / 2, text="TRL%d" % k,
                                 fill="white" if k >= 5 else "#2b3440", font=("Segoe UI", 8, "bold"))
            self.create_polygon(xp(b), yd - 7, xp(b) + 4, yd - 3, xp(b), yd + 1, xp(b) - 4, yd - 3,
                                fill="#222222", outline="")
        ext = None
        if key == "TRL7":
            ext = (7, sch["conf"][5], sch["st"][5],
                   "подтверждение TRL7 продолжается: демонтаж и монтаж на объекте")
        if key in ("TRL6", "TRL5"):
            ext = (6, sch["conf"][4], sch["st"][4],
                   "подтверждение TRL6 продолжается: изготовление и поставка оборудования")
        if ext:
            k, a, b, note = ext
            self.create_rectangle(xp(a), yd, xp(b), yd + rowH, fill=self.light(self.CAL_TC[k]),
                                  outline=self.CAL_TC[k], dash=(5, 3))
            self.create_text(xp(a) + 4, yd + rowH + 10, text=note, fill=MUT, anchor="w",
                             font=("Segoe UI", 8, "italic"))
        yc = yr(1)
        for j in range(8):
            a, b = sch["st"][j], sch["en"][j]
            self.create_rectangle(xp(a), yc, xp(b), yc + rowH, fill=self.CAL_SC[j], outline="white")
            if xp(b) - xp(a) > 30:
                self.create_text((xp(a) + xp(b)) / 2, yc + rowH / 2, text=self.CAL_ST[j],
                                 fill="white", font=("Segoe UI", 8))
        if has:
            yp_ = yr(2)
            end_t = 3.0 if key == "BASE" else sch["conf"][5]
            for a, b, lab, col in ((sch["trl_start"][4], sch["conf"][4], "создание", "#e8d9b0"),
                                   (sch["conf"][4], end_t, "испытания", "#d2b86a")):
                self.create_rectangle(xp(a), yp_, xp(b), yp_ + rowH, fill=col, outline="white")
                if xp(b) - xp(a) > 44:
                    self.create_text((xp(a) + xp(b)) / 2, yp_ + rowH / 2, text=lab,
                                     fill="#3b3b3b", font=("Segoe UI", 8))
        ent, tv = sch["st"][1], sch["tv"]
        bot = yr(3 if has else 2) - gap
        self.create_line(xp(ent), T - 8, xp(ent), bot, fill="#c2453d", dash=(3, 3))
        self.create_text(xp(ent) - 5, T - 16, text="вход: начало ПД", fill="#c2453d",
                         anchor="e", font=("Segoe UI", 8))
        self.create_line(xp(tv), T - 8, xp(tv), bot, fill="#222222", dash=(5, 3))
        self.create_text(xp(tv) + 5, T - 16, text="ввод " + CA.f(tv, 2), fill=INK,
                         anchor="w", font=("Segoe UI", 8))
        self.create_text(L - 10, 16, text=CA.SCL[key], fill=NAVY if "NAVY" in globals() else ACC,
                         anchor="e", font=("Segoe UI", 9, "bold"))

    def tax_bars(self, data):
        """ЧДД при двух порядках налогового признания."""
        hi = max(max(d["npvA"], d["npvB"]) for d in data.values()) * 1.25
        self.frame(0.0, hi, ylab="млн руб.")
        bw = (self.R - self.L) / float(len(CA.SC))
        for i, k in enumerate(CA.SC):
            d = data[k]
            x = self.L + i * bw + bw * 0.18
            w = bw * 0.26
            col = CA.COL[k]
            self.create_rectangle(x, self.ypix(d["npvA"]), x + w, self.ypix(0), fill=col, outline=col)
            self.create_rectangle(x + w + 6, self.ypix(d["npvB"]), x + 2 * w + 6, self.ypix(0),
                                  fill=self.light(col), outline=self.light(col))
            self.create_text(x + w / 2, self.ypix(d["npvA"]) - 9, text=CA.f(d["npvA"], 1),
                             fill=col, font=("Segoe UI", 9, "bold"))
            self.create_text(x + w + 6 + w / 2, self.ypix(d["npvB"]) - 9, text=CA.f(d["npvB"], 1),
                             fill=MUT, font=("Segoe UI", 8))
            self.create_text(self.L + i * bw + bw / 2, self.B + 16, text=CA.SCL[k],
                             fill=MUT, font=("Segoe UI", 8))

    def tax_years(self, data, key):
        """Налог на прибыль по годам при двух порядках признания."""
        a, b = data[key]["a"], data[key]["b"]
        hi = max(max(r["tax"] for r in a), max(r["tax"] for r in b)) * 1.2 or 1.0
        y0, y1 = a[0]["year"], a[-1]["year"]
        self.frame(0.0, hi, ylab="млн руб.")
        xp = lambda yr: self.L + (yr - y0) / float(y1 - y0) * (self.R - self.L)
        def line(rows, col, dash):
            pts = []
            for r in rows:
                pts += [xp(r["year"]), self.ypix(r["tax"])]
            self.create_line(*pts, fill=col, width=2, dash=dash)
        line(a, CA.COL[key], None)
        line(b, "#C4690E", (5, 3))
        for yr in range(y0, y1 + 1, 5):
            self.create_text(xp(yr), self.B + 16, text=str(yr), fill=MUT, font=("Segoe UI", 8))

    def light(self, hexcol):
        r, g, bl = (int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
        mix = lambda v: int(v + (255 - v) * 0.55)
        return "#%02x%02x%02x" % (mix(r), mix(g), mix(bl))

    def risk_adv(self, prof):
        """Преимущество над базовым сценарием и ожидаемые потери от доработок."""
        hi = max(d["adv"] for d in prof) * 1.22
        self.frame(0.0, hi, ylab="млн руб.")
        bw = (self.R - self.L) / float(len(prof))
        for i, d in enumerate(prof):
            x = self.L + i * bw + bw * 0.3
            w = bw * 0.4
            rem = d["adv"] - d["eloss"]
            y0, yr, ya = self.ypix(0), self.ypix(rem), self.ypix(d["adv"])
            col = CA.COL[d["key"]]
            self.create_rectangle(x, yr, x + w, y0, fill=col, outline=col)
            self.create_rectangle(x, ya, x + w, yr, fill="#C4690E", outline="#C4690E")
            self.create_text(x + w / 2, ya - 22, text=CA.f(d["adv"], 1), fill=col,
                             font=("Segoe UI", 9, "bold"))
            self.create_text(x + w / 2, ya - 9, text="потери " + CA.f(d["eloss"], 2),
                             fill="#C4690E", font=("Segoe UI", 8))
            self.create_text(x + w / 2, yr + 13, text=CA.f(rem, 1), fill="white",
                             font=("Segoe UI", 9, "bold"))
            self.create_text(x + w / 2, self.B + 16, text=d["label"], fill=MUT,
                             font=("Segoe UI", 8))

    def risk_contrib(self, prof):
        """Вклад событий доработки в ожидаемые потери."""
        hi = max(v for d in prof for _, v in d["contrib"]) * 1.35
        self.frame(0.0, hi, ylab="млн руб.")
        bw = (self.R - self.L) / float(len(prof))
        for i, d in enumerate(prof):
            n = len(d["contrib"])
            w = min(34.0, bw * 0.72 / n)
            x0 = self.L + i * bw + (bw - n * w) / 2.0
            for j, (k, v) in enumerate(d["contrib"]):
                x = x0 + j * w
                col = ("#E8B384", "#DFA066", "#D4873F", "#C4690E")[min(j, 3)]
                self.create_rectangle(x + 2, self.ypix(v), x + w - 2, self.ypix(0),
                                      fill=col, outline=col)
                self.create_text(x + w / 2, self.ypix(v) - 8, text="TRL%d" % k,
                                 fill=MUT, font=("Segoe UI", 8))
            self.create_text(self.L + i * bw + bw / 2, self.T + 8,
                             text="всего " + CA.f(d["eloss"], 2), fill=CA.COL[d["key"]],
                             font=("Segoe UI", 9, "bold"))
            self.create_text(self.L + i * bw + bw / 2, self.B + 16, text=d["label"],
                             fill=MUT, font=("Segoe UI", 8))

    def hist(self, series, order, cols, labels, neg, smooth=False, bins=46):
        """Распределение прогонов по сценариям: ступенчатая линия или сглаженная кривая."""
        self.delete("all")
        L, R, T = 58, self.W - 16, 14
        B = self.H - 42
        allv = [v for s in order for v in series[s]]
        xlo, xhi = min(allv), max(allv)
        bw = (xhi - xlo) / bins
        cnt, dens = {}, {}
        ymax = 0.0
        for s in order:
            c = [0] * bins
            for v in series[s]:
                i = min(bins - 1, max(0, int((v - xlo) / bw)))
                c[i] += 1
            cnt[s] = c
            ymax = max(ymax, max(c))
        if smooth:
            grid = 160
            for s in order:
                a = sorted(series[s])
                n = len(a)
                mean = sum(a) / n
                sd = (sum((x - mean) ** 2 for x in a) / n) ** 0.5
                h = 1.06 * sd * n ** -0.2
                sub = a[::4]
                k = n * bw / (len(sub) * h * (2 * math.pi) ** 0.5)
                d = []
                for i in range(grid + 1):
                    x = xlo + (xhi - xlo) * i / grid
                    ssum = 0.0
                    for v in sub:
                        z = (x - v) / h
                        if -4 < z < 4:
                            ssum += math.exp(-0.5 * z * z)
                    d.append((x, ssum * k))
                dens[s] = d
            ymax = max(y for s in order for _, y in dens[s])
        ymax *= 1.1
        xp = lambda v: L + (v - xlo) / (xhi - xlo) * (R - L)
        yp = lambda v: T + (ymax - v) / ymax * (B - T)
        for v in self.ticks(0, ymax):
            self.create_line(L, yp(v), R, yp(v), fill="#ededea")
            self.create_text(L - 7, yp(v), text=CA.f(v, 0), anchor="e", fill=MUT,
                             font=("Segoe UI", 8))
        for v in self.ticks(xlo, xhi):
            if xlo <= v <= xhi:
                self.create_text(xp(v), B + 12, text=CA.f(v, 0), fill=MUT, font=("Segoe UI", 8))
        self.create_line(xp(0), T, xp(0), yp(0), fill="#52514e")
        for s in order:
            pts = []
            if smooth:
                for x, y in dens[s]:
                    pts += [xp(x), yp(y)]
            else:
                pts += [xp(xlo), yp(0)]
                for i in range(bins):
                    pts += [xp(xlo + i * bw), yp(cnt[s][i]),
                            xp(xlo + (i + 1) * bw), yp(cnt[s][i])]
                pts += [xp(xhi), yp(0)]
            self.create_line(*pts, fill=cols[s], width=2)
        labs = []
        for s in order:
            a = sorted(series[s])
            m = a[int(0.5 * (len(a) - 1))]
            if smooth:
                d = dens[s]
                k = 0
                while k < len(d) - 1 and d[k][0] < m:
                    k += 1
                hgt = d[k][1]
            else:
                hgt = cnt[s][min(bins - 1, max(0, int((m - xlo) / bw)))]
            self.create_line(xp(m), yp(0), xp(m), yp(hgt), fill=cols[s], dash=(4, 3))
            self.create_polygon(xp(m), yp(0), xp(m) - 5, yp(0) + 8, xp(m) + 5, yp(0) + 8,
                                fill=cols[s], outline="")
            labs.append([xp(m), yp(hgt), m, cols[s]])
        labs.sort(key=lambda q: q[0])
        put = []
        for x, y, m, c in labs:
            yy = y - 8
            while any(abs(q[0] - x) < 52 and abs(q[1] - yy) < 15 for q in put):
                yy -= 15
            put.append((x, yy))
            self.create_text(x, yy, text="Ме %s" % CA.f(m, 0), fill=c,
                             font=("Segoe UI", 8, "bold"))
        lx, ly = R - 250, T + 10
        self.create_rectangle(lx - 6, T + 2, R - 4, T + 6 + len(order) * 16,
                              fill="white", outline="")
        for s in order:
            self.create_line(lx, ly, lx + 20, ly, fill=cols[s], width=2)
            self.create_text(lx + 26, ly, text="%s, убыточных %s %%"
                             % (labels[s], CA.f(neg[s] * 100, 1)), anchor="w",
                             fill="#333", font=("Segoe UI", 8))
            ly += 16
        self.create_text((L + R) / 2, self.H - 10, text="ЧДД, млн руб.", fill=MUT,
                         font=("Segoe UI", 8))
        self.create_text(12, (T + B) / 2, text="число\nпрогонов", fill=MUT,
                         font=("Segoe UI", 8), justify="center")

    def cloud(self, series, rates, order, cols, labels, bins=12, maxpts=2500):
        """Облако прогонов: ставка дисконтирования по горизонтали, ЧДД по вертикали."""
        self.delete("all")
        L, R, T = 62, self.W - 16, 16
        B = self.H - 40
        rr = [v * 100.0 for v in rates]
        allv = sorted(v for s in order for v in series[s])
        q = lambda x: allv[int(x * (len(allv) - 1))]
        ylo, yhi = q(0.004), q(0.996)
        pad = (yhi - ylo) * 0.04
        ylo, yhi = ylo - pad, yhi + pad
        xlo, xhi = 9.9, 16.1
        xp = lambda v: L + (v - xlo) / (xhi - xlo) * (R - L)
        yp = lambda v: T + (yhi - v) / (yhi - ylo) * (B - T)
        for v in self.ticks(ylo, yhi):
            self.create_line(L, yp(v), R, yp(v), fill="#e8e6e0")
            self.create_text(L - 7, yp(v), text=CA.f(v, 0), anchor="e", fill=MUT,
                             font=("Segoe UI", 8))
        for v in range(10, 17):
            self.create_text(xp(v), B + 12, text="%d %%" % v, fill=MUT, font=("Segoe UI", 8))
        n = len(rates)
        step = max(1, n // maxpts)
        for s in order:
            a = series[s]
            c = cols[s]
            for i in range(0, n, step):
                y = a[i]
                if y < ylo or y > yhi:
                    continue
                x0, y0 = xp(rr[i]), yp(y)
                self.create_line(x0, y0, x0 + 1, y0, fill=c)
        if ylo < 0 < yhi:
            self.create_line(L, yp(0), R, yp(0), fill="#52514e", width=1)
            self.create_text(R - 3, yp(0) - 3, text="нулевой доход", anchor="se", fill=MUT,
                             font=("Segoe UI", 8))
        edges = [10 + 6.0 * i / bins for i in range(bins + 1)]
        for s in order:
            a = series[s]
            pts = []
            for i in range(bins):
                v = sorted(a[j] for j in range(n) if edges[i] <= rr[j] < edges[i + 1])
                if not v:
                    continue
                pts.append((xp((edges[i] + edges[i + 1]) / 2), yp(v[int(0.5 * (len(v) - 1))])))
            if len(pts) > 1:
                flat = [c for pt in pts for c in pt]
                self.create_line(*flat, fill="white", width=5, capstyle="round", joinstyle="round")
                self.create_line(*flat, fill=cols[s], width=3, capstyle="round", joinstyle="round")
        ly = T + 6
        self.create_rectangle(L + 6, T - 2, L + 212, T + 4 + len(order) * 15,
                              fill="white", outline="")
        for s in order:
            a = sorted(series[s])
            m = a[int(0.5 * (len(a) - 1))]
            self.create_line(L + 12, ly, L + 32, ly, fill=cols[s], width=3)
            self.create_text(L + 38, ly, text="%s, медиана %s" % (labels[s], CA.f(m, 0)),
                             anchor="w", fill="#333", font=("Segoe UI", 8))
            ly += 15
        self.create_text((L + R) / 2, self.H - 10, text="ставка дисконтирования в прогоне",
                         fill=MUT, font=("Segoe UI", 8))
        self.create_text(12, (T + B) / 2, text="ЧДД,\nмлн руб.", fill=MUT,
                         font=("Segoe UI", 8), justify="center")

    def gantt(self, items, xlab=""):
        """Полосы сроков: (название, вход, ввод, окончание разработки, цвет)."""
        self.delete("all")
        L, R, T = 152, self.W - 50, 18
        B = self.H - 26
        hi = max(i[2] for i in items) * 1.06
        xp = lambda v: L + v / float(hi) * (R - L)
        for v in self.ticks(0, hi):
            x = xp(v)
            self.create_line(x, T - 4, x, B, fill="#e8e6e0")
            self.create_text(x, B + 12, text=CA.f(v, 1), fill=MUT, font=("Segoe UI", 8))
        step = (B - T - 22) / float(max(1, len(items) - 1)) if len(items) > 1 else 0.0
        for i, (k, fin, tv, dev, col) in enumerate(items):
            y = T + 18 + i * step
            self.create_text(6, y, text=k, anchor="w", fill=MUT, font=("Segoe UI", 9))
            self.create_rectangle(xp(0), y - 9, max(xp(fin), xp(0) + 1), y + 9,
                                  fill=col, outline=col, stipple="gray25")
            self.create_rectangle(xp(fin), y - 9, xp(tv), y + 9, fill=col, outline=col)
            self.create_line(xp(dev), y - 13, xp(dev), y + 13, fill="#52514e", width=2)
            self.create_text(xp(tv) + 6, y, text=CA.f(tv, 2), anchor="w", fill=col,
                             font=("Segoe UI", 9, "bold"))
        if xlab:
            self.create_text(6, self.H - 8, text=xlab, anchor="w", fill=MUT, font=("Segoe UI", 8))

    def ranges(self, items, xlab=""):
        """Горизонтальные диапазоны: (название, P10, медиана, P90, цвет)."""
        self.delete("all")
        L, R, T = 152, self.W - 30, 20
        B = self.H - 28
        lo = min(i[1] for i in items)
        hi = max(i[3] for i in items)
        pad = (hi - lo) * 0.08 or 1.0
        lo, hi = lo - pad, hi + pad
        xp = lambda v: L + (v - lo) / float(hi - lo) * (R - L)
        for v in self.ticks(lo, hi):
            x = xp(v)
            self.create_line(x, T - 6, x, B, fill="#e8e6e0")
            self.create_text(x, B + 12, text=CA.f(v, 0), fill=MUT, font=("Segoe UI", 8))
        if lo < 0 < hi:
            self.create_line(xp(0), T - 6, xp(0), B, fill="#b9b6ae")
        step = (B - T - 24) / float(max(1, len(items) - 1)) if len(items) > 1 else 0.0
        for i, (k, p10, p50, p90, col) in enumerate(items):
            y = T + 20 + i * step
            self.create_text(6, y, text=k, anchor="w", fill=MUT, font=("Segoe UI", 9))
            self.create_rectangle(xp(p10), y - 8, xp(p90), y + 8, fill=col, outline=col, stipple="gray25")
            for v in (p10, p90):
                self.create_line(xp(v), y - 11, xp(v), y + 11, fill=col, width=2)
            self.create_oval(xp(p50) - 4, y - 4, xp(p50) + 4, y + 4, fill=col, outline="white")
            self.create_text(xp(p50), y - 17, text=CA.f(p50, 0), fill=col, font=("Segoe UI", 9, "bold"))
        if xlab:
            self.create_text(6, self.H - 8, text=xlab, anchor="w", fill=MUT, font=("Segoe UI", 8))

    def lines(self, xs, series, xfmt=str, ylab="", xlab=""):
        allv = [v for se in series for v in se[2]]
        lo, hi = self.bounds(allv)
        self.frame(lo, hi, ylab=ylab)
        n = len(xs)
        step = max(1, int(round(n / 10.0)))
        xpix = lambda i: self.L + (0 if n == 1 else i / float(n - 1) * (self.R - self.L))
        for i, x in enumerate(xs):
            if n <= 12 or i % step == 0:
                self.create_text(xpix(i), self.B + 14, text=xfmt(x), fill=MUT, font=("Segoe UI", 8))
        for k, col, vals in series:
            pts = []
            for i, v in enumerate(vals):
                pts += [xpix(i), self.ypix(v)]
            self.create_line(*pts, fill=col, width=2, smooth=False)
            if n <= 12:
                for i, v in enumerate(vals):
                    x, y = xpix(i), self.ypix(v)
                    self.create_oval(x - 3, y - 3, x + 3, y + 3, fill=col, outline="white")
        if xlab:
            self.create_text((self.L + self.R) / 2, self.H - 10, text=xlab, fill=MUT, font=("Segoe UI", 8))


def legend(master, items):
    fr = ttk.Frame(master)
    for i, (k, col) in enumerate(items):
        c = tk.Canvas(fr, width=12, height=12, highlightthickness=0, bg=BG)
        c.create_rectangle(1, 1, 11, 11, fill=col, outline=col)
        c.grid(row=0, column=i * 2, padx=(10 if i else 0, 4))
        ttk.Label(fr, text=k).grid(row=0, column=i * 2 + 1)
    return fr


# ------------------------------------------------------------------ окно
class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title(TITLE)
        self.geometry("1420x900")
        self.configure(bg=BG)
        self.state_data = CA.defaults()
        self.vars = {}
        self.rows_w = {}
        self.R = None
        self._style()
        self._head()
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)
        self._panel(body)
        self.nb = ttk.Notebook(body)
        self.nb.pack(side="left", fill="both", expand=True, padx=(8, 8), pady=(0, 8))
        self.tabs = {}
        for key, name in (("pick", "Выбор сценария"), ("cal", "Календарный план"),
                          ("sum", "Показатели эффективности"), ("flow", "Годовые потоки"),
                          ("tax", "Налоговые расчеты"), ("ev", "Доработка"),
                          ("mc", "Имитационное моделирование"), ("sens", "Чувствительность"),
                          ("rep", "Отчет"), ("chk", "Проверка расчета")):
            fr = ttk.Frame(self.nb)
            self.nb.add(fr, text=name)
            self.tabs[key] = fr
        self.flow_scn = tk.StringVar(value="BASE")
        self.cal_scn = tk.StringVar(value="BASE")
        self.ev_scn = tk.StringVar(value="TRL5")
        self.mc = None
        self.mc_n = tk.StringVar(value="5000")
        self.mc_seed = tk.StringVar(value="20261107")
        self.mc_busy = False
        self.mc_smooth = tk.BooleanVar(value=False)
        self.mc_rand = tk.BooleanVar(value=False)
        self.rep_sec = {}
        self.rep_depth = tk.StringVar(value="std")
        self.rep_scn = tk.StringVar(value=CA.SCL["TRL5"])
        self.rep_orient = tk.StringVar(value="land")
        self.run()

    def _style(self):
        st = ttk.Style(self)
        try:
            st.theme_use("clam")
        except Exception:
            pass
        st.configure(".", background=BG, foreground=INK, font=("Segoe UI", 9))
        st.configure("TFrame", background=BG)
        st.configure("TLabel", background=BG)
        st.configure("TLabelframe", background=BG)
        st.configure("TLabelframe.Label", background=BG, foreground=MUT, font=("Segoe UI", 9, "bold"))
        st.configure("Treeview", rowheight=21, fieldbackground="white", background="white")
        st.configure("Treeview.Heading", font=("Segoe UI", 8, "bold"), background="#f0efea")
        st.configure("TNotebook.Tab", padding=(12, 6))
        st.configure("Run.TButton", font=("Segoe UI", 9, "bold"))

    def _head(self):
        h = tk.Frame(self, bg=HEAD)
        h.pack(fill="x")
        tk.Label(h, text=SIGN, bg=HEAD, fg="#dfe9f5", font=("Segoe UI", 8),
                 justify="right", anchor="e").pack(side="right", padx=14, pady=9)
        left = tk.Frame(h, bg=HEAD)
        left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text=TITLE, bg=HEAD, fg="white", font=("Segoe UI", 11, "bold"),
                 anchor="w", justify="left").pack(fill="x", padx=14, pady=(9, 0))
        tk.Label(left, text="Суммы в млн руб. в постоянных ценах, время в годах от начала разработки",
                 bg=HEAD, fg="#c9d8ea", font=("Segoe UI", 8), anchor="w").pack(fill="x", padx=14, pady=(2, 9))

    def _panel(self, body):
        outer = ttk.Frame(body, width=400)
        outer.pack(side="left", fill="y", padx=(8, 0), pady=8)
        outer.pack_propagate(False)
        bar = ttk.Frame(outer)
        bar.pack(fill="x", pady=(0, 6))
        ttk.Button(bar, text="Рассчитать", style="Run.TButton", command=self.run).grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(bar, text="По умолчанию", command=self.reset).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(bar, text="Сохранить набор", command=self.save_set).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(bar, text="Загрузить набор", command=self.load_set).grid(row=1, column=1, padx=2, pady=2)
        ttk.Button(bar, text="Выгрузить в Excel", command=self.to_xlsx).grid(row=2, column=0, padx=2, pady=2)
        ttk.Button(bar, text="Выгрузить в CSV", command=self.to_csv).grid(row=2, column=1, padx=2, pady=2)
        self.msg = ttk.Label(outer, text="", foreground="#1B9E77", wraplength=380)
        self.msg.pack(fill="x", pady=(0, 4))
        cv = tk.Canvas(outer, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=cv.yview)
        self.form = ttk.Frame(cv)
        self.form.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=self.form, anchor="nw", width=366)
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        cv.bind_all("<MouseWheel>", lambda e: cv.yview_scroll(int(-e.delta / 120), "units"))
        self._fields()

    @staticmethod
    def _shown(key, v):
        """Значение в том виде, в каком оно показано в форме."""
        k = 100.0 if CA.PCT.get(key) else 1.0
        fmt = lambda x: ("%.10f" % (x * k)).rstrip("0").rstrip(".") if isinstance(x, float) else str(x)
        if isinstance(v, list):
            return "; ".join(fmt(float(x)) for x in v)
        if isinstance(v, bool):
            return str(v)
        return fmt(float(v)) if CA.PCT.get(key) else str(v)

    def help_box(self, key):
        """Всплывающее пояснение к параметру."""
        top = tk.Toplevel(self)
        top.title("Пояснение")
        top.transient(self)
        top.resizable(False, False)
        fr = ttk.Frame(top, padding=14)
        fr.pack(fill="both", expand=True)
        ttk.Label(fr, text=CA.LABEL[key], font=("Segoe UI", 10, "bold"),
                  wraplength=430, justify="left").pack(anchor="w", pady=(0, 6))
        ttk.Label(fr, text=CA.HELP.get(key, "Пояснение не задано."), wraplength=430,
                  justify="left").pack(anchor="w")
        ttk.Button(fr, text="Закрыть", command=top.destroy).pack(anchor="e", pady=(12, 0))
        top.update_idletasks()
        x = self.winfo_rootx() + 60
        y = self.winfo_rooty() + 80
        top.geometry("+%d+%d" % (x, y))
        top.grab_set()

    def _fields(self):
        for w in self.form.winfo_children():
            w.destroy()
        self.vars = {}
        self.rows_w = {}
        r = 0
        for grp, items in CA.FIELDS:
            lf = ttk.Label(self.form, text=grp.upper(), foreground=MUT, font=("Segoe UI", 8, "bold"))
            lf.grid(row=r, column=0, columnspan=3, sticky="w", pady=(10, 2))
            r += 1
            for item in items:
                key, title, kind = item[0], item[1], item[2]
                ttk.Label(self.form, text=title, wraplength=210).grid(
                    row=r, column=0, sticky="w", padx=(2, 2), pady=1)
                b = tk.Button(self.form, text="?", width=2, font=("Segoe UI", 7, "bold"),
                              relief="groove", cursor="hand2",
                              command=lambda k=key: self.help_box(k))
                b.grid(row=r, column=1, sticky="w", padx=(0, 4), pady=1)
                v = self.state_data[key]
                if kind == "bool":
                    var = tk.BooleanVar(value=bool(v))
                    w = ttk.Checkbutton(self.form, variable=var)
                    w.grid(row=r, column=2, sticky="e", pady=1)
                elif kind == "sel":
                    opts = CA.SEL_OPTS[key]
                    var = tk.StringVar(value=dict(opts).get(v, opts[0][1]))
                    w = ttk.Combobox(self.form, textvariable=var, width=26, state="readonly",
                                     values=[name for _, name in opts])
                    w.grid(row=r, column=2, sticky="e", pady=1)
                    w.bind("<<ComboboxSelected>>", lambda _e: self.apply_deps())
                else:
                    var = tk.StringVar(value=self._shown(key, v))
                    w = ttk.Entry(self.form, textvariable=var, width=14, justify="right")
                    w.grid(row=r, column=2, sticky="e", pady=1)
                self.vars[key] = var
                self.rows_w[key] = (self.form.grid_slaves(row=r, column=0)[0], b, w, r)
                r += 1
        self.form.grid_columnconfigure(0, weight=1)
        self.apply_deps()

    def apply_deps(self):
        """Поля шестикритериальной оценки видны только при выборе этого критерия."""
        for key, (dep_key, dep_val) in CA.DEP.items():
            if key not in self.rows_w:
                continue
            lab, btn, wid, row = self.rows_w[key]
            cur = self._sel_code(dep_key)
            if cur == dep_val:
                lab.grid(row=row, column=0, sticky="w", padx=(2, 2), pady=1)
                btn.grid(row=row, column=1, sticky="w", padx=(0, 4), pady=1)
                wid.grid(row=row, column=2, sticky="e", pady=1)
            else:
                lab.grid_remove(); btn.grid_remove(); wid.grid_remove()

    def _sel_code(self, key):
        """Код выбранного значения списочного поля."""
        name = str(self.vars[key].get())
        for code, title in CA.SEL_OPTS[key]:
            if title == name:
                return code
        return CA.SEL_OPTS[key][0][0]

    # -------------------------------------------------------------- данные
    def read_state(self):
        bad, warn = [], []
        for key in CA.KEYS:
            kind = CA.KIND[key]
            var = self.vars[key]
            if kind == "bool":
                self.state_data[key] = bool(var.get())
                continue
            if kind == "sel":
                self.state_data[key] = self._sel_code(key)
                continue
            raw = str(var.get()).replace(",", ".").strip()
            k = 100.0 if CA.PCT.get(key) else 1.0
            try:
                if kind in ("vec", "vecfree"):
                    a = [float(x) for x in raw.split(";") if x.strip() != ""]
                    if kind == "vec" and len(a) != len(CA.defaults()[key]):
                        bad.append(CA.LABEL[key])
                        continue
                    if kind == "vecfree" and not a:
                        bad.append(CA.LABEL[key])
                        continue
                    if key in CA.SUM100 and abs(sum(a) - 100.0) > 0.01:
                        warn.append("%s дают в сумме %s %% вместо 100 %%"
                                    % (CA.SUM100[key], CA.f(sum(a), 2)))
                    self.state_data[key] = [x / k for x in a]
                else:
                    v = float(raw) / k
                    self.state_data[key] = int(round(v)) if kind == "int" else v
            except ValueError:
                bad.append(CA.LABEL[key])
        for key in ("q_evid", "q_load"):
            a = self.state_data.get(key) or []
            if a and not all(1 <= float(x) <= 5 for x in a):
                warn.append("%s задаются числами от 1 до 5" % CA.LABEL[key])
        return bad, warn

    def run(self):
        bad, warn = self.read_state()
        if bad:
            self.msg.configure(text="Проверьте поля: " + "; ".join(bad), foreground="#B03030")
            return
        if warn:
            self.msg.configure(text="Сумма долей не равна 100 %: " + "; ".join(warn)
                               + ". Расчет не выполнен.", foreground="#B03030")
            return
        try:
            self.R = CA.compute(self.state_data)
        except Exception as e:
            self.msg.configure(text="Ошибка расчета: %s" % e, foreground="#B03030")
            return
        self.mc = None
        self.msg.configure(text="Расчет выполнен", foreground="#1B9E77")
        self.draw()

    def reset(self):
        self.state_data = CA.defaults()
        self._fields()
        self.run()

    def save_set(self):
        self.read_state()
        p = filedialog.asksaveasfilename(defaultextension=".json", initialfile="Входные данные модели.json",
                                         filetypes=[("Набор данных", "*.json")])
        if p:
            CA.save_json(self.state_data, p)
            self.msg.configure(text="Набор сохранен", foreground="#1B9E77")

    def load_set(self):
        p = filedialog.askopenfilename(filetypes=[("Набор данных", "*.json")])
        if not p:
            return
        try:
            self.state_data = CA.load_json(p)
        except Exception as e:
            messagebox.showerror("Ошибка", "Файл не прочитан: %s" % e)
            return
        self._fields()
        self.run()

    # ------------------------------------------------------------- отчет
    def v_rep(self):
        """Вкладка отчета: выбор разделов, глубины детализации и печать в PDF."""
        fr = self.tabs["rep"]
        self.clear(fr)
        ttk.Label(fr, text="Отчет содержит таблицы и графики по результатам расчета. "
                           "Выберите разделы и глубину детализации, затем нажмите кнопку "
                           "«Печать отчета» и укажите, куда сохранить файл.",
                  wraplength=900, foreground=MUT, justify="left").pack(anchor="w", padx=10, pady=(10, 6))
        cols = ttk.Frame(fr)
        cols.pack(anchor="w", fill="x", padx=10)
        c1 = ttk.Frame(cols); c1.grid(row=0, column=0, sticky="nw", padx=(0, 40))
        c2 = ttk.Frame(cols); c2.grid(row=0, column=1, sticky="nw")
        ttk.Label(c1, text="Состав отчета", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        for k, name in RP.SECTIONS:
            if k not in self.rep_sec:
                self.rep_sec[k] = tk.BooleanVar(value=True)
            ttk.Checkbutton(c1, text=name, variable=self.rep_sec[k]).pack(anchor="w")
        bb = ttk.Frame(c1); bb.pack(anchor="w", pady=(6, 0))
        ttk.Button(bb, text="Отметить все",
                   command=lambda: [v.set(True) for v in self.rep_sec.values()]).grid(row=0, column=0, padx=(0, 4))
        ttk.Button(bb, text="Снять все",
                   command=lambda: [v.set(False) for v in self.rep_sec.values()]).grid(row=0, column=1)
        ttk.Label(c2, text="Глубина детализации", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        for k, name in RP.DEPTHS:
            ttk.Radiobutton(c2, text=name, value=k, variable=self.rep_depth).pack(anchor="w")
        ttk.Label(c2, text="Сценарий для графика денежного потока",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 4))
        picked = self.picked_scn()
        if picked:
            self.rep_scn.set(CA.SCL[picked])
        ttk.Combobox(c2, textvariable=self.rep_scn, state="readonly", width=26,
                     values=[CA.SCL[k] for k in CA.SC]).pack(anchor="w")
        ttk.Label(c2, text="По умолчанию подставлен сценарий, выбранный по действующему критерию.",
                  wraplength=420, foreground=MUT, justify="left").pack(anchor="w")
        ttk.Label(c2, text="Ориентация листа отчета",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 4))
        for k, name in (("port", "Книжная"), ("land", "Альбомная")):
            ttk.Radiobutton(c2, text=name, value=k, variable=self.rep_orient).pack(anchor="w")
        ttk.Label(c2, text="Ориентация задает размер страницы и ширину таблиц и графиков отчета.",
                  wraplength=420, foreground=MUT, justify="left").pack(anchor="w")
        ttk.Label(c2, text=("Прогоны выполнены, в отчет войдут результаты %d прогонов" % self.mc["N"])
                  if self.mc else "Прогоны не выполнялись. Раздел имитационного моделирования "
                                  "войдет в отчет после расчета на вкладке "
                                  "«Имитационное моделирование»",
                  wraplength=420, foreground=MUT, justify="left").pack(anchor="w", pady=(10, 0))
        ttk.Button(fr, text="Печать отчета", style="Run.TButton",
                   command=self.make_report).pack(anchor="w", padx=10, pady=14)

    def picked_scn(self):
        """Сценарий, выбранный по действующему критерию."""
        if not self.R:
            return None
        ok = [s for s in ["TRL7", "TRL6", "TRL5"]
              if min(i["npv"] for i in self.R["scn"][s]["out"]["items"]) - self.R["base"] > 0]
        if not ok:
            return "BASE" if self.R["base"] > 0 else None
        p = self.R["p"]
        if p.criterion == "crit":
            opts = CA.crit_options(self.R, ok)
            return max(opts, key=lambda d: (d["total"], -d["tv"]))["key"]
        if p.criterion == "reserve":
            return max(ok, key=lambda s: min(i["npv"] for i in self.R["scn"][s]["out"]["items"]))
        return max(ok, key=lambda s: self.R["scn"][s]["out"]["E_npv"])

    def make_report(self):
        keys = set(k for k, v in self.rep_sec.items() if v.get())
        if not keys:
            messagebox.showinfo("Отчет", "Выберите хотя бы один раздел")
            return
        sel = next((k for k in CA.SC if CA.SCL[k] == self.rep_scn.get()), "TRL5")
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf", initialfile="Отчет по расчету модели.pdf",
            filetypes=[("Документ PDF", "*.pdf")])
        if not path:
            return
        try:
            RP.build(self.R, self.mc, self.state_data,
                     dict(depth=self.rep_depth.get(), sections=keys, scn=sel,
                          orient=self.rep_orient.get()), path)
        except Exception as e:
            messagebox.showerror("Отчет", "Отчет не сформирован: %s" % e)
            return
        self.msg.configure(text="Отчет сохранен", foreground="#1B9E77")

    def to_csv(self):
        if not self.R:
            self.run()
        p = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="Расчет модели интеграции.csv",
                                         filetypes=[("Таблица", "*.csv")])
        if p:
            CA.save_csv(self.R, self.state_data, p)
            self.msg.configure(text="Выгрузка сохранена", foreground="#1B9E77")

    def to_xlsx(self):
        if not self.R:
            self.run()
        p = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile="Модель интеграции (формулы).xlsx",
                                         filetypes=[("Книга Excel", "*.xlsx")])
        if not p:
            return
        try:
            import xlsx_export
            xlsx_export.build(self.state_data, self.R, p)
        except Exception as e:
            messagebox.showerror("Ошибка", "Книга не создана: %s" % e)
            return
        self.msg.configure(text="Книга Excel сохранена", foreground="#1B9E77")

    # -------------------------------------------------------------- вывод
    @staticmethod
    def clear(fr):
        for w in fr.winfo_children():
            w.destroy()

    def draw(self):
        self.v_sum()
        self.v_cal()
        self.v_flow()
        self.v_sens()
        self.v_mc()
        self.v_ev()
        self.v_tax()
        self.v_pick()
        self.v_chk()
        self.v_rep()

    def v_sum(self):
        fr = self.tabs["sum"]
        self.clear(fr)
        h, rows = CA.t_summary(self.R)
        Table(fr, h, rows, widths=[160] + [118] * 7, height=4).pack(fill="x", padx=8, pady=(8, 4))
        pair = ttk.Frame(fr)
        pair.pack(fill="x", padx=8, pady=4)
        left = ttk.Frame(pair); left.pack(side="left", anchor="n")
        right = ttk.Frame(pair); right.pack(side="left", anchor="n", padx=(16, 0))
        ch = Chart(left, 380, 250)
        ch.bars([(CA.SCL[s], self.R["scn"][s]["ind"]["npv"], CA.COL[s]) for s in CA.SC], "ЧДД, млн руб.")
        ch.pack(anchor="w")
        ch2 = Chart(right, 570, 250)
        xs = [r["n"] for r in self.R["scn"]["BASE"]["rows"]]
        ch2.lines(xs, [(CA.SCL[s], CA.COL[s], [r["cumd"] for r in self.R["scn"][s]["rows"]]) for s in CA.SC],
                  str, "Накопленный дисконтированный поток, млн руб.", "год расчетного периода")
        ch2.pack(anchor="w")
        legend(right, [(CA.SCL[s], CA.COL[s]) for s in CA.SC]).pack(anchor="w")
        h2, r2 = CA.t_derived(self.R)
        Table(fr, h2, r2, widths=[320, 140], height=7).pack(fill="x", padx=8, pady=6)

    def _scn_bar(self, fr, var, cmd):
        bar = ttk.Frame(fr)
        bar.pack(fill="x", padx=8, pady=(8, 2))
        ttk.Label(bar, text="Сценарий").pack(side="left", padx=(0, 6))
        cb = ttk.Combobox(bar, state="readonly", width=20,
                          values=[CA.SCL[s] for s in CA.SC], textvariable=var)
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>", lambda e: cmd())
        return bar

    @staticmethod
    def _code(title):
        for s, t in CA.SCL.items():
            if t == title:
                return s
        return "BASE"

    def v_cal(self):
        fr = self.tabs["cal"]
        self.clear(fr)
        ttk.Label(fr, text="Срок реализации и доли этапов по сценариям",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=(10, 2))
        h, rows = CA.t_cal_summary(self.R)
        Table(fr, h, rows, widths=[150, 130, 120, 120, 160, 140, 150, 140, 120], height=4).pack(fill="x", padx=8)
        ttk.Label(fr, text="Срок реализации отсчитывается от начала разработки инновационного продукта "
                           "до ввода объекта в эксплуатацию. Совмещение — это часть срока, в которой "
                           "разработка и строительный процесс идут одновременно.",
                  wraplength=900, foreground=MUT, justify="left").pack(anchor="w", padx=8, pady=(2, 6))
        ttk.Label(fr, text="Календарный план сценариев", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=8, pady=(10, 2))
        maxT = max(CA.cal_info(self.R, s_)["tv"] for s_ in CA.SC) * 1.06
        for s_ in CA.SC:
            sch = self.R["scn"][s_]["sch"]
            hh = 44 + (3 if s_ in ("BASE", "TRL7") else 2) * 44 + 26
            cp = Chart(fr, 1270, hh)
            cp.calendar_panel(s_, sch, maxT)
            cp.pack(anchor="w", padx=8, pady=(0, 4))
        ttk.Label(fr, text="Верхняя полоса каждой панели — переходы между уровнями готовности технологии, "
                           "ромб отмечает подтверждение уровня. Средняя полоса — стадии строительства. "
                           "Нижняя полоса показывает опытную инфраструктуру там, где она создается. "
                           "Штриховая область отмечает продолжение подтверждения уровня на стадиях "
                           "строительства. Красная пунктирная линия — вход в проектирование, черная "
                           "штриховая — ввод объекта. Время в годах от начала разработки.",
                  wraplength=900, foreground=MUT, justify="left").pack(anchor="w", padx=8, pady=(0, 8))
        ttk.Label(fr, text="Светлая часть полосы — время до входа в инвестиционный процесс, насыщенная "
                           "часть — строительный процесс, вертикальный штрих — окончание разработки.",
                  wraplength=900, foreground=MUT, justify="left").pack(anchor="w", padx=8, pady=(0, 8))
        for s in CA.SC:
            d = CA.cal_info(self.R, s)
            (h1, r1), (h2, r2) = CA.t_calendar(self.R, s)
            ttk.Label(fr, text="%s.  Ввод в эксплуатацию: %s лет.  Совмещение: %s лет, или %s %% срока"
                      % (CA.SCL[s], CA.f(d["tv"], 2), CA.f(d["ov"], 2), CA.f(d["ov"] / d["tv"] * 100, 1)),
                      font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=8, pady=(8, 2))
            box = ttk.Frame(fr)
            box.pack(fill="x", padx=8)
            Table(box, h1, r1, widths=[120, 90, 110, 100, 90], height=8).pack(side="left", fill="x", expand=True)
            Table(box, h2, r2, widths=[250, 90, 100, 100, 90], height=8).pack(side="left", fill="x", expand=True, padx=(8, 0))

    def v_flow(self):
        fr = self.tabs["flow"]
        self.clear(fr)
        self._scn_bar(fr, self.flow_scn, self.v_flow)
        s = self._code(self.flow_scn.get()) if self.flow_scn.get() in CA.SCL.values() else self.flow_scn.get()
        if s not in CA.SC:
            s = "BASE"
        rr = self.R["scn"][s]["rows"]
        ch = Chart(fr, 900, 260)
        ch.flow_bars(rr)
        ch.pack(anchor="w", padx=8, pady=(6, 2))
        legend(fr, [("Инновационные затраты", "#8E44AD"),
                    ("Инвестиционные затраты", "#1B9E77"),
                    ("Операционный поток после налога", "#9fb8cf"),
                    ("Накопленный дисконтированный поток", "#003366")]).pack(anchor="w", padx=8)
        ttk.Label(fr, text="Столбцы вниз показывают затраты года, причем инновационные затраты "
                           "включают опытную инфраструктуру, затраты на доработки и затраты "
                           "на хранение и повторную верификацию оборудования. Столбцы вверх "
                           "показывают поступления от эксплуатации за вычетом налога.",
                  wraplength=900, foreground=MUT, justify="left").pack(anchor="w", padx=8, pady=(2, 6))
        h, rows = CA.t_flows(self.R, s)
        marks = [j for j, r in enumerate(rr) if r["rnd"] > 0]
        rtags = []
        for r in rr:
            if r["inn"] + r["pilot"] + r["rework"] + r["t7x"] > 0:
                rtags.append("tinn")
            elif r["inv"] > 0:
                rtags.append("tinv")
            else:
                rtags.append("")
        Table(fr, h, rows, widths=[60] + [104] * (len(h) - 1), height=20, marks=marks,
              extra_tags={"tinn": "#f0e4f7", "tinv": "#e2f4ec"},
              row_tags=rtags).pack(fill="both", expand=True, padx=8, pady=6)
        ttk.Label(fr, text="Сиреневым отмечены годы инновационных затрат, светло-зеленым годы "
                           "инвестиционных затрат, зеленым годы, в которых расходы на научные "
                           "исследования и опытно-конструкторские разработки признаются "
                           "в налоговой базе. Признание отнесено на год завершения этапа, "
                           "а сам расход распределен по годам отдельно в столбце "
                           "инновационной части.",
                  wraplength=900, foreground=MUT, justify="left").pack(anchor="w", padx=8, pady=(0, 8))

    def v_sens(self):
        fr = self.tabs["sens"]
        self.clear(fr)
        nb = ttk.Notebook(fr)
        nb.pack(fill="both", expand=True, padx=8, pady=8)
        spec = [("Ставка дисконтирования", CA.t_rates, "rates", "rate",
                 lambda x: CA.f(x * 100, 0), "ставка дисконтирования, %"),
                ("Опытная инфраструктура", CA.t_pilot, "pilot", "cost",
                 lambda x: CA.f(x, 0), "стоимость опытной инфраструктуры, млн руб."),
                ("Доля инновационной части", CA.t_shares, "shares", "share",
                 lambda x: CA.f(x * 100, 0), "доля инновационной части, %")]
        for name, tfun, key, xk, xfmt, xlab in spec:
            tab = ttk.Frame(nb)
            nb.add(tab, text=name)
            ch = Chart(tab, 820, 270)
            xs = [r[xk] for r in self.R[key]]
            ch.lines(xs, [(CA.SCL[s], CA.COL[s], [r[s] for r in self.R[key]]) for s in CA.SC],
                     xfmt, "ЧДД, млн руб.", xlab)
            ch.pack(anchor="w", padx=6, pady=6)
            legend(tab, [(CA.SCL[s], CA.COL[s]) for s in CA.SC]).pack(anchor="w", padx=6)
            h, rows = tfun(self.R)
            Table(tab, h, rows, widths=[150] + [118] * (len(h) - 1), height=10).pack(fill="x", padx=6, pady=6)

    def v_mc(self):
        fr = self.tabs["mc"]
        self.clear(fr)
        ttk.Label(fr, text="Имитационное моделирование методом Монте-Карло",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=(10, 2))
        for s in ("В каждом прогоне сроки разработки и строительства, вероятности и затраты доработок, "
                  "выручка и ставка дисконтирования отклоняются одновременно и случайно, а доработки "
                  "наступают случайно с заданными вероятностями. Все четыре сценария одного прогона "
                  "считаются на одном наборе отклонений, поэтому сценарии сравнимы между собой.",
                  "Приняты следующие отклонения. Сроки разработки и строительства, а также выручка "
                  "отклоняются на 15 %, вероятности событий на 50 %, затраты и задержки событий на 40 %, "
                  "ставка дисконтирования распределена равномерно от 10 до 16 %."):
            ttk.Label(fr, text=s, wraplength=900, foreground=MUT, justify="left").pack(anchor="w", padx=8)
        bar = ttk.Frame(fr)
        bar.pack(anchor="w", padx=8, pady=8)
        ttk.Label(bar, text="Число прогонов").grid(row=0, column=0, padx=(0, 6))
        ttk.Combobox(bar, textvariable=self.mc_n, values=("1000", "5000", "20000"),
                     width=8, state="readonly").grid(row=0, column=1, padx=(0, 14))
        ttk.Label(bar, text="Начальное значение генератора").grid(row=0, column=2, padx=(0, 6))
        self.mc_seed_e = ttk.Entry(bar, textvariable=self.mc_seed, width=12,
                                   state="readonly" if self.mc_rand.get() else "normal")
        self.mc_seed_e.grid(row=0, column=3, padx=(0, 10))
        ttk.Checkbutton(bar, text="случайное начальное значение", variable=self.mc_rand,
                        command=self._mc_rand_toggle).grid(row=0, column=4, padx=(0, 14))
        self.mc_btn = ttk.Button(bar, text="Повторить прогоны" if self.mc else "Выполнить прогоны",
                                 command=self.run_mc)
        self.mc_btn.grid(row=0, column=5)
        self.mc_msg = ttk.Label(bar, text="", foreground=MUT)
        self.mc_msg.grid(row=0, column=6, padx=(14, 0))
        if self.mc_busy:
            self.mc_btn.state(["disabled"])
            self.mc_msg.configure(text="Идет расчет, ожидайте")
        if not self.mc:
            ttk.Label(fr, text="Прогоны не выполнены. Расчет 5 000 прогонов занимает около пятнадцати секунд.",
                      foreground=MUT).pack(anchor="w", padx=8, pady=6)
            return
        mc = self.mc
        ttk.Label(fr, text="Расчет выполнен при начальном значении генератора %d. Чтобы повторить "
                           "его в точности, впишите это число в поле и снимите флажок случайного "
                           "значения." % mc["seed"],
                  wraplength=900, foreground=MUT, justify="left").pack(anchor="w", padx=8, pady=(6, 2))
        ttk.Label(fr, text="Распределение чистого дисконтированного дохода, прогонов %d" % mc["N"],
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=(6, 2))
        h, rows = CA.t_mc(mc)
        Table(fr, h, rows, widths=[150, 100, 110, 100, 110, 150, 140, 150], height=4).pack(fill="x", padx=8)
        hb = ttk.Frame(fr)
        hb.pack(anchor="w", padx=8, pady=(8, 2))
        ttk.Label(hb, text="Распределение чистого дисконтированного дохода по сценариям",
                  font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=(0, 14))
        ttk.Checkbutton(hb, text="сглаженная кривая вместо ступенчатой",
                        variable=self.mc_smooth,
                        command=self.v_mc).grid(row=0, column=1)
        hs = Chart(fr, 1020, 400)
        hs.hist(mc["series"], CA.SC, CA.COL, CA.SCL,
                {s: mc["scn"][s]["neg"] for s in CA.SC}, self.mc_smooth.get())
        hs.pack(anchor="w", padx=8, pady=(2, 2))
        ttk.Label(fr, text=("Показана сглаженная оценка плотности. Она выглядит аккуратнее, "
                            "но зависит от ширины сглаживания и может размыть пик, поэтому "
                            "для работы рекомендуется ступенчатый вид."
                            if self.mc_smooth.get() else
                            "Ступенчатая линия показывает число прогонов в каждом из сорока "
                            "шести интервалов дохода и не добавляет значений, которых в расчете "
                            "не было. Вертикальная линия отмечает нулевой доход, пунктир "
                            "и треугольник отмечают медиану сценария."),
                  wraplength=900, foreground=MUT, justify="left").pack(anchor="w", padx=8, pady=(0, 8))
        cl = Chart(fr, 1020, 380)
        cl.cloud(mc["series"], mc["rates"], CA.SC, CA.COL, CA.SCL)
        cl.pack(anchor="w", padx=8, pady=(6, 2))
        ttk.Label(fr, text="Каждая точка — один прогон, цвет означает сценарий. Жирные линии "
                           "показывают медиану сценария в двенадцати диапазонах ставки, медиана "
                           "по всем прогонам указана в легенде. Линия ломаная, поскольку каждая "
                           "ее точка это медиана фактических прогонов. Для скорости отрисовки "
                           "показана часть прогонов, медианы считаются по всем.",
                  wraplength=900, foreground=MUT, justify="left").pack(anchor="w", padx=8, pady=(0, 8))
        h2, r2 = CA.t_mc_adv(mc)
        ttk.Label(fr, text="Преимущество сценариев интеграции к базовому сценарию",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=(4, 2))
        Table(fr, h2, r2, widths=[150, 110, 120, 110, 160], height=3).pack(fill="x", padx=8)
        h3, r3 = CA.t_mc_d56(mc)
        Table(fr, h3, r3, widths=[380, 110], height=7).pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(fr, text="Доли оценены с 95-процентным доверительным интервалом, его полуширина при пяти тысячах прогонов не превышает 1,4 процентного пункта.",
                  wraplength=900, foreground=MUT, justify="left").pack(anchor="w", padx=8, pady=(0, 8))

    def _mc_rand_toggle(self):
        self.mc_seed_e.configure(state="readonly" if self.mc_rand.get() else "normal")

    def run_mc(self):
        if self.mc_busy or not self.R:
            return
        try:
            n = int(self.mc_n.get())
        except ValueError:
            n = 5000
        if self.mc_rand.get():
            seed = random.randrange(1, 2147483647)
            self.mc_seed.set(str(seed))
        else:
            try:
                seed = int(self.mc_seed.get())
            except ValueError:
                seed = 20261107
        self.mc_busy = True
        self.mc_btn.state(["disabled"])
        self.mc_msg.configure(text="Идет расчет, ожидайте")
        p = self.R["p"]

        def work():
            try:
                res = CA.M.monte_carlo(p, n, seed, progress=lambda i, k: self.after(
                    0, lambda: self.mc_msg.configure(text="Выполнено %d из %d" % (i, k))))
            except Exception as e:
                self.after(0, lambda: self._mc_done(None, str(e)))
                return
            self.after(0, lambda: self._mc_done(res, None))

        threading.Thread(target=work, daemon=True).start()

    def _mc_done(self, res, err):
        self.mc_busy = False
        if err:
            self.mc = None
            self.v_mc()
            self.mc_msg.configure(text="Ошибка расчета: " + err, foreground="#B03030")
            return
        self.mc = res
        self.v_mc()

    def v_ev(self):
        fr = self.tabs["ev"]
        self.clear(fr)
        nb = ttk.Notebook(fr)
        nb.pack(fill="both", expand=True, padx=8, pady=8)
        prof = CA.risk_profile(self.R)
        tab0 = ttk.Frame(nb)
        nb.add(tab0, text="Анализ риска")
        c1 = Chart(tab0, width=820, height=270)
        c1.pack(fill="x", padx=6, pady=6)
        c1.risk_adv(prof)
        ttk.Label(tab0, text="Высота столбца равна преимуществу сценария над базовым без событий "
                             "доработки. Оранжевая часть показывает ожидаемые потери, то есть сумму "
                             "произведений вероятности каждого исхода на потерю дохода в нем. Число "
                             "внутри столбца равно преимуществу с учетом ожидаемых потерь.",
                  wraplength=900, foreground=MUT).pack(anchor="w", padx=8)
        c2 = Chart(tab0, width=820, height=250)
        c2.pack(fill="x", padx=6, pady=6)
        c2.risk_contrib(prof)
        ttk.Label(tab0, text="Вклад события равен произведению его вероятности на потерю дохода "
                             "при одиночном наступлении этого события. Сумма вкладов совпадает "
                             "с ожидаемой потерей по полному перебору с точностью до исходов, "
                             "где события наступают совместно.",
                  wraplength=900, foreground=MUT).pack(anchor="w", padx=8, pady=(0, 6))
        for s in ("TRL5", "TRL6", "TRL7"):
            tab = ttk.Frame(nb)
            nb.add(tab, text=CA.SCL[s])
            (h1, r1), (h2, r2), note = CA.t_events(self.R, s)
            Table(tab, h1, r1, widths=[200, 300, 110, 140, 110], height=5).pack(fill="x", padx=6, pady=6)
            Table(tab, h2, r2, widths=[220, 110, 130, 120, 130, 140], height=17).pack(fill="both", expand=True, padx=6)
            ttk.Label(tab, text=note, wraplength=900).pack(anchor="w", padx=6, pady=6)

    def v_tax(self):
        fr = self.tabs["tax"]
        self.clear(fr)
        h1, r1, n1, h2, r2, n2, txt, data = CA.t_tax(self.R)
        ttk.Label(fr, text="Разложение чистого дисконтированного дохода по сценариям",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=(8, 2))
        Table(fr, h1, r1, widths=[150, 190, 150, 190, 110, 110], height=4).pack(
            fill="x", padx=8)
        ttk.Label(fr, text=n1, wraplength=900, foreground=MUT).pack(anchor="w", padx=8, pady=(2, 8))
        ttk.Label(fr, text="Сравнение двух порядков налогового признания инновационных затрат",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=(4, 2))
        Table(fr, h2, r2, widths=[150] + [108] * (len(h2) - 1), height=4).pack(fill="x", padx=8)
        ttk.Label(fr, text=n2, wraplength=900, foreground=MUT).pack(anchor="w", padx=8, pady=(2, 8))
        c1 = Chart(fr, width=820, height=250)
        c1.pack(fill="x", padx=6, pady=6)
        c1.tax_bars(data)
        bar = ttk.Frame(fr)
        bar.pack(fill="x", padx=8)
        ttk.Label(bar, text="Сценарий для графика по годам: ").pack(side="left")
        var = tk.StringVar(value="TRL5")
        c2 = Chart(fr, width=820, height=240)

        def redraw(*_):
            c2.delete("all")
            c2.tax_years(data, var.get())
        cb = ttk.Combobox(bar, state="readonly", width=24,
                          values=[CA.SCL[k] for k in CA.SC])
        cb.set(CA.SCL["TRL5"])
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>",
                lambda e: (var.set([k for k in CA.SC if CA.SCL[k] == cb.get()][0]), redraw()))
        c2.pack(fill="x", padx=6, pady=6)
        redraw()
        box = tk.Frame(fr, bg="#f1f6fb", highlightthickness=1, highlightbackground=ACC)
        box.pack(fill="x", padx=8, pady=6)
        tk.Label(box, text=txt, bg="#f1f6fb", fg=INK, wraplength=900, justify="left",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=8)

    def v_pick(self):
        fr = self.tabs["pick"]
        self.clear(fr)
        h, rows, txt = CA.t_pick(self.R)
        Table(fr, h, rows, widths=[150] + [118] * (len(h) - 1), height=4).pack(fill="x", padx=8, pady=8)
        box = tk.Frame(fr, bg="#f1f6fb", highlightthickness=1, highlightbackground=ACC)
        box.pack(fill="x", padx=8)
        tk.Label(box, text=txt, bg="#f1f6fb", fg=INK, wraplength=900, justify="left",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=8)
        ttk.Label(fr, text="Правило выбора. Сценарий проходит допуск, если преимущество к базовому "
                           "сохраняется в наихудшем исходе событий доработки. Из допущенных "
                           "выбирается сценарий по действующему критерию, который задается "
                           "списком в разделе «Критерий выбора».", wraplength=900,
                  foreground=MUT).pack(anchor="w", padx=8, pady=8)
        if self.R["p"].criterion == "crit":
            ok = [s for s in ["TRL7", "TRL6", "TRL5"]
                  if min(i["npv"] for i in self.R["scn"][s]["out"]["items"]) - self.R["base"] > 0]
            if ok:
                h1, r1, h2, r2 = CA.t_crit(self.R, ok)
                ttk.Label(fr, text="Шестикритериальная оценка", font=("Segoe UI", 11, "bold")).pack(
                    anchor="w", padx=8, pady=(10, 2))
                Table(fr, h1, r1, widths=[150] + [110] * (len(h1) - 1), height=4).pack(fill="x", padx=8)
                ttk.Label(fr, text="Исходные величины оценки. Остаток базового варианта принят равным "
                                   "нулю, запас устойчивости базового варианта принят наибольшим среди "
                                   "вариантов, поскольку доработок в нем нет.", wraplength=900,
                          foreground=MUT).pack(anchor="w", padx=8, pady=(2, 6))
                Table(fr, h2, r2, widths=[150] + [100] * (len(h2) - 1), height=4).pack(fill="x", padx=8)
                ttk.Label(fr, text="Количественные критерии нормированы линейно по наилучшему и "
                                   "наихудшему значению среди вариантов, для срока ввода нормировка "
                                   "обращена. Экспертные оценки переведены в баллы по формуле, в которой "
                                   "из оценки вычитается единица и результат делится на четыре. "
                                   "Оценка S является взвешенной суммой баллов.", wraplength=900,
                          foreground=MUT).pack(anchor="w", padx=8, pady=(2, 8))

    def v_chk(self):
        fr = self.tabs["chk"]
        self.clear(fr)
        h1, r1, ok1 = CA.t_inputs(self.R)
        ttk.Label(fr, text="Проверка введенных данных", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=8, pady=(10, 2))
        ttk.Label(fr, text="Все условия выполнены на введенных данных" if ok1
                  else "Часть условий нарушена, проверьте отмеченные строки",
                  foreground="#1B9E77" if ok1 else "#B03030").pack(anchor="w", padx=8, pady=(0, 4))
        Table(fr, h1, r1, widths=[430, 230, 110], height=10).pack(fill="x", padx=8)

        h2, r2, ok2 = CA.t_identities(self.R)
        ttk.Label(fr, text="Проверка расчета на введенных данных",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=(12, 2))
        Table(fr, h2, r2, widths=[430, 230, 110], height=10).pack(fill="x", padx=8)


def main():
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])) or ".")
    App().mainloop()


if __name__ == "__main__":
    main()

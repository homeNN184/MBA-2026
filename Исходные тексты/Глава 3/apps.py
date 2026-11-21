# -*- coding: utf-8 -*-
import openpyxl, re
from docx.enum.section import WD_SECTION
from docx_util import *
WB = openpyxl.load_workbook("/home/claude/work/model/final_calc.xlsx", data_only=True)
NB = " "
def fmt(v, d=2):
    if v is None: return ""
    if isinstance(v, bool): return "да" if v else "нет"
    if isinstance(v, int): return str(v)
    if isinstance(v, float):
        if abs(v - round(v)) < 1e-9 and d == 0: return str(int(round(v)))
        s = f"{v:.{d}f}".replace(".", ",")
        return s.replace("-", "−")
    return str(v).replace(".", ",") if re.fullmatch(r"-?\d+\.\d+", str(v)) else str(v)
def para(doc, text, size=14, align=AL.JUSTIFY, first=1.25, bold=False, line=1.5, keep=False, before=0, after=0, italic=False):
    p = doc.add_paragraph(); r = p.add_run(text); set_font(r, size, bold=bold, italic=italic)
    pf(p, align=align, first=Cm(first), line=line, before=before, after=after, keep=keep)
    return p
def app_head(doc, num, title, newpage=True):
    p = para(doc, f"Приложение {num}", 14, AL.RIGHT, 0, bold=True, line=1.0, keep=True, after=6)
    if newpage: p.paragraph_format.page_break_before = True
    para(doc, title, 14, AL.CENTER, 0, bold=True, line=1.0, keep=True, after=10)
def tab_cap(doc, num, title, cont=False):
    para(doc, ("Продолжение таблицы " if cont else "Таблица ") + num, 12, AL.RIGHT, 0, line=1.0, keep=True, before=4)
    if not cont: para(doc, title, 12, AL.CENTER, 0, line=1.0, keep=True, after=3)
def grid(doc, head, rows, widths, size=8, aligns=None, bold_last=False, zero_pad=True, shade_cols=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(head)); t.autofit = False
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    tot = sum(widths); widths = [w * min(1.0, W_AVAIL[0] / tot) for w in widths]
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); t._tbl.tblPr.append(lay)
    for gc, w in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), widths): gc.set(qn("w:w"), str(int(w * 567)))
    aligns = aligns or (["l"] + ["r"] * (len(head) - 1))
    for ri, row in enumerate([head] + rows):
        for ci, v in enumerate(row):
            c = t.rows[ri].cells[ci]; c.width = Cm(widths[ci])
            p = c.paragraphs[0]; p.text = ""; r = p.add_run(str(v))
            hdr = ri == 0
            set_font(r, size, bold=True if (hdr or (bold_last and ri == len(rows))) else None)
            a = AL.CENTER if hdr else (AL.RIGHT if aligns[ci] == "r" else (AL.CENTER if aligns[ci] == "c" else AL.LEFT))
            pf(p, align=a, first=Cm(0), left=Cm(0), line=1.0)
    style_table_light(t, size)
    return t
def style_table_light(t, size):
    borders(t, 4); cell_margins(t, top=0 if size <= 8 else 20, bottom=0 if size <= 8 else 20, left=45, right=45)
    for ri, row in enumerate(t.rows):
        cant_split(row)
        if ri == 0: repeat_header(row)
        for c in row.cells:
            c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if ri == 0: shade(c)
def expl(doc, num, items, size=10):
    para(doc, f"Пояснения к столбцам таблицы {num}:", size + 1, AL.LEFT, 0, bold=True, line=1.0, before=6, after=2, keep=True)
    for k, (name, txt) in enumerate(items, 1):
        p = doc.add_paragraph(); pf(p, align=AL.JUSTIFY, first=Cm(0), left=Cm(0.6), line=1.0, after=1)
        p.paragraph_format.first_line_indent = Cm(-0.6)
        r = p.add_run(f"{k}. "); set_font(r, size)
        r = p.add_run(name); set_font(r, size, bold=True)
        r = p.add_run(" — " + txt); set_font(r, size)
def note(doc, text, size=10):
    para(doc, text, size, AL.JUSTIFY, 0, line=1.0, before=3, after=3)
W_AVAIL = [16.5]
def set_width(w): W_AVAIL[0] = w
def orient(doc, landscape):
    s = doc.add_section(WD_SECTION.NEW_PAGE); set_margins(s, landscape); set_width(25.2 if landscape else 16.5)
    s.footer.is_linked_to_previous = True
# ---------- разбор листов
def rows_of(ws, r1, r2, c2):
    return [[ws.cell(r, c).value for c in range(1, c2 + 1)] for r in range(r1, r2 + 1)]
def generic(ws, r1, r2, c2):
    R = rows_of(ws, r1, r2, c2); out = []; cur = None; mode = None
    def nxt(i):
        for j in range(i + 1, len(R)):
            k = sum(v is not None for v in R[j])
            if k: return k
        return 0
    for i, v in enumerate(R):
        nn = sum(x is not None for x in v)
        if nn == 0:
            if mode != "head": cur = None; mode = None
            continue
        if nn == 1 and v[0] is not None and nxt(i) >= 3 and (cur is None):
            cur = {"title": v[0], "head": None, "rows": []}; out.append(cur); mode = "head"; continue
        if nn == 1 and cur is None: out.append({"note": v[0]}); continue
        if cur is None:
            cur = {"title": None, "head": v, "rows": []}; out.append(cur); mode = "data"; continue
        if mode == "head": cur["head"] = v; mode = "data"; continue
        cur["rows"].append(v)
    return out
def trim(tab):
    cols = max(i for r in [tab["head"]] + tab["rows"] for i, x in enumerate(r) if x not in (None, "")) + 1
    return [str(h) for h in tab["head"][:cols]], [r[:cols] for r in tab["rows"]]
def wid(head, rows, mn=1.6, mx=9.0, k=0.20):
    w = []
    for j, h in enumerate(head):
        L = max([len(fmt(r[j])) for r in rows] + [len(h) * 0.55])
        w.append(max(mn, min(mx, 0.9 + L * k)))
    return w

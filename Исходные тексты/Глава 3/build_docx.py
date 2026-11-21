# -*- coding: utf-8 -*-
import subprocess, sys, re
sys.path.insert(0, ".")
from docx_util import *
subprocess.run(["pandoc", "ch3.md", "-f", "markdown+tex_math_dollars+footnotes+pipe_tables+fenced_divs", "-o", "raw.docx"], check=True)
PDF = "--pdf" in sys.argv
NOAPP = "--noapp" in sys.argv
sys.argv = [a for a in sys.argv if a not in ("--pdf", "--noapp")]
doc = Document("raw.docx")
sec = doc.sections[0]; set_margins(sec)
st = doc.styles
def S(name):
    try: return st[name]
    except KeyError: return None
for nm in ("Normal", "Body Text", "First Paragraph", "Compact", "Heading 1", "Heading 2", "Heading 3", "Heading 4", "Footnote Text", "TabNum", "TabTitle", "FigImg", "FigCap", "Table"):
    s = S(nm)
    if s is None: continue
    set_font(s, 14)
for nm in ("Normal", "Body Text", "First Paragraph", "Compact"):
    s = S(nm)
    if s is not None:
        s.paragraph_format.alignment = AL.JUSTIFY; s.paragraph_format.first_line_indent = Cm(1.25)
        s.paragraph_format.line_spacing = 1.5; s.paragraph_format.space_before = Pt(0); s.paragraph_format.space_after = Pt(0)
set_font(S("Footnote Text"), 10)
ft = S("Footnote Text"); ft.paragraph_format.line_spacing = 1.0; ft.paragraph_format.first_line_indent = Cm(0); ft.paragraph_format.alignment = AL.JUSTIFY
body = doc.element.body
first_h1 = True
for p in doc.paragraphs:
    sn = p.style.name
    txt = p.text.strip()
    if sn == "Heading 1":
        pf(p, align=AL.JUSTIFY, first=Cm(0), line=1.5, before=0, after=6, keep=True, pb=not first_h1 and True or False); first_h1 = False
        for r in p.runs: set_font(r, 14, bold=True)
    elif sn in ("Heading 2", "Heading 3"):
        pf(p, align=AL.JUSTIFY, first=Cm(0), line=1.5, before=6 if sn == "Heading 2" else 0, after=0, keep=True)
        for r in p.runs: set_font(r, 14, bold=True)
    elif sn == "TabNum":
        pf(p, align=AL.RIGHT, first=Cm(0), line=1.0, before=6, after=0, keep=True)
        for r in p.runs: set_font(r, 12)
    elif sn == "TabTitle":
        pf(p, align=AL.CENTER, first=Cm(0), line=1.0, before=0, after=4, keep=True)
        for r in p.runs: set_font(r, 12, bold=False)
    elif sn == "FigImg":
        pf(p, align=AL.CENTER, first=Cm(0), line=1.0, before=6, after=2, keep=True)
    elif sn == "FigCap":
        pf(p, align=AL.CENTER, first=Cm(0), line=1.0, before=0, after=8)
        for r in p.runs: set_font(r, 12)
    elif sn in ("Body Text", "First Paragraph", "Compact", "Normal"):
        if txt.startswith("где "): pf(p, first=Cm(0), line=1.5)
        for r in p.runs: set_font(r, 14)
# таблицы данных
for t in doc.tables:
    ncol = len(t.columns)
    style_table(t, size=11 if ncol <= 5 else 10)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    fit_width(t, 16.5)
for t in doc.tables:
    nx = t._tbl.getnext()
    if nx is not None and nx.tag == qn("w:p"):
        from docx.text.paragraph import Paragraph
        q = Paragraph(nx, doc.element.body); q.paragraph_format.space_before = Pt(8)
# формулы: таблица 2 столбца (формула / номер)
eq = 0
for p in list(doc.paragraphs):
    if not p._p.findall(".//" + qn("m:oMathPara")): continue
    eq += 1
    tbl = doc.add_table(rows=1, cols=2)
    tbl.autofit = False
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c0, c1 = tbl.rows[0].cells
    c0.width = Cm(14.0); c1.width = Cm(2.5)
    tbl.columns[0].width = Cm(14.0); tbl.columns[1].width = Cm(2.5)
    tp = tbl._tbl.tblPr
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tp.append(lay)
    for gc, w in zip(tbl._tbl.tblGrid.findall(qn("w:gridCol")), (14.0, 2.5)): gc.set(qn("w:w"), str(int(w * 567)))
    for c in (c0, c1): c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p._p.addprevious(tbl._tbl)
    old = c0.paragraphs[0]._p
    old.addprevious(p._p); c0._tc.remove(old)
    LN = 2.0 if eq in (7, 8, 9) else 1.0
    pf(p, align=AL.CENTER, first=Cm(0), line=LN, before=3, after=3)
    q = c1.paragraphs[0]; q.text = f"({eq})"
    pf(q, align=AL.RIGHT, first=Cm(0), line=LN)
    for r in q.runs: set_font(r, 14)
    cant_split(tbl.rows[0])
    if PDF:
        from PIL import Image
        om = p._p.find(qn("m:oMathPara")); p._p.remove(om)
        im = Image.open(f"eq/e{eq}.png"); w_cm = min(13.8, im.width / 300 * 2.54)
        p.add_run().add_picture(f"eq/e{eq}.png", width=Cm(w_cm))
print("equations", eq)
if PDF:
    def allparas():
        for pp in doc.paragraphs: yield pp
        for t in doc.tables:
            for row in t.rows:
                for c in row.cells:
                    for pp in c.paragraphs: yield pp
    for pp in allparas(): inline_math_to_runs(pp)
from apps2 import add_appendices
if not NOAPP: add_appendices(doc)
add_page_number(doc.sections[0])
import os
out = sys.argv[1] if len(sys.argv) > 1 else "main.docx"
doc.save(out)

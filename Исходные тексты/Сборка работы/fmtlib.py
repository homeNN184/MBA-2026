# -*- coding: utf-8 -*-
"""Общие процедуры оформления: ё→е, заголовки, таблицы, нумерация страниц, перенумерация таблиц/рисунков."""
import re, sys, copy
sys.path.insert(0, "/home/claude/work/ch3")
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
from lxml import etree
WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MNS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W = "{%s}" % WNS; M = "{%s}" % MNS
FONT = "Times New Roman"

# ---------- ё -> е ----------
def yo_root(root):
    k = 0
    for el in root.iter(W + "t", M + "t"):
        if el.text and ("ё" in el.text or "Ё" in el.text):
            el.text = el.text.replace("ё", "е").replace("Ё", "Е"); k += 1
    return k
def yo_doc(doc):
    k = yo_root(doc.element)
    for rel in doc.part.rels.values():
        if rel.reltype.endswith(("/footer", "/header", "/footnotes", "/endnotes")):
            try:
                root = etree.fromstring(rel.target_part.blob)
                if yo_root(root):
                    rel.target_part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            except Exception: pass
    return k

# ---------- шрифты ----------
def fix_run(r, size=None, bold=None, italic=None):
    rpr = r.find(qn("w:rPr"))
    if rpr is None:
        rpr = OxmlElement("w:rPr"); r.insert(0, rpr)
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): rf.set(qn(a), FONT)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
    def setv(tag, val):
        for t in rpr.findall(qn(tag)): rpr.remove(t)
        if val is None: return
        e = OxmlElement(tag); e.set(qn("w:val"), val); rpr.append(e)
    if size is not None:
        setv("w:sz", str(int(round(size * 2)))); setv("w:szCs", str(int(round(size * 2))))
    if bold is not None:
        for tag in ("w:b", "w:bCs"):
            for t in rpr.findall(qn(tag)): rpr.remove(t)
            if bold: rpr.append(OxmlElement(tag))
            else:
                e = OxmlElement(tag); e.set(qn("w:val"), "0"); rpr.append(e)
    if italic is not None:
        for t in rpr.findall(qn("w:i")): rpr.remove(t)
        if italic: rpr.append(OxmlElement("w:i"))
    # порядок элементов rPr для строгих парсеров: rFonts первым
    # (остальное допускается произвольным для Word/LibreOffice)

def para_fmt(p, align=None, first=None, left=None, line=None, before=None, after=None, keep=None, pb=None):
    q = p.paragraph_format
    if align is not None: q.alignment = align
    if first is not None: q.first_line_indent = first
    if left is not None: q.left_indent = left
    if line is not None: q.line_spacing = line
    if before is not None: q.space_before = Pt(before)
    if after is not None: q.space_after = Pt(after)
    if keep is not None: q.keep_with_next = keep
    if pb is not None: q.page_break_before = pb

# ---------- заголовки ----------
def style_headings(doc, first_pb=True):
    first = True
    for p in doc.paragraphs:
        sn = p.style.name
        if sn == "Heading 1":
            ctr = p.text.strip().startswith(("Введение", "Список литературы", "Выводы", "Приложение"))
            para_fmt(p, AL.CENTER if ctr else AL.JUSTIFY, Cm(0), Cm(0), 1.5, 0, 12, True, first_pb if first else True); first = False
            for r in p._p.iter(W + "r"): fix_run(r, 14, True, False)
        elif sn in ("Heading 2", "Heading 3", "Heading 4"):
            para_fmt(p, AL.JUSTIFY, Cm(0), Cm(0), 1.5, 6 if sn == "Heading 2" else 0, 0, True, False)
            for r in p._p.iter(W + "r"): fix_run(r, 14, True, False)

# ---------- таблицы ----------
def _run_size(r, pstyle_size):
    sz = r.find(qn("w:rPr") + "/" + qn("w:sz")) if False else None
    rpr = r.find(qn("w:rPr"))
    if rpr is not None:
        e = rpr.find(qn("w:sz"))
        if e is not None: return int(e.get(qn("w:val"))) / 2
    return pstyle_size
def _tc_width_map(tbl):
    grid = tbl._tbl.find(qn("w:tblGrid")).findall(qn("w:gridCol"))
    return grid
def fit_table(tbl, cm):
    tw = int(round(cm / 2.54 * 1440))
    el = tbl._tbl
    grid = el.find(qn("w:tblGrid")); cols = grid.findall(qn("w:gridCol"))
    ws = [int(c.get(qn("w:w")) or 0) for c in cols]
    if not ws or sum(ws) == 0: ws = [1] * len(cols)
    tot = sum(ws); new = [max(300, int(w / tot * tw)) for w in ws]
    new[-1] += tw - sum(new)
    for c, w in zip(cols, new): c.set(qn("w:w"), str(w))
    pr = el.tblPr
    for tag in ("w:tblW", "w:tblLayout", "w:tblInd"):
        for e in pr.findall(qn(tag)): pr.remove(e)
    w = OxmlElement("w:tblW"); w.set(qn("w:w"), str(tw)); w.set(qn("w:type"), "dxa"); pr.append(w)
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); pr.append(lay)
    for tr in el.findall(qn("w:tr")):
        gi = 0
        for tc in tr.findall(qn("w:tc")):
            tcpr = tc.find(qn("w:tcPr"))
            if tcpr is None:
                tcpr = OxmlElement("w:tcPr"); tc.insert(0, tcpr)
            span = tcpr.find(qn("w:gridSpan")); n = int(span.get(qn("w:val"))) if span is not None else 1
            wsum = sum(new[gi:gi + n]); gi += n
            for e in tcpr.findall(qn("w:tcW")): tcpr.remove(e)
            e = OxmlElement("w:tcW"); e.set(qn("w:w"), str(wsum)); e.set(qn("w:type"), "dxa"); tcpr.insert(0, e)
    # выравнивание по центру страницы
    for e in pr.findall(qn("w:jc")): pr.remove(e)
    jc = OxmlElement("w:jc"); jc.set(qn("w:val"), "center"); pr.append(jc)

def table_header_rows(tbl):
    rows = tbl._tbl.findall(qn("w:tr"))
    hdr = [tr for tr in rows if tr.find(qn("w:trPr")) is not None and tr.find(qn("w:trPr")).find(qn("w:tblHeader")) is not None]
    return hdr or rows[:1]

def fix_table(tbl, width_cm=16.5, default_body=12.0, many_cols=5):
    """Шапка: без заливки, не жирная, размер = размер тела + 2 пт (если столбцов много — как в теле). Ширина = ширине страницы."""
    el = tbl._tbl
    rows = el.findall(qn("w:tr"))
    hdr = table_header_rows(tbl)
    hdr_ids = {id(h) for h in hdr}
    sizes = {}
    for tr in rows:
        if id(tr) in hdr_ids: continue
        for r in tr.iter(qn("w:r")):
            if not "".join(t.text or "" for t in r.iter(qn("w:t"))).strip(): continue
            s = _run_size(r, default_body); sizes[s] = sizes.get(s, 0) + 1
    body = max(sizes, key=sizes.get) if sizes else default_body
    ncol = len(el.find(qn("w:tblGrid")).findall(qn("w:gridCol")))
    delta = 2 if ncol <= many_cols else 0
    for tr in hdr:
        for tc in tr.findall(qn("w:tc")):
            tcpr = tc.find(qn("w:tcPr"))
            if tcpr is not None:
                for s in tcpr.findall(qn("w:shd")): tcpr.remove(s)
            for r in tc.iter(qn("w:r")):
                if not "".join(t.text or "" for t in r.iter(qn("w:t"))).strip(): continue
                fix_run(r, body + delta, False)
    # строки-подзаголовки (заливка) — без заливки
    for tr in rows:
        for tc in tr.findall(qn("w:tc")):
            tcpr = tc.find(qn("w:tcPr"))
            if tcpr is not None:
                for s in tcpr.findall(qn("w:shd")):
                    if s.get(qn("w:fill")) not in (None, "auto", "FFFFFF"): tcpr.remove(s)
    fit_table(tbl, width_cm)
    return body, delta

# ---------- нумерация страниц ----------
def page_footer(section, size=12):
    from docx_util import add_page_number
    add_page_number(section, size)
def set_page_start(doc, start):
    sp = doc.sections[0]._sectPr
    for e in sp.findall(qn("w:pgNumType")): sp.remove(e)
    e = OxmlElement("w:pgNumType"); e.set(qn("w:start"), str(start))
    after = [c for c in sp if c.tag in (qn("w:pgSz"), qn("w:pgMar"), qn("w:paperSrc"), qn("w:pgBorders"), qn("w:lnNumType"))]
    after[-1].addnext(e)

# ---------- перенумерация таблиц/рисунков ----------
REF = re.compile(r"((?:[Тт]аблиц|[Рр]исун)[а-я]*\s+)(\d+\.\d+(?:\s*(?:,|и|–|-|—)\s*\d+\.\d+)*)")
def renumber_text(s, tmap, fmap):
    def sub(m):
        word = m.group(1); isT = word.lower().startswith("табл"); mp = tmap if isT else fmap
        return word + re.sub(r"\d+\.\d+", lambda x: str(mp.get(x.group(0), x.group(0))), m.group(2))
    return REF.sub(sub, s)
def renumber_doc(doc, tmap, fmap):
    """Меняет номера в тексте по результатам, сверяя целостность на уровне абзаца."""
    bad = []
    for p in doc.element.body.iter(W + "p"):
        runs = [r for r in p.iter(W + "r")]
        ts = [t for r in runs for t in r.findall(W + "t")]
        full = "".join(t.text or "" for t in ts)
        newfull = renumber_text(full, tmap, fmap)
        if newfull == full: continue
        # попытка по-ранно
        ok = True
        for t in ts:
            if t.text:
                nt = renumber_text(t.text, tmap, fmap)
                t.text = nt
        chk = "".join(t.text or "" for t in ts)
        if chk != newfull: bad.append((full[:80], chk[:80]))
    return bad

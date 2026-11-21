# -*- coding: utf-8 -*-
import copy, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement
FONT = "Times New Roman"
def set_font(style_or_run, size=None, bold=None, italic=None):
    f = style_or_run.font
    f.name = FONT
    rpr = (style_or_run.element if hasattr(style_or_run, "element") else style_or_run._r).get_or_add_rPr() if False else None
    el = style_or_run.element if hasattr(style_or_run, "element") else style_or_run._r
    rPr = el.get_or_add_rPr()
    rf = rPr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rPr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): rf.set(qn(a), FONT)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
    if size: f.size = Pt(size)
    if bold is not None: f.bold = bold
    if italic is not None: f.italic = italic
    f.color.rgb = RGBColor(0, 0, 0)
def pf(p, align=None, first=None, line=None, before=0, after=0, keep=None, left=None, pb=None):
    q = p.paragraph_format
    if align is not None: q.alignment = align
    if first is not None: q.first_line_indent = first
    if left is not None: q.left_indent = left
    if line is not None: q.line_spacing = line
    q.space_before = Pt(before); q.space_after = Pt(after)
    if keep is not None: q.keep_with_next = keep
    if pb is not None: q.page_break_before = pb
def borders(tbl, sz=4):
    tblPr = tbl._tbl.tblPr
    b = tblPr.find(qn("w:tblBorders"))
    if b is not None: tblPr.remove(b)
    xml = "<w:tblBorders %s>" % nsdecls("w") + "".join('<w:%s w:val="single" w:sz="%d" w:space="0" w:color="000000"/>' % (e, sz) for e in ("top","left","bottom","right","insideH","insideV")) + "</w:tblBorders>"
    tblPr.append(parse_xml(xml))
def shade(cell, fill="E7E6E1"):
    tcPr = cell._tc.get_or_add_tcPr()
    for s in tcPr.findall(qn("w:shd")): tcPr.remove(s)
    tcPr.append(parse_xml('<w:shd %s w:val="clear" w:color="auto" w:fill="%s"/>' % (nsdecls("w"), fill)))
def cell_margins(tbl, top=30, bottom=30, left=70, right=70):
    tblPr = tbl._tbl.tblPr
    for s in tblPr.findall(qn("w:tblCellMar")): tblPr.remove(s)
    tblPr.append(parse_xml('<w:tblCellMar %s><w:top w:w="%d" w:type="dxa"/><w:left w:w="%d" w:type="dxa"/><w:bottom w:w="%d" w:type="dxa"/><w:right w:w="%d" w:type="dxa"/></w:tblCellMar>' % (nsdecls("w"), top, left, bottom, right)))
def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    if trPr.find(qn("w:tblHeader")) is None: trPr.append(OxmlElement("w:tblHeader"))
def cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    if trPr.find(qn("w:cantSplit")) is None: trPr.append(OxmlElement("w:cantSplit"))
def style_table(tbl, size=11, header_rows=1, align_first_left=True):
    borders(tbl); cell_margins(tbl)
    for ri, row in enumerate(tbl.rows):
        cant_split(row)
        if ri < header_rows: repeat_header(row)
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER if ri < header_rows else WD_ALIGN_VERTICAL.TOP
            if ri < header_rows: shade(cell)
            for p in cell.paragraphs:
                al = p.paragraph_format.alignment
                pf(p, align=(AL.CENTER if ri < header_rows else (al if al in (AL.RIGHT, AL.CENTER) else AL.LEFT)), first=Cm(0), left=Cm(0), line=1.0)
                for r in p.runs: set_font(r, size, bold=True if ri < header_rows else None)
def add_page_number(section, size=12):
    f = section.footer; f.is_linked_to_previous = False
    p = f.paragraphs[0] if f.paragraphs else f.add_paragraph()
    for ch in list(p._p):
        if ch.tag != qn('w:pPr'): p._p.remove(ch)
    for extra in f.paragraphs[1:]: extra._p.getparent().remove(extra._p)
    p.alignment = AL.CENTER
    r = p.add_run()
    for t, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if t:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), t); r._r.append(e)
        else:
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; r._r.append(e)
    set_font(r, size)
def set_margins(section, landscape=False):
    from docx.enum.section import WD_ORIENT
    if landscape:
        section.orientation = WD_ORIENT.LANDSCAPE; section.page_width = Cm(29.7); section.page_height = Cm(21.0)
    else:
        section.orientation = WD_ORIENT.PORTRAIT; section.page_width = Cm(21.0); section.page_height = Cm(29.7)
    section.left_margin = Cm(3); section.right_margin = Cm(1.5); section.top_margin = Cm(2); section.bottom_margin = Cm(2)
    section.footer_distance = Cm(1.0); section.header_distance = Cm(1.0)

# ---- версия для PDF: формулы-картинки и встроенные обозначения текстом
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
def _txt(el, out, state):
    tag = el.tag.replace(M, "")
    if tag == "r":
        t = "".join(x.text or "" for x in el.findall(M + "t"))
        rpr = el.find(M + "rPr")
        plain = rpr is not None and (rpr.find(M + "nor") is not None or (rpr.find(M + "sty") is not None and rpr.find(M + "sty").get(M + "val") == "p"))
        it = (not plain) and bool(re.search("[A-Za-z]", t))
        out.append((t, it, state))
    elif tag == "sSub":
        _txt(el.find(M + "e"), out, state); _txt(el.find(M + "sub"), out, "sub")
    elif tag == "sSup":
        _txt(el.find(M + "e"), out, state); _txt(el.find(M + "sup"), out, "sup")
    elif tag == "sSubSup":
        _txt(el.find(M + "e"), out, state); _txt(el.find(M + "sub"), out, "sub"); _txt(el.find(M + "sup"), out, "sup")
    elif tag == "d":
        pr = el.find(M + "dPr"); b, e = "(", ")"
        if pr is not None:
            bc, ec = pr.find(M + "begChr"), pr.find(M + "endChr")
            if bc is not None: b = bc.get(M + "val")
            if ec is not None: e = ec.get(M + "val")
        out.append((b, False, state))
        for ch in el.findall(M + "e"): _txt(ch, out, state)
        out.append((e, False, state))
    else:
        for ch in el: _txt(ch, out, state)
def inline_math_to_runs(p):
    from docx.text.run import Run
    for om in list(p._p.findall(qn("m:oMath"))):
        out = []; _txt(om, out, None)
        anchor = om
        for t, it, vs in out:
            r = OxmlElement("w:r"); rPr = OxmlElement("w:rPr"); r.append(rPr)
            rf = OxmlElement("w:rFonts")
            for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): rf.set(qn(a), FONT)
            rPr.append(rf)
            if it: rPr.append(OxmlElement("w:i"))
            if vs:
                va = OxmlElement("w:vertAlign"); va.set(qn("w:val"), "subscript" if vs == "sub" else "superscript"); rPr.append(va)
            tt = OxmlElement("w:t"); tt.text = t; tt.set(qn("xml:space"), "preserve"); r.append(tt)
            anchor.addnext(r); anchor = r
        om.getparent().remove(om)

def fit_width(tbl, cm=16.5):
    """Растянуть таблицу на заданную ширину (по ширине текста страницы), сохранив пропорции столбцов."""
    from docx.oxml import OxmlElement
    tw = int(cm / 2.54 * 1440)
    el = tbl._tbl
    grid = el.find(qn("w:tblGrid"))
    cols = grid.findall(qn("w:gridCol")) if grid is not None else []
    ws = [int(c.get(qn("w:w")) or 0) for c in cols]
    if not ws or sum(ws) == 0: ws = [1] * len(cols)
    tot = sum(ws); new = [max(300, int(w / tot * tw)) for w in ws]
    k = tw - sum(new); new[-1] += k
    for c, w in zip(cols, new): c.set(qn("w:w"), str(w))
    pr = el.tblPr
    for tag in ("w:tblW", "w:tblLayout"):
        for e in pr.findall(qn(tag)): pr.remove(e)
    w = OxmlElement("w:tblW"); w.set(qn("w:w"), str(tw)); w.set(qn("w:type"), "dxa"); pr.append(w)
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); pr.append(lay)
    for row in tbl.rows:
        for i, cell in enumerate(row.cells):
            if i < len(new):
                tcPr = cell._tc.get_or_add_tcPr()
                for e in tcPr.findall(qn("w:tcW")): tcPr.remove(e)
                tw_ = OxmlElement("w:tcW"); tw_.set(qn("w:w"), str(new[i])); tw_.set(qn("w:type"), "dxa"); tcPr.insert(0, tw_)

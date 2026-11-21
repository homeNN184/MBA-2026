# -*- coding: utf-8 -*-
"""Презентация к защите. Основная часть и резервные слайды для ответов на вопросы."""
import copy, re, io
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION

TPL = "/tmp/claude-0/-home-claude/dd9faf01-b370-5003-bf0f-0f5597645131/scratchpad/tpl/tpl.pptx"
FIG = "/home/claude/work/fig/"
CH2 = "ch2/"
OUT = "/home/claude/work/pres/Презентация к защите.pptx"
DOK = "/home/claude/work/dokl/doklad.txt"

NAVY = RGBColor(0, 0x33, 0x66); BLUE = RGBColor(0, 0x79, 0xC2); LIGHT = RGBColor(0xE8, 0xF2, 0xFA)
GREEN = RGBColor(0x1B, 0x9E, 0x77); PURPLE = RGBColor(0x8E, 0x44, 0xAD); ORANGE = RGBColor(0xC4, 0x69, 0x0E)
GREY = RGBColor(0x59, 0x59, 0x59); DARK = RGBColor(0x1A, 0x1A, 0x1A)

# текст доклада по слайдам
NOTES = {}
_t = io.open(DOK, encoding="utf-8").read()
for b in re.split(r"\n\s*\n", _t.strip()):
    m = re.match(r"\[(\d+)[^\]]*\]\s*(.*)", b, re.S)
    NOTES[int(m.group(1))] = " ".join(m.group(2).split())

prs = Presentation(TPL)
LAY = prs.slides[2].slide_layout
lst = prs.slides._sldIdLst
for sid in list(lst)[2:]:
    prs.part.drop_rel(sid.rId); lst.remove(sid)


def set_text(shape, lines):
    tf = shape.text_frame
    p0 = tf.paragraphs[0]; r0 = p0.runs[0]
    for p in tf.paragraphs[1:]:
        p._p.getparent().remove(p._p)
    for r in p0.runs[1:]:
        r._r.getparent().remove(r._r)
    r0.text = lines[0]
    for l in lines[1:]:
        np_ = copy.deepcopy(p0._p); tf._txBody.append(np_)
        from pptx.text.text import _Paragraph
        pp = _Paragraph(np_, tf)
        for r in pp.runs[1:]:
            r._r.getparent().remove(r._r)
        pp.runs[0].text = l


prs.slides[0].notes_slide.notes_text_frame.text = NOTES[1]
for sh in prs.slides[1].shapes:
    if sh.name == "Прямоугольник 1":
        set_text(sh, ["Модель управления внедрением инновационных решений при реализации "
                      "инвестиционного проекта строительства отраслевого метрологического "
                      "центра расходометрии ПАО «Газпром»"])
        sh.top = Inches(1.55); sh.height = Inches(1.4)
    if sh.name == "Текст 1":
        set_text(sh, ["Постаутов Константин Владимирович",
                      "заместитель главного инженера по автоматизации и метрологическому обеспечению",
                      "ООО «Газпром трансгаз Екатеринбург», группа МВА-ИН-25",
                      "Руководитель — Соколова Галина Николаевна, д-р экон. наук, профессор"])
prs.slides[1].notes_slide.notes_text_frame.text = NOTES[2]

N = [2]


def new_slide(num, title):
    s = prs.slides.add_slide(LAY)
    for ph in list(s.placeholders):
        if ph.placeholder_format.idx == 0:
            ph.text_frame.text = title
        else:
            ph._element.getparent().remove(ph._element)
    s.notes_slide.notes_text_frame.text = NOTES.get(num, "")
    N.append(num)
    return s


def tb(s, x, y, w, h, text, size=14, bold=False, color=DARK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    t = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = t.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05); tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = anchor
    for i, l in enumerate(text if isinstance(text, list) else [text]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run(); r.text = l
        r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = "Arial"
    return t


def card(s, x, y, w, h, head, body, hsize=13, bsize=12, accent=BLUE, fill=LIGHT):
    r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    r.fill.solid(); r.fill.fore_color.rgb = fill; r.line.fill.background(); r.shadow.inherit = False
    a = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(0.07), Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb = accent; a.line.fill.background(); a.shadow.inherit = False
    if head:
        tb(s, x + 0.17, y + 0.07, w - 0.27, 0.38, head, hsize, True, NAVY)
        tb(s, x + 0.17, y + 0.46, w - 0.27, h - 0.52, body, bsize, False, DARK)
    else:
        tb(s, x + 0.17, y + 0.08, w - 0.27, h - 0.16, body, hsize, False, DARK, anchor=MSO_ANCHOR.MIDDLE)


def stat(s, x, y, w, big, cap, bigsize=26, color=BLUE):
    tb(s, x, y, w, 0.62, big, bigsize, True, color, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    tb(s, x, y + 0.62, w, 0.5, cap, 11.5, False, GREY, PP_ALIGN.CENTER)


def pic(s, name, x, y, maxw, maxh):
    from PIL import Image
    w, h = Image.open(FIG + name).size
    sc = min(maxw / w, maxh / h); pw, ph = w * sc, h * sc
    s.shapes.add_picture(FIG + name, Inches(x + (maxw - pw) / 2), Inches(y + (maxh - ph) / 2), Inches(pw), Inches(ph))




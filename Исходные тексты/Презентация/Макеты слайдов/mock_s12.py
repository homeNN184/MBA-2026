# -*- coding: utf-8 -*-
"""Макет слайда 2 на корпоративном шаблоне."""
from pptx import Presentation
from pptx.util import Inches
from pptx.enum.text import MSO_ANCHOR
from PIL import Image

TPL = "/tmp/claude-0/-home-claude/dd9faf01-b370-5003-bf0f-0f5597645131/scratchpad/tpl/tpl.pptx"
FIG = "/home/claude/work/fig/"
OUT = "/home/claude/work/pres/mock_s12.pptx"

prs = Presentation(TPL)
LAY = prs.slides[2].slide_layout
lst = prs.slides._sldIdLst
for sid in list(lst):
    prs.part.drop_rel(sid.rId); lst.remove(sid)

s = prs.slides.add_slide(LAY)
BAND_TOP, BAND_H = 0.0, 0.87   # синяя шапка шаблона
for ph in list(s.placeholders):
    if ph.placeholder_format.idx == 0:
        ph.left, ph.width = Inches(2.195), Inches(7.79)
        ph.top, ph.height = Inches(BAND_TOP), Inches(BAND_H)
        tf = ph.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_top = tf.margin_bottom = 0
        tf.text = "Экономическая модель. Входные параметры"
    else:
        ph._element.getparent().remove(ph._element)

w, h = Image.open(FIG + "s12_inputs.png").size
maxw, maxh = 9.3, 4.0
sc = min(maxw / w, maxh / h)
pw, ph_ = w * sc, h * sc
s.shapes.add_picture(FIG + "s12_inputs.png", Inches(0.35 + (maxw - pw) / 2),
                     Inches(1.05 + (maxh - ph_) / 2), Inches(pw), Inches(ph_))
prs.save(OUT)
print("слайдов", len(prs.slides), "| размер картинки на слайде", round(pw, 2), "x", round(ph_, 2), "дюйма")

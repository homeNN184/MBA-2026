# -*- coding: utf-8 -*-
"""Промежуточная презентация к защите: согласованные слайды 0-5."""
import io, re, copy, os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from PIL import Image

TPL = "/tmp/claude-0/-home-claude/dd9faf01-b370-5003-bf0f-0f5597645131/scratchpad/tpl/tpl.pptx"
FIG = "/home/claude/work/fig/"
OUT = "/home/claude/work/pres2/Презентация к защите.pptx"
DOK = "/home/claude/work/pres2/doklad.txt"

NOTES = {}
DEF_NOTE = ("Дополнительный слайд. В доклад не входит, показывается по вопросам комиссии о расчетной модели и порядке выбора сценария.")
for b in re.split(r"\n\s*\n", io.open(DOK, encoding="utf-8").read().strip()):
    m = re.match(r"\[(\d+)\]\s*(.*)", b, re.S)
    NOTES[int(m.group(1))] = " ".join(m.group(2).split())

TMP = "/tmp/claude-0/-home-claude/dd9faf01-b370-5003-bf0f-0f5597645131/scratchpad/sl"
os.makedirs(TMP, exist_ok=True)


MAXPX = 1150          # ширина растра на слайде шириной 9,3 дюйма


def shrink(path):
    """Сжатие изображения: ограничение ширины, для схем еще и палитра 128 цветов."""
    im = Image.open(path).convert("RGB")
    if im.width > MAXPX:
        im = im.resize((MAXPX, round(im.height * MAXPX / im.width)), Image.LANCZOS)
    jpg = path.lower().endswith((".jpg", ".jpeg"))
    out = os.path.join(TMP, os.path.basename(path))
    if jpg:
        im.save(out, quality=84, optimize=True)
    else:
        im.quantize(colors=96, method=Image.MEDIANCUT, dither=Image.NONE).save(out, optimize=True)
    return out


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
    from pptx.text.text import _Paragraph
    for l in lines[1:]:
        np_ = copy.deepcopy(p0._p); tf._txBody.append(np_)
        pp = _Paragraph(np_, tf)
        for r in pp.runs[1:]:
            r._r.getparent().remove(r._r)
        pp.runs[0].text = l


# слайд 1 — тема работы и слушатель
for sh in prs.slides[1].shapes:
    if sh.name == "Прямоугольник 1":
        set_text(sh, ["Разработка модели управления инновационной деятельностью "
                      "при реализации инвестиционных проектов"])
        sh.top = Inches(1.55); sh.height = Inches(1.5)
        sh.width = Inches(9.2)
        sh.left = Inches((10.01 - 9.2) / 2)          # по центру ширины слайда
        for par in sh.text_frame.paragraphs:
            par.alignment = PP_ALIGN.CENTER
    if sh.name == "Текст 1":
        set_text(sh, ["Постаутов Константин Владимирович",
                      "заместитель главного инженера по автоматизации",
                      "и метрологическому обеспечению",
                      "ООО «Газпром трансгаз Екатеринбург»"])
        for par in sh.text_frame.paragraphs:                # на два пункта мельче
            for r in par.runs:
                r.font.size = Pt(16)
prs.slides[1].notes_slide.notes_text_frame.text = NOTES[1]

BAND_TOP, BAND_H = 0.0, 0.87
SL = [(2, "Актуальность", "s2_v2.png"),
      (3, "Цель и задачи", "s3_goal.png"),
      (4, "Нормативная и методическая база", "s4_norm.png"),
      (5, "Результат анализа", "s5_res.png"),
      (6, "Прототип реализации механизма", "s6_proto.jpg"),
      (7, "Реализованные инновационные решения", "s7_sol.jpg"),
      (8, "Последовательность реализации проекта-прототипа", "s8_road.png"),
      (9, "SWOT-анализ организации работ", "s9_swot.png"),
      (10, "Разработка механизма интеграции", "s10_mech.jpg"),
      (11, "Экономическая модель интеграции. Структура", "s11_model.png"),
      (12, "Экономическая модель. Входные параметры", "s12_inputs.png"),
      (13, "Риск и имитационное моделирование", "s13_risk.png"),
      (14, "Календарный план сценариев интеграции", "s14_cal.png"),
      (15, "Результаты моделирования сценарных условий", "s15_res.png"),
      (16, "Проверка устойчивости результата моделирования", "s16_sens.png"),
      (17, "Профиль риска и распределение ЧДД", "s21_risk2.png"),
      (18, "Процесс принятия решения об интеграции", "s17_proc.png"),
      (19, "Программная реализация расчетной модели", "s20_prog.jpg"),
      (20, "Выводы", "s18_concl.png"),
      (21, "Спасибо за внимание", None),
      (22, "Дополнительные материалы", "SECTION"),
      (23, "Структура расчетной модели", "mod_struct.png"),
      (24, "Алгоритм моделирования", "mod_alg.png"),
      (25, "Последовательность определения сценария", "mod_seq.png"),
      (26, "Работа с программой. Шаг 1. Итоги", "step1.png"),
      (27, "Работа с программой. Шаг 2. Календарный план", "step2.png"),
      (28, "Работа с программой. Шаг 3. Годовые потоки", "step3.png"),
      (29, "Работа с программой. Шаг 4. Чувствительность", "step4.png"),
      (30, "Работа с программой. Шаг 5. Имитационное моделирование", "step5.png"),
      (31, "Работа с программой. Шаг 6. Переделки", "step6.png"),
      (32, "Работа с программой. Шаг 7. Выбор сценария", "step7.png"),
      (33, "Работа с программой. Шаг 8. Проверка расчета", "step8.png"),
      (34, "Работа с программой. Шаг 9. Отчет по расчету", "step9.png")]

from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

for num, title, png in SL:
    s = prs.slides.add_slide(LAY)
    if png in (None, "SECTION"):                      # фон без шапки: финал и разделитель
        fillc = RGBColor(0x00, 0x33, 0x66) if png == "SECTION" else RGBColor(0x00, 0x79, 0xC2)
        for ph in list(s.placeholders):
            ph._element.getparent().remove(ph._element)
        bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                                prs.slide_width, prs.slide_height)
        bg.fill.solid(); bg.fill.fore_color.rgb = fillc
        bg.line.fill.background(); bg.shadow.inherit = False
        tf = bg.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_top = tf.margin_bottom = 0
        par = tf.paragraphs[0]; par.alignment = PP_ALIGN.CENTER
        r = par.add_run(); r.text = title
        r.font.size = Pt(34 if png == "SECTION" else 40); r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        s.notes_slide.notes_text_frame.text = NOTES.get(num, DEF_NOTE)
        continue
    for ph in list(s.placeholders):
        if ph.placeholder_format.idx == 0:
            ph.left, ph.width = Inches(2.195), Inches(7.79)
            ph.top, ph.height = Inches(BAND_TOP), Inches(BAND_H)
            tf = ph.text_frame
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf.margin_top = tf.margin_bottom = 0
            tf.text = title
        else:
            ph._element.getparent().remove(ph._element)
    src = shrink(FIG + png)
    w, h = Image.open(src).size
    maxw, maxh = 9.3, 4.0
    sc = min(maxw / w, maxh / h)
    pw, ph_ = w * sc, h * sc
    s.shapes.add_picture(src, Inches(0.35 + (maxw - pw) / 2),
                         Inches(1.05 + (maxh - ph_) / 2), Inches(pw), Inches(ph_))
    s.notes_slide.notes_text_frame.text = NOTES.get(num, DEF_NOTE)

prs.save(OUT)
print("слайдов", len(prs.slides), "->", OUT)
_FILES_AUTHOR = [OUT]

# служебные свойства: автор и разработчик
import subprocess as _sp, sys as _sys
_sp.call([_sys.executable, "/home/claude/work/setauthor.py"] + _FILES_AUTHOR)

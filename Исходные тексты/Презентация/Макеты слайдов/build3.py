# -*- coding: utf-8 -*-
"""Презентация к защите на корпоративном шаблоне. 18 слайдов, доклад 9 минут."""
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


for sh in prs.slides[1].shapes:
    if sh.name == "Прямоугольник 1":
        set_text(sh, ["Модель управления внедрением инновационных решений при реализации "
                      "инвестиционного проекта строительства отраслевого метрологического "
                      "центра расходометрии ПАО «Газпром»"])
        sh.top = Inches(1.55); sh.height = Inches(1.4)
    if sh.name == "Текст 1":
        set_text(sh, ["[Фамилия, имя, отчество слушателя]", "[должность, дочернее общество ПАО «Газпром»]"])
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



# ---------------------------------------------------------------- 3 Актуальность
s = new_slide(3, "Актуальность")
for i, (h, b, col) in enumerate([
        ("Срок ввода", "Строительство откладывается до готовности оборудования", BLUE),
        ("Подтверждение", "Только на инфраструктуре масштаба объекта", PURPLE),
        ("Регулирование", "Общих контрольных точек нет", ORANGE)]):
    card(s, 0.4 + i * 3.1, 1.25, 2.95, 1.95, h, b, 13, 12, accent=col)
card(s, 0.4, 3.4, 9.2, 0.95, "Объект исследования",
     "ОМЦР, третий пусковой комплекс. СПУ ПГ-018, 10 МПа, 40 000 м³/ч", 13, 13, accent=GREEN)
# ---------------------------------------------------------------- 4 Цель и задачи
s = new_slide(4, "Цель и задачи")
card(s, 0.4, 1.2, 9.2, 0.95, None,
     "Цель — модель управления внедрением инноваций при одновременном строительстве объекта", 14)
for i, (h, b, col) in enumerate([
        ("Задача 1", "Нормативная база и практика", BLUE),
        ("Задача 2", "Организация работ и проблемы управления", PURPLE),
        ("Задача 3", "Предложения, модель, порядок решения", GREEN)]):
    card(s, 0.4 + i * 3.1, 2.35, 2.95, 1.9, h, b, 14, 13, accent=col)
# ---------------------------------------------------------------- 5 Что показало исследование
s = new_slide(5, "Исследование показало")
items5 = ["Порядок согласования процессов не определен",
          "Уровни готовности технологии не применяются",
          "Совмещение выполнимо, опыт объекта подтверждает",
          "Порядка связи с этапами строительства не было"]
for i, b in enumerate(items5):
    y = 1.25 + i * 0.78
    r = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.45), Inches(y + 0.1), Inches(0.46), Inches(0.46))
    r.fill.solid(); r.fill.fore_color.rgb = NAVY; r.line.fill.background(); r.shadow.inherit = False
    tf = r.text_frame; tf.text = str(i + 1)
    pr = tf.paragraphs[0]; pr.alignment = PP_ALIGN.CENTER
    pr.runs[0].font.size = Pt(14); pr.runs[0].font.bold = True
    pr.runs[0].font.color.rgb = RGBColor(255, 255, 255); pr.runs[0].font.name = "Arial"
    card(s, 1.05, y, 8.55, 0.66, None, b, 13)
card(s, 0.45, 4.4, 9.15, 0.6, None, "Нужна детализация существующих связей", 13.5, accent=GREEN)
# ---------------------------------------------------------------- 6 Предложение
s = new_slide(6, "Предлагаемый механизм интеграции")
pic(s, "pres_mech.png", 0.4, 1.15, 9.2, 2.65)
card(s, 0.4, 3.95, 9.2, 0.62, None,
     "Точка входа — начало проектной документации. Уровень входа TRL5–TRL7. Шесть контрольных точек", 13)
# ---------------------------------------------------------------- 7 Результаты расчета
s = new_slide(7, "Результат расчета к традиционной схеме")
cd = CategoryChartData()
cd.categories = ["Традиционная\nсхема", "Интеграция\nTRL5", "Интеграция\nTRL6", "Интеграция\nTRL7"]
cd.add_series("Чистый дисконтированный доход, раз", (1.00, 2.67, 2.48, 1.69))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.5), Inches(1.15), Inches(5.6), Inches(3.0), cd)
ch = gf.chart; ch.has_title = False; ch.has_legend = False
ch.font.size = Pt(11); ch.font.name = "Arial"
pl = ch.plots[0]; pl.has_data_labels = True
dl = pl.data_labels; dl.number_format = '0.00'; dl.number_format_is_linked = False
dl.position = XL_LABEL_POSITION.OUTSIDE_END; dl.font.size = Pt(11); dl.font.bold = True
va = ch.value_axis; va.has_major_gridlines = True
va.major_gridlines.format.line.color.rgb = RGBColor(0xD9, 0xD9, 0xD9)
va.format.line.fill.background(); va.tick_labels.font.size = Pt(10)
ch.category_axis.tick_labels.font.size = Pt(10)
for i, col in enumerate((BLUE, GREEN, PURPLE, ORANGE)):
    pt = pl.series[0].points[i]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = col
tb(s, 0.5, 4.15, 5.6, 0.3, "Рост чистого дисконтированного дохода, раз", 11, False, GREY)
card(s, 6.3, 1.15, 3.3, 1.42, "Срок ввода короче", "на 26, 21 и 15 %", 13, 13, accent=GREEN)
card(s, 6.3, 2.72, 3.3, 1.43, "Прирост дохода", "19,8–48,1 % инновационных затрат", 13, 13, accent=PURPLE)
tb(s, 0.4, 4.52, 9.2, 0.3, "Нормированные данные, величины относительные", 11, False, GREY)
# ---------------------------------------------------------------- 8 Устойчивость и доля инноваций
s = new_slide(8, "Устойчивость результата")
pic(s, "pres_share.png", 0.35, 1.1, 5.8, 3.1)
card(s, 6.3, 1.10, 3.3, 0.98, "Доля инноваций",
     "Выше доля — больше выигрыш", 12.5, 11.5, accent=GREEN)
card(s, 6.3, 2.18, 3.3, 0.98, "Пять проверок",
     "Порядок сценариев не меняется", 12.5, 11.5, accent=PURPLE)
card(s, 6.3, 3.26, 3.3, 0.98, "Монте-Карло",
     "5 000 прогонов, интеграция лучше в 99,9 %", 12.5, 11.5, accent=ORANGE)
tb(s, 0.35, 4.35, 9.25, 0.3, "Правило выбора — допустимость, затем уровень входа", 11.5, False, GREY)
# ---------------------------------------------------------------- 9 Рекомендации
s = new_slide(9, "Наши рекомендации")
rec = ["Уровень готовности и точки — в целевую программу",
       "Объект — в программу внедрения",
       "Исходные данные — в техническое задание",
       "Решение коллегиальное"]
for i, b in enumerate(rec):
    y = 1.2 + i * 0.76
    r = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.45), Inches(y + 0.08), Inches(0.44), Inches(0.44))
    r.fill.solid(); r.fill.fore_color.rgb = NAVY; r.line.fill.background(); r.shadow.inherit = False
    tf = r.text_frame; tf.text = str(i + 1)
    pr = tf.paragraphs[0]; pr.alignment = PP_ALIGN.CENTER
    pr.runs[0].font.size = Pt(13); pr.runs[0].font.bold = True
    pr.runs[0].font.color.rgb = RGBColor(255, 255, 255); pr.runs[0].font.name = "Arial"
    card(s, 1.05, y, 8.55, 0.64, None, b, 12.5)
card(s, 0.45, 4.3, 9.15, 0.72, None,
     "Начать с пилотного проекта", 13.5, accent=GREEN)
# ---------------------------------------------------------------- 10 Спасибо
s = new_slide(10, "")
tb(s, 0.4, 1.9, 9.2, 1.0, "Спасибо за внимание!", 34, True, NAVY, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
tb(s, 0.4, 3.05, 9.2, 0.8, ["Новизна — модель интеграции и механизм контрольных точек",
                            "Значимость — обоснование решения расчетом"], 13, False, GREY, PP_ALIGN.CENTER)

prs.save(OUT)
print("слайдов:", len(prs.slides), "| сохранено:", OUT)

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


# ---------------------------------------------------------------- 3
s = new_slide(3, "Проблема")
card(s, 0.4, 1.25, 3.0, 1.55, "Традиционная схема", "Сначала готовое оборудование, затем проектирование и строительство", 13, 12)
card(s, 3.5, 1.25, 3.0, 1.55, "Срок ввода", "Увеличивается на весь срок разработки оборудования", 13, 12)
card(s, 6.6, 1.25, 3.0, 1.55, "Подтверждение характеристик", "Только на инфраструктуре масштаба объекта. Затраты на нее безвозвратны", 13, 12)
card(s, 0.4, 3.0, 9.2, 1.25, "Два процесса регулируются раздельно",
     "Инновационная деятельность идет по документам о НИОКР и внедрении, инвестиционная по документам о планировании, "
     "проектировании и строительстве. Общих контрольных точек и критериев готовности нет", 14, 13, accent=ORANGE)
# ---------------------------------------------------------------- 4
s = new_slide(4, "Объект исследования")
card(s, 0.4, 1.2, 9.2, 0.85, None,
     "Отраслевой метрологический центр расходометрии, третий пусковой комплекс. "
     "Основание — Дорожная карта 2019 года Минпромторга России и ПАО «Газпром»", 13)
stat(s, 0.5, 2.2, 2.9, "10 МПа", "рабочее давление")
stat(s, 3.55, 2.2, 2.9, "40 000 м³/ч", "расход")
stat(s, 6.6, 2.2, 2.9, "СПУ ПГ-018", "основное технологическое оборудование")
card(s, 0.4, 3.55, 9.2, 0.7, None,
     "Серийных аналогов нет. С 2022 года разработка собственная, одновременно с проектированием и строительством", 13,
     accent=ORANGE)
# ---------------------------------------------------------------- 5
s = new_slide(5, "Цель и задачи дипломной работы")
card(s, 0.4, 1.2, 9.2, 0.95, None,
     "Цель — разработать модель управления внедрением инновационных решений от идеи до промышленной эксплуатации "
     "при одновременной реализации инвестиционного строительного проекта", 14)
for i, (h, b, col) in enumerate([
        ("Задача 1", "Анализ нормативной и методической базы, российской и зарубежной практики", BLUE),
        ("Задача 2", "Анализ организации работ на объекте и выявление проблем управления", PURPLE),
        ("Задача 3", "Разработка предложений, экономической модели и порядка принятия решения", GREEN)]):
    card(s, 0.4 + i * 3.1, 2.35, 2.95, 1.9, h, b, 13, 12, accent=col)
# ---------------------------------------------------------------- 6
s = new_slide(6, "Методы и информационная база")
for i, (h, b) in enumerate([
        ("Анализ", "Системный, сравнительный и SWOT-анализ"),
        ("Механизм", "Стадийный подход с контрольными точками, шкала уровней готовности технологии"),
        ("Расчет", "Сценарное и имитационное моделирование, показатели NPV, PI, PP, DPP, IRR")]):
    card(s, 0.4 + i * 3.1, 1.3, 2.95, 1.85, h, b, 13, 12)
card(s, 0.4, 3.35, 9.2, 0.9, "Информационная база",
     "Нормативные правовые акты, документы стратегического планирования, корпоративные документы ПАО «Газпром», "
     "материалы проекта, открытые публикации", 13, 12, accent=GREY)
# ---------------------------------------------------------------- 7
s = new_slide(7, "Результат анализа нормативной базы")
card(s, 0.4, 1.2, 9.2, 0.62, None, "Шесть групп источников, от федеральных актов до российской и зарубежной практики", 12.5, accent=GREY)
rows7 = [("Федеральные акты и стратегические документы", "Задают требования и направления, порядок согласования не определяют"),
         ("Связи инноваций и строительства", "Предусмотрены, однако односторонние"),
         ("Документы по внедрению инновационной продукции", "Разработку под конкретный проект не предусматривают"),
         ("Уровни готовности технологии", "В корпоративных документах не применяются")]
for i, (h, b) in enumerate(rows7):
    x = 0.4 + (i % 2) * 4.7; y = 2.0 + (i // 2) * 1.15
    card(s, x, y, 4.5, 1.05, h, b, 12, 11.5, accent=ORANGE if i >= 2 else BLUE)
# ---------------------------------------------------------------- 8
s = new_slide(8, "Опыт объекта и выявленные проблемы")
pic(s, "f2_road.png", 0.4, 1.15, 5.65, 2.1)
card(s, 6.25, 1.15, 3.35, 3.1, "Проблемы по SWOT-анализу",
     ["Формализованного порядка связи разработки и строительства не было",
      "",
      "Соответствие проверяется только после завершения строительства",
      "",
      "Права на результаты и срок гарантии не урегулированы"], 12.5, 11.5, accent=ORANGE)
card(s, 0.4, 3.4, 5.65, 0.85, None,
     "Разработка несерийного наукоемкого изделия велась внутри договора поставки комплектного оборудования", 12)
# ---------------------------------------------------------------- 9
s = new_slide(9, "Состав разработанной модели")
parts = [("1. Механизм контрольных точек", "Связь стадий строительства с уровнями готовности", BLUE),
         ("2. Экономическая модель", "Четыре сценария, срок ввода и ЧДД", PURPLE),
         ("3. Правило выбора сценария", "Проверка устойчивости и меры управления рисками", GREEN),
         ("4. Процесс принятия решения", "Пять стадий от замысла до оценки результата", ORANGE)]
for i, (h, b, col) in enumerate(parts):
    x = 0.4 + (i % 2) * 4.7; y = 1.3 + (i // 2) * 1.5
    card(s, x, y, 4.5, 1.35, h, b, 13, 12, accent=col)
# ---------------------------------------------------------------- 10
s = new_slide(10, "Механизм интеграции")
pic(s, "pres_mech.png", 0.4, 1.15, 9.2, 2.65)
card(s, 0.4, 3.95, 9.2, 0.62, None,
     "Точка входа — начало проектной документации. Уровень входа от TRL5 до TRL7. "
     "Шесть контрольных точек, решение по результатам испытаний", 12.5)
# ---------------------------------------------------------------- 11
s = new_slide(11, "Четыре сценария организации работ")
pic(s, "pres_scen.png", 0.4, 1.15, 9.2, 2.5)
card(s, 0.4, 3.75, 9.2, 0.6, None,
     "Три сценария интеграции сравниваются с традиционной схемой, при которой сначала получают готовое оборудование", 12.5)
# ---------------------------------------------------------------- 12
s = new_slide(12, "Экономический результат к традиционной схеме")
cd = CategoryChartData()
cd.categories = ["Традиционная\nсхема", "Интеграция\nTRL5", "Интеграция\nTRL6", "Интеграция\nTRL7"]
cd.add_series("Чистый дисконтированный доход, раз", (1.00, 2.67, 2.48, 1.69))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.5), Inches(1.15), Inches(5.6), Inches(3.1), cd)
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
tb(s, 0.5, 4.2, 5.6, 0.3, "Рост чистого дисконтированного дохода, раз", 11, False, GREY)
card(s, 6.3, 1.15, 3.3, 1.5, "Срок ввода короче",
     "на 26, 21 и 15 % при входе на TRL5, TRL6 и TRL7", 13, 12.5, accent=GREEN)
card(s, 6.3, 2.8, 3.3, 1.45, "Прирост ЧДД",
     "от 19,8 до 48,1 % инновационных затрат проекта", 13, 12.5, accent=PURPLE)
tb(s, 0.4, 4.6, 9.2, 0.3, "Расчет на нормированных данных, все величины относительные", 11, False, GREY)
# ---------------------------------------------------------------- 13
s = new_slide(13, "Устойчивость и правило выбора")
for i, (h, b) in enumerate([("Пять проверок", "Ставка, доля инновационных затрат, стоимость опытной инфраструктуры, стресс-сценарий, имитационный расчет"),
                            ("Порядок сценариев", "Не меняется ни при одной из проверок"),
                            ("Доработки", "При доработке на каждом уровне сохраняется от 10 до 47 % преимущества")]):
    card(s, 0.4 + i * 3.1, 1.25, 2.95, 1.75, h, b, 13, 11.5)
card(s, 0.4, 3.2, 9.2, 1.05, "Правило выбора из двух шагов",
     "Сначала проверяется допустимость интеграции по четырем условиям, затем выбирается уровень входа "
     "по отношению заказчика к риску", 14, 13, accent=GREEN)
# ---------------------------------------------------------------- 14
s = new_slide(14, "Процесс принятия решения об интеграции")
pic(s, "f34_process.png", 0.4, 1.15, 9.2, 2.45)
card(s, 0.4, 3.7, 9.2, 0.6, None,
     "Решение на этапе замысла, уточнение до начала проектирования. Пять стадий, на четырех расчет по модели", 12.5)
# ---------------------------------------------------------------- 15
s = new_slide(15, "Программная реализация расчета")
pic(s, "app_screen_crop.png", 0.4, 1.15, 6.3, 3.1)
card(s, 6.95, 1.15, 2.65, 3.1, "Две формы расчета",
     ["Книга Excel с действующими формулами", "", "Программа в формате HTML с расчетом на языке JavaScript", "",
      "Установка не требуется", "", "Принимает параметры конкретного проекта"], 12.5, 11.5, accent=PURPLE)
# ---------------------------------------------------------------- 16
s = new_slide(16, "Рекомендации по внедрению")
rec = ["Включать сведения об уровне готовности и контрольные точки в комплексную целевую программу и обоснование инвестиций",
       "Указывать объект строительства в программе внедрения инновационной продукции",
       "Закреплять в техническом задании передачу исходных данных к каждой контрольной точке",
       "Принимать решение коллегиально на совещании по ходу строительства"]
for i, b in enumerate(rec):
    card(s, 0.4, 1.2 + i * 0.78, 9.2, 0.7, None, b, 12.5)
card(s, 0.4, 4.35, 9.2, 0.0 + 0.6, None, "Применение начинать с пилотного инвестиционного проекта", 12.5, accent=ORANGE)
# ---------------------------------------------------------------- 17
s = new_slide(17, "Научная новизна и практическая значимость")
card(s, 0.4, 1.3, 4.5, 2.0, "Научная новизна",
     "Экономическая модель интеграции двух процессов. Механизм согласованных контрольных точек, связывающий "
     "стадии строительства с уровнями готовности технологии", 14, 13, accent=PURPLE)
card(s, 5.1, 1.3, 4.5, 2.0, "Практическая значимость",
     "Возможность обосновать решение об интеграции расчетом на данных конкретного проекта", 14, 13, accent=GREEN)
card(s, 0.4, 3.5, 9.2, 0.75, None,
     "Интеграция управляема, если связать стадии строительства с уровнями готовности технологии в контрольных точках", 14)
# ---------------------------------------------------------------- 18
s = new_slide(18, "")
tb(s, 0.4, 1.9, 9.2, 1.0, "Благодарю за внимание", 32, True, NAVY, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
tb(s, 0.4, 3.0, 9.2, 0.8, ["Руководителю дипломного проекта, консультантам, рецензенту",
                           "и членам аттестационной комиссии"], 14, False, GREY, PP_ALIGN.CENTER)

prs.save(OUT)
print("слайдов:", len(prs.slides), "| сохранено:", OUT)

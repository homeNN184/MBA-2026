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
CH2 = "ch2s/"
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
        sh.top = Inches(2.95); sh.height = Inches(1.45)
        for _p in sh.text_frame.paragraphs:
            for _r in _p.runs:
                _r.font.size = Pt(12.5)
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




def cap(s, x, y, w, text):
    tb(s, x, y, w, 0.26, text, 10.5, False, GREY, PP_ALIGN.CENTER)


def num_list(s, items, y0, step, size=12.5, h=0.64, x=0.45, w=8.55):
    for i, b in enumerate(items):
        y = y0 + i * step
        r = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y + 0.08), Inches(0.44), Inches(0.44))
        r.fill.solid(); r.fill.fore_color.rgb = NAVY; r.line.fill.background(); r.shadow.inherit = False
        tf = r.text_frame; tf.text = str(i + 1)
        pr = tf.paragraphs[0]; pr.alignment = PP_ALIGN.CENTER
        pr.runs[0].font.size = Pt(13); pr.runs[0].font.bold = True
        pr.runs[0].font.color.rgb = RGBColor(255, 255, 255); pr.runs[0].font.name = "Arial"
        card(s, x + 0.6, y, w, h, None, b, size)


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
# ---------------------------------------------------------------- 5 Нормативная база
s = new_slide(5, "Нормативная база и практика")
num_list(s, ["Порядок согласования строительства и инноваций не определен",
             "Уровни готовности технологии в процедурах не применяются",
             "Российская и зарубежная практика такую шкалу использует"], 1.3, 0.86, 13, 0.7)
card(s, 0.45, 4.0, 9.15, 0.66, None,
     "Нужна детализация существующих связей, а не построение новых", 13.5, accent=GREEN)
# ---------------------------------------------------------------- 6 Объект
s = new_slide(6, "Объект: метрологический центр и установка СПУ ПГ-018")
pic(s, CH2 + "f01.jpg", 0.4, 1.12, 2.95, 1.78)
pic(s, CH2 + "f04.jpg", 3.52, 1.12, 2.95, 1.78)
pic(s, CH2 + "f05.jpg", 6.64, 1.12, 2.95, 1.78)
cap(s, 0.4, 2.94, 2.95, "Площадка третьего комплекса")
cap(s, 3.52, 2.94, 2.95, "Технологический зал БКК")
cap(s, 6.64, 2.94, 2.95, "Технологический зал МКК")
for i, (big, c) in enumerate([("10 МПа", "рабочее давление"), ("40 000 м³/ч", "предельный расход"),
                              ("5,5 МВт", "потребляемая мощность"), ("2 контура", "БКК и МКК")]):
    stat(s, 0.4 + i * 2.33, 3.28, 2.25, big, c, 20, (BLUE, GREEN, PURPLE, ORANGE)[i])
card(s, 0.4, 4.42, 9.19, 0.6, None,
     "Серийных аналогов нет. С 2022 года потребовалась собственная разработка", 12.5, accent=ORANGE)
# ---------------------------------------------------------------- 7 Технические решения
s = new_slide(7, "Инновационные технические решения")
pic(s, CH2 + "f10.jpg", 0.4, 1.12, 4.5, 1.28)
pic(s, CH2 + "f12.jpg", 5.1, 1.12, 4.5, 1.28)
cap(s, 0.4, 2.42, 4.5, "Раструб из двух отводов DN 700 в составе БКК")
cap(s, 5.1, 2.42, 4.5, "Вентилятор высокого давления в составе установки")
pic(s, CH2 + "f13.jpg", 0.4, 2.74, 4.5, 1.42)
pic(s, CH2 + "f14.jpg", 5.1, 2.74, 4.5, 1.42)
cap(s, 0.4, 4.18, 4.5, "Заводские испытания соединительной детали")
cap(s, 5.1, 4.18, 4.5, "Заводские испытания вентилятора на воздухе")
card(s, 0.4, 4.5, 9.2, 0.55, None,
     "Моделирование течения газа, нестандартные детали до DN 700, пять агрегатов ПВВД", 12, accent=GREEN)
# ---------------------------------------------------------------- 8 Последовательность и SWOT
s = new_slide(8, "Последовательность реализации и SWOT-анализ")
pic(s, CH2 + "f15.png", 0.35, 1.10, 5.95, 2.35)
cap(s, 0.35, 3.44, 5.95, "Разработка СПУ ПГ-018 и стадии строительства шли параллельно")
card(s, 6.42, 1.10, 3.18, 1.02, "Сильные стороны",
     "Требования закреплены, расчеты до изготовления", 12, 11, accent=GREEN)
card(s, 6.42, 2.20, 3.18, 1.02, "Слабые стороны",
     "Связи разработки и стройки не формализованы", 12, 11, accent=PURPLE)
card(s, 6.42, 3.30, 3.18, 1.02, "Угрозы",
     "Соответствие проверяется после создания объекта", 12, 11, accent=ORANGE)
card(s, 0.35, 3.78, 5.95, 1.14, "Вывод",
     "Слабые стороны устранимы управлением, без изменения изделия. Координацию ведет заказчик", 12.5, 12)
tb(s, 6.42, 4.45, 3.18, 0.3, "Шесть проблем — вход главы 3", 11.5, False, GREY)
# ---------------------------------------------------------------- 9 Механизм
s = new_slide(9, "Предлагаемый механизм интеграции")
pic(s, "s/pres_mech.png", 0.4, 1.15, 9.2, 2.65)
card(s, 0.4, 3.95, 9.2, 0.62, None,
     "Точка входа — начало проектной документации. Уровень входа TRL5–TRL7. Шесть контрольных точек", 13)
# ---------------------------------------------------------------- 10 Календарный план
s = new_slide(10, "Четыре сценария и календарный план")
pic(s, "s/f32_calendar.png", 0.25, 1.10, 4.7, 3.42)
card(s, 5.15, 1.10, 4.45, 1.05, "Традиционная схема",
     "Подтверждение TRL9 на временной опытной инфраструктуре, затем строительство", 12.5, 11.5, accent=BLUE)
card(s, 5.15, 2.23, 4.45, 1.05, "Интеграция TRL5–TRL7",
     "Вход в начале проектной документации, шесть контрольных точек", 12.5, 11.5, accent=GREEN)
card(s, 5.15, 3.36, 4.45, 1.05, "Плата за ранний вход",
     "Риск переделок документации учтен вероятностью и стоимостью", 12.5, 11.5, accent=ORANGE)
tb(s, 5.15, 4.52, 4.45, 0.3, "Раньше вход — раньше ввод объекта", 11.5, False, GREY)
# ---------------------------------------------------------------- 11 Результат расчета
s = new_slide(11, "Результат расчета к традиционной схеме")
cd = CategoryChartData()
cd.categories = ["Традиционная\nсхема", "Интеграция\nTRL5", "Интеграция\nTRL6", "Интеграция\nTRL7"]
cd.add_series("Чистый дисконтированный доход, раз", (1.00, 2.67, 2.48, 1.69))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.35), Inches(1.15), Inches(5.2), Inches(2.95), cd)
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
tb(s, 0.35, 4.08, 5.2, 0.3, "Рост чистого дисконтированного дохода, раз", 11, False, GREY)
pic(s, "s/f34_cumdisc.png", 5.75, 1.15, 3.85, 1.95)
cap(s, 5.75, 3.08, 3.85, "Накопленный дисконтированный поток и сроки окупаемости")
card(s, 5.75, 3.42, 3.85, 1.05, "Срок ввода короче",
     "на 26, 21 и 15 %. Окупаемость быстрее на 31, 28 и 16 %", 12.5, 11.5, accent=GREEN)
tb(s, 0.35, 4.55, 9.25, 0.3, "Нормированные данные, величины относительные", 11, False, GREY)
# ---------------------------------------------------------------- 12 Чувствительность
s = new_slide(12, "Чувствительность и доля инноваций")
pic(s, "s/f35_sens.png", 0.3, 1.10, 5.5, 3.25)
cap(s, 0.3, 4.38, 5.5, "Ставка дисконтирования (а, б) и доля инновационных затрат (в, г)")
card(s, 6.0, 1.10, 3.6, 1.02, "Пять проверок",
     "Порядок сценариев не меняется ни в одной", 12.5, 11.5, accent=PURPLE)
card(s, 6.0, 2.23, 3.6, 1.02, "Доля инноваций 10 → 50 %",
     "Традиционная схема теряет 72 %, интеграция 2 %", 12.5, 11.5, accent=GREEN)
card(s, 6.0, 3.36, 3.6, 1.02, "Худший случай",
     "Переделка на каждом уровне оставляет 10–47 % выигрыша", 12.5, 11.5, accent=ORANGE)
# ---------------------------------------------------------------- 13 Монте-Карло
s = new_slide(13, "Имитационное моделирование, 5 000 прогонов")
pic(s, "s/pres_mc.png", 0.3, 1.10, 6.15, 3.25)
cap(s, 0.3, 4.38, 6.15, "Каждая точка — один прогон, линии показывают медиану сценария")
card(s, 6.6, 1.10, 3.0, 1.02, "Все параметры сразу",
     "Сроки, затраты, выручка, ставка отклоняются вместе", 12.5, 11.5, accent=PURPLE)
card(s, 6.6, 2.23, 3.0, 1.02, "Интеграция лучше",
     "в 99,9 % прогонов", 12.5, 11.5, accent=GREEN)
card(s, 6.6, 3.36, 3.0, 1.02, "Убыточных прогонов",
     "меньше в 2,5 раза", 12.5, 11.5, accent=ORANGE)
# ---------------------------------------------------------------- 14 Рекомендации
s = new_slide(14, "Наши рекомендации")
num_list(s, ["Уровень готовности и контрольные точки — в целевую программу",
             "Объект строительства — в программу внедрения продукции",
             "Передача исходных данных — в техническое задание",
             "Решение в контрольной точке — коллегиальное"], 1.2, 0.76, 12.5, 0.64)
card(s, 0.45, 4.3, 9.15, 0.72, None, "Начать с пилотного проекта", 13.5, accent=GREEN)
# ---------------------------------------------------------------- 15 Спасибо
s = new_slide(15, "")
tb(s, 0.4, 1.9, 9.2, 1.0, "Спасибо за внимание!", 34, True, NAVY, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
tb(s, 0.4, 3.05, 9.2, 0.8, ["Новизна — модель интеграции и механизм контрольных точек",
                            "Значимость — обоснование решения расчетом"], 13, False, GREY, PP_ALIGN.CENTER)

# ================================ резервные слайды для ответов на вопросы
s = new_slide(16, "Резерв. Устройство установки")
pic(s, CH2 + "f06.png", 0.4, 1.12, 3.1, 3.3)
pic(s, CH2 + "f11.png", 3.7, 1.12, 5.9, 3.3)
cap(s, 0.4, 4.46, 3.1, "Принципиальная схема СПУ ПГ-018")
cap(s, 3.7, 4.46, 5.9, "Сборочный чертеж вентилятора высокого давления")
s = new_slide(17, "Резерв. Исходы переделок")
pic(s, "s/f37_outcomes.png", 0.4, 1.12, 9.2, 3.3)
cap(s, 0.4, 4.46, 9.2, "Остаток преимущества интеграции в исходах переделок")
s = new_slide(18, "Резерв. Диапазоны ЧДД и влияние параметров")
pic(s, "s/f39_risk.png", 0.4, 1.12, 9.2, 3.3)
cap(s, 0.4, 4.46, 9.2, "Диапазон ЧДД от P10 до P90 (а) и влияние параметров на разность TRL5 и TRL6 (б)")
s = new_slide(19, "Резерв. Область предпочтения сценариев")
pic(s, "s/f38_threshold.png", 0.4, 1.12, 9.2, 3.3)
cap(s, 0.4, 4.46, 9.2, "Выбор между Интеграцией TRL5 и Интеграцией TRL6 по вероятности и ущербу")
s = new_slide(20, "Резерв. Программа расчета модели")
pic(s, "app_screen2s.jpg", 0.4, 1.12, 9.2, 3.3)
cap(s, 0.4, 4.46, 9.2, "Браузерная программа, расчет повторяется на данных конкретного проекта")

prs.save(OUT)


def shrink(path, limit=250000, colors=192, maxw=1920):
    """Пережатие крупных растровых вложений, чтобы файл проходил по размеру."""
    import zipfile, io, shutil, os
    from PIL import Image
    tmp = path + ".tmp"
    zin = zipfile.ZipFile(path)
    zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data = zin.read(it.filename)
        if it.filename.startswith("ppt/media/") and it.filename.endswith(".png") and len(data) > limit:
            im = Image.open(io.BytesIO(data)).convert("RGB")
            if im.width > maxw:
                im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
            buf = io.BytesIO()
            im.convert("P", palette=Image.ADAPTIVE, colors=colors).save(buf, format="PNG", optimize=True)
            if buf.tell() < len(data):
                data = buf.getvalue()
        zout.writestr(it, data)
    zout.close(); zin.close()
    shutil.move(tmp, path)
    return os.path.getsize(path)


sz = shrink(OUT)
print("слайдов:", len(prs.slides), "| размер, КБ:", round(sz / 1024), "| сохранено:", OUT)

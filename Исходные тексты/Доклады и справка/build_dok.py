# -*- coding: utf-8 -*-
"""Сборка доклада к защите из doklad.txt."""
import io, re, subprocess, os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

SRC = "/home/claude/work/dokl/doklad.txt"
OUT = "/home/claude/work/dokl/Доклад к защите.docx"
WPM = 125.0
NAMES = {1: "Титульный лист работы", 2: "Тема, слушатель, руководитель",
         3: "Актуальность", 4: "Цель и задачи", 5: "Нормативная база и практика",
         6: "Объект и установка СПУ ПГ-018", 7: "Инновационные технические решения",
         8: "Последовательность реализации и SWOT-анализ",
         9: "Предлагаемый механизм интеграции", 10: "Четыре сценария и календарный план",
         11: "Результат расчета", 12: "Чувствительность и доля инноваций",
         13: "Имитационное моделирование", 14: "Наши рекомендации",
         15: "Спасибо за внимание"}
SECT = {3: "Введение", 5: "Результаты исследования", 9: "Предложения и расчет", 14: "Рекомендации"}

t = io.open(SRC, encoding="utf-8").read().replace(" ", " ")
blocks = []
for b in re.split(r"\n\s*\n", t.strip()):
    m = re.match(r"\[(\d+)[^\]]*\]\s*(.*)", b, re.S)
    blocks.append((int(m.group(1)), " ".join(m.group(2).split())))

total = sum(len(x[1].split()) for x in blocks)
mmss = lambda sec: "%d:%02d" % (int(sec) // 60, int(sec) % 60)

d = Document()
s = d.sections[0]
s.left_margin, s.right_margin, s.top_margin, s.bottom_margin = Cm(3), Cm(1.5), Cm(2), Cm(2)
st = d.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(14)
st.paragraph_format.line_spacing = 1.5
st.paragraph_format.space_after = Pt(0)


def par(text, size=None, bold=False, align=None, before=0, after=0):
    p = d.add_paragraph()
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    if size:
        r.font.size = Pt(size)
    r.bold = bold
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    return p


par("Доклад к защите дипломного проекта", 16, True, WD_ALIGN_PARAGRAPH.CENTER, 0, 6)
par("Модель управления внедрением инновационных решений при реализации инвестиционного "
    "проекта строительства отраслевого метрологического центра расходометрии ПАО «Газпром»",
    None, False, WD_ALIGN_PARAGRAPH.CENTER, 0, 10)
par("Объем текста %d слов, продолжительность %d минут при темпе %d слов в минуту. "
    "Презентация 20 слайдов, из них 15 основных и 5 резервных для ответов на вопросы. "
    "Доклад построен как сжатое введение и развернутое заключение "
    "с акцентом на выводах и предложениях. Номер слайда и отметка времени указаны перед "
    "каждым блоком." % (total, round(total / WPM), WPM), None, False, None, 0, 12)

acc = 0.0
rows = []
for num, txt in blocks:
    if num in SECT:
        par(SECT[num], 14, True, WD_ALIGN_PARAGRAPH.LEFT, 12, 4)
    par("Слайд %d. %s   (%s)" % (num, NAMES[num], mmss(acc)), 13, True,
        WD_ALIGN_PARAGRAPH.LEFT, 10, 2)
    par(txt)
    w = len(txt.split())
    rows.append((num, NAMES[num], w, mmss(w / WPM * 60)))
    acc += w / WPM * 60

par("Хронометраж по слайдам", 14, True, WD_ALIGN_PARAGRAPH.LEFT, 14, 6)
tb = d.add_table(rows=len(rows) + 2, cols=4)
tb.style = "Table Grid"
hd = ["Слайд", "Содержание", "Слов", "Длительность"]
for j, h in enumerate(hd):
    c = tb.cell(0, j).paragraphs[0]
    r = c.add_run(h); r.bold = True; r.font.size = Pt(12); r.font.name = "Times New Roman"
    c.paragraph_format.line_spacing = 1.0
for i, (num, name, w, dur) in enumerate(rows, start=1):
    for j, v in enumerate((str(num), name, str(w), dur)):
        c = tb.cell(i, j).paragraphs[0]
        r = c.add_run(v); r.font.size = Pt(12); r.font.name = "Times New Roman"
        c.paragraph_format.line_spacing = 1.0
for j, v in enumerate(("Итого", "", str(total), mmss(total / WPM * 60))):
    c = tb.cell(len(rows) + 1, j).paragraphs[0]
    r = c.add_run(v); r.bold = True; r.font.size = Pt(12); r.font.name = "Times New Roman"
    c.paragraph_format.line_spacing = 1.0
for col, wd in zip(tb.columns, (1.8, 9.0, 2.0, 3.2)):
    for cell in col.cells:
        cell.width = Cm(wd)

d.save(OUT)
print("слов", total, "длительность", mmss(total / WPM * 60))
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir",
                os.path.dirname(OUT), OUT], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("готово")

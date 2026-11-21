# -*- coding: utf-8 -*-
"""Доклад к защите, промежуточная редакция по согласованным слайдам."""
import io, re, os, subprocess
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

SRC = "/home/claude/work/pres2/doklad.txt"
OUT = "/home/claude/work/pres2/Доклад к защите.docx"
NAVY = RGBColor(0, 0x33, 0x66)

TITLES = {1: "Слайд 1. Тема работы и слушатель",
          2: "Слайд 2. Актуальность",
          3: "Слайд 3. Цель и задачи",
          4: "Слайд 4. Нормативная и методическая база",
          5: "Слайд 5. Результат анализа",
          6: "Слайд 6. Прототип реализации механизма",
          7: "Слайд 7. Реализованные инновационные решения",
          8: "Слайд 8. Последовательность реализации проекта-прототипа",
          9: "Слайд 9. SWOT-анализ организации работ",
          10: "Слайд 10. Разработка механизма интеграции",
          11: "Слайд 11. Экономическая модель интеграции. Структура",
          12: "Слайд 12. Экономическая модель. Входные параметры",
          13: "Слайд 13. Риск и имитационное моделирование",
          14: "Слайд 14. Календарный план сценариев интеграции",
          15: "Слайд 15. Результаты моделирования сценарных условий",
          16: "Слайд 16. Проверка устойчивости результата моделирования",
          17: "Слайд 17. Профиль риска и распределение ЧДД",
          18: "Слайд 18. Процесс принятия решения об интеграции",
          19: "Слайд 19. Программная реализация расчетной модели",
          20: "Слайд 20. Выводы",
          21: "Слайд 21. Спасибо за внимание"}

BLOCKS = {}
for b in re.split(r"\n\s*\n", io.open(SRC, encoding="utf-8").read().strip()):
    m = re.match(r"\[(\d+)\]\s*(.*)", b, re.S)
    BLOCKS[int(m.group(1))] = " ".join(m.group(2).split())

d = Document()
st = d.styles["Normal"]
st.font.name = "Times New Roman"; st.font.size = Pt(14)
st.paragraph_format.line_spacing = 1.5
st.paragraph_format.space_after = Pt(0)
sec = d.sections[0]
sec.left_margin, sec.right_margin = Cm(3), Cm(1.5)
sec.top_margin, sec.bottom_margin = Cm(2), Cm(2)


def par(text, size=14, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
        before=0, after=0, indent=1.25, color=None, italic=False):
    p = d.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before, pf.space_after = Pt(before), Pt(after)
    pf.first_line_indent = Cm(indent)
    r = p.add_run(text)
    r.font.size, r.font.bold, r.font.italic = Pt(size), bold, italic
    if color is not None:
        r.font.color.rgb = color
    return p


par("Доклад к защите дипломного проекта", 16, True, WD_ALIGN_PARAGRAPH.CENTER, 0, 6, 0, NAVY)
par("Редакция от 15 ноября 2026 года", 12, False,
    WD_ALIGN_PARAGRAPH.CENTER, 0, 14, 0, NAVY, True)

WORDS = 0
for n in sorted(BLOCKS):
    par(TITLES[n], 14, True, WD_ALIGN_PARAGRAPH.LEFT, 12, 4, 0, NAVY)
    par(BLOCKS[n])
    WORDS += len(BLOCKS[n].split())

par("Справочная информация (на слайд не выносится, произносится только при вопросах)",
    14, True, WD_ALIGN_PARAGRAPH.LEFT, 16, 4, 0, NAVY)
par("Для целей исследования инновационным решением считается новое или существенно "
    "усовершенствованное для рассматриваемого применения техническое либо технологическое "
    "решение, внедрение которого требует подтверждения характеристик и согласования "
    "с проектируемым объектом. Это рабочее определение задает границы анализа.")
par("Под механизмом интеграции понимается совокупность правил планирования, распределения "
    "ответственности, обмена исходными данными, подтверждения готовности и принятия решений, "
    "согласующих разработку технологии с проектированием и строительством. Технологическая "
    "готовность показывает, насколько работоспособность решения подтверждена в заданных "
    "условиях. Готовность проектной документации и инженерной инфраструктуры характеризует "
    "возможность выполнения соответствующих работ на объекте. Технологическая готовность "
    "оборудования, готовность проектной документации и готовность инженерной инфраструктуры "
    "взаимосвязаны, но не подменяют друг друга.")

mins = WORDS / 135.0
par("Объем произносимого текста %d слов, ориентировочное время %d мин %02d с "
    "при темпе 135 слов в минуту." % (WORDS, int(mins), round((mins - int(mins)) * 60)),
    12, False, WD_ALIGN_PARAGRAPH.LEFT, 16, 0, 0, NAVY, True)

d.save(OUT)
print("слов", WORDS, "| минут", round(mins, 1))
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir",
                os.path.dirname(OUT), OUT], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("готово")

# служебные свойства: автор и разработчик
import subprocess as _sp, sys as _sys
_sp.call([_sys.executable, "/home/claude/work/setauthor.py", OUT,
          OUT[:-5] + ".pdf"])

# -*- coding: utf-8 -*-
"""Склейка итогового PDF из посекционных файлов (глава 3 — версия с формулами-рисунками)."""
import pikepdf, os

FILES = "/home/claude/work/final/files2/"
ORDER = ["00 Титульный лист, содержание, введение.pdf", "01 Глава 1.pdf", "02 Глава 2.pdf",
         "03 Глава 3.pdf", "04 Выводы.pdf", "05 Список литературы.pdf", "06 Приложения.pdf"]
OUT = FILES + "Дипломный проект (полный текст).pdf"

out = pikepdf.Pdf.new()
for f in ORDER:
    p = FILES + f
    if not os.path.exists(p):
        raise SystemExit("нет файла: " + f)
    with pikepdf.open(p) as src:
        out.pages.extend(src.pages)
    print("%-48s %4d стр." % (f, len(pikepdf.open(p).pages)))
with out.open_metadata(update_docinfo=True) as m:
    m["dc:title"] = "Дипломный проект"
    m["dc:creator"] = ["Postautov_K_V"]
out.docinfo["/Author"] = "Postautov_K_V"
out.save(OUT)
print("итого", len(out.pages), "страниц ->", OUT)

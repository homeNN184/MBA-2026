# -*- coding: utf-8 -*-
import sys, re
from fmtlib import *
for src, out in (("/home/claude/work/ch3/full.docx", "build/ch3.docx"), ("/home/claude/work/ch3/full_pdf.docx", "build/ch3_pdfver.docx")):
    d = Document(src)
    n = 0
    for t in d.tables:
        last = t.rows[0].cells[-1].text.strip()
        if len(t.columns) == 2 and re.match(r"^\(\d+\)$", last): continue
        fix_table(t, 16.5, 11.0); n += 1
    style_headings(d)
    yo_doc(d)
    d.save(out); print(out, "tables fixed", n)

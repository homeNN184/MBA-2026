# -*- coding: utf-8 -*-
import re, copy, sys
from fmtlib import *
import biblio
OUT = sys.argv[1]
d = Document("/tmp/att/ch1.docx")
P = d.paragraphs
# --- список литературы: удалить (выносится в отдельный файл)
st = [i for i, p in enumerate(P) if p.text.strip().upper().startswith("СПИСОК ЛИТЕРАТУРЫ")][0]
for p in P[st:]: p._p.getparent().remove(p._p)
P = d.paragraphs
# --- ссылки [n; m] -> новые номера
mp = biblio.ch1_map()
def sub_ref(m):
    nums = sorted(mp[int(x)] for x in re.split(r";\s*", m.group(1)))
    return "[" + ", ".join(map(str, nums)) + "]"
cnt = 0
for p in P:
    for r in p.runs:
        if "[" in r.text:
            new = re.sub(r"\[(\d+(?:;\s*\d+)*)\]", sub_ref, r.text)
            if new != r.text: cnt += 1; r.text = new
print("ссылок заменено в runs:", cnt)
# --- заголовки
def set_text(p, text):
    runs = p.runs
    runs[0].text = text
    for r in runs[1:]: r.text = ""
for i, p in enumerate(P):
    if p.style.name == "Title":
        t = p.text.strip()
        t = re.sub(r"^1\.\s*", "", t)
        t = t[0] + t[1:].lower()
        set_text(p, "Глава 1. " + t); p.style = d.styles["Heading 1"]
    elif p.style.name == "Heading 1":
        t = p.text.strip()
        m = re.match(r"^(1\.\d+)\.?\s+(.*)$", t)
        set_text(p, f"{m.group(1)} {m.group(2)}"); p.style = d.styles["Heading 2"]
# --- подпись таблицы
for p in d.paragraphs:
    m = re.match(r"^Таблица 1\.1\.\s*(.*)$", p.text.strip())
    if m:
        title = m.group(1)
        # номер
        set_text(p, "Таблица 1.1")
        for r in p.runs: pass
        para_fmt(p, AL.RIGHT, Cm(0), Cm(0), 1.0, 6, 0, True)
        for r in p._p.iter(W + "r"): fix_run(r, 12, False)
        newp = copy.deepcopy(p._p); p._p.addnext(newp)
        q = Paragraph(newp, p._parent)
        set_text(q, title); para_fmt(q, AL.CENTER, Cm(0), Cm(0), 1.0, 0, 4, True)
        for r in q._p.iter(W + "r"): fix_run(r, 12, False)
        break
# --- шрифт основного текста (Normal) и абзацы
for p in d.paragraphs:
    if p.style.name in ("Normal",) and not p.text.startswith(("Таблица", )) and p.paragraph_format.alignment != AL.RIGHT:
        pass
style_headings(d)
# --- таблицы
for t in d.tables:
    print("table ch1:", fix_table(t, 16.5, 10.5))
# --- нумерация таблиц
bad = renumber_doc(d, {"1.1": 1}, {})
print("renumber issues:", bad)
print("yo:", yo_doc(d))
d.save(OUT)

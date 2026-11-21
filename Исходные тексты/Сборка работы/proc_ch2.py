# -*- coding: utf-8 -*-
import re, sys
from fmtlib import *
import biblio
OUT = sys.argv[1]
d = Document("/home/claude/work/out/Глава 2 (редакция 3).docx")
body = d.element.body
# 1. список источников главы — удалить (общий список — отдельным файлом)
st = [i for i, p in enumerate(d.paragraphs) if p.text.startswith("Список использованных источников")][0]
for p in d.paragraphs[st:]: p._p.getparent().remove(p._p)
# 2. сноски -> [n]
fp = [r.target_part for r in d.part.rels.values() if r.reltype.endswith("/footnotes")][0]
n_rep = 0
for ref in list(body.iter(W + "footnoteReference")):
    fid = ref.get(W + "id"); keys = biblio.CH2_FN[fid]
    txt = biblio.cite(*keys)
    run = ref.getparent()
    prev = run.getprevious()
    nxt = run.getnext()
    # предыдущий текст
    pt = None
    while prev is not None and pt is None:
        ts = prev.findall(W + "t")
        if ts: pt = ts[-1]
        else: prev = prev.getprevious()
    nt = None
    if nxt is not None and nxt.findall(W + "t"): nt = nxt.findall(W + "t")[0]
    add = " " + txt
    if pt is not None and pt.text and pt.text.rstrip().endswith(".") and not (nt is not None and nt.text and nt.text.startswith(".")):
        pt.text = pt.text.rstrip()[:-1]; add += "."
    t = etree.SubElement(run, W + "t"); t.text = add; t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    # убрать признак сноски/надстрочность
    rpr = run.find(W + "rPr")
    if rpr is not None:
        run.remove(rpr)
    run.remove(ref); n_rep += 1
print("сносок заменено:", n_rep)
froot = etree.fromstring(fp.blob)
for f in list(froot):
    if f.get(W + "type") not in ("separator", "continuationSeparator", "continuationNotice"): froot.remove(f)
fp._blob = etree.tostring(froot, xml_declaration=True, encoding="UTF-8", standalone=True)
# 3. таблицы
for i, t in enumerate(d.tables):
    ncol = len(t._tbl.find(qn("w:tblGrid")).findall(qn("w:gridCol")))
    print("table", i + 1, "cols", ncol, fix_table(t, 16.5, 10.0))
# 4. нумерация
tmap = {f"2.{n}": n + 1 for n in range(1, 6)}
fmap = {f"2.{n}": n for n in range(1, 13)}
print("renumber issues:", renumber_doc(d, tmap, fmap))
style_headings(d)
print("yo:", yo_doc(d))
d.save(OUT)

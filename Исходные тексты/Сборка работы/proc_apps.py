# -*- coding: utf-8 -*-
import os, re, sys
sys.path.insert(0, "/home/claude/work/ch3")
os.chdir("/home/claude/work/ch3")
from docx_util import set_margins
import apps2
from fmtlib import *
OUT = "/home/claude/work/final/build/apps.docx"
doc = Document("raw.docx")
body = doc.element.body
for el in list(body):
    if el.tag != qn("w:sectPr"): body.remove(el)
set_margins(doc.sections[0])
apps2.add_appendices(doc)
# убрать «Перечень приложений к главе 3» и его список (10 строк)
ps = doc.paragraphs
i = [k for k, p in enumerate(ps) if p.text.startswith("Перечень приложений")][0]
for p in ps[i:i + 11]: p._p.getparent().remove(p._p)
# сдвиг номеров
def shift(s):
    s = re.sub(r"Приложения (\d+)–(\d+)", lambda m: f"Приложения {int(m.group(1))+1}–{int(m.group(2))+1}", s)
    s = re.sub(r"Приложение (\d+)", lambda m: f"Приложение {int(m.group(1))+1}", s)
    s = re.sub(r"П(\d+)\.(\d+)", lambda m: f"П{int(m.group(1))+1}.{m.group(2)}", s)
    s = re.sub(r"\(3\.(\d+)\)", r"(\1)", s)
    s = re.sub(r"(формул[а-я]*) 3\.(\d+)", r"\1 (\2)", s)
    return s
for t in body.iter(W + "t"):
    if t.text:
        n = shift(t.text)
        if n != t.text: t.text = n
# Приложение 1 — Дорожная карта (3 страницы, альбомная секция)
first = [p for p in doc.paragraphs if p.text.strip() == "Приложение 2"][0]
from apps import para
from docx.shared import Cm as _Cm
from docx.oxml import OxmlElement as _OE
def mk(text, al, bold, after=0):
    p = para(doc, text, 14, al, 0, bold=bold, line=1.0, keep=True, after=after)
    first._p.addprevious(p._p)
    return p
mk("Приложение 1", AL.RIGHT, True, 6)
mk("Дорожная карта на период 2019–2024 годы по созданию Государственного первичного специального эталона расхода природного газа высокого давления", AL.CENTER, True, 10)
def _fit(fn, bw, bh):
    from PIL import Image as _I
    w, h = _I.open("/home/claude/work/ap1/" + fn).size
    if w / h > bw / bh: return {"width": _Cm(bw)}
    return {"height": _Cm(bh)}
for k, f in enumerate(["rmh-1c.png", "rmh-2c.png", "rmh-3c.png"]):
    ip = doc.add_paragraph(); ip.alignment = AL.CENTER
    ip.paragraph_format.first_line_indent = _Cm(0); ip.paragraph_format.space_after = Pt(0)
    ip.paragraph_format.line_spacing = 1.0
    if k: ip.paragraph_format.page_break_before = True
    ip.add_run().add_picture("/home/claude/work/ap1/" + f, **_fit(f, 26.6, 16.0 if k == 0 else 18.3))
    first._p.addprevious(ip._p)
# конец альбомной секции приложения 1
sp = _OE("w:sectPr")
ps_ = _OE("w:pgSz"); ps_.set(qn("w:w"), "16838"); ps_.set(qn("w:h"), "11906"); ps_.set(qn("w:orient"), "landscape"); sp.append(ps_)
pm = _OE("w:pgMar")
for k_, v_ in (("top", "567"), ("right", "567"), ("bottom", "794"), ("left", "850"), ("header", "284"), ("footer", "284"), ("gutter", "0")): pm.set(qn("w:" + k_), v_)
sp.append(pm)
sp_par = _OE("w:p"); sp_ppr = _OE("w:pPr"); sp_ppr.append(sp); sp_par.append(sp_ppr)
first._p.addprevious(sp_par)
# «Приложение 2» начинается с новой страницы (новая секция)
# первый абзац файла не должен начинаться с разрыва страницы — снять у «Приложение 1»
# таблицы: ширина по ширине страницы в своей секции
secs = []
for sp in body.iter(qn("w:sectPr")):
    sz = sp.find(qn("w:pgSz")); mg = sp.find(qn("w:pgMar"))
    wd = (int(sz.get(qn("w:w"))) - int(mg.get(qn("w:left"))) - int(mg.get(qn("w:right")))) / 1440 * 2.54
    secs.append(wd)
si = 0; n = 0
for ch in list(body):
    if ch.tag == qn("w:tbl"):
        from docx.table import Table
        fix_table(Table(ch, doc), round(secs[min(si, len(secs) - 1)], 2), 8.5); n += 1
    elif ch.tag == qn("w:p") and ch.find(qn("w:pPr")) is not None and ch.find(qn("w:pPr")).find(qn("w:sectPr")) is not None:
        si += 1
print("sections", [round(x, 1) for x in secs], "tables", n)
yo_doc(doc)
doc.save(OUT)
# заголовки приложений
res = []
ps = doc.paragraphs
for k, p in enumerate(ps):
    if re.match(r"^Приложение \d+$", p.text.strip()): res.append((p.text.strip(), ps[k + 1].text.strip()))
import json; json.dump(res, open("/home/claude/work/final/build/app_titles.json", "w"), ensure_ascii=False, indent=1)
print(res)

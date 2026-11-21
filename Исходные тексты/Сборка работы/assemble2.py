# -*- coding: utf-8 -*-
"""Сборка итоговых файлов из base.docx (Введение, Главы 1–2), новой Главы 3, литературы и приложений."""
import os, re, sys, json, copy, shutil, subprocess
sys.path.insert(0, "/home/claude/work/final")
sys.path.insert(0, "/home/claude/work/ch3")
from fmtlib import *
import biblio
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.shared import RGBColor

B2 = "/home/claude/work/final/build2"
FILES = "/home/claude/work/final/files2/"
os.makedirs(B2, exist_ok=True)
os.makedirs(FILES, exist_ok=True)
BASE = "/home/claude/work/v2/base.docx"
FIN = {"front": "00 Титульный лист, содержание, введение", "ch1": "01 Глава 1", "ch2": "02 Глава 2",
       "ch3": "03 Глава 3", "concl": "04 Выводы", "bib": "05 Список литературы", "apps": "06 Приложения"}


def q(t):
    return qn("w:" + t)


def pdf_of(docx, outdir=None):
    outdir = outdir or os.path.dirname(docx)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, docx], capture_output=True)
    return os.path.join(outdir, os.path.splitext(os.path.basename(docx))[0] + ".pdf")


def pages_text(pdf):
    out = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    return out.split("\f")[:-1]


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower().replace("ё", "е")


def find_heading(pages, text, after=0):
    key = norm(text)[:28]
    for i, pg in enumerate(pages[after:], after):
        if key in norm(pg):
            return i + 1
    return None


# ---------------- 1. нарезка base.docx ----------------
def drop_unused_rels(doc):
    xml = etree.tostring(doc.element).decode()
    for rid, rel in list(doc.part.rels.items()):
        if rel.reltype == RT.IMAGE and f'"{rid}"' not in xml:
            doc.part.drop_rel(rid)


def slice_parts():
    base = Document(BASE)
    kids = [c for c in base.element.body if c.tag != q("sectPr")]
    groups, cur = [], []
    for c in kids:
        cur.append(c)
        if c.tag == q("p") and c.find(q("pPr")) is not None and c.find(q("pPr")).find(q("sectPr")) is not None:
            groups.append(cur)
            cur = []
    groups.append(cur)
    assert len(groups) >= 6, len(groups)
    names = {0: "front", 1: "ch1", 2: "ch2", 4: "bib_old"}
    out = {}
    for gi, nm in names.items():
        d = Document(BASE)
        body = d.element.body
        for c in list(body):
            if c.tag != q("sectPr"):
                body.remove(c)
        sp_final = body.find(q("sectPr"))
        g = groups[gi]
        last = g[-1]
        sp = last.find(q("pPr")).find(q("sectPr"))
        new_sp = copy.deepcopy(sp)
        for c in g:
            body.insert(len(body) - 1, copy.deepcopy(c)) if False else sp_final.addprevious(copy.deepcopy(c))
        # убрать sectPr из последнего абзаца среза и сделать итоговым
        lp = [c for c in body if c.tag != q("sectPr")][-1]
        lp.find(q("pPr")).remove(lp.find(q("pPr")).find(q("sectPr")))
        body.remove(sp_final)
        body.append(new_sp)
        drop_unused_rels(d)
        path = f"{B2}/{nm}.docx"
        d.save(path)
        out[nm] = path
    return out


# ---------------- 2. ссылки: перенумерация по первому упоминанию ----------------
CIT = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)((?:,\s*[^\]\d][^\]]*)?)\]")


def para_ts(p):
    return [t for t in p.iter(W + "t")]


def collect_order(docs):
    order = []
    for d in docs:
        for p in d.element.body.iter(W + "p"):
            full = "".join(t.text or "" for t in para_ts(p))
            for m in CIT.finditer(full):
                for n in re.split(r"\s*,\s*", m.group(1)):
                    n = int(n)
                    if n not in order:
                        order.append(n)
    return order


def apply_map(doc, mp):
    k = 0
    for p in doc.element.body.iter(W + "p"):
        ts = para_ts(p)
        if not ts:
            continue
        texts = [t.text or "" for t in ts]
        full = "".join(texts)
        ms = list(CIT.finditer(full))
        if not ms:
            continue
        # границы t
        bounds, pos = [], 0
        for s in texts:
            bounds.append((pos, pos + len(s)))
            pos += len(s)
        for m in reversed(ms):
            nums = sorted(mp[int(n)] for n in re.split(r"\s*,\s*", m.group(1)))
            new = "[" + ", ".join(map(str, nums)) + m.group(2) + "]"
            a, b = m.span()
            # заменить: первый затронутый t получает новый текст, остальные теряют часть
            first = True
            for i, (s0, s1) in enumerate(bounds):
                if s1 <= a or s0 >= b:
                    continue
                t = ts[i]
                tx = t.text or ""
                la, lb = max(a, s0) - s0, min(b, s1) - s0
                if first:
                    t.text = tx[:la] + new + tx[lb:]
                    first = False
                else:
                    t.text = tx[:la] + tx[lb:]
                t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            k += 1
    return k


# ---------------- 3. список литературы ----------------
OLD = dict(biblio.LIST)
OLD[84] = OLD[84]


def make_bib(path, items):
    from docx_util import set_margins
    d = Document()
    s = d.sections[0]
    set_margins(s)
    st = d.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(14)
    h = d.add_paragraph("Список литературы")
    h.style = d.styles["Heading 1"]
    for _r in h.runs:
        _r.font.color.rgb = RGBColor(0, 0, 0)
    for n, t in items:
        p = d.add_paragraph(f"{n}. {t}")
        para_fmt(p, AL.JUSTIFY, Cm(1.25), Cm(0), 1.5, 0, 0)
        for r in p._p.iter(W + "r"):
            fix_run(r, 14, False)
    style_headings(d)
    yo_doc(d)
    d.save(path)


def make_concl(path, src_txt="/home/claude/work/final/concl.txt"):
    """Раздел «Выводы» из текстового источника, оформление как у остальных разделов."""
    from docx_util import set_margins
    d = Document()
    s = d.sections[0]
    set_margins(s)
    st = d.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(14)
    h = d.add_paragraph("Выводы")
    h.style = d.styles["Heading 1"]
    for _r in h.runs:
        _r.font.color.rgb = RGBColor(0, 0, 0)
    text = open(src_txt, encoding="utf-8").read()
    for block in [b.strip() for b in text.split("\n\n") if b.strip()]:
        p = d.add_paragraph(" ".join(block.split()))
        para_fmt(p, AL.JUSTIFY, Cm(0), Cm(0), 1.5, 0, 0)
        p.paragraph_format.first_line_indent = Cm(1.25)
        for r in p._p.iter(W + "r"):
            fix_run(r, 14, False)
    style_headings(d)
    yo_doc(d)
    d.save(path)


# ---------------- 4. титул + оглавление ----------------
def make_front(src, path, toc):
    d = Document(src)
    for t_ in d.tables:
        for r_ in t_.rows:
            for c_ in r_.cells:
                for p_ in c_.paragraphs:
                    if "/Подпись/" in p_.text:
                        _full = p_.text.replace("/Подпись/", "")
                        for _i, run_ in enumerate(p_.runs):
                            run_.text = _full if _i == 0 else ""
    P = d.paragraphs
    i0 = [i for i, p in enumerate(P) if p.text.strip() == "Содержание"][0]
    i1 = [i for i, p in enumerate(P) if i > i0 and p.text.strip() == "Введение"][0]
    tmpl = {0: None, 1: None}
    for p in P[i0 + 1:i1]:
        lv = 1 if (p.paragraph_format.left_indent or 0) > 0 else 0
        if tmpl[lv] is None:
            tmpl[lv] = copy.deepcopy(p._p)
    for p in P[i0 + 1:i1]:
        p._p.getparent().remove(p._p)
    anchor = P[i1]._p
    for lvl, text, page in toc:
        ne = copy.deepcopy(tmpl[lvl])
        for ch in list(ne):
            if ch.tag != q("pPr"):
                ne.remove(ch)
        ppr = ne.find(q("pPr"))
        tabs = ppr.find(q("tabs"))
        if tabs is not None:
            for tb in tabs:
                tb.set(q("leader"), "dot")
        ne.append(OxmlElement("w:r"))
        r = ne[-1]
        rpr = OxmlElement("w:rPr")
        rf = OxmlElement("w:rFonts")
        for a in ("ascii", "hAnsi", "cs", "eastAsia"):
            rf.set(qn("w:" + a), FONT)
        rpr.append(rf)
        bold = lvl == 0 and text.startswith("Глава")
        b = OxmlElement("w:b")
        b.set(qn("w:val"), "1" if bold else "0")
        rpr.append(b)
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), "28")
        rpr.append(sz)
        r.append(rpr)
        t1 = OxmlElement("w:t")
        t1.text = text
        t1.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        r.append(t1)
        r.append(OxmlElement("w:tab"))
        t2 = OxmlElement("w:t")
        t2.text = str(page)
        r.append(t2)
        anchor.addprevious(ne)
    yo_doc(d)
    d.save(path)


def headings_of(path, kind):
    out = []
    d = Document(path)
    for p in d.paragraphs:
        tx = p.text.strip()
        sn = p.style.name
        if kind == "flat":
            bold = any(r.bold for r in p.runs if r.text.strip())
            if not bold or len(tx) > 260:
                continue
            if re.match(r"^Глава \d+\.", tx):
                out.append((0, tx))
            elif re.match(r"^\d+\.\d+ ", tx):
                out.append((1, tx))
            elif re.match(r"^Выводы по главе \d+$", tx):
                out.append((1, tx))
        else:
            if sn == "Heading 1":
                out.append((0 if tx.startswith("Глава") else 1, tx))
            elif sn == "Heading 2":
                out.append((1, tx))
    return out


def build():
    # 1. срезы
    sl = slice_parts()
    # 2. Глава 3 и приложения (внешние конвейеры)
    subprocess.run(["bash", "/home/claude/work/ch3/rebuild.sh"], check=True, capture_output=True)
    os.chdir("/home/claude/work/final")
    subprocess.run([sys.executable, "proc_ch3.py"], check=True, capture_output=True)
    subprocess.run([sys.executable, "proc_apps.py"], check=True, capture_output=True)
    shutil.copy("build/ch3.docx", f"{B2}/ch3.docx")
    shutil.copy("build/ch3_pdfver.docx", f"{B2}/ch3_pdfver.docx")
    shutil.copy("build/apps.docx", f"{B2}/apps.docx")
    shutil.copy("build/app_titles.json", f"{B2}/app_titles.json")
    paths = {"front": sl["front"], "ch1": sl["ch1"], "ch2": sl["ch2"], "ch3": f"{B2}/ch3.docx", "ch3pdf": f"{B2}/ch3_pdfver.docx", "apps": f"{B2}/apps.docx"}
    # 3. ссылки
    docs = {k: Document(v) for k, v in paths.items()}
    # номера в base.docx (введение, главы 1-2) даны по списку до добавления источников ADDED_AFTER_BASE;
    # приводим их к текущей нумерации biblio.NUM (глава 3 и приложения уже в ней)
    import ch12_refs
    _shift = {n: biblio.NUM[k] for n, k in ch12_refs.MAP.items()}
    for _k in ("front", "ch1", "ch2"):
        apply_map(docs[_k], _shift)
    order = collect_order([docs[k] for k in ("front", "ch1", "ch2", "ch3", "apps")])
    mp = {old: i + 1 for i, old in enumerate(order)}
    missing = [n for n in order if n not in OLD]
    print("цитируется источников:", len(order), "нет в списке:", missing)
    unused = sorted(set(OLD) - set(order))
    print("не используется (удалено из списка):", unused)
    for k, d in docs.items():
        n = apply_map(d, mp)
        yo_doc(d)
        d.save(paths[k])
        print(k, "ссылок заменено:", n)
    items = [(i + 1, OLD[old]) for i, old in enumerate(order)]
    json.dump({"order": order, "unused": unused, "items": items}, open(f"{B2}/bib.json", "w"), ensure_ascii=False, indent=1)
    paths["concl"] = f"{B2}/concl.docx"
    make_concl(paths["concl"])
    paths["bib"] = f"{B2}/bib.docx"
    make_bib(paths["bib"], items)
    return paths, items


def finalize(paths):
    app_titles = json.load(open(f"{B2}/app_titles.json"))
    cnt, pgs = {}, {}
    toc0 = [(0, "Введение", "0")]
    make_front(paths["front"], f"{B2}/front_t.docx", toc0)
    srcs = {"front": f"{B2}/front_t.docx", "ch1": paths["ch1"], "ch2": paths["ch2"], "ch3": paths["ch3pdf"], "concl": paths["concl"], "bib": paths["bib"], "apps": paths["apps"]}
    for k, src in srcs.items():
        pdf = pdf_of(src)
        pgs[k] = pages_text(pdf)
        cnt[k] = len(pgs[k])
    print("страниц (проход 1):", cnt)
    hs = {"ch1": headings_of(paths["ch1"], "flat"), "ch2": headings_of(paths["ch2"], "flat"), "ch3": headings_of(paths["ch3"], "style")}
    for it in range(5):
        starts = {"front": 1}
        order = ["front", "ch1", "ch2", "ch3", "concl", "bib", "apps"]
        for a, b in zip(order, order[1:]):
            starts[b] = starts[a] + cnt[a]
        toc = []
        fp = pgs["front"]
        ip = [i for i, t in enumerate(fp) if re.search(r"^\s*Введение\s*$", t, re.M) and "Содержание" not in t][0] + 1
        toc.append((0, "Введение", str(ip)))
        for k in ("ch1", "ch2", "ch3"):
            last = 0
            for lvl, t in hs[k]:
                pg = find_heading(pgs[k], t, last)
                if pg is None:
                    print("НЕ НАЙДЕН", t)
                    pg = last + 1
                last = pg - 1
                toc.append((lvl, t, str(starts[k] + pg - 1)))
        toc.append((0, "Выводы", str(starts["concl"])))
        toc.append((0, "Список литературы", str(starts["bib"])))
        for i, pg in enumerate(pgs["apps"], 1):
            m = re.search(r"^\s*Приложение (\d+)\s*$", pg, re.M)
            if m:
                num = m.group(1)
                title = [t for a, t in app_titles if a == f"Приложение {num}"][0]
                toc.append((0, f"Приложение {num}. {title}", str(starts["apps"] + i - 1)))
        make_front(paths["front"], f"{B2}/front_t.docx", toc)
        pdf = pdf_of(f"{B2}/front_t.docx")
        pgs["front"] = pages_text(pdf)
        if len(pgs["front"]) == cnt["front"]:
            break
        cnt["front"] = len(pgs["front"])
    print("начальные страницы:", starts, "строк оглавления:", len(toc))
    # итоговые файлы
    shutil.copy(f"{B2}/front_t.docx", f"{B2}/front_final.docx")
    out = {}
    for k in ("front", "ch1", "ch2", "ch3", "concl", "bib", "apps"):
        src = f"{B2}/front_final.docx" if k == "front" else paths[k]
        d = Document(src)
        if k != "front":
            page_footer(d.sections[0])
            set_page_start(d, starts[k])
        path = f"{FILES}{FIN[k]}.docx"
        d.save(path)
        out[k] = path
        # PDF: для главы 3 — версия с формулами-рисунками
        if k == "ch3":
            d2 = Document(paths["ch3pdf"])
            page_footer(d2.sections[0])
            set_page_start(d2, starts[k])
            tmp = f"{B2}/{FIN[k]} (pdf).docx"
            d2.save(tmp)
            subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", B2, tmp], capture_output=True)
            shutil.copy(f"{B2}/{FIN[k]} (pdf).pdf", f"{FILES}{FIN[k]}.pdf")
        else:
            subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", FILES, path], capture_output=True)
    json.dump({"starts": starts, "toc": toc, "cnt": cnt}, open(f"{B2}/final.json", "w"), ensure_ascii=False)
    return out


if __name__ == "__main__":
    paths, items = build()
    finalize(paths)

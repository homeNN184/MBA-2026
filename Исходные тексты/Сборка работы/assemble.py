# -*- coding: utf-8 -*-
import os, re, sys, json, subprocess, shutil
from fmtlib import *
import biblio, intro
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
B = "/home/claude/work/final/build"; OUTD = "/home/claude/work/final/files"
os.makedirs(OUTD, exist_ok=True)
FIN = {"front": "00 Титульный лист, содержание, введение", "ch1": "01 Глава 1", "ch2": "02 Глава 2", "ch3": "03 Глава 3", "bib": "04 Список литературы", "apps": "05 Приложения"}
def pdf_of(docx, outdir=None):
    outdir = outdir or os.path.dirname(docx)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, docx], capture_output=True)
    return os.path.splitext(docx)[0].replace(os.path.dirname(docx), outdir) + ".pdf"
def pages_text(pdf):
    out = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    return out.split("\f")[:-1]
def norm(s): return re.sub(r"\s+", " ", s).strip().lower().replace("ё", "е")
def find_heading(pages, text, after=0):
    key = norm(text)[:28]
    for i, pg in enumerate(pages[after:], after):
        if key in norm(pg): return i + 1
    return None

# ---------- список литературы ----------
def make_bib(path):
    d = Document(); s = d.sections[0]
    from docx_util import set_margins, set_font
    set_margins(s)
    st = d.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(14)
    h = d.add_paragraph("Список литературы"); h.style = d.styles["Heading 1"]
    for r in h.runs: pass
    for n, t in biblio.LIST:
        p = d.add_paragraph(f"{n}. {t}")
        para_fmt(p, AL.JUSTIFY, Cm(1.25), Cm(0), 1.5, 0, 0)
        for r in p._p.iter(W + "r"): fix_run(r, 14, False)
    style_headings(d)
    d.save(path)

# ---------- титул + содержание + введение ----------
def make_front(path, toc):
    d = Document("/tmp/att/a.docx")
    body = d.element.body
    sect = d.sections[0]
    # разрыв страницы после титула
    def add_p(text="", al=AL.JUSTIFY, bold=False, first=1.25, line=1.5, pb=False, after=0, left=0, tabs=False, right=0, size=14):
        p = d.add_paragraph()
        if text:
            r = p.add_run(text)
        para_fmt(p, al, Cm(first), Cm(left), line, 0, after, None, pb)
        if right: p.paragraph_format.right_indent = Cm(right)
        for r in p._p.iter(W + "r"): fix_run(r, size, bold)
        return p
    h = add_p("Содержание", AL.CENTER, True, 0, 1.5, True, 6)
    for lvl, text, page in toc:
        left = {0: 0, 1: 0.8}[lvl]
        p = d.add_paragraph()
        para_fmt(p, AL.LEFT, Cm(0), Cm(left), 1.15, 0, 3)
        p.paragraph_format.right_indent = Cm(1.0)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(16.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        r = p.add_run(f"{text}\t{page}")
        fix_run(r._r, 14, lvl == 0 and text.startswith("Глава"))
    h = add_p("Введение", AL.CENTER, True, 0, 1.5, True, 12)
    for t in intro.INTRO:
        add_p(t, AL.JUSTIFY, False, 1.25, 1.5)
    # колонтитулы: титул без номера
    sect.different_first_page_header_footer = True
    page_footer(sect)
    yo_doc(d)
    d.save(path)

def build_all():
    # --- исходные документы
    docs = {"ch1": f"{B}/ch1.docx", "ch2": f"{B}/ch2.docx", "ch3": f"{B}/ch3.docx", "ch3pdf": f"{B}/ch3_pdfver.docx", "apps": f"{B}/apps.docx", "bib": f"{B}/bib.docx"}
    make_bib(docs["bib"])
    # --- проход 1: счет страниц
    toc0 = [(0, "Введение", "0")]
    make_front(f"{B}/front.docx", toc0)
    cnt = {}; pgs = {}
    for k in ("front", "ch1", "ch2", "ch3pdf", "bib", "apps"):
        src = f"{B}/front.docx" if k == "front" else docs[k]
        pdf = pdf_of(src); pgs[k] = pages_text(pdf); cnt[k] = len(pgs[k])
    print("pages", cnt)
    return docs, cnt, pgs


def finalize():
    docs, cnt, pgs = build_all()
    heads = {}
    def hs(doc, k, pdfk):
        out = []
        for p in Document(doc).paragraphs:
            if p.style.name in ("Heading 1", "Heading 2"): out.append((1 if p.style.name == "Heading 1" else 2, p.text.strip()))
        return out
    app_titles = json.load(open(f"{B}/app_titles.json"))
    fn = 0
    for it in range(4):
        front_n = cnt["front"]
        starts = {"front": 1, "ch1": front_n + 1}
        starts["ch2"] = starts["ch1"] + cnt["ch1"]; starts["ch3"] = starts["ch2"] + cnt["ch2"]
        starts["bib"] = starts["ch3"] + cnt["ch3pdf"]; starts["apps"] = starts["bib"] + cnt["bib"]
        toc = []
        # введение
        fp = pgs["front"]; ip = [i for i, t in enumerate(fp) if norm(t).startswith("введение")][0] + 1
        toc.append((0, "Введение", str(ip)))
        for k, src, pk in (("ch1", docs["ch1"], "ch1"), ("ch2", docs["ch2"], "ch2"), ("ch3", docs["ch3"], "ch3pdf")):
            last = 0
            for lvl, t in hs(src, k, pk):
                pg = find_heading(pgs[pk], t, last)
                if pg is None: print("НЕ НАЙДЕН", t); pg = last + 1
                last = pg - 1
                toc.append((0 if lvl == 1 else 1, t, str(starts[k] + pg - 1)))
        toc.append((0, "Список литературы", str(starts["bib"])))
        for i, pg in enumerate(pgs["apps"], 1):
            m = re.search(r"^\s*Приложение (\d+)\s*$", pg, re.M)
            if m:
                num = m.group(1); title = [t for a, t in app_titles if a == f"Приложение {num}"][0]
                toc.append((0, f"Приложение {num}. {title}", str(starts["apps"] + i - 1)))
        make_front(f"{B}/front.docx", toc)
        pdf = pdf_of(f"{B}/front.docx"); pgs["front"] = pages_text(pdf)
        if len(pgs["front"]) == cnt["front"]: break
        cnt["front"] = len(pgs["front"])
    print("starts", starts, "toc entries", len(toc))
    # --- финальные файлы
    for k, src in (("front", f"{B}/front.docx"), ("ch1", docs["ch1"]), ("ch2", docs["ch2"]), ("ch3", docs["ch3"]), ("ch3pdf", docs["ch3pdf"]), ("bib", docs["bib"]), ("apps", docs["apps"])):
        d = Document(src)
        kk = "ch3" if k == "ch3pdf" else k
        if k != "front": page_footer(d.sections[0]); set_page_start(d, starts[kk])
        name = FIN[kk] + (" (для PDF)" if k == "ch3pdf" else "")
        path = f"{B}/{name}.docx"; d.save(path)
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", B, path], capture_output=True)
        if k == "ch3pdf":
            shutil.copy(f"{B}/{name}.pdf", f"{OUTD}/{FIN['ch3']}.pdf"); os.remove(path)
        else:
            shutil.copy(path, f"{OUTD}/{name}.docx")
            if k != "ch3": shutil.copy(f"{B}/{name}.pdf", f"{OUTD}/{name}.pdf")
    json.dump({"starts": starts, "toc": toc}, open(f"{B}/final.json", "w"), ensure_ascii=False)

if __name__ == '__main__':
    finalize()

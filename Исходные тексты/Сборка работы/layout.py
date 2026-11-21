# -*- coding: utf-8 -*-
"""Оформительская постобработка глав 1-3: разрывы страниц, заголовки, рисунки.
Смысл и формулировки текста не изменяются; меняются только свойства абзацев и размеры рисунков."""
import glob, os, re, subprocess
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

LINE_PT = 21.0            # шаг строки: 14 пт x 1,5
MIN_LINES = 3             # минимальное число строк текста после заголовка / в начале абзаца на странице
TMP = "/tmp/lay"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
BODY_LIM = 0.925          # граница тела страницы (доля высоты), ниже — нижний колонтитул

RE_SEC = re.compile(r"^\d+\.\d+\s")
RE_SUB = re.compile(r"^\d+\.\d+\.\d+\s")


def ptext(p):
    return "".join(t.text or "" for t in p.iter(W + "t"))


def norm(s):
    return re.sub(r"[^0-9a-zа-я]", "", s.lower())


def is_bold_para(p):
    runs = [r for r in p.iter(W + "r") if "".join(t.text or "" for t in r.iter(W + "t")).strip()]
    if not runs:
        return False
    for r in runs:
        rp = r.find(W + "rPr")
        b = rp.find(W + "b") if rp is not None else None
        if b is None or b.get(W + "val") in ("0", "false"):
            return False
    return True


def style_of(p):
    ppr = p.find(W + "pPr")
    st = ppr.find(W + "pStyle") if ppr is not None else None
    return st.get(W + "val") if st is not None else ""


def heading_kind(p):
    """'chap' | 'sec' | 'sub' | None"""
    if p.tag != W + "p":
        return None
    tx = ptext(p).strip()
    if not tx or len(tx) > 260:
        return None
    if not (style_of(p).startswith("Heading") or is_bold_para(p)):
        return None
    if re.match(r"^Глава \d+\.", tx):
        return "chap"
    if tx.startswith("Выводы по главе"):
        return "sub"
    if RE_SUB.match(tx):
        return "sub"
    if RE_SEC.match(tx):
        return "sec"
    return None


def _ppr(p):
    ppr = p.find(W + "pPr")
    if ppr is None:
        ppr = OxmlElement("w:pPr")
        p.insert(0, ppr)
    return ppr


def set_pb(p, val=True):
    ppr = _ppr(p)
    for e in ppr.findall(W + "pageBreakBefore"):
        ppr.remove(e)
    e = OxmlElement("w:pageBreakBefore")
    e.set(qn("w:val"), "1" if val else "0")
    anchor = None
    for tag in ("keepLines", "keepNext", "pStyle"):
        a = ppr.find(W + tag)
        if a is not None:
            anchor = a
            break
    if anchor is not None:
        anchor.addnext(e)
    else:
        ppr.insert(0, e)


def has_pb(p):
    ppr = p.find(W + "pPr")
    e = ppr.find(W + "pageBreakBefore") if ppr is not None else None
    return e is not None and e.get(W + "val") not in ("0", "false")


def set_keepnext(p):
    ppr = _ppr(p)
    if ppr.find(W + "keepNext") is None:
        e = OxmlElement("w:keepNext")
        st = ppr.find(W + "pStyle")
        if st is not None:
            st.addnext(e)
        else:
            ppr.insert(0, e)


def body_items(doc):
    return list(doc.element.body)


# ---------- размеры рисунков ----------
def scale_drawing(p, width_emu):
    for ext in p.iter(WP + "extent"):
        cx, cy = int(ext.get("cx")), int(ext.get("cy"))
        k = width_emu / cx
        ext.set("cx", str(int(cx * k))); ext.set("cy", str(int(cy * k)))
    for ext in p.iter(A + "ext"):
        if ext.get("cx") and ext.get("cy"):
            cx, cy = int(ext.get("cx")), int(ext.get("cy"))
            k = width_emu / cx
            ext.set("cx", str(int(cx * k))); ext.set("cy", str(int(cy * k)))


def scale_drawing_h(p, height_emu):
    """Масштабирование рисунка по заданной высоте с сохранением пропорций."""
    for ext in p.iter(WP + "extent"):
        cx, cy = int(ext.get("cx")), int(ext.get("cy"))
        k = height_emu / cy
        ext.set("cx", str(int(cx * k))); ext.set("cy", str(int(cy * k)))
    for ext in p.iter(A + "ext"):
        if ext.get("cx") and ext.get("cy"):
            cx, cy = int(ext.get("cx")), int(ext.get("cy"))
            k = height_emu / cy
            ext.set("cx", str(int(cx * k))); ext.set("cy", str(int(cy * k)))


def _cap(e):
    return ptext(e).replace("\xa0", " ")


def scale_figure(doc, caption_start, width_cm):
    items = body_items(doc)
    for i, e in enumerate(items):
        if e.tag == W + "p" and _cap(e).startswith(caption_start):
            scale_drawing(items[i - 1], int(width_cm * 360000))
            return True
    return False


def figure_width_cm(doc, caption_start):
    items = body_items(doc)
    for i, e in enumerate(items):
        if e.tag == W + "p" and _cap(e).startswith(caption_start):
            for ext in items[i - 1].iter(WP + "extent"):
                return int(ext.get("cx")) / 360000
    return None


# ---------- рисунки рядом ----------
def make_row_table(cells, widths_tw):
    tbl = OxmlElement("w:tbl")
    pr = OxmlElement("w:tblPr")
    tw = OxmlElement("w:tblW"); tw.set(qn("w:w"), str(sum(widths_tw))); tw.set(qn("w:type"), "dxa"); pr.append(tw)
    jc = OxmlElement("w:jc"); jc.set(qn("w:val"), "center"); pr.append(jc)
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); pr.append(lay)
    mar = OxmlElement("w:tblCellMar")
    for side in ("left", "right"):
        m = OxmlElement("w:" + side); m.set(qn("w:w"), "85"); m.set(qn("w:type"), "dxa"); mar.append(m)
    pr.append(mar)
    tbl.append(pr)
    grid = OxmlElement("w:tblGrid")
    for w in widths_tw:
        g = OxmlElement("w:gridCol"); g.set(qn("w:w"), str(w)); grid.append(g)
    tbl.append(grid)
    tr = OxmlElement("w:tr")
    trpr = OxmlElement("w:trPr"); trpr.append(OxmlElement("w:cantSplit")); tr.append(trpr)
    for paras, w in zip(cells, widths_tw):
        tc = OxmlElement("w:tc")
        tcpr = OxmlElement("w:tcPr")
        tcw = OxmlElement("w:tcW"); tcw.set(qn("w:w"), str(w)); tcw.set(qn("w:type"), "dxa"); tcpr.append(tcw)
        tc.append(tcpr)
        for p in paras:
            tc.append(p)
        tr.append(tc)
    tbl.append(tr)
    return tbl


def figs_side_by_side(doc, cap_a, cap_b, table_caption, width_cm=7.8, height_cm=None):
    """Смежные пары «рисунок + подпись» cap_a, cap_b помещаются в таблицу 1x2 без границ.
    Таблица с подписью table_caption, пустая строка за ней и ряд рисунков удерживаются на одной странице."""
    items = body_items(doc)
    idx = {}
    for i, e in enumerate(items):
        if e.tag == W + "p":
            t = _cap(e)
            if t.startswith(cap_a): idx["a"] = i
            if t.startswith(cap_b): idx["b"] = i
            if t.strip() == table_caption: idx["t"] = i
    if len(idx) < 3 or idx["b"] != idx["a"] + 2:
        return False
    ia, ib = idx["a"], idx["b"]
    pa, ca, pb, cb = items[ia - 1], items[ia], items[ib - 1], items[ib]
    anchor = pa.getprevious()
    for p in (pa, pb):
        if height_cm:
            scale_drawing_h(p, int(height_cm * 360000))
        else:
            scale_drawing(p, int(width_cm * 360000))
        set_keepnext(p)
    for c in (pa, ca, pb, cb):
        c.getparent().remove(c)
    tbl = make_row_table([[pa, ca], [pb, cb]], [4677, 4677])
    anchor.addnext(tbl)
    nxt = items[idx["t"]]
    while nxt is not None and nxt is not tbl:
        if nxt.tag == W + "tbl":
            for p in nxt.iter(W + "p"):
                set_keepnext(p)
        elif nxt.tag == W + "p":
            set_keepnext(nxt)
        nxt = nxt.getnext()
    return True


# ---------- замеры по PDF ----------
def soffice_pdf(docx_path, outdir=TMP):
    os.makedirs(outdir, exist_ok=True)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, docx_path], capture_output=True)
    return os.path.join(outdir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")


def parse_lines(pdf):
    xml = subprocess.run(["pdftotext", "-bbox-layout", pdf, "-"], capture_output=True).stdout.decode("utf-8", "ignore")
    xml = re.sub(r"<!DOCTYPE[^>]*>", "", xml).replace("xmlns=", "xmlnsx=")
    root = ET.fromstring(xml)
    pages, H = [], []
    for pg in root.iter("page"):
        H.append(float(pg.get("height")))
        ls = []
        for ln in pg.iter("line"):
            tx = " ".join(w.text or "" for w in ln.iter("word"))
            ls.append((float(ln.get("yMin")), float(ln.get("yMax")), float(ln.get("xMin")), tx))
        ls.sort(key=lambda z: (round(z[0]), z[2]))
        merged = []
        for y0, y1, x0, tx in ls:
            if merged and abs(merged[-1][0] - y0) < 2:
                m = merged[-1]
                merged[-1] = (m[0], max(m[1], y1), m[2] + " " + tx)
            else:
                merged.append((y0, y1, tx))
        pages.append(merged)
    return pages, H


def content_bottoms(pdf, H, dpi=40):
    """для каждой страницы: нижняя граница содержимого тела (пт)"""
    out = os.path.join(TMP, "px")
    os.makedirs(out, exist_ok=True)
    for f in glob.glob(os.path.join(out, "q-*.png")):
        os.remove(f)
    subprocess.run(["pdftoppm", "-r", str(dpi), "-gray", "-png", pdf, os.path.join(out, "q")], capture_output=True)
    fs = sorted(glob.glob(os.path.join(out, "q-*.png")))
    res = []
    for i, f in enumerate(fs):
        a = np.array(Image.open(f).convert("L"))
        h = a.shape[0]
        lim = int(h * BODY_LIM)
        rows = np.where((a[:lim] < 200).sum(1) > 0)[0]
        res.append(rows.max() / h * H[i] if len(rows) else 0.0)
    return res


def find_start(pages, key, pos):
    k = norm(key)[:12]
    pi, li = pos
    for p in range(pi, len(pages)):
        for l in range(li if p == pi else 0, len(pages[p])):
            if pages[p][l][0] > 0.925 * 842:
                continue
            cur = norm(pages[p][l][2])
            if cur.startswith(k):
                return p, l
            if len(cur) < len(k) and k.startswith(cur) and l + 1 < len(pages[p]):
                if (cur + norm(pages[p][l + 1][2])).startswith(k):
                    return p, l
    return None


def measure(pdf, targets):
    """targets: [{kind:'heading'|'para', text}] в порядке следования в документе."""
    pages, H = parse_lines(pdf)
    cb = content_bottoms(pdf, H)
    pos, res = (0, 0), []
    for t in targets:
        r = find_start(pages, t["text"], pos)
        if r is None:
            res.append({**t, "found": False})
            continue
        p, l = r
        Hp = H[p]
        lim = BODY_LIM * Hp
        full = norm(t["text"])
        if t["kind"] == "heading":
            acc, k = "", l
            while k < len(pages[p]):
                acc += norm(pages[p][k][2]); k += 1
                if len(acc) >= len(full) * 0.97 or acc != full[:len(acc)]:
                    break
            bottom = pages[p][k - 1][1]
            after = cb[p] - bottom
            n_text = len([x for x in pages[p][k:] if x[0] < lim])
            at_top = pages[p][l][0] < 90
            pos = (p, k)
            res.append({**t, "found": True, "page": p + 1, "after_pt": after, "n_text": n_text, "at_top": at_top,
                        "viol": (after < (MIN_LINES - 0.5) * LINE_PT) and not at_top})
        elif t["kind"] == "sec":
            pos = (p, l + 1)
            res.append({**t, "found": True, "page": p + 1, "at_top": pages[p][l][0] < 90, "viol": False})
        else:
            lines = [x for x in pages[p][l:] if x[0] < lim]
            shown = sum(len(norm(x[2])) for x in lines)
            split = shown < len(full) * 0.97
            pos = (p, l + 1)
            res.append({**t, "found": True, "page": p + 1, "n_text": len(lines), "split": split,
                        "viol": split and len(lines) < MIN_LINES})
    fill = [cb[i] / H[i] for i in range(len(pages))]
    return res, fill, len(pages)


def targets_of(doc):
    """цели замера: заголовки подразделов и абзацы после рисунков/таблиц"""
    tg = []
    items = body_items(doc)
    prev_fig = False
    for i, e in enumerate(items):
        if e.tag == W + "tbl":
            prev_fig = True
            continue
        if e.tag != W + "p":
            continue
        tx = ptext(e).strip()
        k = heading_kind(e)
        if k == "sub":
            tg.append({"kind": "heading", "text": tx})
            prev_fig = False
        elif k == "sec":
            tg.append({"kind": "sec", "text": tx})
            prev_fig = False
        elif k == "chap":
            prev_fig = False
        elif prev_fig and tx and not re.match(r"^(Рисунок|Таблица|Источник|Примечание)", tx.replace("\xa0", " ")) and len(tx) > 40:
            tg.append({"kind": "para", "text": tx})
            prev_fig = False
        else:
            c = tx.replace("\xa0", " ")
            if re.match(r"^Рисунок \d+", c):
                prev_fig = True
            elif tx and not re.match(r"^(Таблица|Источник|Примечание)", c):
                prev_fig = False
    return tg


def apply_flags(doc, flags):
    """flags: множество ключей norm(text)[:40] -> pageBreakBefore"""
    n = 0
    for e in doc.element.body:
        if e.tag == W + "p":
            tx = ptext(e).strip()
            if tx and norm(tx)[:40] in flags and not has_pb(e):
                set_pb(e, True)
                n += 1
    return n


def unkeep_captions(doc):
    """Подпись под рисунком не удерживается со следующим абзацем (иначе рисунок уходит на следующую страницу вместе с текстом)."""
    n = 0
    for e in doc.element.body.iter(W + "p"):
        c = ptext(e).replace("\xa0", " ").strip()
        if re.match(r"^Рисунок \d+", c) and len(c) < 400:
            ppr = _ppr(e)
            for k in ppr.findall(W + "keepNext"):
                ppr.remove(k)
            kn = OxmlElement("w:keepNext"); kn.set(qn("w:val"), "0")
            st = ppr.find(W + "pStyle")
            if st is not None: st.addnext(kn)
            else: ppr.insert(0, kn)
            n += 1
    return n


def clear_pb(doc, text_prefix_norm):
    for e in doc.element.body:
        if e.tag == W + "p" and norm(ptext(e).strip())[:40] == text_prefix_norm and has_pb(e):
            set_pb(e, False)

# -*- coding: utf-8 -*-
import copy, io, re, sys
from fmtlib import *
from docx.opc.constants import RELATIONSHIP_TYPE as RT
FILES = "/home/claude/work/final/files2/"
ORDER = ["00 Титульный лист, содержание, введение", "01 Глава 1", "02 Глава 2", "03 Глава 3", "04 Выводы", "05 Список литературы", "06 Приложения"]
OUT = "/home/claude/work/final/files2/Дипломный проект (полный текст)"
PP = ("jc", "ind", "spacing", "keepNext", "keepLines")
RP = ("rFonts", "sz", "szCs", "b", "bCs", "i", "iCs", "u", "caps", "color")
def q(t): return qn("w:" + t)
class Styles:
    def __init__(self, doc):
        self.root = doc.styles.element
        self.by = {s.get(q("styleId")): s for s in self.root.findall(q("style"))}
        dd = self.root.find(q("docDefaults"))
        self.dp = dd.find(q("pPrDefault") + "/" + q("pPr")) if dd is not None and dd.find(q("pPrDefault")) is not None else None
        self.dr = dd.find(q("rPrDefault") + "/" + q("rPr")) if dd is not None and dd.find(q("rPrDefault")) is not None else None
        self.default_p = next((s for s in self.root.findall(q("style")) if s.get(q("type")) == "paragraph" and s.get(q("default")) == "1"), None)
    def chain(self, sid):
        out = []; seen = set()
        while sid and sid in self.by and sid not in seen:
            seen.add(sid); s = self.by[sid]; out.append(s)
            b = s.find(q("basedOn")); sid = b.get(q("val")) if b is not None else None
        return out[::-1]
def merge_into(eff, el, tags):
    if el is None: return
    for c in el:
        t = c.tag.replace("{%s}" % WNS, "")
        if t not in tags: continue
        if t in ("spacing", "ind", "rFonts"):
            cur = eff.setdefault(t, {}); cur.update({k: v for k, v in c.attrib.items()})
        else:
            eff[t] = dict(c.attrib)
def write(parent, eff, tags_order, first=False):
    for t in list(parent):
        if t.tag.replace("{%s}" % WNS, "") in tags_order: parent.remove(t)
    for t in tags_order:
        if t in eff:
            e = OxmlElement("w:" + t)
            for k, v in eff[t].items(): e.set(k, v)
            parent.append(e)
def flatten(doc):
    S = Styles(doc)
    n = 0
    for p in doc.element.body.iter(q("p")):
        ppr = p.find(q("pPr"))
        pst = ppr.find(q("pStyle")).get(q("val")) if ppr is not None and ppr.find(q("pStyle")) is not None else (S.default_p.get(q("styleId")) if S.default_p is not None else None)
        chain = S.chain(pst)
        eff = {}; reff = {}
        merge_into(eff, S.dp, PP); merge_into(reff, S.dr, RP)
        for s in chain:
            merge_into(eff, s.find(q("pPr")), PP); merge_into(reff, s.find(q("rPr")), RP)
        pe = dict(eff)
        merge_into(pe, ppr, PP)
        sname = pst or ""
        lvl = {"Heading1": 0, "Heading2": 1, "Heading3": 2}.get(sname)
        if ppr is None:
            ppr = OxmlElement("w:pPr"); p.insert(0, ppr)
        # порядок: pStyle(убрать) keepNext keepLines pageBreakBefore ... spacing ind jc outlineLvl — сохраняем прочие элементы
        keep = [c for c in ppr if c.tag.replace("{%s}" % WNS, "") not in PP + ("pStyle", "outlineLvl", "rPr", "sectPr")]
        rpr_para = ppr.find(q("rPr")); sect = ppr.find(q("sectPr"))
        for c in list(ppr): ppr.remove(c)
        for t in ("keepNext", "keepLines"):
            if t in pe: ppr.append(OxmlElement("w:" + t))
        for c in keep: ppr.append(c)
        for t in ("spacing", "ind", "jc"):
            if t in pe:
                e = OxmlElement("w:" + t)
                for k, v in pe[t].items(): e.set(k, v)
                ppr.append(e)
        if lvl is not None:
            e = OxmlElement("w:outlineLvl"); e.set(qn("w:val"), str(lvl)); ppr.append(e)
        if rpr_para is not None: ppr.append(rpr_para)
        if sect is not None: ppr.append(sect)
        for r in p.findall(q("r")):
            rpr = r.find(q("rPr")); re_ = {k: dict(v) if isinstance(v, dict) else v for k, v in reff.items()}
            merge_into(re_, rpr, RP)
            if rpr is None:
                rpr = OxmlElement("w:rPr"); r.insert(0, rpr)
            others = [c for c in rpr if c.tag.replace("{%s}" % WNS, "") not in RP + ("rStyle",)]
            for c in list(rpr): rpr.remove(c)
            # Word требует порядок: rFonts b bCs i iCs caps color sz szCs u vertAlign...
            re_["rFonts"] = {qn("w:ascii"): "Times New Roman", qn("w:hAnsi"): "Times New Roman", qn("w:cs"): "Times New Roman", qn("w:eastAsia"): "Times New Roman"}
            re_.pop("color", None)
            for t in ("rFonts", "b", "bCs", "i", "iCs", "caps", "sz", "szCs", "u"):
                if t in re_:
                    e = OxmlElement("w:" + t)
                    for k, v in re_[t].items(): e.set(k, v)
                    rpr.append(e)
            for c in others: rpr.append(c)
        n += 1
    # таблицы: стиль сетки -> явные границы
    for t in doc.element.body.iter(q("tbl")):
        pr = t.find(q("tblPr"))
        st = pr.find(q("tblStyle")) if pr is not None else None
        if pr is not None and pr.find(q("tblBorders")) is None and st is not None and "Grid" in (st.get(q("val")) or ""):
            b = OxmlElement("w:tblBorders")
            for e in ("top", "left", "bottom", "right", "insideH", "insideV"):
                x = OxmlElement("w:" + e); x.set(qn("w:val"), "single"); x.set(qn("w:sz"), "4"); x.set(qn("w:space"), "0"); x.set(qn("w:color"), "000000"); b.append(x)
            pr.append(b)
        if st is not None: pr.remove(st)
    return n

def copy_parts(src, dst, el):
    """перенос изображений: r:embed -> новый rId в dst"""
    A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    cache = {}
    for node in el.iter():
        for att in (RNS + "embed", RNS + "link", RNS + "id"):
            rid = node.get(att)
            if rid and rid in src.part.rels:
                rel = src.part.rels[rid]
                if rel.reltype != RT.IMAGE: continue
                if rid not in cache:
                    new, _ = dst.part.get_or_add_image(io.BytesIO(rel.target_part.blob)); cache[rid] = new
                node.set(att, cache[rid])

def strip_sect(sp, keep_title=False):
    for t in list(sp):
        tag = t.tag.replace("{%s}" % WNS, "")
        if tag in ("footerReference", "headerReference", "pgNumType") or (tag == "titlePg" and not keep_title): sp.remove(t)
    return sp

docs = [Document(FILES + n + ".docx") for n in ORDER]
for d in docs: flatten(d); 
base = docs[0]
bbody = base.element.body
# ---- конец титульной части: sectPr в последнем абзаце
def end_with_sect(body, sp_src, keep_title=False):
    sp = strip_sect(copy.deepcopy(sp_src), keep_title)
    last = [c for c in body if c.tag != q("sectPr")][-1]
    if last.tag == q("p"):
        ppr = last.find(q("pPr"))
        if ppr is None: ppr = OxmlElement("w:pPr"); last.insert(0, ppr)
        ppr.append(sp)
    else:
        p = OxmlElement("w:p"); ppr = OxmlElement("w:pPr"); ppr.append(sp); p.append(ppr); last.addnext(p)
bsect = bbody.find(q("sectPr"))
end_with_sect(bbody, bsect, True)
bbody.remove(bsect)
for i, d in enumerate(docs[1:], 1):
    sb = d.element.body; ssp = sb.find(q("sectPr"))
    kids = [c for c in sb if c.tag != q("sectPr")]
    for c in kids:
        c2 = copy.deepcopy(c); copy_parts(d, base, c2)
        for sp_ in ([c2] if c2.tag == q('sectPr') else []) + list(c2.iter(q('sectPr'))): strip_sect(sp_)
        bbody.append(c2)
    if i < len(docs) - 1:
        end_with_sect(bbody, ssp)
    else:
        bbody.append(strip_sect(copy.deepcopy(ssp)))
# ---- колонтитулы: у первой секции и далее наследуются
base.sections[0].different_first_page_header_footer = True
page_footer(base.sections[0])
yo_doc(base)
base.save(OUT + ".docx")
print("saved", len(base.sections), "sections")

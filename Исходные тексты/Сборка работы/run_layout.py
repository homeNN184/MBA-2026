# -*- coding: utf-8 -*-
import sys, os, shutil, json, re
sys.path.insert(0, "/home/claude/work/final")
os.chdir("/home/claude/work/final")
import assemble2 as A
import layout as L
from docx import Document
B2 = A.B2
PRE = B2 + "/pre"
CFG = json.load(open("layout_cfg.json")) if os.path.exists("layout_cfg.json") else {}

def stage_build():
    paths, items = A.build()
    os.makedirs(PRE, exist_ok=True)
    for k in ("ch1", "ch2", "ch3", "ch3pdf"):
        shutil.copy(paths[k], f"{PRE}/{k}.docx")
    json.dump(paths, open(PRE + "/paths.json", "w"))
    print("snapshot ok")

def stage_layout(finalize=True):
    paths = json.load(open(PRE + "/paths.json"))
    log = {"sec_pb": [], "flags": {}, "fill": {}, "pages": {}}
    parts = {"ch1": ["ch1"], "ch2": ["ch2"], "ch3": ["ch3", "ch3pdf"]}
    for part, keys in parts.items():
        docs = {k: Document(f"{PRE}/{k}.docx") for k in keys}
        meas = keys[-1]
        for k, d in docs.items():
            if part == "ch2":
                ok = L.figs_side_by_side(d, "Рисунок 4", "Рисунок 5", "Таблица 3", CFG.get("fig45_cm", 7.8), CFG.get("fig45_h_cm", 5.2))
                if k == "ch2": log["fig45"] = ok
            L.unkeep_captions(d)
            for cap, w in CFG.get("scale", {}).get(part, {}).items():
                L.scale_figure(d, cap, w)
            for e in d.element.body:
                if L.heading_kind(e) == "sec" and not L.has_pb(e) and not re.match(r"^\d+\.1\s", L.ptext(e).strip()):
                    L.set_pb(e, True)
                    if k == meas: log["sec_pb"].append(L.ptext(e).strip())
        flags = set(); released = set()
        for f in CFG.get("flags", {}).get(part, []):
            flags.add(L.norm(f)[:40])
        for d in docs.values():
            L.apply_flags(d, flags)
        for it in range(10):
            tmp = f"{L.TMP}/{part}.docx"
            os.makedirs(L.TMP, exist_ok=True)
            docs[meas].save(tmp)
            pdf = L.soffice_pdf(tmp)
            tg = L.targets_of(docs[meas])
            res, fill, n = L.measure(pdf, tg)
            bad = [r for r in res if r.get("viol")]
            miss = [r for r in res if not r["found"]]
            print(part, "проход", it, "страниц", n, "нарушений", len(bad), "не найдено", len(miss))
            nopb = set()
            for r_ in res:
                if r_["kind"] == "sec" and r_["found"] and r_["at_top"] and r_["page"] > 1 and fill[r_["page"] - 2] < 0.25:
                    nopb.add(L.norm(r_["text"])[:40])
            nopb -= released
            if nopb:
                released |= nopb
                for d in docs.values():
                    for h in nopb: L.clear_pb(d, h)
                log.setdefault("released", []).extend(sorted(x["text"][:60] for x in res if L.norm(x["text"])[:40] in nopb))
                print(part, "освобождено разделов:", len(nopb))
                if not bad: continue
            if not bad:
                break
            new = set(L.norm(r["text"])[:40] for r in bad) - flags
            if not new:
                break
            flags |= new
            for d in docs.values():
                L.apply_flags(d, new)
            for r in bad:
                log["flags"].setdefault(part, []).append({"text": r["text"][:90], "kind": r["kind"], "page_before": r["page"], "lines": r.get("n_text")})
        log["fill"][part] = [round(x, 2) for x in fill]
        log["pages"][part] = n
        for k, d in docs.items():
            d.save(paths[k])
    json.dump(log, open("layout_log.json", "w"), ensure_ascii=False, indent=1)
    if finalize:
        A.finalize(paths)

if __name__ == "__main__":
    if sys.argv[1] == "build": stage_build()
    elif sys.argv[1] == "lay": stage_layout(finalize=("nofin" not in sys.argv))

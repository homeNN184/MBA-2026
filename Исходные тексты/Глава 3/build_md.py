# -*- coding: utf-8 -*-
import re, sys
sys.path.insert(0, ".")
from common import *
from formulas import FORM, SYM, NOTES
import part1, part2, part3, part4
sys.path.insert(0,"/home/claude/work/final")
import biblio
TOFF, FOFF, EQOFF, APOFF = 6, 15, 0, 1
body = "\n\n".join(m.text() for m in (part1, part2, part3, part4))
tabs, figs, eqs = {}, {}, []
for m in re.finditer(r"⟦(TAB|FIG|F):([a-z0-9]+)", body):
    kind, key = m.group(1), m.group(2)
    if kind == "TAB": tabs.setdefault(key, len(tabs) + 1)
    elif kind == "FIG": figs.setdefault(key, len(figs) + 1)
    else: eqs.append(key)
assert len(set(eqs)) == len(eqs)
eqn = {k: i + 1 for i, k in enumerate(eqs)}
def sub_marker(m):
    kind, rest = m.group(1), m.group(2)
    if kind == "TAB":
        key, title = rest.split("|", 1)
        return f'\n::: {{custom-style="TabNum"}}\nТаблица {TOFF+tabs[key]}\n:::\n\n::: {{custom-style="TabTitle"}}\n{title}\n:::\n'
    if kind == "FIG":
        key, f, w, title = rest.split("|", 3)
        return (f'\n::: {{custom-style="FigImg"}}\n![](/home/claude/work/fig/{f}){{width={w}cm}}\n:::\n\n'
                f'::: {{custom-style="FigCap"}}\nРисунок {FOFF+figs[key]}{NB}— {title}\n:::\n')
    return "\n$$" + FORM[rest] + "$$\n"
body = re.sub(r"⟦(TAB|FIG|F):([^⟧]+)⟧", sub_marker, body)
def sub_ref(m):
    k, key = m.group(1), m.group(2)
    return {"t": lambda: f"{TOFF+tabs[key]}", "f": lambda: f"{FOFF+figs[key]}", "e": lambda: f"({EQOFF+eqn[key]})"}[k]()
body = re.sub(r"⟦([tfe]):([a-z0-9]+)⟧", sub_ref, body)
# --- «где»-строки: символы в формулы
def where(line):
    head = "где "
    rest = line[len(head):]
    items = rest.split("; ")
    out = []
    for it in items:
        if " — " in it:
            l, d = it.split(" — ", 1)
            l = l.strip()
            if l in SYM: l = "$" + SYM[l] + "$"
            d = re.sub(r"(?<![\w$\\{^_])([A-Za-z])(?![\w$}])", r"$\1$", d)
            out.append(l + " — " + d)
        else:
            out.append(it)
    return head + "; ".join(out)
lines = body.split("\n")
lines = [where(l) if l.startswith("где ") else l for l in lines]
body = "\n".join(lines)
# --- обозначения вида R_s вне формул
def mathify(seg):
    def f(m):
        base, sub = m.group(1), m.group(2).strip("{}")
        sub = r"\text{%s}" % sub if re.search("[А-Яа-я]", sub) else sub
        return "$" + base + "_{" + sub + "}$"
    return re.sub(r"(?<![\w$])(R|Q|NPV|CF|E)_(\{[^{}]+\}|[A-Za-zА-Яа-я]+)(?![\w])", f, seg)
parts = re.split(r"(\$\$.*?\$\$|\$[^$\n]+\$)", body, flags=re.S)
body = "".join(p if i % 2 else mathify(p) for i, p in enumerate(parts))
# --- ссылки на источники вместо сносок
CIT = {"gao": (("gao",), None, None), "gost58048": (("gost58048",), "п. 5.1.2", "п. 5.1.2"), "gost58048p13": (("gost58048",), "п. 5.1.13", "п. 5.1.13"), "gost58048p15": (("gost58048",), "п. 4.15", "п. 4.15"),
       "pp87p22": (("a3",), "п. 22", "п. 22"), "pp87p4": (("a3",), "п. 4", "п. 4"), "grk49": (("a1",), "ст. 49", "ст. 49"), "grk49v38": (("a1",), "ст. 49, ч. 3.8", "ст. 49, ч. 3.8"), "grk49v39": (("a1",), "ст. 49, ч. 3.9–3.10", "ст. 49, ч. 3.9–3.10"),
       "sp68": (("a25",), "п. 6.6", "п. 6.6"), "doe": (("a40",), None, None), "p102": (("a38",), None, None), "cooper": (("cooper",), None, None),
       "iso10007": (("iso10007",), None, None), "iso31000": (("iso31000",), "п. 6.5.2–6.5.3", "п. 6.5"), "iec31010": (("iec31010",), None, None),
       "fz176": (("fz176",), None, None), "nk283": (("nk",), "ст. 283, п. 2.1", "ст. 283, п. 2.1"), "nk262": (("nk",), "ст. 262", "ст. 262"),
       "brasco": (("brasco",), None, None), "love": (("love",), None, None), "hwang": (("hwang",), None, None), "adkar": (("adkar",), None, None),
       "kotter": (("kotter",), None, None), "kcp": (("a19",), None, None), "p318": (("p318",), None, None), "invp": (("a20",), None, None), "predinv": (("a21",), None, None), "niokr": (("a27",), None, None), "k418": (("a26",), None, None), "p102pl": (("a38",), "п. 4.2.3, 4.2.7", "п. 4.2.3, 4.2.7"), "krishnan": (("krishnan",), None, None), "prof": (("p526",), None, None), "vk477": (("vk477",), "п. 2.5, 2.7–2.8, 11.3–11.4", None), "vilen": (("vilen",), None, None), "lukas": (("lukas",), None, None), "tsarev": (("tsarev",), None, None), "plotnikov": (("plotnikov",), None, None), "limit": (("limit",), None, None), "tebekin": (("tebekin",), None, None)}
seen = {}
def sub_note(m):
    k = m.group(1); ks, l1, l2 = CIT[k]
    seen[k] = seen.get(k, 0) + 1
    c = biblio.cite(*ks, loc=(l1 if seen[k] == 1 else l2))
    return " \\" + c[:-1] + "\\]"
body = re.sub(r"\[\^([a-z0-9]+)\]", sub_note, body)
# --- приложения: сдвиг номеров (Приложение 1 — Дорожная карта)
def shift_app(m):
    a = int(m.group(2)) + APOFF; b = m.group(4)
    return m.group(1) + str(a) + (("–" + str(int(b) + APOFF)) if b else "")
body = re.sub(r"(приложени[а-я]+ )(\d+)(–(\d+))?", shift_app, body)
body = body.replace("ё", "е").replace("Ё", "Е")
open("ch3.md", "w", encoding="utf-8").write(body)
print("tables", len(tabs), "figures", len(figs), "formulas", len(eqs), "chars", len(body))

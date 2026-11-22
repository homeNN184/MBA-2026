# -*- coding: utf-8 -*-
"""Единый алфавитный список литературы и карта ссылок для глав 1–3."""
import json, re
RAW = json.load(open("/home/claude/work/final/raw_src.json", encoding="utf-8"))
E = {}          # key -> text
C1 = {}         # номер в главе 1 -> key
for i, t in enumerate(RAW["c1"], 1):
    k = f"a{i}"; E[k] = t; C1[i] = k
for i, t in enumerate(RAW["c2"], 1):
    E[f"b{i}"] = t
# дубли и уточнения
C1[37] = "gost58048"; E["gost58048"] = E.pop("a37")
C1[31] = "nk"; E["nk"] = "Налоговый кодекс Российской Федерации (часть вторая) от 05.08.2000 № 117-ФЗ (с посл. изм. и доп.)."; E.pop("a31")
E.update({
 "vk477": "Методические рекомендации по оценке эффективности инвестиционных проектов (вторая редакция): утв. Минэкономики РФ, Минфином РФ, Госстроем РФ 21.06.1999 № ВК 477. – М.: Экономика, 2000.",
 "gao": "GAO-20-48G. Technology Readiness Assessment Guide: Best Practices for Evaluating the Readiness of Technology for Use in Acquisition Programs and Projects. – Washington: U.S. Government Accountability Office, 2020. URL: https://www.gao.gov/assets/710/704769.pdf (дата обращения: 05.11.2026).",
 "cooper": "Cooper R.G. Perspective: The Stage-Gate idea-to-launch process — update, what's new, and NexGen systems // Journal of Product Innovation Management. 2008. Vol. 25, No. 3. P. 213–232. DOI: 10.1111/j.1540-5885.2008.00296.x.",
 "gost15301": "ГОСТ Р 15.301-2016. Система разработки и постановки продукции на производство. Продукция производственно-технического назначения. Порядок разработки и постановки продукции на производство. – М.: Стандартинформ, 2017.",
 "iso10007": "ГОСТ Р ИСО 10007-2019. Менеджмент качества. Руководящие указания по менеджменту конфигурации. – М.: Стандартинформ, 2019.",
 "iso31000": "ГОСТ Р ИСО 31000-2019. Менеджмент риска. Принципы и руководство. – М.: Стандартинформ, 2020.",
 "iec31010": "ГОСТ Р МЭК 31010-2021. Менеджмент риска. Методы оценки риска. – М.: Российский институт стандартизации, 2021.",
 "fz176": "Федеральный закон от 12.07.2024 № 176-ФЗ «О внесении изменений в части первую и вторую Налогового кодекса Российской Федерации, отдельные законодательные акты Российской Федерации и признании утратившими силу отдельных положений законодательных актов Российской Федерации».",
 "brasco": "Brasco C.J., Anzidei C.M. Concurrent Delay and the Critical Path. – Navigant Consulting, 2014. URL: https://mail.mosaicprojects.com.au/PDF_Papers/P011_Concurrent_Delays-3.pdf (дата обращения: 05.11.2026).",
 "love": "Love P.E.D., Smith J. Unpacking the ambiguity of rework in construction: making sense of the literature // Civil Engineering and Environmental Systems. 2019. Vol. 35, No. 1–4. P. 180–203.",
 "hwang": "Hwang B.-G., Thomas S.R., Haas C.T., Caldas C.H. Measuring the impact of rework on construction cost performance // Journal of Construction Engineering and Management. 2009. Vol. 135, No. 3. P. 187–198.",
 "adkar": "Prosci. ADKAR: the core of the people side of change (дата обращения: 05.11.2026).",
 "krishnan": "Krishnan V., Eppinger S.D., Whitney D.E. A model-based framework to overlap product development activities // Management Science. 1997. Vol. 43, No. 4. P. 437–451.",
 "kotter": "Kotter J.P. Leading Change. – Boston: Harvard Business School Press, 1996.",
 "p318": "Приказ ПАО «Газпром» от 10.05.2017 № 318 «Об утверждении Порядка планирования и организации предынвестиционных исследований для инвестиционных проектов ПАО «Газпром», осуществляемых в форме капитального строительства» (с последующими изменениями).",
 "p526": "Приказ Минтруда России от 29.06.2017 № 526н «Об утверждении профессионального стандарта «Специалист по метрологии»».",
 "p231": "Приказ Минтруда России от 21.04.2022 № 231н (профессиональный стандарт в области организации строительства).",
 "vilen": "Виленский П. Л., Лившиц В. Н., Смоляк С. А. Оценка эффективности инвестиционных проектов. Теория и практика: учеб. пособие. – 4-е изд., перераб. и доп. – М.: Дело, 2008. – 1104 с.",
 "lukas": "Лукасевич И. Я. Инвестиции: учебник. – М.: Вузовский учебник: ИНФРА-М, 2013. – 412 с.",
 "tsarev": "Царев В. В. Оценка экономической эффективности инвестиций. – СПб.: Питер, 2004. – 460 с.",
 "plotnikov": "Плотников А. Н. Учет факторов риска и неопределенности при оценке эффективности инвестиционных проектов: учеб. пособие. – Саратов: СГТУ, 1998. – 76 с.",
 "limit": "Лимитовский М. А. Современные технологии обоснования инвестиционных и финансовых решений: дайджест теории и кейсы. – 2-е изд., доп. – М.: ВШФМ, 2009. – 212 с.",
 "tebekin": "Тебекин А. В. Методы принятия управленческих решений: учебник для бакалавров. – М.: Юрайт, 2013. – 572 с.",
 "p562": "Приказ Минтруда России от 14.10.2024 № 562н (профессиональный стандарт в области информационного моделирования в строительстве).",
})
# ё -> е
for k in E: E[k] = E[k].replace("ё", "е").replace("Ё", "Е")
# нормализация тире/дефисов в ГОСТ
E["gost58048"] = E["gost58048"].replace("58048–2017", "58048-2017")
# ---- сортировка: кириллица (по названию/автору), затем латиница
def skey(t):
    s = t.lower().replace("ё", "е")
    s = re.sub(r"[«»\"“”]", "", s)
    m = re.match(r"^(.*?) от (\d\d)\.(\d\d)\.(\d{4})\s*(.*)$", s)
    if m: s = f"{m.group(1)} {m.group(4)}{m.group(3)}{m.group(2)} {m.group(5)}"
    return s
def is_cyr(t): return bool(re.match(r"^[А-Яа-яЁё]", t))
keys = sorted(E, key=lambda k: (0 if is_cyr(E[k]) else 1, skey(E[k])))
ADDED_AFTER_BASE = ("krishnan",)
NUM = {k: i + 1 for i, k in enumerate(keys)}
LIST = [(NUM[k], E[k]) for k in keys]
def cite(*keys_, loc=None):
    ns = sorted(NUM[k] for k in keys_)
    s = ", ".join(str(n) for n in ns)
    if loc: s += ", " + loc
    return "[" + s + "]"
def ch1_map(): return {i: NUM[k] for i, k in C1.items()}
# ---- сноски главы 2 (id -> keys)
CH2_FN = {"0": ("b1",), "1": ("b4",), "3": ("b13",), "4": ("b14", "b15"), "5": ("b16",), "6": ("b16",), "10": ("b17",), "15": ("b22",), "16": ("b23",)}
if __name__ == "__main__":
    for n, t in LIST: print(n, t[:110])
    print(len(LIST))
